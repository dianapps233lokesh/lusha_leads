from pydantic import BaseModel


class ContactSearchRequest(BaseModel):
    search_text: str
