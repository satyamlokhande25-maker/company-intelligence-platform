import sys
import os

# =========================================================
# ADD PROJECT ROOT TO PYTHON PATH
# =========================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.insert(
    0,
    PROJECT_ROOT
)


from app.scraper.crawler import crawl_website
from app.extractor.people import extract_people


# =========================================================
# COMPANY WEBSITE
# =========================================================

url = "https://bestpeers.com/"


# =========================================================
# START CRAWLER
# =========================================================

result = crawl_website(url)


print("\n")
print("=" * 70)
print("PEOPLE / LEADERSHIP EXTRACTION")
print("=" * 70)


# =========================================================
# EXTRACT PEOPLE
# =========================================================

all_people = []


for page_type, html in result["pages_html"].items():

    if not html:
        continue

    people = extract_people(
        html
    )

    if people:

        print(
            f"\n{page_type}"
        )

        for person in people:

            print(
                f"- {person['name']} | "
                f"{person['designation']}"
            )

            all_people.append(
                person
            )


# =========================================================
# REMOVE DUPLICATES
# =========================================================

unique_people = []

seen = set()


for person in all_people:

    key = (
        person["name"].lower(),
        person["designation"].lower()
    )

    if key not in seen:

        seen.add(key)

        unique_people.append(
            person
        )


# =========================================================
# FINAL PEOPLE
# =========================================================

print("\n")
print("=" * 70)
print("FINAL PEOPLE")
print("=" * 70)


if unique_people:

    for person in unique_people:

        print(
            f"- {person['name']} | "
            f"{person['designation']}"
        )

else:

    print(
        "No leadership/team members found"
    )