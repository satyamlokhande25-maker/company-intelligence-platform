import re
from bs4 import BeautifulSoup


EMAIL_PATTERN = re.compile(
    r"""
    [A-Za-z0-9._%+-]+
    @
    [A-Za-z0-9.-]+
    \.
    [A-Za-z]{2,}
    """,
    re.VERBOSE
)


PHONE_PATTERN = re.compile(
    r"""
    (?:
        \+?\d{1,3}[\s().-]*
    )?
    (?:\d[\s().-]*){7,14}
    """,
    re.VERBOSE
)


def clean_email(email):

    email = email.strip().lower()

    email = email.replace(
        "mailto:",
        ""
    )

    email = email.split("?")[0]

    return email


def clean_phone(phone):

    phone = phone.strip()

    # Remove common HTML/text junk
    phone = phone.replace(
        "tel:",
        ""
    )

    # Keep digits and +
    phone = re.sub(
        r"[^\d+]",
        "",
        phone
    )

    return phone


def is_valid_email(email):

    if not EMAIL_PATTERN.fullmatch(email):
        return False

    # Ignore obvious non-contact emails
    ignored = [
        "example.com",
        "example.org",
        "test.com"
    ]

    for domain in ignored:

        if email.endswith(domain):
            return False

    return True


def is_valid_phone(phone):

    digits = re.sub(
        r"\D",
        "",
        phone
    )

    return 7 <= len(digits) <= 15


def extract_emails(html):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    emails = set()

    # =================================================
    # 1. mailto links
    # =================================================

    for link in soup.find_all(
        "a",
        href=True
    ):

        href = link["href"].strip()

        if href.lower().startswith("mailto:"):

            email = clean_email(href)

            if is_valid_email(email):

                emails.add(email)

    # =================================================
    # 2. Visible page text
    # =================================================

    text = soup.get_text(
        " ",
        strip=True
    )

    for email in EMAIL_PATTERN.findall(text):

        email = clean_email(email)

        if is_valid_email(email):

            emails.add(email)

    # =================================================
    # 3. Raw HTML
    # =================================================

    for email in EMAIL_PATTERN.findall(html):

        email = clean_email(email)

        if is_valid_email(email):

            emails.add(email)

    return sorted(emails)


def extract_phones(html):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    phones = set()

    # =================================================
    # 1. tel links
    # =================================================

    for link in soup.find_all(
        "a",
        href=True
    ):

        href = link["href"].strip()

        if href.lower().startswith("tel:"):

            phone = clean_phone(href)

            if is_valid_phone(phone):

                phones.add(phone)

    # =================================================
    # 2. Visible text
    # =================================================

    text = soup.get_text(
        " ",
        strip=True
    )

    for phone in PHONE_PATTERN.findall(text):

        phone = clean_phone(phone)

        if is_valid_phone(phone):

            phones.add(phone)

    return sorted(phones)


def extract_contact_information(html):

    emails = extract_emails(html)

    phones = extract_phones(html)

    return {
        "emails": emails,
        "phones": phones
    }