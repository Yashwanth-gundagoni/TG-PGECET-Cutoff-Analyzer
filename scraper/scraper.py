import re

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By  # <-- Add this line
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException
)

from database import db
from models import Candidate
from app import app


def setup_driver():
    """
    Creates and returns a Chrome WebDriver and WebDriverWait object.
    """
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install())
    )

    driver.maximize_window()

    wait = WebDriverWait(driver, 20)

    return driver, wait


def restart_browser(year):
    """
    Opens a fresh browser and loads the website.
    """
    driver, wait = setup_driver()
    open_website(driver, year)
    return driver, wait


URLS = {
    2025: "https://pgecetadm.tgche.ac.in/allotp2/info/allotmentlist",
    2026: "https://pgecetadm.tgche.ac.in/Allot26/info/allotmentlist"
}

YEAR = 2026
RESTART_AFTER_RECORDS = 1000


def open_website(driver, year):
    """
    Opens the TG PGECET allotment website for the given year.
    """
    if year not in URLS:
        raise ValueError(f"No URL configured for year {year}")

    driver.get(URLS[year])


def get_college_dropdown(wait):
    """
    Returns the College dropdown as a Selenium Select object.
    """
    dropdown = Select(
        wait.until(
            EC.presence_of_element_located((By.ID, "collcode"))
        )
    )

    return dropdown


def get_all_colleges(dropdown):
    """
    Returns all college options except the first placeholder.
    """
    colleges = []

    for index in range(1, len(dropdown.options)):
        option_text = dropdown.options[index].text.strip()
        colleges.append((index, option_text))

    return colleges


def select_college(wait, index):
    """
    Selects a college using its index and returns its name.
    """
    dropdown = get_college_dropdown(wait)

    dropdown.select_by_index(index)

    return dropdown.first_selected_option.text.strip()


def click_search(driver, wait):
    """
    Clicks the Search button and waits until
    the previous results are replaced.
    """

    # Store the current results container (if it exists)
    old_container = None

    try:
        old_container = driver.find_element(By.CSS_SELECTOR, "div.rajc")
    except Exception:
        pass

    search_button = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "input.btn.btn-success.dd")
        )
    )

    search_button.click()

    # Wait until the previous results disappear
    if old_container:
        wait.until(EC.staleness_of(old_container))


def get_table_rows(wait):
    """
    Returns only the PGECET candidate rows.
    Works for both:
    1. Colleges with GATE + PGECET
    2. Colleges with only PGECET
    """

    container = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div.rajc")
        )
    )

    tables = container.find_elements(By.TAG_NAME, "table")

    for table in tables:
        rows = table.find_elements(By.TAG_NAME, "tr")

        if len(rows) < 2:
            continue

        first_data_row = rows[1]
        cells = first_data_row.find_elements(By.TAG_NAME, "td")

        if len(cells) < 3:
            continue

        value = cells[2].text.strip()

        # PGECET values look like: 99.2755 (65)
        if "(" in value and ")" in value:
            return rows[1:]   # Skip header row

    raise Exception("PGECET table not found!")


def extract_candidate(row):
    """
    Extracts candidate information from a table row.
    """

    cells = row.find_elements(By.TAG_NAME, "td")

    # Expected columns:
    # 0 -> SNO
    # 1 -> Empty Cell
    # 2 -> Percentile(Rank)
    # 3 -> Name
    # 4 -> Category
    # 5 -> Gender
    # 6 -> Region
    # 7 -> Allotted Category
    # 8 -> Phase

    if len(cells) < 9:
        return None

    sno = cells[0].text.strip()

    percentile_rank = cells[2].text.strip()

    numbers = re.findall(r"[\d.]+", percentile_rank)

    percentile = numbers[0] if len(numbers) >= 1 else ""
    rank = numbers[1] if len(numbers) >= 2 else ""

    candidate = {
        "sno": sno,
        "percentile": percentile,
        "rank": rank,
        "name": cells[3].text.strip(),
        "category": cells[4].text.strip(),
        "gender": cells[5].text.strip(),
        "region": cells[6].text.strip(),
        "allotted_category": cells[7].text.strip(),
        "phase": cells[8].text.strip()
    }

    return candidate


def scrape_college(wait):
    """
    Scrapes all candidates for the selected college.
    """

    rows = get_table_rows(wait)

    candidates = []

    for row in rows:
        candidate = extract_candidate(row)

        if candidate:
            candidates.append(candidate)

    return candidates


def save_candidate(candidate_data, college, year):
    """
    Saves one candidate into the database.
    """

    candidate = Candidate(
        college=college,
        sno=int(candidate_data["sno"]),
        percentile=float(candidate_data["percentile"]),
        rank=int(candidate_data["rank"]),
        name=candidate_data["name"],
        category=candidate_data["category"],
        gender=candidate_data["gender"],
        region=candidate_data["region"],
        allotted_category=candidate_data["allotted_category"],
        phase=candidate_data["phase"],
        year=year
    )

    db.session.add(candidate)


if __name__ == "__main__":
    driver, wait = setup_driver()

    try:
        open_website(driver, YEAR)

        dropdown = get_college_dropdown(wait)
        colleges = get_all_colleges(dropdown)

        print(f"Total Colleges: {len(colleges)}")

        with app.app_context():

            total_saved = 0
            next_restart = RESTART_AFTER_RECORDS
            skipped_colleges = 0

            for count, (index, college) in enumerate(colleges, start=1):

                print("\n" + "=" * 80)
                print(f"[{count}/{len(colleges)}]")
                print(college)

                try:
                    # Select college
                    selected = select_college(wait, index)

                    # Click Search
                    click_search(driver, wait)

                    # Scrape candidates
                    candidates = scrape_college(wait)

                    print(f"Candidates Found: {len(candidates)}")

                    for candidate in candidates:
                        save_candidate(
                            candidate_data=candidate,
                            college=selected,
                            year=YEAR
                        )
                        total_saved += 1

                    db.session.commit()

                    print("Saved Successfully!")
                    print(f"Total Records Saved: {total_saved}")

# Restart browser after every 1000 records
                    if total_saved >= next_restart:

                        print("\n" + "=" * 80)
                        print(f"Restarting browser after {total_saved} records...")
                        print("=" * 80)

                        try:
                            driver.quit()
                        except Exception:
                            pass

                        driver, wait = restart_browser(YEAR)

                        next_restart += RESTART_AFTER_RECORDS

                        print("Browser restarted successfully.")

                except Exception as e:
                    db.session.rollback()
                    skipped_colleges += 1
                    print(f"Skipped: {e}")

        print("\n" + "=" * 60)
        print("Scraping Completed!")
        print("=" * 60)

        print(f"Total Colleges : {len(colleges)}")
        print(f"Total Records  : {total_saved}")
        print(f"Skipped        : {skipped_colleges}")

        input("\nPress Enter to close the browser...")

    finally:
        try:
            driver.quit()
        except Exception:
            pass