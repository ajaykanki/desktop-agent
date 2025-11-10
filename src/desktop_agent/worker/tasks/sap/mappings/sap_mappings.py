from dataclasses import dataclass
from enum import Enum


class ElementType(str, Enum):
    TEXT = "TEXT"
    BUTTON = "BUTTON"
    TABLE = "TABLE"
    CHECKBOX = "CHECKBOX"
    RADIOBUTTON = "RADIOBUTTON"
    SHELL = "SHELL"


class ActionType(str, Enum):
    CLICK = "CLICK"
    ENTER = "ENTER"
    BACK = "BACK"


@dataclass
class Action:
    type: ActionType
    target_id: str | None = None  # GuiElement ID for CLICK action
    description: str | None = None


@dataclass
class CallInternalFunction:
    func: str
    params: list[str] | None
    description: str | None = None


@dataclass
class SetInternalAttribute:
    attribute: str
    value: str | None = None
    description: str | None = None


@dataclass
class GuiElement:
    id: str
    type: ElementType = ElementType.TEXT
    set_attributes: list[SetInternalAttribute] | None = None
    call_functions: list[CallInternalFunction] | None = None


@dataclass
class Screen:
    name: str
    elements: dict[str, GuiElement]
    entry_point: list[Action] | None = (
        None  # Actions to perform to reach this screen. This is like pre_actions
    )
    press_enter: bool = True  # Whether to press enter after filling all fields


@dataclass
class ScreenOrder:
    name: str
    post_actions: list[Action] | Action | None = None


PRESS_HEADER_BUTTON_ACTION = Action(
    type=ActionType.CLICK,
    target_id=r"wnd[0]/usr/subSUBSCREEN_HEADER:SAPMV45A:4021/btnBT_HEAD",
    description="Click header data button",
)
