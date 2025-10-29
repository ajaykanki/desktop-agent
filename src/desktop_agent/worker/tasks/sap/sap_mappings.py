from pydantic import BaseModel
from typing import Any, auto
from enum import Enum


class ElementType(str, Enum):
    TEXT = "TEXT"
    BUTTON = "BUTTON"
    COMBOBOX = "COMBOBOX"
    TABLE = "TABLE"
    CHECKBOX = "CHECKBOX"
    RADIOBUTTON = "RADIOBUTTON"


class ActionType(str, Enum):
    CLICK = "CLICK"
    PRESS_ENTER = "PRESS_ENTER"


class GuiElement(BaseModel):
    id: str
    name: str
    type: ElementType


class EntryPoint(BaseModel):
    """The entry point for a screen. This tells us how to reach the screen."""

    element: GuiElement
    action: ActionType = ActionType.PRESS_ENTER


class Screen(BaseModel):
    name: str
    entry_point: EntryPoint | None = None
    