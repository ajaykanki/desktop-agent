from enum import Enum, auto
from pydantic import BaseModel


class ActionType(str, Enum):
    FILL = "FILL"
    EDIT = "EDIT"


class PostActionType(str, Enum):
    PRESS_ENTER = "PRESS_ENTER"
    CLICK = "CLICK"
    BACK = "BACK"


class Screen(BaseModel):
    name: str
    action: ActionType = ActionType.FILL
    post_action: PostActionType | None = PostActionType.PRESS_ENTER
