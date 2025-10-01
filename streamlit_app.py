import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from app.services.lusha_service import lusha_service

load_dotenv()


# --- Authentication ---
def check_password():
    """Returns `True` if the user had a correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if (
            st.session_state["username"] == "admin"
            and st.session_state["password"] == "admin@123"
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input("Username", key="username")
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    if not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input("Username", key="username")
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 User not known or password incorrect")
        return False
    # Password correct.
    return True


if not check_password():
    st.stop()  # Do not continue if check_password is not True.

# Set page configuration for a modern look
st.set_page_config(page_title="Lusha Search", layout="wide")

st.markdown(
    """
<style>
    /* Main app background */
    .stApp {
        background: linear-gradient(to right, #283048, #859398);
        color: #FFFFFF;
    }
    /* Main content area */
    .main .block-container {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 2rem;
        border-radius: 10px;
    }
    /* Title styling */
    h1 {
        color: #FFFFFF;
        text-align: center;
        font-family: 'Arial', sans-serif;
    }
    /* Input field styling */
    .stTextInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.2);
        color: #FFFFFF;
        border-radius: 5px;
    }
    /* Button styling */
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        border: none;
        font-weight: bold;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    .stButton > button:hover {
        background-color: #45a049;
    }
    /* Dataframe styling */
    .stDataFrame {
        background-color: rgba(0, 0, 0, 0.3);
        border-radius: 10px;
    }
    /* Download button styling */
    .stDownloadButton > button {
        background-color: #008CBA;
    }
    .stDownloadButton > button:hover {
        background-color: #007B9A;
    }
</style>
""",
    unsafe_allow_html=True,
)

# App header
st.title("DianApps Lead Search")
st.markdown("---")

# --- Session State Initialization ---
if "page_number" not in st.session_state:
    st.session_state.page_number = 0
if "data" not in st.session_state:
    st.session_state.data = []
if "query" not in st.session_state:
    st.session_state.query = ""
if "total_hits" not in st.session_state:
    st.session_state.total_hits = 0


# --- Data Fetching and Processing ---
def fetch_and_process_data(query, page):
    # print(f"--- Fetching data for query: '{query}', page: {page} ---")
    with st.spinner("Searching..."):
        try:
            data = lusha_service.get_company_details(query, page)

            if data and "error" in data:
                st.error(f"An API error occurred: {data['error']}")
                st.session_state.data = []
                return

            contacts_data = data.get("contacts", {})
            contacts_list = contacts_data.get("results", [])
            company_details = contacts_data.get("unique_companies", {})

            total_hits = contacts_data.get("total", 0)
            # print(f"--- API returned total_hits: {total_hits} ---")
            st.session_state.total_hits = total_hits

            if not contacts_list:
                st.warning("No contacts found for the current page.")
                st.session_state.data = []
                return

            processed_data = []
            for contact in contacts_list:
                job_title_info = contact.get("job_title", {})
                title = job_title_info.get("title", "")

                if (
                    "founder" in title.lower()
                    or "cto" in title.lower()
                    or "chief technology officer" in title.lower()
                ):
                    full_name = contact.get("name", {}).get("full", "N/A")
                    contact_company_id = contact.get("company_id")
                    details = company_details.get(str(contact_company_id), {})
                    company_name = details.get("name", "Not found")
                    location_info = contact.get("location", {})
                    location = f"{location_info.get('city', '')}, {location_info.get('country', '')}".strip(
                        ", "
                    )

                    phones = [
                        p.get("number", "0000000000")
                        for p in contact.get("phones", [])
                        if p.get("number")
                    ]
                    phone_numbers = ", ".join(phones) if phones else "0000000000"

                    emails = [
                        e.get("address", "test@company.com")
                        for e in contact.get("emails", [])
                        if e.get("address")
                    ]
                    email_addresses = (
                        ", ".join(emails) if emails else "test@company.com"
                    )

                    industry = details.get("industry", {}).get("primary_industry", {})

                    processed_data.append(
                        {
                            "Company": company_name,
                            "Website": details.get("homepage_url", ""),
                            "Industry": industry.get("key", ""),
                            "Sub-Industry": industry.get("sub_industry", {}).get(
                                "key", ""
                            ),
                            "Name (Founder/CTO)": f"{full_name} ({title})",
                            "Founder LinkedIn": contact.get("social_link", ""),
                            "Company LinkedIn": details.get("social", {}).get(
                                "linkedin", ""
                            ),
                            "Phone": phone_numbers,
                            "Email": email_addresses,
                            "Location": location,
                        }
                    )
            st.session_state.data = processed_data

        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.session_state.data = []


# --- Search Form ---
with st.form("search_form", clear_on_submit=False):
    col1, col2 = st.columns([10, 1])
    with col1:
        query_input = st.text_input(
            "",
            placeholder="Enter your query...",
            label_visibility="collapsed",
            key="query_input",
        )
    with col2:
        search_button = st.form_submit_button("Search")

if search_button and query_input:
    st.session_state.query = query_input
    st.session_state.page_number = 0
    fetch_and_process_data(st.session_state.query, st.session_state.page_number)


# --- Pagination and Display ---
def go_to_previous_page():
    # print("--- In go_to_previous_page ---")
    if st.session_state.page_number > 0:
        st.session_state.page_number -= 1
        # print(f"Page number decremented to: {st.session_state.page_number}")
        fetch_and_process_data(st.session_state.query, st.session_state.page_number)
    # print("--- Exiting go_to_previous_page ---")


def go_to_next_page():
    # print("--- In go_to_next_page ---")
    st.session_state.page_number += 1
    # print(f"Page number incremented to: {st.session_state.page_number}")
    fetch_and_process_data(st.session_state.query, st.session_state.page_number)
    # print("--- Exiting go_to_next_page ---")


if st.session_state.data:
    st.success(
        f"Showing {len(st.session_state.data)} matching contacts on this page. Total found: {st.session_state.total_hits}"
    )

    df = pd.DataFrame(st.session_state.data)
    st.dataframe(df)

    # Pagination controls
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.button(
            "Previous",
            on_click=go_to_previous_page,
            disabled=(st.session_state.page_number == 0),
        )
    with col3:
        st.button(
            "Next",
            on_click=go_to_next_page,
            disabled=(
                (st.session_state.page_number + 1) * 25 >= st.session_state.total_hits
            ),
        )

    csv = pd.DataFrame(st.session_state.data).to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Export to CSV",
        data=csv,
        file_name=f"{st.session_state.query}_founders_ctos_page_{st.session_state.page_number + 1}.csv",
        mime="text/csv",
    )
elif search_button and st.session_state.query:
    st.info("No Founders or CTOs found for this company.")
