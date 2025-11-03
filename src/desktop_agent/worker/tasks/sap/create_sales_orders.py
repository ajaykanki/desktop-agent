import polars as pl
from sap_gui_engine import SAPGuiEngine, VKey
from rpa_toolkit.excel import read_excel
from typing import Any
from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_fixed, Retrying, RetryError
from desktop_agent.logger import logger
from desktop_agent.worker.core import sapConfig, task
from sap_gui_engine.objects.gui_session import GuiSession
from .mappings import (
    ScreenOrder,
    Screen,
    ActionType,
    ElementType,
    Action,
    VA01_MAPPINGS,
)


# For all the tasks going in the same queue, you must use the same lock for all task if you want them to execute sequentially.
@task(name="create_sales_orders", lock="sap")
def create_sales_orders(
    po_working: str,
    va01_details: dict[str, Any],
    screen_order: list[dict[str, Any]] = None,
):
    logger.info("Converting screen_order to list of ScreenOrder objects...")
    screen_order_objects = [
        ScreenOrder(
            name=screen.get("name"),
            post_actions=[Action(**action) for action in screen.get("post_actions")],
        )
        if isinstance(screen, dict)
        else ScreenOrder(name=screen)
        for screen in screen_order
    ]

    logger.info("Checking if PO working file exists...")
    check_if_po_file_exists(po_working)

    logger.info("Reading the po working file...")
    df = read_excel(po_working, drop_empty_cols=False, drop_empty_rows=False).collect()
    df = insert_sales_order_col(df)

    logger.info("Collecting sales order data as per the gaps in the excel sheet...")
    sales_orders = collect_sales_orders_data(df)

    total_sales_orders = len(sales_orders)
    logger.info("Total Sales Orders to be created: {}", total_sales_orders)

    sap = init_sap_and_login()
    for so_count, line_items in sales_orders.items():
        logger.info(f"Creating sales order {so_count} of {total_sales_orders}")
        try:
            so_number = va01(
                sap.session, line_items, va01_details, screen_order_objects
            )
        except Exception as e:
            error_message = str(e)
            logger.error(e)
            # TODO: Capture screenshot
            # TODO: Create error object
            # TODO: Update line items with this error message back in dataframe
        finally:
            # TODO: Save df to write changes
            pass


def va01(
    session: GuiSession,
    line_items: list[dict[str, Any]],
    va01_details: dict[str, Any],
    screen_order: list[ScreenOrder],
) -> str:
    session.start_transaction("va01")

    for screen in screen_order:
        current_data = line_items
        mapping: Screen | None = VA01_MAPPINGS.get(screen.name)
        if not mapping:
            raise ValueError(
                f"Mappings not found for screen: {screen.name} in VA01_MAPPINGS"
            )

        logger.info("Current screen: {name}", name=screen.name)

        # Perform entry point actions
        if mapping.entry_point:
            perform_entry_point_actions(session, mapping)

        # Change current data for initial screen
        if screen.name == "VA01_INITIAL":
            current_data = va01_details

        fill_screen(session, mapping, current_data)

        # Perform post actions specified by the user in screen_order
        if screen.post_actions:
            perform_post_actions(session, screen)

    # Save document
    # Get document number
    # Return document number
    # TODO: Set partner function, and partner in po_working file


