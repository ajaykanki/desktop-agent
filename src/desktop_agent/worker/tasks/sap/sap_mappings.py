from pydantic import BaseModel
from enum import Enum


class ElementType(str, Enum):
    TEXT = "TEXT"
    BUTTON = "BUTTON"
    COMBOBOX = "COMBOBOX"
    TABLE = "TABLE"
    CHECKBOX = "CHECKBOX"
    RADIOBUTTON = "RADIOBUTTON"
    TREE = "TREE"


class ActionType(str, Enum):
    CLICK = "CLICK"
    PRESS_ENTER = "PRESS_ENTER"
    BACK = "BACK"


class Action(BaseModel):
    type: ActionType
    target_id: str | None = None  # GuiElement ID for CLICK action
    description: str | None = None


class GuiElement(BaseModel):
    id: str
    name: str
    type: ElementType = ElementType.TEXT


class Screen(BaseModel):
    name: str
    elements: list[GuiElement]
    entry_point: list[Action] | None = (
        None  # Actions to perform to reach this screen. This is like pre_actions
    )
    post_actions: list[Action] | None = None


PRESS_ENTER_ACTION = Action(type=ActionType.PRESS_ENTER)

PRESS_HEADER_BUTTON_ACTION = Action(
    type=ActionType.CLICK,
    target_id=r"wnd[0]/usr/subSUBSCREEN_HEADER:SAPMV45A:4021/btnBT_HEAD",
    description="Click header data button",
)
