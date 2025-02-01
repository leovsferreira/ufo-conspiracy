import time
import re
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

def generate_months(start, end):
    """
    Generates a list of month strings in 'yyyymm' format between start and end (inclusive).

    Parameters:
        start (str): Start month in 'yyyymm' format (e.g., '202001').
        end (str): End month in 'yyyymm' format (e.g., '202012').

    Returns:
        list: List of months as strings (e.g., ['202001', '202002', ..., '202012']).
    """
    start_year = int(start[:4])
    start_month = int(start[4:6])
    end_year = int(end[:4])
    end_month = int(end[4:6])
    
    months = []
    year = start_year
    month = start_month
    while (year < end_year) or (year == end_year and month <= end_month):
        months.append(f"{year}{month:02d}")
        month += 1
        if month > 12:
            month = 1
            year += 1
    return months

def init_driver(browser='chrome', headless=True):
    """
    Initializes a Selenium WebDriver for the chosen browser.

    Parameters:
        browser (str): Which browser to use. Options include 'chrome' or 'firefox'.
        headless (bool): Whether to run the browser in headless mode (without a GUI).

    Returns:
        webdriver instance: The initialized Selenium WebDriver.

    Important:
        - If you use Chrome, you need to have Google Chrome installed and the matching ChromeDriver.
        - If you choose Firefox, you need Mozilla Firefox and geckodriver installed.
        - To change browsers, simply pass browser='firefox' (or any other supported option).
    """
    if browser.lower() == 'chrome':
        options = Options()
        if headless:
            options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)
    elif browser.lower() == 'firefox':
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        options = FirefoxOptions()
        if headless:
            options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)
    else:
        raise ValueError("Unsupported browser. Please use 'chrome' or 'firefox'.")
    return driver

def scrape_month(driver, scraping_month, waiting_time=5):
    """
    Scrapes UFO report data from NUFORC for a given month.

    Parameters:
        driver (webdriver instance): The Selenium WebDriver (already initialized).
        scraping_month (str): Month to scrape in 'yyyymm' format.
        waiting_time (int): Seconds to wait after page loads for AJAX content to populate.

    Returns:
        list: A list of dictionaries with the data for each UFO report.
    
    Process:
        - The URL for a month is formed using the provided scraping_month.
        - The page is loaded and we wait for the AJAX-loaded table to appear.
        - We parse the page using BeautifulSoup to extract the total number of records.
        - Then we loop through the table pages (clicking the "Next" button as long as it is enabled)
          until all records for that month have been scraped.
    """
    url = f"https://nuforc.org/subndx/?id=e{scraping_month}"
    driver.get(url)
    time.sleep(waiting_time)  # Wait for the page and AJAX content to load

    # Parse the page and extract the total number of entries from the info div.
    soup = BeautifulSoup(driver.page_source, "html.parser")
    records_info = soup.find("div", {"class": "dataTables_info"})
    if records_info is None:
        print(f"Could not find records info for month {scraping_month}")
        return []
    records_text = records_info.text
    match = re.search(r'of (\d+) entries', records_text)
    if not match:
        print(f"Could not extract total records for month {scraping_month}")
        return []
    total_records = int(match.group(1))
    print(f"Month {scraping_month}: Total records to scrape: {total_records}")

    scraped_rows = []

    # Loop through pages until we have scraped all records for the month.
    while len(scraped_rows) < total_records:
        soup = BeautifulSoup(driver.page_source, "html.parser")
        table = soup.find("table", id="table_1")
        if table is None:
            print("Table not found.")
            break
        
        # Get the table body (all rows)
        tbody = table.find("tbody")
        if tbody:
            for row in tbody.find_all("tr"):
                cols = row.find_all("td")
                # We expect at least 5 columns: adjust if the table format changes.
                if len(cols) >= 5:
                    scraped_rows.append({
                        "datetime": cols[1].text.strip(),
                        "city": cols[2].text.strip(),
                        "state": cols[3].text.strip(),
                        "country": cols[4].text.strip(),
                        "shape": cols[5].text.strip(),
                        "summary": cols[6].text.strip(),
                    })
            print(f"Month {scraping_month}: Scraped {len(scraped_rows)} of {total_records} records so far...")
        else:
            print("Table body not found on this page.")
            break

        # If we have scraped all records, exit the loop.
        if len(scraped_rows) >= total_records:
            break

        # Find the "Next" button and click it if it is enabled.
        try:
            next_button = driver.find_element("id", "table_1_next")
        except Exception as e:
            print("Next button not found:", e)
            break

        next_class = next_button.get_attribute("class")
        if "disabled" in next_class:
            print("Next button disabled. End of pages for this month.")
            break

        # Click the next page button and wait for the new content to load.
        next_button.click()
        time.sleep(waiting_time)

    return scraped_rows

def scrape_nuforc_data(start_period=None, end_period=None, waiting_time=5, browser='chrome', headless=True):
    """
    Scrapes UFO report data from NUFORC over a specified time range.

    Parameters:
        start_period (str): Start month in 'yyyymm' format (e.g., '202001'). Defaults to current month.
        end_period (str): End month in 'yyyymm' format. Defaults to current month.
        waiting_time (int): Seconds to wait for each page load (adjust based on your connection).
        browser (str): Which browser to use with Selenium ('chrome' or 'firefox').
        headless (bool): Run the browser in headless mode if True (no GUI).

    Returns:
        pd.DataFrame: A DataFrame containing all scraped records over the specified period.

    Process:
        - If no start or end period is provided, defaults to the current month.
        - Generates a list of months between the start and end.
        - Initializes the WebDriver for the chosen browser.
        - For each month in the list, it calls scrape_month and aggregates the results.
        - Finally, it quits the driver and returns the combined DataFrame.
    """
    # Default to the current month if no range is provided.
    current_month = datetime.now().strftime('%Y%m')
    if start_period is None:
        start_period = current_month
    if end_period is None:
        end_period = current_month

    # Generate a list of months to scrape.
    months = generate_months(start_period, end_period)
    print("Months to scrape:", months)

    # Initialize the Selenium WebDriver.
    driver = init_driver(browser=browser, headless=headless)
    
    all_rows = []
    for month in months:
        print(f"Scraping month: {month}")
        month_data = scrape_month(driver, month, waiting_time=waiting_time)
        all_rows.extend(month_data)
    
    driver.quit()
    
    # Create a Pandas DataFrame from all the scraped records.
    df = pd.DataFrame(all_rows)
    return df

if __name__ == "__main__":
    # Example usage:
    # To scrape data for the current month only (default):
    # df = scrape_nuforc_data()
    
    # To scrape data for a range, for example from January 2023 to January 2025:
    df = scrape_nuforc_data(start_period="202301", end_period="202501", waiting_time=5, browser='chrome', headless=True)
    
    # Save the scraped data to CSV
    df.to_csv("../raw/nuforc_reports.csv", index=False)
    print("🛸 UFO data saved! (Watch out for black helicopters...)")
