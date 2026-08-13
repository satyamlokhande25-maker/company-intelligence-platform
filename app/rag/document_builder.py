import json

def load_company_documents(json_path: str = "output/company_profile.json") -> list[dict]:
    """
    Reads extracted company profile JSON and builds structured text documents with metadata.
    Optimized for Semantic Search (RAG) to prevent hallucination.
    """
    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    documents = []
    company_name = data.get("company_name", "Company")

    # 1. Overview Document
    industry_raw = data.get("industry", [])
    if isinstance(industry_raw, list):
        industry_str = ", ".join(industry_raw)
    else:
        industry_str = str(industry_raw) if industry_raw else "N/A"

    overview = (
        f"Company Name: {company_name}\n"
        f"Website: {data.get('website', 'N/A')}\n"
        f"Industry: {industry_str}\n"
        f"Founded Year: {data.get('founded_year', 'N/A')}\n\n"
        f"About {company_name}:\n{data.get('about', 'N/A')}"
    )
    documents.append({"text": overview, "metadata": {"category": "overview"}})

    # 2. Services Document
    services = data.get("services", [])
    if services:
        services_text = f"{company_name} offers the following services and solutions:\n" + "\n".join([f"- {s}" for s in services])
        documents.append({"text": services_text, "metadata": {"category": "services"}})

    # 3. Technologies Document
    techs = data.get("technologies", [])
    if techs:
        tech_text = f"{company_name} tech stack and engineering technologies:\n" + ", ".join(techs)
        documents.append({"text": tech_text, "metadata": {"category": "technologies"}})

    # 4. People / Leadership Document (CRITICAL FIX FOR FOUNDER/EXEC QUERIES)
    people = data.get("people", [])
    if people:
        people_lines = []
        for p in people:
            if isinstance(p, dict):
                name = p.get('name', '').strip()
                desig = p.get('designation', '').strip()
                if name:
                    people_lines.append(f"- Name: {name} | Title/Role: {desig if desig else 'Executive/Team Member'}")
            elif isinstance(p, str):
                people_lines.append(f"- {p}")

        if people_lines:
            people_text = (
                f"Key Executive Leadership, Founders, Board Members, and Team at {company_name}:\n" 
                + "\n".join(people_lines)
            )
            documents.append({"text": people_text, "metadata": {"category": "people"}})

    # 5. Contact & Locations Document
    emails = ", ".join(data.get("email", [])) if data.get("email") else "N/A"
    phones = ", ".join(data.get("phone", [])) if data.get("phone") else "N/A"
    locations = " | ".join(data.get("locations", [])) if data.get("locations") else "N/A"
    
    contact_text = (
        f"Contact Details and Office Locations for {company_name}:\n"
        f"Emails: {emails}\n"
        f"Phones: {phones}\n"
        f"Locations: {locations}"
    )
    documents.append({"text": contact_text, "metadata": {"category": "contact"}})

    # 6. Important Links Document
    pages_info = (
        f"Key Website URLs and Pages of {company_name}:\n"
        f"About Page: {data.get('about_page', 'N/A')}\n"
        f"Services Page: {data.get('services_page', 'N/A')}\n"
        f"Contact Page: {data.get('contact_page', 'N/A')}\n"
        f"Careers Page: {data.get('careers_page', 'N/A')}"
    )
    documents.append({"text": pages_info, "metadata": {"category": "pages"}})

    return documents