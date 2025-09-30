import pandas as pd
import requests
import streamlit as st

# Set the title of the Streamlit app
st.title("Lusha Founder & CTO Search")

# Create a text input field for the search query
query = st.text_input("Enter company name to search for founders and CTOs:")

# Create a search button
if st.button("Search"):
    if query:
        # Display a spinner while fetching data
        with st.spinner("Searching..."):
            try:
                # Make a request to the FastAPI backend
                response = requests.post(
                    "http://127.0.0.1:8000/api/search-founders",
                    json={"search_text": query},
                )
                print(
                    f"api response for the streamlit ui app------------{response.json()}"
                )
                response.raise_for_status()  # Raise an exception for bad status codes
                data = response.json()

                if data:
                    contacts_list = data.get("contacts", {}).get("results", [])

                    if not contacts_list:
                        st.write("No contacts found in the API response.")
                    else:
                        processed_data = []
                        for contact in contacts_list:
                            job_title_info = contact.get("job_title", {})
                            title = job_title_info.get("title", "")

                            # Filter for founders and CTOs by checking for keywords in the title
                            if "founder" in title.lower() or "cto" in title.lower() or "chief technology officer" in title.lower():
                                full_name = contact.get("name", {}).get("full", "N/A")
                                
                                location_info = contact.get("location", {})
                                location = f"{location_info.get('city', '')}, {location_info.get('country', '')}".strip(", ")

                                phones = contact.get("phones", [])
                                phone_numbers = ", ".join([p.get("number", "0000000000") for p in phones]) if phones else "0000000000"

                                emails = contact.get("emails", [])
                                email_addresses = ", ".join([e.get("address", "test@company.com") for e in emails]) if emails else "test@company.com"

                                processed_data.append({
                                    "Company": query,  # Use the search query as the company name
                                    "Website": "",  # Not available in the contact response
                                    "Industry": "",  # Not available in the contact response
                                    "Contact (Founder/CTO)": f"{full_name} ({title})",
                                    "LinkedIn": contact.get("social_link", ""),
                                    "Phone": phone_numbers,
                                    "Email": email_addresses,
                                    "Location": location,
                                })

                        if processed_data:
                            df = pd.DataFrame(processed_data)
                            st.dataframe(df)

                            csv = df.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label="Export to CSV",
                                data=csv,
                                file_name=f"{query}_founders_ctos.csv",
                                mime="text/csv",
                            )
                        else:
                            st.write("No Founders or CTOs found for this company.")
                else:
                    st.write("No results found.")
            except requests.exceptions.RequestException as e:
                st.error(f"An error occurred: {e}")
    else:
        st.write("Please enter a search query.")
