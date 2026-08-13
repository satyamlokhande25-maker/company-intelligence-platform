import re
from bs4 import BeautifulSoup


def extract_locations(html):

    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")

    # Remove unwanted elements
    for tag in soup([
        "script",
        "style",
        "noscript",
        "svg"
    ]):
        tag.decompose()

    text = soup.get_text(
        " ",
        strip=True
    )

    locations = []

    # -------------------------------------------------
    # COUNTRY / CITY / ADDRESS KEYWORDS
    # -------------------------------------------------

    keywords = [
        "address",
        "location",
        "office",
        "head office",
        "headquarters",
        "registered office",
        "india",
        "usa",
        "united states",
        "canada",
        "uk",
        "united kingdom"
    ]

    # -------------------------------------------------
    # Find sentences containing location keywords
    # -------------------------------------------------

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text
    )

    for sentence in sentences:

        sentence = sentence.strip()

        if len(sentence) < 20:
            continue

        lower_sentence = sentence.lower()

        if any(
            keyword in lower_sentence
            for keyword in keywords
        ):

            # Avoid extremely large text blocks
            if len(sentence) <= 500:

                locations.append(sentence)

    # -------------------------------------------------
    # Remove duplicates
    # -------------------------------------------------

    unique_locations = []

    seen = set()

    for location in locations:

        normalized = re.sub(
            r"\s+",
            " ",
            location
        ).strip()

        key = normalized.lower()

        if key not in seen:

            seen.add(key)

            unique_locations.append(
                normalized
            )

    return unique_locations[:20]