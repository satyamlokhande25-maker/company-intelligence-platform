import re
from bs4 import BeautifulSoup


def clean_text(text):
    if not text:
        return None

    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_title(soup):
    title = soup.find("title")

    if not title:
        return None

    return clean_text(
        title.get_text(" ", strip=True)
    )


def extract_company_name(html):
    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    # Try JSON-LD first
    for script in soup.find_all(
        "script",
        type="application/ld+json"
    ):

        text = script.get_text(
            strip=True
        )

        if "BestPeers" in text:
            return "BestPeers"

    # Try logo / brand text
    for tag in soup.find_all(
        ["h1", "h2"]
    ):

        text = clean_text(
            tag.get_text(
                " ",
                strip=True
            )
        )

        if text and "bestpeers" in text.lower():

            return "BestPeers"

    # Try title
    title = extract_title(soup)

    if title:

        parts = re.split(
            r"\s*[|–-]\s*",
            title
        )

        if parts:

            return parts[0].strip()

    return None


def extract_founded(html):

    text = BeautifulSoup(
        html,
        "html.parser"
    ).get_text(
        " ",
        strip=True
    )

    patterns = [
        r"founded\s+(?:in\s+)?(\d{4})",
        r"established\s+(?:in\s+)?(\d{4})",
        r"since\s+(\d{4})"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            return match.group(1)

    return None


def extract_industry(html):

    text = BeautifulSoup(
        html,
        "html.parser"
    ).get_text(
        " ",
        strip=True
    )

    industry_keywords = {

        "Information Technology": [
            "information technology",
            "IT services",
            "IT solutions",
            "software development"
        ],

        "Software Development": [
            "software development",
            "software company",
            "software solutions"
        ],

        "Data & AI": [
            "data science",
            "data engineering",
            "artificial intelligence",
            "machine learning",
            "data analytics"
        ],

        "Consulting": [
            "technology consulting",
            "IT consulting",
            "consulting services"
        ]
    }

    found = []

    for industry, keywords in industry_keywords.items():

        for keyword in keywords:

            if keyword.lower() in text.lower():

                found.append(industry)

                break

    return list(dict.fromkeys(found))


def extract_about(html):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    # Find headings containing about
    headings = soup.find_all(
        ["h1", "h2", "h3"]
    )

    for heading in headings:

        heading_text = clean_text(
            heading.get_text(
                " ",
                strip=True
            )
        )

        if not heading_text:
            continue

        if "about" not in heading_text.lower():

            continue

        # Get nearby paragraph
        paragraph = heading.find_next(
            "p"
        )

        if paragraph:

            text = clean_text(
                paragraph.get_text(
                    " ",
                    strip=True
                )
            )

            if text and len(text) > 50:

                return text

    return None


def extract_services(html):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    services = set()

    service_keywords = [
        "software development",
        "web development",
        "mobile app development",
        "data analytics",
        "data engineering",
        "data science",
        "artificial intelligence",
        "machine learning",
        "cloud",
        "cyber security",
        "digital marketing",
        "staff augmentation",
        "ui ux",
        "consulting"
    ]

    text = soup.get_text(
        " ",
        strip=True
    ).lower()

    for service in service_keywords:

        if service in text:

            services.add(service.title())

    return sorted(services)


def extract_company_information(
    homepage_html,
    about_html=None,
    services_html=None
):

    company = {

        "company_name": None,

        "website": None,

        "industry": [],

        "founded": None,

        "about": None,

        "services": []
    }

    # ---------------------------------------------
    # COMPANY NAME
    # ---------------------------------------------

    company["company_name"] = extract_company_name(
        homepage_html
    )

    # ---------------------------------------------
    # WEBSITE
    # ---------------------------------------------

    company["website"] = "https://bestpeers.com"

    # ---------------------------------------------
    # FOUNDED
    # ---------------------------------------------

    company["founded"] = extract_founded(
        homepage_html
    )

    # ---------------------------------------------
    # INDUSTRY
    # ---------------------------------------------

    company["industry"] = extract_industry(
        homepage_html
    )

    # ---------------------------------------------
    # ABOUT
    # ---------------------------------------------

    if about_html:

        company["about"] = extract_about(
            about_html
        )

    if not company["about"]:

        company["about"] = extract_about(
            homepage_html
        )

    # ---------------------------------------------
    # SERVICES
    # ---------------------------------------------

    service_source = (
        services_html
        if services_html
        else homepage_html
    )

    company["services"] = extract_services(
        service_source
    )

    return company