from urllib.parse import urljoin, urlparse

from app.scraper.browser import create_driver
from app.scraper.page_loader import load_page


# =========================================================
# POSITIVE KEYWORDS
# =========================================================

PAGE_KEYWORDS = {

    "about_page": [
        "about",
        "about-us",
        "aboutus",
        "who-we-are",
        "our-story",
        "company-profile",
        "corporate-profile"
    ],

    "contact_page": [
        "contact",
        "contact-us",
        "contactus",
        "get-in-touch",
        "reach-us"
    ],

    "services_page": [
        "services",
        "service",
        "solutions",
        "capabilities",
        "offerings",
        "what-we-do"
    ],

    "careers_page": [
        "careers",
        "career",
        "jobs",
        "job-opportunities",
        "work-with-us",
        "join-us"
    ]
}


# =========================================================
# NEGATIVE KEYWORDS
# =========================================================

NEGATIVE_KEYWORDS = [

    "news",
    "newsroom",
    "press",
    "press-release",
    "press-releases",
    "blog",
    "blogs",
    "article",
    "articles",
    "event",
    "events",
    "media",
    "investor",
    "investors",
    "financial",
    "annual-report",
    "privacy",
    "terms",
    "cookie",
    "login",
    "search"
]


# =========================================================
# NORMALIZE URL
# =========================================================

def normalize_url(url):

    return url.rstrip("/")


# =========================================================
# SAME DOMAIN CHECK
# =========================================================

def is_same_domain(base_url, target_url):

    base_domain = urlparse(base_url).netloc.lower()

    target_domain = urlparse(target_url).netloc.lower()

    return base_domain == target_domain


# =========================================================
# CHECK NEGATIVE URL
# =========================================================

def contains_negative_keyword(url):

    url_lower = url.lower()

    for keyword in NEGATIVE_KEYWORDS:

        if keyword in url_lower:

            return True

    return False


# =========================================================
# CLASSIFY PAGE
# =========================================================

def classify_link(url, link_text="", title=""):

    url_lower = url.lower()

    text_lower = link_text.lower()

    title_lower = title.lower()

    # ---------------------------------------------
    # First reject unwanted pages
    # ---------------------------------------------

    if contains_negative_keyword(url):

        return None

    # ---------------------------------------------
    # Combine URL + link text + title
    # ---------------------------------------------

    combined_text = (
        url_lower
        + " "
        + text_lower
        + " "
        + title_lower
    )

    # ---------------------------------------------
    # Check page types
    # ---------------------------------------------

    for page_type, keywords in PAGE_KEYWORDS.items():

        for keyword in keywords:

            if keyword in combined_text:

                return page_type

    return None


# =========================================================
# DISCOVER IMPORTANT PAGES
# =========================================================

def discover_pages(driver, base_url):

    links = driver.find_elements("tag name", "a")

    discovered = {

        "about_page": None,

        "contact_page": None,

        "services_page": None,

        "careers_page": None
    }

    for link in links:

        try:

            href = link.get_attribute("href")

            if not href:
                continue

            # Link text
            link_text = link.text.strip()

            # Convert relative URL → absolute URL
            absolute_url = urljoin(
                base_url,
                href
            )

            # Only same website
            if not is_same_domain(
                base_url,
                absolute_url
            ):
                continue

            # Classify
            page_type = classify_link(
                absolute_url,
                link_text
            )

            if not page_type:
                continue

            # Save first valid page
            if discovered[page_type] is None:

                discovered[page_type] = absolute_url

        except Exception:

            continue

    return discovered


# =========================================================
# MAIN CRAWLER
# =========================================================

def crawl_website(url):

    url = normalize_url(url)

    driver = create_driver()

    pages_html = {}

    try:

        # ---------------------------------------------
        # STEP 1: Homepage
        # ---------------------------------------------

        print("\nLoading homepage...")

        homepage_html = load_page(
            driver,
            url
        )

        pages_html["homepage"] = homepage_html

        # ---------------------------------------------
        # STEP 2: Discover important pages
        # ---------------------------------------------

        print("\nDiscovering important company pages...")

        discovered_pages = discover_pages(
            driver,
            url
        )

        # ---------------------------------------------
        # STEP 3: Load only important pages
        # ---------------------------------------------

        for page_type, page_url in discovered_pages.items():

            if not page_url:

                pages_html[page_type] = None

                continue

            try:

                print(
                    f"\nLoading {page_type}:"
                )

                print(page_url)

                html = load_page(
                    driver,
                    page_url
                )

                pages_html[page_type] = html

            except Exception as error:

                print(
                    f"Failed to load {page_type}: {error}"
                )

                pages_html[page_type] = None

        # ---------------------------------------------
        # RETURN RESULT
        # ---------------------------------------------

        return {

            "source_url": url,

            "pages": discovered_pages,

            "pages_html": pages_html
        }

    finally:

        driver.quit()