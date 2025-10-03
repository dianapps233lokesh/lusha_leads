import copy

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from app.services.lusha_service import lusha_service
from app.services.mongo_service import mongo_service
from app.utils.helper import (
    check_password,
    csv_exporter,
    parse_data,
)
from app.utils.logger import logging

load_dotenv()

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
                logging.error(f"An API error occurred: {data['error']}")
                st.error(f"An API error occurred: {data['error']}")
                st.session_state.data = []
                return
            processed_data = parse_data(data)
            logging.info(f"type of processed data is {type(processed_data)}")
            st.session_state.data = copy.deepcopy(processed_data)
            mongo_service.save_data(processed_data)
            logging.info("data saved into the mongodb successfully.")

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            st.error(f"An error occurred: {e}")
            st.session_state.data = []


# --- Pagination and Display ---
def go_to_previous_page():
    logging.info("clicked the previous button")
    if st.session_state.page_number > 0:
        st.session_state.page_number -= 1
        fetch_and_process_data(st.session_state.query, st.session_state.page_number)
        logging.info("previous page data fetched successfully")


def go_to_next_page():
    logging.info("clicked the next button")
    st.session_state.page_number += 1
    fetch_and_process_data(st.session_state.query, st.session_state.page_number)
    logging.info("next page data fetched successfully")


# --- Search Form ---
with st.form("search_form", clear_on_submit=False):
    col1, col2 = st.columns([10, 1])
    with col1:
        query_input = st.text_input(
            "Search Query",
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


if st.session_state.data:
    st.success(
        f"Showing {len(st.session_state.data)} matching contacts on this page. Total found: {st.session_state.total_hits}"
    )

    df = pd.DataFrame(st.session_state.data)
    start_index = st.session_state.page_number * 25 + 1
    df.index = range(start_index, start_index + len(df))
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

    st.download_button(
        label="Export to CSV",
        data=csv_exporter(),
        file_name=f"founders_page_{st.session_state.page_number + 1}.csv",
        mime="text/csv",
    )


elif search_button and st.session_state.query:
    logging.info("no data found for founders.")
    st.info("No Founders or CTOs found for this company.")
