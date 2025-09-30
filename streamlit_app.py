import pandas as pd
import requests
import streamlit as st

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
    col1, col2 = st.columns([3, 1])
    with col1:
        query = st.text_input(
            "",
            placeholder="Enter company name...",
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
                response = requests.post(
                    "http://127.0.0.1:8000/api/search-founders",
                    json={"search_text": query},
                    timeout=50,
                )
                response.raise_for_status()  # Raise an exception for bad status codes
                data = response.json()
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

                                # Get company details from the lookup
                                contact_company_id = contact.get("company_id")
                                details = company_details.get(
                                    str(contact_company_id),
                                    {},
                                )
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
            except requests.exceptions.RequestException as e:
                st.error(f"An error occurred while connecting to the API: {e}")
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
    st.dataframe(df)

    # Pagination controls
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("Previous") and st.session_state.page_number > 0:
            st.session_state.page_number -= 1
    with col3:
        if st.button("Next") and end_index < len(processed_data):
            st.session_state.page_number += 1

    csv = pd.DataFrame(processed_data).to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Export to CSV",
        data=csv,
        file_name=f"{query}_founders_ctos.csv",
        mime="text/csv",
    )
else:
    if search_button and query:
        st.info("No Founders or CTOs found for this company.")
