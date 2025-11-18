import polars as pl
import re
from procrastinate import JobContext
from typing import Any
from pathlib import Path
from tenacity import (
    retry,
    stop_after_attempt,
    wait_fixed,
    Retrying,
    RetryError,
)
from app.logging import log
from app.worker.core import task
from app.config import config

from rpatoolkit.df import read_excel
from sap_gui_engine import SAPGuiEngine, VKey
from sap_gui_engine.objects.gui_session import GuiSession
from .mappings import (
    ScreenOrder,
    Screen,
    ActionType,
    ElementType,
    Action,
    VA01_MAPPINGS,
)


def safe_filename(s: str, max_length: int = 150) -> str:
    # Replace forbidden characters
    s = re.sub(r'[<>:"/\\|?*]', "_", s)

    # Replace whitespace/newlines/tabs
    s = re.sub(r"\s+", "_", s.strip())

    # Remove other problematic characters
    s = re.sub(r"[',;`~]", "_", s)

    # Remove non-printable/control chars
    s = "".join(c for c in s if 32 <= ord(c) < 127)

    # Avoid reserved names
    reserved = {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        *(f"COM{i}" for i in range(1, 10)),
        *(f"LPT{i}" for i in range(1, 10)),
    }
    if s.upper().split(".")[0] in reserved:
        s = f"_{s}"

    # Truncate to max length (keep .png suffix space)
    s = s[:max_length]
    return s


# For all the tasks going in the same queue, you must use the same lock for all task if you want them to execute sequentially.
# All tasks first parameter must be the JobContext
@task(name="create_sales_orders", pass_context=True, lock="sap", queue="sap")
def create_sales_orders(
    context: JobContext,
    po_working_path: str,
    va01_details: dict[str, Any],
    screen_order: list[dict[str, Any]],
):
    log.info("Converting screen_order to list of ScreenOrder objects...")
    screen_order_objects = [
        ScreenOrder(
            name=screen.get("name"),
            post_actions=[Action(**action) for action in screen.get("post_actions")]
            if isinstance(screen.get("post_actions"), list)
            else Action(**screen.get("post_actions")),
        )
        if isinstance(screen, dict)
        else ScreenOrder(name=screen)
        for screen in screen_order
    ]

    log.info("Checking if PO working file exists...")
    po_working_path = validate_and_merge_base_path(
        config.worker.network_drive_letter, po_working_path
    )

    log.info("Reading the po working file...")
    df = read_excel(
        po_working_path, drop_empty_cols=False, drop_empty_rows=False
    ).collect()
    df = insert_sales_order_col(df)

    log.info("Collecting sales order data from the excel sheet...")
    sales_orders = collect_sales_orders_data(df)

    total_sales_orders = len(sales_orders)
    log.info("Total sales orders to be created: {}", total_sales_orders)

    sap = init_sap_and_login()

    # Create an empty output dataframe with the same schema as the input dataframe
    output_df = pl.DataFrame(schema=df.schema)
    error_df = pl.DataFrame(
        schema=df.schema
    )  #  Send as attachment if some so creation fails
    error_list = []  # PO Number and Screenshot Path
    for so_count, line_items in sales_orders.items():
        log.info(f"Creating sales order {so_count} of {total_sales_orders}")

        so_number = None
        error_message = None

        try:
            so_number = va01(
                sap.session, line_items, va01_details, screen_order_objects
            )
        except Exception as e:
            error_message = str(e)
            log.error(
                "Error creating sales order {so_count} of {total_sales_orders}: {error_message} : {e}",
                so_count=so_count,
                total_sales_orders=total_sales_orders,
                error_message=error_message,
                e=e,
            )
            screenshot_path = f"{po_working_path.parent}/screenshot_{so_count}_{line_items[0].get('po number')}_{safe_filename(error_message)}.png"
            sap.session.take_screenshot(screenshot_path, window=1, format="png")
            log.info(f"Screenshot saved to {screenshot_path}")
            error_list.append(
                {
                    "type": type(e).__name__,
                    "message": error_message,
                    "po number": line_items[0].get("po number", None),
                    "screenshot_path": screenshot_path,
                }
            )
        finally:
            # Update line items with error message or the sales order number
            for item in line_items:
                item["sales order"] = so_number if so_number else error_message

            # Add a blank row to line_items
            if so_count != total_sales_orders:
                line_items.append({key: None for key in line_items[0].keys()})

            # Create a new temporary dataframe with the updated line items
            df = pl.DataFrame(data=line_items)

            # Append this updated dataframe to the main output or error df
            df_to_write = error_df if error_message else output_df
            suffix = ".errors.xlsx" if error_message else ".updated.xlsx"

            df_to_write.extend(df)
            output_path = po_working_path.with_suffix(suffix)
            df_to_write.write_excel(
                output_path,
                autofit=True,
                dtype_formats={pl.Int64: "0"},
                header_format={"bold": True, "bg_color": "yellow", "border": 1},
                freeze_panes=(1, 2),  # First header row, and first two columns
            )

    so_created = total_sales_orders - len(error_list)
    so_failed = len(error_list)
    log.info(
        "Sales orders created: {created} and failed: {failed}",
        created=so_created,
        failed=so_failed,
    )
    return {
        "total_sales_orders": total_sales_orders,
        "sales_orders_created": so_created,
        "sales_orders_failed": so_failed,
        "error_list": error_list,
        "output_path": output_path,
        "error_path": output_path.with_suffix(".errors.xlsx")
        if len(error_list) > 0
        else None,
    }


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

        log.info("Current screen: {name}", name=screen.name)

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
    log.info("Saving Document")
    session.sendVKey(VKey.CTRL_S)
    session.dismiss_popups()
    # Check for GuiModalWindow which is not a popup dialog (F8)
    error_message = session.check_for_error_dialog()
    if error_message:
        raise RuntimeError(error_message)

    doc_number = session.get_document_number()
    log.info("Sales Order saved with document number: {}", doc_number)
    return doc_number


