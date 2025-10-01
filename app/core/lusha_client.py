import time
import uuid

import requests
import streamlit as st

from app.core import MAX_ROWS_PER_PAGE
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

    def get_prospecting_data(self, search_text: str, page: int = 0):
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
            "pages": {"page": page, "pageSize": 25},
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
            data = response.json()

            # Specifically check for the quota exceeded error from the API
            if data.get("searchQuotaExceeded"):
                print(f"Lusha API response: {data}")
                error_message = "Your Lusha API request could not be completed. This may be due to exceeding the monthly search quota or other API limitations. Please check your Lusha account for more details."
                st.warning(error_message)
                return {"error": error_message}

            # Check for other application-level errors
            if "error" in data:
                print(f"API Error: {data['error']}")
                return data

            return data
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            # Return a structured error for HTTP errors
            return {"error": str(e)}

    def get_all_prospecting_data(self, search_text: str):
        all_contacts = []
        all_companies = {}
        page = 0
        while True:
            data = self.get_prospecting_data(search_text, page)
            if not data:
                break

            contacts_data = data.get("contacts", {})
            results = contacts_data.get("results", [])
            unique_companies = contacts_data.get("unique_companies", {})

            if not results:
                break

            all_contacts.extend(results)
            all_companies.update(unique_companies)

            if len(results) < MAX_ROWS_PER_PAGE:
                break

            page += 1

            time.sleep(1)

        return {
            "contacts": {"results": all_contacts, "unique_companies": all_companies},
        }


# You can create a single instance to be used across the application
lusha_api_client = LushaApiClient()
