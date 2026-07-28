import re

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException
)


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


URLS = {
    2025: "https://pgecetadm.tgche.ac.in/allotp2/info/allotmentlist",
    2026: "https://pgecetadm.tgche.ac.in/Allot26/info/allotmentlist"
}


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


def click_search(wait):
    """
    Clicks the Search button.
    """
    search_button = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "input.btn.btn-success.dd")
        )
    )

    search_button.click()


def get_table_rows(wait):
    """
    Returns all candidate rows from the results table.
    """
    table = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div.rajc table")
        )
    )

    rows = table.find_elements(By.TAG_NAME, "tr")

    # Skip header row
    return rows[1:]


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


if __name__ == "__main__":
    driver, wait = setup_driver()

    try:
        open_website(driver, 2026)

        dropdown = get_college_dropdown(wait)

        colleges = get_all_colleges(dropdown)

        print(f"Total Colleges: {len(colleges)}")

        selected = select_college(wait, 1)

        print(f"\nSelected College:\n{selected}")

        click_search(wait)

        print("\nSearch button clicked successfully!")

        rows = get_table_rows(wait)

        print(f"\nTotal Candidate Rows: {len(rows)}")

        if rows:
            print("\nFirst Candidate:\n")

            candidate = extract_candidate(rows[0])

            for key, value in candidate.items():
                print(f"{key}: {value}")

        input("\nPress Enter to close the browser...")

    finally:
        driver.quit()