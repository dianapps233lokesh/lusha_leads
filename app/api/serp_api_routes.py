from fastapi import APIRouter

from app.models.request_models import CompanyFounderRequest
from app.services.serp_api_service import get_founder_email

router = APIRouter()


@router.post("/get_founder_email")
def get_founder_email_route(request: CompanyFounderRequest):
    return get_founder_email(request.company_name, request.founder_name)
