from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.models.request_models import ContactSearchRequest
from app.services.lusha_service import lusha_service
from app.utils.export_csv import export_to_csv

router = APIRouter()


@router.post("/search-founders")
def search_founders(request: ContactSearchRequest):
    return lusha_service.get_company_details(request.search_text)


@router.post("/search-founders-csv")
def search_founders_csv(request: ContactSearchRequest):
    data = lusha_service.get_company_details(request.search_text)
    # print("Lusha API Response:", data)
    file_path = export_to_csv(data, "founders.csv")
    return FileResponse(file_path, media_type="text/csv", filename="founders.csv")
