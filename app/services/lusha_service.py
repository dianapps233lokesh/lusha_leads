from app.core.lusha_client import lusha_api_client


class LushaService:
    def get_company_details(self, search_text: str):
        # This method now uses the new client
        return lusha_api_client.get_prospecting_data(search_text)


lusha_service = LushaService()
