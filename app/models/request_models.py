from pydantic import BaseModel


class ContactSearchRequest(BaseModel):
    search_text: str


class CompanyFounderRequest(BaseModel):
    company_name: str
    founder_name: str
