import json
import os
import sys
from pathlib import Path

# Path resolution for output directory
BASE_DIR = Path(__file__).resolve().parent

from app.scraper.crawler import crawl_website
from app.extractor.contact import extract_contact_information
from app.extractor.company import extract_company_information
from app.extractor.location import extract_locations
from app.extractor.social import extract_social_information
from app.extractor.technology import extract_technologies
from app.extractor.people import extract_people
from app.cleaner.company_cleaner import clean_company_data
from app.rag.retriever import RAGPipeline


def run_pipeline(target_url: str):
    # Ensure scheme is present (http:// or https://)
    target_url = target_url.strip()
    if not target_url.startswith(("http://", "https://")):
        target_url = f"https://{target_url}"

    print("=" * 70)
    print("STARTING COMPANY INTELLIGENCE PIPELINE")
    print("=" * 70)
    print(f"Target URL: {target_url}\n")

    # =================================================
    # 1. CRAWL WEBSITE
    # =================================================
    result = crawl_website(target_url)

    print("IMPORTANT COMPANY PAGES")
    print("-" * 70)
    for page_type, page_url in result.get("pages", {}).items():
        print(f"{page_type}: {page_url}")

    # =================================================
    # 2. CONTACT INFORMATION EXTRACTION
    # =================================================
    print("\nEXTRACTING CONTACTS")
    print("-" * 70)

    all_emails = set()
    all_phones = set()

    for page_type, html in result.get("pages_html", {}).items():
        if not html:
            continue
        contact_data = extract_contact_information(html)
        
        emails = contact_data.get("emails", [])
        phones = contact_data.get("phones", [])

        all_emails.update(emails)
        all_phones.update(phones)

    print(f"Emails found: {len(all_emails)}")
    print(f"Phones found: {len(all_phones)}")

    # =================================================
    # 3. LOCATION EXTRACTION
    # =================================================
    print("\nEXTRACTING LOCATIONS")
    print("-" * 70)

    all_locations = []
    for page_type, html in result.get("pages_html", {}).items():
        if not html:
            continue
        locations = extract_locations(html)
        if locations:
            all_locations.extend(locations)

    # Remove duplicates preserving order
    all_locations = list(dict.fromkeys(all_locations))
    print(f"Unique locations found: {len(all_locations)}")

    # =================================================
    # 4. SOCIAL MEDIA EXTRACTION
    # =================================================
    print("\nEXTRACTING SOCIAL LINKS")
    print("-" * 70)

    all_social_links = {
        "linkedin": set(),
        "facebook": set(),
        "instagram": set(),
        "youtube": set(),
        "twitter": set(),
        "github": set()
    }

    for page_type, html in result.get("pages_html", {}).items():
        if not html:
            continue
        social_data = extract_social_information(html, result["source_url"])

        for platform, links in social_data.items():
            if platform not in all_social_links:
                all_social_links[platform] = set()
            all_social_links[platform].update(links)

    cleaned_social_links = {
        platform: sorted(list(links))
        for platform, links in all_social_links.items()
    }

    # =================================================
    # 5. TECHNOLOGY EXTRACTION
    # =================================================
    print("\nEXTRACTING TECHNOLOGIES")
    print("-" * 70)

    all_technologies = set()
    for page_type, html in result.get("pages_html", {}).items():
        if not html:
            continue
        technologies = extract_technologies(html)
        if technologies:
            all_technologies.update(technologies)

    sorted_technologies = sorted(list(all_technologies))
    print(f"Technologies detected: {len(sorted_technologies)}")

    # =================================================
    # 6. PEOPLE / LEADERSHIP EXTRACTION
    # =================================================
    print("\nEXTRACTING PEOPLE & LEADERSHIP")
    print("-" * 70)

    all_people = []
    for page_type, html in result.get("pages_html", {}).items():
        if not html:
            continue
        people = extract_people(html)
        if people:
            all_people.extend(people)

    unique_people = []
    seen_people = set()

    for person in all_people:
        key = (
            person.get("name", "").lower().strip(),
            person.get("designation", "").lower().strip()
        )
        if key not in seen_people and key[0]:
            seen_people.add(key)
            unique_people.append(person)

    print(f"Unique leadership entries: {len(unique_people)}")

    # =================================================
    # 7. COMPANY INTELLIGENCE EXTRACTION
    # =================================================
    print("\nEXTRACTING COMPANY INTELLIGENCE")
    print("-" * 70)

    pages_html = result.get("pages_html", {})
    company_data = extract_company_information(
        homepage_html=pages_html.get("homepage"),
        about_html=pages_html.get("about_page"),
        services_html=pages_html.get("services_page")
    )

    company_data["social_links"] = cleaned_social_links
    company_data["technologies"] = sorted_technologies
    company_data["people"] = unique_people

    # =================================================
    # 8. CLEAN DATA & CONVERT TYPES
    # =================================================
    print("\nCLEANING & STRUCTURING DATA")
    print("-" * 70)

    cleaned_company = clean_company_data(
        company_data=company_data,
        emails=sorted(list(all_emails)),
        phones=sorted(list(all_phones)),
        locations=all_locations,
        technologies=sorted_technologies,
        pages=result.get("pages", {}),
        source_url=result.get("source_url", target_url)
    )

    # =================================================
    # 9. SAVE TO OUTPUT JSON (Absolute Path)
    # =================================================
    output_dir = BASE_DIR / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "company_profile.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(cleaned_company, file, indent=4, ensure_ascii=False)

    print("\n" + "=" * 70)
    print("SUCCESS: JSON FILE GENERATED")
    print(f"Saved to: {output_file}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    # Accept target URL dynamically from CLI argument (e.g., Streamlit input)
    if len(sys.argv) > 1 and sys.argv[1].strip():
        target_url = sys.argv[1]
    else:
        target_url = "https://bestpeers.com/"

    run_pipeline(target_url)