@retry(reraise=True, stop=stop_after_attempt(2), wait=wait_fixed(1))
def fill_screen(
    session: GuiSession,
    screen: Screen,
    data: list[dict[str, Any]] | dict[str, Any],
):
    for element in screen.elements:
        # Use only the first row of the data for fields
        current_data = data[0] if isinstance(data, list) else data
        if element.type == ElementType.TABLE:
            current_data = data
            # TODO: fill table here. We don't need to retry filling table As we are capturing errors while filling table.
            continue
        elif element.type == ElementType.SHELL:
            # Set attributes and call internal functions for SHELL type
            if element.call_functions:
                for item in element.call_functions:
                    el = session.findById(element.id).element
                    if hasattr(el, item.func):
                        logger.info(
                            "Calling internal function: {func} of element {name} with params: {params}",
                            func=item.func,
                            name=element.name,
                            params=item.params,
                        )
                        getattr(el, item.func)(*item.params)
                    else:
                        logger.error(
                            "Internal function {func} not found for element {name}",
                            func=item.func,
                            name=element.name,
                        )
            if element.set_attributes:
                for item in element.set_attributes:
                    el = session.findById(element.id).element
                    if hasattr(el, item.attribute):
                        logger.info(
                            "Setting attributes: {attr} of element {name} with value: {value}",
                            func=item.attribute,
                            name=element.name,
                            value=item.value,
                        )
                        setattr(el, item.attribute, item.value)
                    else:
                        logger.error(
                            "Attribute {attr} not found for element {name}",
                            attr=item.attribute,
                            name=element.name,
                        )
        elif element.type == ElementType.BUTTON:
            pass
        else:
            # must be a text/combobox for now
            logger.info(
                "Setting element: {name} of type {type} in screen: {screen}",
                name=element.name,
                type=element.type.value,
                screen=screen.name,
            )
            # Set element with retrying.
            try:
                for attempt in Retrying(
                    reraise=True,
                    stop=stop_after_attempt(3),
                    wait=wait_fixed(1),
                ):
                    with attempt:
                        try:
                            if element.name in current_data:
                                session.findById(element.id).text = current_data[
                                    element.name
                                ]
                        except Exception as e:
                            # Press enter before retrying
                            logger.error(str(e))
                            session.press_enter()
                            raise e
            except RetryError:
                pass

    # Press a final enter after filling all fields in the screen
    # Check for errors in status bar
    if screen.press_enter:
        logger.info("Pressing enter for screen {}", screen.name)
        session.press_enter()
        session.dismiss_popups_until_none()
        status_bar = session.get_status_info()
        if status_bar["type"] == "E":
            # Retry filling entire screen
            logger.info("Error in status bar: {message}", message=status_bar["message"])
            logger.info("Retrying entire screen")
            raise ValueError(status_bar["message"])


def perform_post_actions(session: GuiSession, screen: ScreenOrder):
    for action in screen.post_actions:
        logger.info(
            "Performing post action: {action} in screen {name} at target: {target_id}Description: {description}",
            action=action.description,
            name=screen.name,
            target_id=action.target_id,
            description=action.description,
        )
        if action.type == ActionType.CLICK:
            session.findById(action.target_id).click()
        elif action.type == ActionType.ENTER:
            session.press_enter()
        elif action.type == ActionType.BACK:
            session.sendVKey(VKey.F3)


def perform_entry_point_actions(session: GuiSession, screen: Screen):
    for action in screen.entry_point:
        logger.info(
            "Performing entry point action: {action} for screen {name} at target: {target_id} Description: {description}",
            action=action.type.value,
            name=screen.name,
            target_id=action.target_id,
            description=action.description,
        )
        if action.type == ActionType.CLICK:
            try:
                session.findById(action.target_id).click()
            except Exception:
                logger.info(
                    "Already executed entry point for this screen or target_id not found."
                )
        elif action.type == ActionType.ENTER:
            session.press_enter()
        elif action.type == ActionType.BACK:
            session.sendVKey(VKey.F3)


@retry(reraise=True, stop=stop_after_attempt(3), wait=wait_fixed(3))
def init_sap_and_login():
    sap = SAPGuiEngine(
        connection_name=sapConfig.connection_name,
        window_title=sapConfig.window_title,
        executable_path=sapConfig.executable_path,
    )
    sap.login(sapConfig.username, sapConfig.password)
    return sap


@retry(reraise=True, stop=stop_after_attempt(3), wait=wait_fixed(1))
def collect_sales_orders_data(df: pl.DataFrame) -> dict[str, list[dict[str, Any]]]:
    sales_orders = {}
    so_count = 1
    for row in df.iter_rows(named=True):
        # We would to collect all rows until we find an empty po number. These rows would mark the end of line items in the current sales order.
        if row.get("po number") is not None:
            # Create empty list in sales_order for current so_count if not exists
            # This list would contain all records/line items in dictionary format
            if so_count not in sales_orders:
                sales_orders[so_count] = []
            sales_orders[so_count].append(row)
            continue

        # This means that we have encountered a gap in the excel sheet, so next non-empty row would be the start of a new sales order
        so_count += 1
    return sales_orders


@retry(reraise=True, stop=stop_after_attempt(3), wait=wait_fixed(1))
def insert_sales_order_col(df: pl.DataFrame) -> pl.DataFrame:
    if "po number" in df.columns:
        idx = df.columns.index("po number")
        df.insert_column(idx + 1, pl.Series("sales order", [None] * len(df)))
    else:
        # insert after 1st column
        df.insert_column(1, pl.Series("sales order", [None] * len(df)))

    return df


@retry(reraise=True, stop=stop_after_attempt(3), wait=wait_fixed(5))
def check_if_po_file_exists(file_path: str) -> bool:
    if not Path(file_path).exists():
        raise FileNotFoundError(
            f"PO working file not found at {file_path} or Network drive may be down. Please check"
        )

    return True
