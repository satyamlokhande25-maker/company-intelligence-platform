import re
from datetime import datetime
from urllib.parse import urlparse


# =========================================================
# CLEAN EMAIL
# =========================================================

def clean_email(email):
    """
    Remove mailto, Markdown formatting and normalize email.
    """

    if not email:
        return None

    email = str(email).strip()

    # Markdown mail link:
    # [resume@bestpeers.com](mailto:resume@bestpeers.com)
    email = re.sub(
        r"\[([^\]]+)\]\(mailto:[^)]+\)",
        r"\1",
        email
    )

    # Remove mailto
    email = email.replace(
        "mailto:",
        ""
    )

    # Remove markdown artifacts
    email = (
        email
        .replace("[", "")
        .replace("]", "")
    )

    return email.strip().lower()


# =========================================================
# CLEAN PHONE
# =========================================================

def clean_phone(phone):
    """
    Normalize phone number.
    """

    if not phone:
        return None

    phone = str(phone).strip()

    # Keep + and numbers only
    phone = re.sub(
        r"[^\d+]",
        "",
        phone
    )

    return phone


# =========================================================
# CLEAN SERVICES
# =========================================================

def clean_services(services):
    """
    Remove duplicate services and normalize names.
    """

    if not services:
        return []

    cleaned = []
    seen = set()

    for service in services:

        service = str(
            service
        ).strip()

        if not service:
            continue

        # Normalize UI/UX
        if service.lower() in (
            "ui ux",
            "ui/ux"
        ):
            service = "UI/UX"

        key = service.lower()

        if key not in seen:

            seen.add(key)

            cleaned.append(
                service
            )

    return sorted(
        cleaned,
        key=str.lower
    )


# =========================================================
# CLEAN INDUSTRY
# =========================================================

def clean_industry(industry):
    """
    Remove duplicate industries.
    """

    if not industry:
        return []

    cleaned = []
    seen = set()

    for item in industry:

        item = str(
            item
        ).strip()

        if not item:
            continue

        key = item.lower()

        if key not in seen:

            seen.add(key)

            cleaned.append(
                item
            )

    return cleaned


# =========================================================
# CLEAN TECHNOLOGIES
# =========================================================

def clean_technologies(technologies):
    """
    Remove duplicate technologies
    and normalize technology names.
    """

    if not technologies:
        return []

    cleaned = []
    seen = set()

    technology_map = {

        "aws":
            "AWS",

        "amazon web services":
            "AWS",

        "gcp":
            "Google Cloud",

        "google cloud":
            "Google Cloud",

        "google cloud platform":
            "Google Cloud",

        "azure":
            "Microsoft Azure",

        "microsoft azure":
            "Microsoft Azure",

        "node":
            "Node.js",

        "nodejs":
            "Node.js",

        "node.js":
            "Node.js",

        "javascript":
            "JavaScript",

        "js":
            "JavaScript",

        "python":
            "Python",

        "java":
            "Java",

        "react":
            "React",

        "reactjs":
            "React",

        "react.js":
            "React"
    }

    for technology in technologies:

        technology = str(
            technology
        ).strip()

        if not technology:
            continue

        normalized_key = (
            technology
            .lower()
            .strip()
        )

        technology = technology_map.get(
            normalized_key,
            technology
        )

        key = technology.lower()

        if key not in seen:

            seen.add(key)

            cleaned.append(
                technology
            )

    return sorted(
        cleaned,
        key=str.lower
    )


# =========================================================
# CLEAN LOCATIONS
# =========================================================

def clean_locations(locations):
    """
    Remove duplicate and empty locations.
    """

    if not locations:
        return []

    cleaned = []
    seen = set()

    for location in locations:

        location = re.sub(
            r"\s+",
            " ",
            str(location)
        ).strip()

        if not location:
            continue

        key = location.lower()

        if key not in seen:

            seen.add(key)

            cleaned.append(
                location
            )

    return cleaned


# =========================================================
# NORMALIZE URL
# =========================================================

def normalize_url(url):
    """
    Normalize website URL.
    """

    if not url:
        return None

    url = str(
        url
    ).strip()

    # Markdown URL
    # [https://example.com](https://example.com)
    markdown_match = re.match(
        r"\[([^\]]+)\]\((https?://[^)]+)\)",
        url
    )

    if markdown_match:

        url = markdown_match.group(
            2
        )

    # Remove trailing punctuation
    url = url.rstrip(
        ".,;)"
    )

    if not url.startswith(
        (
            "http://",
            "https://"
        )
    ):

        url = "https://" + url

    parsed = urlparse(
        url
    )

    if not parsed.netloc:
        return None

    return (
        f"{parsed.scheme}://"
        f"{parsed.netloc}"
    )


# =========================================================
# CLEAN ABOUT
# =========================================================

def clean_about(about):
    """
    Clean company description.
    """

    if not about:
        return None

    about = re.sub(
        r"\s+",
        " ",
        str(about)
    ).strip()

    return about


# =========================================================
# CLEAN SOCIAL LINKS
# =========================================================

