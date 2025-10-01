from app.core.lusha_client import lusha_api_client


class LushaService:
    def get_company_details(self, search_text: str, page: int = 0):
        # This method now uses the new client
        return lusha_api_client.get_prospecting_data(search_text, page)


lusha_service = LushaService()
