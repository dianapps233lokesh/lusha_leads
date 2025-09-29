import pandas as pd


def export_to_csv(data: dict, file_name: str = "founders.csv"):
    contacts_data = data.get("contacts", {}).get("results", [])
    companies_data = data.get("unique_companies", {})

    rows = []
    for contact in contacts_data:
        # Extract contact details
        first_name = contact.get("name", {}).get("first")
        last_name = contact.get("name", {}).get("last")
        full_name = contact.get("name", {}).get("full")
        job_title = contact.get("job_title", {}).get("title")
        company_id = contact.get("company_id")
        linkedin_profile = contact.get("social_link")

        # Extract location details
        location = contact.get("location", {})
        city = location.get("city")
        state = location.get("state")
        country = location.get("country")

        # Extract emails
        emails = ", ".join(
            [e.get("address") for e in contact.get("emails", []) if e.get("address")]
        )

        # Extract phones
        phones = ", ".join(
            [p.get("number") for p in contact.get("phones", []) if p.get("number")]
        )

        # Get company details from unique_companies using company_id
        company = companies_data.get(str(company_id), {})
        company_name = company.get("name")
        company_domain = company.get("domains", {}).get("homepage")
        company_description = company.get("description")
        company_size_min = company.get("company_size", {}).get("min")
        company_size_max = company.get("company_size", {}).get("max")
        company_industry = (
            company.get("industry", {}).get("primary_industry", {}).get("key")
        )

        row = {
            "first_name": first_name,
            "last_name": last_name,
            "full_name": full_name,
            "job_title": job_title,
            "company_id": company_id,
            "company_name": company_name,
            "company_domain": company_domain,
            "company_description": company_description,
            "company_size_min": company_size_min,
            "company_size_max": company_size_max,
            "company_industry": company_industry,
            "city": city,
            "state": state,
            "country": country,
            "linkedin_profile": linkedin_profile,
            "emails": emails,
            "phones": phones,
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv(file_name, index=False)
    return file_name
