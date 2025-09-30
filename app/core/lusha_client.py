import uuid

import requests

from app.core.config import settings


class LushaApiClient:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://dashboard-services.lusha.com/v2"
        self.headers = {
            "_csrf": settings.LUSHA_CSRF_TOKEN,
            "accept": "application/json",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
            "cookie": settings.LUSHA_COOKIE,
            "origin": "https://dashboard.lusha.com",
            "priority": "u=1, i",
            "referer": "https://dashboard.lusha.com/",
            "sec-ch-ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            "x-version": "1.0.0",
            "x-xsrf-token": settings.LUSHA_XSRF_TOKEN,
        }

    def get_prospecting_data(self, search_text: str):
        url = f"{self.base_url}/prospecting-full"
        session_id = str(uuid.uuid4())

        payload = {
            "filters": {"searchText": [search_text]},
            "filtersMetadata": {
                "isViewEmployeesMode": False,
                "excludeRevealedContacts": False,
                "excludePartialProfiles": False,
            },
            "display": "contacts",
            "pages": {"page": 0, "pageSize": 25},
            "sessionId": session_id,
            "searchTrigger": "NewFilter",
            "savedSearchId": 0,
            "bulkSearchCompanies": {},
            "isRecent": False,
            "isSaved": False,
            "pageAbove400": None,
            "totalPagesAbove400": 0,
            "enforceFlexLLM": False,
            "fetchIntentTopics": True,
        }

        try:
            response = self.session.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            # In a real app, you'd want to handle this more gracefully
            # For example, by raising a custom exception
            return None


# You can create a single instance to be used across the application
lusha_api_client = LushaApiClient()
