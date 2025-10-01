import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables from .env.dev file for local development
load_dotenv(dotenv_path=".env.dev")

class Settings:
    LUSHA_API_KEY: str
    LUSHA_API_SECRET: str
    LUSHA_CSRF_TOKEN: str
    LUSHA_XSRF_TOKEN: str
    LUSHA_COOKIE: str
    SERP_API_KEY: str

    try:
        # Try to get secrets from Streamlit's secrets management (for deployment)
        LUSHA_API_KEY = st.secrets["LUSHA_API_KEY"]
        LUSHA_API_SECRET = st.secrets["LUSHA_API_SECRET"]
        LUSHA_CSRF_TOKEN = st.secrets["LUSHA_CSRF_TOKEN"]
        LUSHA_XSRF_TOKEN = st.secrets["LUSHA_XSRF_TOKEN"]
        LUSHA_COOKIE = st.secrets["LUSHA_COOKIE"]
        SERP_API_KEY = st.secrets["SERP_API_KEY"]
    except (KeyError, st.errors.StreamlitAPIException):
        # Fallback to environment variables (for local development)
        LUSHA_API_KEY = os.getenv("LUSHA_API_KEY")
        LUSHA_API_SECRET = os.getenv("LUSHA_API_SECRET")
        LUSHA_CSRF_TOKEN = os.getenv("LUSHA_CSRF_TOKEN")
        LUSHA_XSRF_TOKEN = os.getenv("LUSHA_XSRF_TOKEN")
        LUSHA_COOKIE = os.getenv("LUSHA_COOKIE")
        SERP_API_KEY = os.getenv("SERP_API_KEY")


settings = Settings()
