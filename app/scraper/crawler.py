import sys
import os
from pathlib import Path
from urllib.parse import urljoin, urlparse

# Ensure Project Root Path Resolution
FILE_PATH = Path(__file__).resolve()
ROOT_DIR = FILE_PATH.parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Safe Module Imports
try:
    from app.scraper.browser import create_driver
    from app.scraper.page_loader import load_page
except ModuleNotFoundError:
    from scraper.browser import create_driver
    from scraper.page_loader import load_page


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
# HELPER FUNCTIONS
# =========================================================

def normalize_url(url):
    return url.rstrip("/")


def is_same_domain(base_url, target_url):
    base_domain = urlparse(base_url).netloc.lower().replace("www.", "")
    target_domain = urlparse(target_url).netloc.lower().replace("www.", "")
    return base_domain == target_domain


def contains_negative_keyword(url):
    url_lower = url.lower()
    for keyword in NEGATIVE_KEYWORDS:
        if keyword in url_lower:
            return True
    return False


def classify_link(url, link_text="", title=""):
    url_lower = url.lower()
    text_lower = link_text.lower()
    title_lower = title.lower()

    # Reject unwanted URLs first
    if contains_negative_keyword(url_lower):
        return None

    # Combine metadata
    combined_text = f"{url_lower} {text_lower} {title_lower}"

    # Priority matching
    for page_type, keywords in PAGE_KEYWORDS.items():
        for keyword in keywords:
            if keyword in combined_text:
                return page_type

    return None


# =========================================================
# DISCOVER IMPORTANT PAGES
# =========================================================

def discover_pages(driver, base_url):
    discovered = {
        "about_page": None,
        "contact_page": None,
        "services_page": None,
        "careers_page": None
    }

    try:
        # Extract link attributes in one go to prevent StaleElement Exceptions
        links = driver.find_elements("tag name", "a")
        raw_links_data = []

        for link in links:
            try:
                href = link.get_attribute("href")
                text = link.text.strip() or link.get_attribute("title") or ""
                if href:
                    raw_links_data.append((href, text))
            except Exception:
                continue

        for href, link_text in raw_links_data:
            absolute_url = urljoin(base_url, href)

            if not is_same_domain(base_url, absolute_url):
                continue

            page_type = classify_link(absolute_url, link_text)

            if page_type and discovered[page_type] is None:
                discovered[page_type] = absolute_url

            # Break early if all pages are found
            if all(val is not None for val in discovered.values()):
                break

    except Exception as err:
        print(f"Error during link discovery: {err}")

    return discovered


# =========================================================
# MAIN CRAWLER
# =========================================================

def crawl_website(url):
    url = normalize_url(url)
    driver = create_driver()
    pages_html = {}

    try:
        # STEP 1: Homepage
        print("\nLoading homepage...")
        homepage_html = load_page(driver, url)
        pages_html["homepage"] = homepage_html

        # STEP 2: Discover important pages
        print("\nDiscovering important company pages...")
        discovered_pages = discover_pages(driver, url)

        # STEP 3: Load discovered pages
        for page_type, page_url in discovered_pages.items():
            if not page_url:
                pages_html[page_type] = None
                continue

            try:
                print(f"\nLoading {page_type}: {page_url}")
                html = load_page(driver, page_url)
                pages_html[page_type] = html
            except Exception as error:
                print(f"Failed to load {page_type}: {error}")
                pages_html[page_type] = None

        return {
            "source_url": url,
            "pages": discovered_pages,
            "pages_html": pages_html
        }

    finally:
        driver.quit()