def clean_social_links(social_links):
    """
    Normalize social media links.

    Converts Markdown links into plain URLs.
    Removes duplicates.
    """

    if not social_links:
        return {}

    cleaned = {}

    for platform, links in social_links.items():

        if not links:
            cleaned[platform] = []
            continue

        platform_links = []
        seen = set()

        # Handle both:
        # string
        # list/set of strings

        if isinstance(
            links,
            str
        ):

            links = [links]

        for link in links:

            normalized = normalize_url(
                link
            )

            if not normalized:
                continue

            key = normalized.lower()

            if key not in seen:

                seen.add(key)

                platform_links.append(
                    normalized
                )

        cleaned[platform] = sorted(
            platform_links
        )

    return cleaned


# =========================================================
# CLEAN PEOPLE
# =========================================================

def clean_people(people):
    """
    Clean and deduplicate leadership/team data.

    Expected format:

    [
        {
            "name": "Rich Miller",
            "designation": "CTO"
        }
    ]
    """

    if not people:
        return []

    cleaned = []
    seen = set()

    for person in people:

        if not isinstance(
            person,
            dict
        ):
            continue

        name = str(
            person.get(
                "name",
                ""
            )
        ).strip()

        designation = str(
            person.get(
                "designation",
                ""
            )
        ).strip()

        if not name:
            continue

        if not designation:
            designation = "Unknown"

        # Normalize whitespace
        name = re.sub(
            r"\s+",
            " ",
            name
        )

        designation = re.sub(
            r"\s+",
            " ",
            designation
        )

        # Remove duplicate people
        key = (
            name.lower(),
            designation.lower()
        )

        if key in seen:
            continue

        seen.add(
            key
        )

        cleaned.append(
            {
                "name": name,
                "designation": designation
            }
        )

    return sorted(
        cleaned,
        key=lambda person: (
            person["name"].lower()
        )
    )


# =========================================================
# CLEAN COMPANY DATA
# =========================================================

def clean_company_data(
    company_data,
    emails,
    phones,
    locations,
    technologies,
    pages,
    source_url
):
    """
    Create final normalized company profile.
    """

    # -----------------------------------------------------
    # CLEAN EMAILS
    # -----------------------------------------------------

    cleaned_emails = sorted(
        set(
            cleaned
            for email in emails
            if (
                cleaned := clean_email(
                    email
                )
            )
        )
    )

    # -----------------------------------------------------
    # CLEAN PHONES
    # -----------------------------------------------------

    cleaned_phones = sorted(
        set(
            cleaned
            for phone in phones
            if (
                cleaned := clean_phone(
                    phone
                )
            )
        )
    )

    # -----------------------------------------------------
    # CLEAN TECHNOLOGIES
    # -----------------------------------------------------

    cleaned_technologies = (
        clean_technologies(
            technologies
        )
    )

    # -----------------------------------------------------
    # CLEAN LOCATIONS
    # -----------------------------------------------------

    cleaned_locations = (
        clean_locations(
            locations
        )
    )

    # -----------------------------------------------------
    # CLEAN SOCIAL LINKS
    # -----------------------------------------------------

    cleaned_social_links = (
        clean_social_links(
            company_data.get(
                "social_links",
                {}
            )
        )
    )

    # -----------------------------------------------------
    # CLEAN PEOPLE
    # -----------------------------------------------------

    cleaned_people = (
        clean_people(
            company_data.get(
                "people",
                []
            )
        )
    )

    # -----------------------------------------------------
    # FINAL COMPANY OBJECT
    # -----------------------------------------------------

    cleaned = {

        "company_name":
            company_data.get(
                "company_name"
            ),

        "website":
            normalize_url(
                company_data.get(
                    "website"
                )
                or source_url
            ),

        "company_type":
            company_data.get(
                "company_type"
            ),

        "industry":
            clean_industry(
                company_data.get(
                    "industry"
                )
            ),

        "founded_year":
            company_data.get(
                "founded"
            ),

        "about":
            clean_about(
                company_data.get(
                    "about"
                )
            ),

        "services":
            clean_services(
                company_data.get(
                    "services"
                )
            ),

        "technologies":
            cleaned_technologies,

        "employees":
            company_data.get(
                "employees"
            ),

        "clients":
            company_data.get(
                "clients"
            ),

        "projects":
            company_data.get(
                "projects"
            ),

        "people":
            cleaned_people,

        "email":
            cleaned_emails,

        "phone":
            cleaned_phones,

        "locations":
            cleaned_locations,

        "social_links":
            cleaned_social_links,

        "about_page":
            pages.get(
                "about_page"
            ),

        "contact_page":
            pages.get(
                "contact_page"
            ),

        "services_page":
            pages.get(
                "services_page"
            ),

        "careers_page":
            pages.get(
                "careers_page"
            ),

        "source_url":
            normalize_url(
                source_url
            ),

        "scraped_at":
            datetime.now().isoformat(),

        "status":
            "success"
    }

    return cleaned