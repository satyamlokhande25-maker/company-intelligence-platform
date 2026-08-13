from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# =========================================================
# JUNK / SHARE SUBPATHS TO IGNORE
# =========================================================
IGNORE_PATHS = [
    "/sharer", "/share", "/intent", "/dialog", "/widgets",
    "/tr", "/login", "/home", "/hashtag"
]

# =========================================================
# IDENTIFY SOCIAL PLATFORM
# =========================================================

def identify_social_platform(url):
    """
    Identify social media platform from URL and ignore root/generic links.
    """
    if not url:
        return None

    try:
        parsed = urlparse(url)
        hostname = parsed.netloc.lower().replace("www.", "")
        path = parsed.path.strip().lower()

        # Direct root links ya empty path skip karo (e.g. "", "/")
        if not path or path == "/":
            return None

        # Ignore share/intent/login URLs
        if any(junk in path for junk in IGNORE_PATHS):
            return None

        # ---------------------------------------------
        # LinkedIn
        # ---------------------------------------------
        if hostname == "linkedin.com":
            if (
                path.startswith("/company/")
                or path.startswith("/in/")
                or path.startswith("/school/")
            ):
                return "linkedin"

        # ---------------------------------------------
        # Facebook
        # ---------------------------------------------
        if hostname == "facebook.com":
            return "facebook"

        # ---------------------------------------------
        # Instagram
        # ---------------------------------------------
        if hostname == "instagram.com":
            return "instagram"

        # ---------------------------------------------
        # YouTube
        # ---------------------------------------------
        if hostname == "youtube.com":
            if (
                path.startswith("/@")
                or path.startswith("/channel/")
                or path.startswith("/c/")
                or path.startswith("/user/")
            ):
                return "youtube"

        if hostname == "youtu.be":
            return "youtube"

        # ---------------------------------------------
        # Twitter / X
        # ---------------------------------------------
        if hostname in ("twitter.com", "x.com"):
            return "twitter"

        # ---------------------------------------------
        # GitHub
        # ---------------------------------------------
        if hostname == "github.com":
            return "github"

    except Exception:
        return None

    return None


# =========================================================
# CLEAN SOCIAL URL
# =========================================================

def clean_social_url(url):
    """
    Clean and normalize social media URL.
    """
    if not url:
        return None

    url = str(url).strip().strip("\"'")

    if url.startswith("//"):
        url = "https:" + url
    elif not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            return None

        # Clean tracking query parameters
        clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")
        return clean_url
    except Exception:
        return None


# =========================================================
# VALIDATE SOCIAL URL
# =========================================================

def is_valid_social_url(url):
    """
    Validate whether URL belongs to a supported social media profile.
    """
    if not url:
        return False

    platform = identify_social_platform(url)
    return platform is not None


# =========================================================
# EXTRACT SOCIAL LINKS
# =========================================================

def extract_social_links(html, base_url=None):
    """
    Extract official social media links from HTML.
    """
    social_links = {
        "linkedin": [],
        "facebook": [],
        "instagram": [],
        "youtube": [],
        "twitter": [],
        "github": []
    }

    if not html:
        return social_links

    soup = BeautifulSoup(html, "html.parser")

    for link in soup.find_all("a", href=True):
        href = link.get("href")
        if not href:
            continue

        href = href.strip()

        if href.lower().startswith(("mailto:", "tel:", "javascript:", "#")):
            continue

        if base_url:
            href = urljoin(base_url, href)

        href = clean_social_url(href)

        if not href or not is_valid_social_url(href):
            continue

        platform = identify_social_platform(href)

        if platform and href not in social_links[platform]:
            social_links[platform].append(href)

    return social_links


# =========================================================
# GET PRIMARY SOCIAL LINKS
# =========================================================

def get_primary_social_links(social_links):
    """
    Select one primary URL for each platform.
    """
    primary = {
        "linkedin": None,
        "facebook": None,
        "instagram": None,
        "youtube": None,
        "twitter": None,
        "github": None
    }

    if not social_links:
        return primary

    for platform in primary:
        links = social_links.get(platform, [])
        if links:
            primary[platform] = links[0]

    return primary


# =========================================================
# MAIN SOCIAL EXTRACTION FUNCTION
# =========================================================

def extract_social_information(html, base_url=None):
    """
    Complete social media extraction.
    """
    return extract_social_links(html, base_url)