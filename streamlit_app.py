import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from app.services.lusha_service import lusha_service
# from app.services.serp_api_service import get_founder_email

load_dotenv()

# --- Authentication ---
def check_password():
    """Returns `True` if the user had a correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if (st.session_state["username"] == os.getenv("STREAMLIT_USERNAME")) and (
            st.session_state["password"] == os.getenv("STREAMLIT_PASSWORD")
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

# Custom CSS for a professional and attractive UI
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
# st.markdown(
#     "<h3 style='text-align: center; color: #E0E0E0;'>Enter a company name to find key contacts.</h3>",
#     unsafe_allow_html=True,
# )
st.markdown("---")

# Search input and button
with st.form("search_form", clear_on_submit=False):
    col1, col2 = st.columns([10, 1])
    with col1:
        query = st.text_input(
            "",
            placeholder="Enter your query...",
            label_visibility="collapsed",
        )
    with col2:
        search_button = st.form_submit_button("Search")

if "page_number" not in st.session_state:
    st.session_state.page_number = 0

if "data" not in st.session_state:
    st.session_state.data = []

if search_button:
    st.session_state.page_number = 0  # Reset page number on new search
    st.session_state.data = []  # Clear previous data
    if query:
        # Display a spinner while fetching data
        with st.spinner("Searching..."):
            try:
                # Make a request to the FastAPI backend
                data = lusha_service.get_company_details(query)
                # print(f"data is ------------->>>>>>{data}")

                if data:
                    contacts_list = data.get("contacts", {}).get("results", [])
                    company_details = data.get("contacts", {}).get(
                        "unique_companies",
                        {},
                    )

                    if not contacts_list:
                        st.warning("No contacts found in the API response.")
                    else:
                        processed_data = []
                        for contact in contacts_list:
                            job_title_info = contact.get("job_title", {})
                            title = job_title_info.get("title", "")
                            # company_id = contact.get("company_id", None)

                            # Filter for founders and CTOs by checking for keywords in the title
                            if (
                                "founder" in title.lower()
                                or "cto" in title.lower()
                                or "chief technology officer" in title.lower()
                            ):
                                full_name = contact.get("name", {}).get("full", "N/A")

                                # Get company details from the lookup
                                contact_company_id = contact.get("company_id")
                                details = company_details.get(
                                    str(contact_company_id),
                                    {},
                                )
                                company_name = details.get("name", "Not found")

                                location_info = contact.get("location", {})
                                location = f"{location_info.get('city', '')}, {location_info.get('country', '')}".strip(
                                    ", ",
                                )

                                phones = contact.get("phones", [])
                                processed_phones = []
                                for p in phones:
                                    number = p.get("number")
                                    if number and number.endswith("..."):
                                        processed_phones.append("0000000000")
                                    elif number:
                                        processed_phones.append(number)
                                if not processed_phones:
                                    phone_numbers = "0000000000"
                                else:
                                    phone_numbers = ", ".join(processed_phones)

                                emails = contact.get("emails", [])
                                processed_emails = []
                                for e in emails:
                                    address = e.get("address")
                                    if address and address.startswith("..."):
                                        processed_emails.append("test@company.com")
                                    elif address:
                                        processed_emails.append(address)
                                if not processed_emails:
                                    email_addresses = "test@company.com"
                                else:
                                    email_addresses = ", ".join(processed_emails)

                                # if (
                                #     email_addresses == "test@company.com"
                                #     and full_name != "N/A"
                                #     and company_name != "Not found"
                                # ):
                                #     # try:
                                #     print(
                                #         f"full name is {full_name} and company name is {company_name}"
                                #     )
                                #     serp_data = get_founder_email(
                                #         company_name,
                                #         full_name,
                                #     )
                                #     print(
                                #         f"response of serp api is ------------>>>>>>>>{serp_data}"
                                #     )
                                #     if serp_data and serp_data.get("email"):
                                #         email_addresses = serp_data.get("email")
                                # except requests.exceptions.RequestException:
                                #     # Silently fail and keep test@company.com
                                #     pass

                                emails = contact.get("emails", [])
                                processed_emails = []
                                for e in emails:
                                    address = e.get("address")
                                    if address and address.startswith("..."):
                                        processed_emails.append("test@company.com")
                                    elif address:
                                        processed_emails.append(address)
                                if not processed_emails:
                                    email_addresses = "test@company.com"
                                else:
                                    email_addresses = ", ".join(processed_emails)

                                industry = details.get("industry", {}).get(
                                    "primary_industry",
                                    {},
                                )

                                processed_data.append(
                                    {
                                        "Company": details.get(
                                            "name",
                                            "Not found",
                                        ),
                                        "Website": details.get("homepage_url", ""),
                                        "Industry": industry.get("key", ""),
                                        "Sub-Industry": industry.get(
                                            "sub_industry",
                                            {},
                                        ).get("key", ""),
                                        "Name (Founder/CTO)": f"{full_name} ({title})",
                                        "Founder LinkedIn": contact.get(
                                            "social_link",
                                            "",
                                        ),
                                        "Company LinkedIn": details.get(
                                            "social",
                                            {},
                                        ).get("linkedin", ""),
                                        "Phone": phone_numbers,
                                        "Email": email_addresses,
                                        "Location": location,
                                    },
                                )
                        st.session_state.data = processed_data
                else:
                    st.error("No results found or an error occurred.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a search query.")

if st.session_state.data:
    processed_data = st.session_state.data
    st.success(
        f"Found {len(processed_data)} matching contacts.",
    )

    page_size = 100
    start_index = st.session_state.page_number * page_size
    end_index = start_index + page_size

    df = pd.DataFrame(processed_data[start_index:end_index])
    df.index = range(start_index + 1, start_index + len(df) + 1)
    st.dataframe(df)

    # Pagination controls
    def go_to_previous_page():
        st.session_state.page_number -= 1

    def go_to_next_page():
        st.session_state.page_number += 1

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
            disabled=(end_index >= len(processed_data)),
        )

    csv = pd.DataFrame(processed_data).to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Export to CSV",
        data=csv,
        file_name=f"{query}_founders_ctos.csv",
        mime="text/csv",
    )
elif search_button and query:
    st.info("No Founders or CTOs found for this company.")