def attach_pis(session: GuiSession, pis: str, select_all_id: str):
    session.findById(select_all_id).click()
    session.findById("wnd[0]/mbar/menu[3]/menu[10]").select()
    session.findById(
        r"wnd[1]/usr/tblSAPLCVOBTCTRL_DOKUMENTE/ctxtDRAW-DOKAR[0,0]"
    ).text = "PIS"
    session.findById(
        r"wnd[1]/usr/tblSAPLCVOBTCTRL_DOKUMENTE/ctxtDRAW-DOKNR[1,0]"
    ).text = pis
    session.press_enter()


# @retry(
# reraise=True,
# stop=stop_after_attempt(2),
# wait=wait_fixed(1),
# retry=retry_if_not_exception_type(TableConfigurationError),
# )
def fill_screen(
    session: GuiSession,
    screen: Screen,
    data: list[dict[str, Any]] | dict[str, Any],
):
    for element_name, element in screen.elements.items():
        # Use only the first row of the data for fields
        current_data = data[0] if isinstance(data, list) else data
        if element.type == ElementType.TABLE:
            current_data = data
            session.fill_table(id=element.id, data=current_data)
            pis = data[0].get("pis", None)
            log.info("Attaching PIS: {}", pis)
            if pis:
                attach_pis(
                    session, data[0]["pis"], screen.elements.get("select all").id
                )
                session.dismiss_popups()
        elif element.type == ElementType.SHELL:
            # Set attributes and call internal functions for SHELL type
            if element.call_functions:
                for item in element.call_functions:
                    el = session.findById(element.id).element
                    if hasattr(el, item.func):
                        log.info(
                            "Calling internal function: {func} of element {name} with params: {params}",
                            func=item.func,
                            name=element_name,
                            params=item.params,
                        )
                        getattr(el, item.func)(*item.params)
                    else:
                        log.error(
                            "Internal function {func} not found for element {name}",
                            func=item.func,
                            name=element_name,
                        )
            if element.set_attributes:
                for item in element.set_attributes:
                    el = session.findById(element.id).element
                    if hasattr(el, item.attribute):
                        log.info(
                            "Setting attributes: {attr} of element {name} with value: {value}",
                            func=item.attribute,
                            name=element_name,
                            value=item.value,
                        )
                        setattr(el, item.attribute, item.value)
                    else:
                        log.error(
                            "Attribute {attr} not found for element {name}",
                            attr=item.attribute,
                            name=element_name,
                        )
        elif element.type == ElementType.TEXT:
            # must be a text/combobox for now
            log.info(
                "Setting element: {name} of type {type} in screen: {screen}",
                name=element_name,
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
                            if (
                                element_name in current_data
                                and current_data[element_name]
                            ):
                                session.findById(element.id).text = current_data[
                                    element_name
                                ]
                        except Exception as e:
                            # Press enter before retrying
                            log.error(str(e))
                            session.press_enter()
                            raise e
            except RetryError:
                pass

    # Press a final enter after filling all fields in the screen
    # Check for errors in status bar
    if screen.press_enter:
        log.info("Pressing enter for screen {}", screen.name)
        session.press_enter()
        session.dismiss_popups()
        status_bar = session.get_status_info()
        if status_bar["type"] == "E":
            # Retry filling entire screen
            log.info("Error in status bar: {message}", message=status_bar["message"])
            log.info("Retrying entire screen")
            raise ValueError(status_bar["message"])


def perform_post_actions(session: GuiSession, screen: ScreenOrder):
    if isinstance(screen.post_actions, list):
        for action in screen.post_actions:
            log.info(
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

            session.dismiss_popups()
    else:
        log.info(
            "Performing post action: {action} in screen {name} at target: {target_id}",
            action=screen.post_actions.description,
            name=screen.name,
            target_id=screen.post_actions.target_id,
            description=screen.post_actions.description,
        )
        if screen.post_actions.type == ActionType.CLICK:
            session.findById(screen.post_actions.target_id).click()
        elif screen.post_actions.type == ActionType.ENTER:
            session.press_enter()
        elif screen.post_actions.type == ActionType.BACK:
            session.sendVKey(VKey.F3)

        session.dismiss_popups()


def perform_entry_point_actions(session: GuiSession, screen: Screen):
    for action in screen.entry_point:
        log.info(
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
                log.info(
                    "Already executed entry point for this screen or target_id not found."
                )
        elif action.type == ActionType.ENTER:
            session.press_enter()
        elif action.type == ActionType.BACK:
            session.sendVKey(VKey.F3)


@retry(reraise=True, stop=stop_after_attempt(3), wait=wait_fixed(3))
def init_sap_and_login():
    sap = SAPGuiEngine(
        connection_name=config.sap.connection_name,
        window_title=config.sap.window_title,
        executable_path=config.sap.executable_path,
    )
    sap.login(config.sap.username, config.sap.password)
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
        df.insert_column(
            idx + 1, pl.Series("sales order", [None] * len(df), dtype=pl.String)
        )
    else:
        # insert after 1st column
        df.insert_column(1, pl.Series("sales order", [None] * len(df), dtype=pl.String))

    return df


@retry(reraise=True, stop=stop_after_attempt(3), wait=wait_fixed(5))
def validate_and_merge_base_path(base_path: str, file_path: str) -> Path:
    merged_path = Path(base_path) / file_path

    if not Path(merged_path).exists():
        raise FileNotFoundError(
            f"File not found at {file_path} or Network drive may be down. Please check"
        )

    return merged_path
