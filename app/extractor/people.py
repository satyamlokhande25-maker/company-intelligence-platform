import re
from bs4 import BeautifulSoup


# =========================================================
# LEADERSHIP / PEOPLE EXTRACTION
# =========================================================

def extract_people(html):
    """
    Extract leadership/team members from company website HTML.

    Returns:
        [
            {
                "name": "Rich Miller",
                "designation": "CTO"
            }
        ]
    """

    if not html:
        return []

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    people = []

    # =====================================================
    # LEADERSHIP ROLES
    # =====================================================

    role_patterns = {

        "CEO": [
            r"\bCEO\b",
            r"\bChief Executive Officer\b"
        ],

        "CTO": [
            r"\bCTO\b",
            r"\bChief Technology Officer\b"
        ],

        "CFO": [
            r"\bCFO\b",
            r"\bChief Financial Officer\b"
        ],

        "COO": [
            r"\bCOO\b",
            r"\bChief Operating Officer\b"
        ],

        "Founder": [
            r"\bFounder\b"
        ],

        "Co-Founder": [
            r"\bCo-Founder\b",
            r"\bCoFounder\b"
        ],

        "Director": [
            r"\bManaging Director\b",
            r"\bDirector\b"
        ],

        "President": [
            r"\bPresident\b"
        ],

        "Vice President": [
            r"\bVice President\b",
            r"\bVP\b"
        ],

        "Head": [
            r"\bHead of\b"
        ],

        "Manager": [
            r"\bManager\b"
        ]
    }

    # =====================================================
    # INVALID WORDS
    # =====================================================

    invalid_words = {

        "governance",
        "compliance",
        "design",
        "services",
        "solutions",
        "solution",
        "technology",
        "technologies",
        "software",
        "development",
        "artificial",
        "intelligence",
        "cloud",
        "cyber",
        "security",
        "data",
        "analytics",
        "engineering",
        "machine",
        "learning",
        "digital",
        "marketing",
        "consulting",
        "innovation",
        "strategy",
        "business",
        "platform",
        "platforms",
        "framework",
        "process",
        "project",
        "projects",
        "product",
        "products",
        "capability",
        "capabilities"
    }

    # =====================================================
    # PERSON NAME VALIDATION
    # =====================================================

    def is_valid_person_name(name):

        if not name:
            return False

        name = name.strip()

        # Length
        if len(name) < 4:
            return False

        if len(name) > 80:
            return False

        # URLs / Emails
        if "http://" in name.lower():
            return False

        if "https://" in name.lower():
            return False

        if "www." in name.lower():
            return False

        if "@" in name:
            return False

        # Remove separators for validation
        cleaned = re.sub(
            r"[|,:;()\[\]{}]",
            " ",
            name
        )

        cleaned = re.sub(
            r"\s+",
            " ",
            cleaned
        ).strip()

        words = cleaned.split()

        # A person name should have at least 2 words
        if len(words) < 2:
            return False

        if len(words) > 5:
            return False

        # Reject known non-person words
        lower_name = cleaned.lower()

        for word in invalid_words:

            if re.search(
                r"\b" + re.escape(word) + r"\b",
                lower_name
            ):
                return False

        # Validate name words
        valid_word_count = 0

        for word in words:

            word = word.strip(".-")

            if not word:
                continue

            if re.fullmatch(
                r"[A-Za-zÀ-ÖØ-öø-ÿ]+(?:['-][A-Za-zÀ-ÖØ-öø-ÿ]+)*",
                word
            ):
                valid_word_count += 1

        if valid_word_count < 2:
            return False

        # Reject sentence-like text
        sentence_words = {
            "our",
            "the",
            "and",
            "with",
            "for",
            "from",
            "this",
            "that",
            "your",
            "we",
            "you",
            "by",
            "of"
        }

        if any(
            word.lower() in sentence_words
            for word in words
        ):
            return False

        return True

    # =====================================================
    # REMOVE DESIGNATION FROM NAME
    # =====================================================

    def remove_designation(
        candidate,
        designation
    ):
        """
        Convert:

            Rich Miller, CTO
            Rich Miller - CTO
            Rich Miller | CTO
            Rich Miller : CTO
            Rich Miller CTO

        into:

            Rich Miller
        """

        if not candidate:
            return None

        candidate = re.sub(
            r"\s+",
            " ",
            candidate
        ).strip()

        # -----------------------------------------------
        # Rich Miller, CTO
        # Rich Miller - CTO
        # Rich Miller | CTO
        # Rich Miller : CTO
        # -----------------------------------------------

        candidate = re.sub(
            r"\s*[,|:\-–—]\s*"
            + re.escape(designation)
            + r"\b.*$",
            "",
            candidate,
            flags=re.IGNORECASE
        )

        # -----------------------------------------------
        # Rich Miller CTO
        # -----------------------------------------------

        candidate = re.sub(
            r"\s+"
            + re.escape(designation)
            + r"\b.*$",
            "",
            candidate,
            flags=re.IGNORECASE
        )

        candidate = re.sub(
            r"\s+",
            " ",
            candidate
        ).strip()

        candidate = candidate.strip(
            ".,:;|-–—"
        )

        return candidate

    # =====================================================
    # EXTRACT NAME FROM ELEMENT
    # =====================================================

    def extract_name_from_element(
        element,
        text,
        designation
    ):

        # =================================================
        # 1. HEADING
        # =================================================

        heading = element.find(
            [
                "h1",
                "h2",
                "h3",
                "h4",
                "h5",
                "h6"
            ]
        )

        if heading:

            candidate = heading.get_text(
                " ",
                strip=True
            )

            candidate = remove_designation(
                candidate,
                designation
            )

            if is_valid_person_name(
                candidate
            ):
                return candidate

        # =================================================
        # 2. STRONG / BOLD
        # =================================================

        strong = element.find(
            [
                "strong",
                "b"
            ]
        )

        if strong:

            candidate = strong.get_text(
                " ",
                strip=True
            )

            candidate = remove_designation(
                candidate,
                designation
            )

            if is_valid_person_name(
                candidate
            ):
                return candidate

        # =================================================
        # 3. NAME BEFORE DESIGNATION
        # =================================================

        patterns = [

            # Rich Miller, CTO
            r"([A-Za-zÀ-ÖØ-öø-ÿ]"
            r"[A-Za-zÀ-ÖØ-öø-ÿ .'-]{1,60}?)"
            r"\s*,\s*"
            + re.escape(designation)
            + r"\b",

            # Rich Miller - CTO
            r"([A-Za-zÀ-ÖØ-öø-ÿ]"
            r"[A-Za-zÀ-ÖØ-öø-ÿ .'-]{1,60}?)"
            r"\s*[-–—]\s*"
            + re.escape(designation)
            + r"\b",

            # Rich Miller | CTO
            r"([A-Za-zÀ-ÖØ-öø-ÿ]"
            r"[A-Za-zÀ-ÖØ-öø-ÿ .'-]{1,60}?)"
            r"\s*\|\s*"
            + re.escape(designation)
            + r"\b",

            # Rich Miller CTO
            r"([A-Za-zÀ-ÖØ-öø-ÿ]"
            r"[A-Za-zÀ-ÖØ-öø-ÿ .'-]{1,60}?)"
            r"\s+"
            + re.escape(designation)
            + r"\b"
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE
            )

            if match:

                candidate = (
                    match.group(1)
                    .strip()
                )

                candidate = remove_designation(
                    candidate,
                    designation
                )

                if is_valid_person_name(
                    candidate
                ):
                    return candidate

        # =================================================
        # 4. GENERIC FALLBACK
        # =================================================

        role_match = re.search(
            r"(.{2,80}?)"
            r"\s*,?\s*"
            + re.escape(designation),
            text,
            re.IGNORECASE
        )

        if role_match:

            candidate = (
                role_match
                .group(1)
                .strip()
            )

            candidate = remove_designation(
                candidate,
                designation
            )

            if is_valid_person_name(
                candidate
            ):
                return candidate

        return None

    # =====================================================
    # SEARCH HTML ELEMENTS
    # =====================================================

    elements = soup.find_all(
        [
            "div",
            "section",
            "article",
            "li",
            "p",
            "header"
        ]
    )

    # =====================================================
    # PROCESS ELEMENTS
    # =====================================================

    for element in elements:

        text = element.get_text(
            " ",
            strip=True
        )

        if not text:
            continue

        # Ignore very large sections
        if len(text) > 500:
            continue

        # Ignore very small text
        if len(text) < 5:
            continue

        # =================================================
        # FIND DESIGNATION
        # =================================================

        designation = None

        for role, patterns in role_patterns.items():

            for pattern in patterns:

                if re.search(
                    pattern,
                    text,
                    re.IGNORECASE
                ):

                    designation = role

                    break

            if designation:
                break

        if not designation:
            continue

        # =================================================
        # FIND PERSON NAME
        # =================================================

        name = extract_name_from_element(
            element,
            text,
            designation
        )

        if not name:
            continue

        # =================================================
        # CLEAN NAME
        # =================================================

        name = re.sub(
            r"\s+",
            " ",
            name
        ).strip()

        name = name.strip(
            ".,:;|-–—"
        )

        # =================================================
        # FINAL VALIDATION
        # =================================================

        if not is_valid_person_name(
            name
        ):
            continue

        # =================================================
        # ADD PERSON
        # =================================================

        people.append(
            {
                "name": name,
                "designation": designation
            }
        )

    # =====================================================
    # REMOVE DUPLICATES
    # =====================================================

    unique_people = []

    seen = set()

    for person in people:

        key = (
            person["name"]
            .lower()
            .strip(),
            person["designation"]
            .lower()
            .strip()
        )

        if key in seen:
            continue

        seen.add(key)

        unique_people.append(
            person
        )

    # =====================================================
    # FINAL RESULT
    # =====================================================

    return unique_people