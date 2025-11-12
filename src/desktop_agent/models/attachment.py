from pydantic import BaseModel


class Attachment(BaseModel):
    name: str
    content: str
