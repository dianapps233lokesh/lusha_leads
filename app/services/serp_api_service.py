import requests

from app.core.config import settings


def get_founder_email(company_name: str, founder_name: str):
    """Searches for the email of a founder using the SERP API."""
    params = {
        "api_key": settings.SERP_API_KEY,
        "engine": "google",
        "q": f"email of {founder_name} {company_name}",
    }

    response = requests.get("https://serpapi.com/search", params=params, timeout=30)
    response.raise_for_status()

    data = response.json()

    if "answer_box" in data and "snippet_highlighted_words" in data["answer_box"]:
        email = data["answer_box"]["snippet_highlighted_words"][0]
        return {"email": email}
    return None
