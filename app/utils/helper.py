import pandas as pd
import streamlit as st

from app.core.config import settings


def parse_data(data):
    contacts_data = data.get("contacts", {})
    contacts_list = contacts_data.get("results", [])
    company_details = contacts_data.get("unique_companies", {})

    total_hits = contacts_data.get("total", 0)
    st.session_state.total_hits = total_hits

    if not contacts_list:
        st.warning("No contacts found for the current page.")
        st.session_state.data = []
        return None

    processed_data = []
    for contact in contacts_list:
        job_title_info = contact.get("job_title", {})
        title = job_title_info.get("title", "")

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
        email_addresses = ", ".join(emails) if emails else "test@company.com"

        industry = details.get("industry", {}).get("primary_industry", {})

        processed_data.append(
            {
                "Company": company_name,
                "Website": details.get("homepage_url", ""),
                "Industry": industry.get("key", ""),
                "Sub-Industry": industry.get("sub_industry", {}).get("key", ""),
                "Name (Founder/CTO)": f"{full_name} ({title})",
                "Founder LinkedIn": contact.get("social_link", ""),
                "Company LinkedIn": details.get("social", {}).get("linkedin", ""),
                "Phone": phone_numbers,
                "Email": email_addresses,
                "Location": location,
            }
        )
    return processed_data


# --- Authentication ---
def check_password():
    """Returns `True` if the user is authenticated."""
    if st.session_state.get("password_correct", False):
        return True

    # Use a form for the login
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if (
                username == settings.STREAMLIT_USERNAME
                and password == settings.STREAMLIT_PASSWORD
            ):
                st.session_state["password_correct"] = True
                st.rerun()  # Rerun the script to reflect the authenticated state
            else:
                st.error("😕 User not known or password incorrect")

    return False


def csv_exporter():
    csv = pd.DataFrame(st.session_state.data).to_csv(index=False).encode("utf-8")
    return csv
