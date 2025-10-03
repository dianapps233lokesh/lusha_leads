import os

import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env.dev file for local development
load_dotenv(dotenv_path=".env.dev")


class Settings:
    LUSHA_API_KEY: str
    LUSHA_API_SECRET: str
    LUSHA_CSRF_TOKEN: str
    LUSHA_XSRF_TOKEN: str
    LUSHA_COOKIE: str
    SERP_API_KEY: str
    MONGO_URI: str
    MONGO_DB_NAME: str
    STREAMLIT_USERNAME: str
    STREAMLIT_PASSWORD: str

    try:
        # Try to get secrets from Streamlit's secrets management (for deployment)
        LUSHA_API_KEY = st.secrets["LUSHA_API_KEY"]
        LUSHA_API_SECRET = st.secrets["LUSHA_API_SECRET"]
        LUSHA_CSRF_TOKEN = st.secrets["LUSHA_CSRF_TOKEN"]
        LUSHA_XSRF_TOKEN = st.secrets["LUSHA_XSRF_TOKEN"]
        LUSHA_COOKIE = st.secrets["LUSHA_COOKIE"]
        SERP_API_KEY = st.secrets["SERP_API_KEY"]
        MONGO_URI = st.secrets["MONGO_URI"]
        MONGO_DB_NAME = st.secrets["MONGO_DB_NAME"]
        STREAMLIT_USERNAME = st.secrets["STREAMLIT_USERNAME"]
        STREAMLIT_PASSWORD = st.secrets["STREAMLIT_PASSWORD"]
    except (KeyError, st.errors.StreamlitAPIException):
        # Fallback to environment variables (for local development)
        LUSHA_API_KEY = os.getenv("LUSHA_API_KEY")
        LUSHA_API_SECRET = os.getenv("LUSHA_API_SECRET")
        LUSHA_CSRF_TOKEN = os.getenv("LUSHA_CSRF_TOKEN")
        LUSHA_XSRF_TOKEN = os.getenv("LUSHA_XSRF_TOKEN")
        LUSHA_COOKIE = os.getenv("LUSHA_COOKIE")
        SERP_API_KEY = os.getenv("SERP_API_KEY")
        MONGO_URI = os.getenv("MONGO_URI")
        MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
        STREAMLIT_USERNAME = os.getenv("STREAMLIT_USERNAME")
        STREAMLIT_PASSWORD = os.getenv("STREAMLIT_PASSWORD")


settings = Settings()
