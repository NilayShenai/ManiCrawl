from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, WebDriverException
import time
import json
import concurrent.futures
import os
import sys

def crawl_year(year):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)

    driver.get("https://libportal.manipal.edu/MIT/Question%20Paper.aspx")
    time.sleep(2)

    pdfs = []
    visited = set()

    def click_folder_by_name(name, retries=3):
        for attempt in range(retries):
            try:
                time.sleep(1)
                folder_links = driver.find_elements(By.XPATH,
                    "//a[starts-with(@id, 'ctl') and contains(@href, '__doPostBack') and img[contains(@src, 'folder')]]")
                for link in folder_links:
                    if link.text.strip() == name:
                        wait.until(EC.element_to_be_clickable(link)).click()
                        time.sleep(2)
                        return True
            except (StaleElementReferenceException, TimeoutException, WebDriverException) as e:
                print(f"Retry {attempt+1}/{retries} for folder '{name}': {e}", flush=True)
        return False

    def go_back():
        try:
            back_link = driver.find_element(By.XPATH, "//a[contains(text(), '..')]")
            wait.until(EC.element_to_be_clickable(back_link)).click()
            time.sleep(2)
        except Exception as e:
            print(f"Back navigation failed: {e}", flush=True)

    def crawl_folder(path):
        path_key = " / ".join(path)
        if path_key in visited:
            return
        visited.add(path_key)

        print(f"Currently at: {path_key}", flush=True)

        try:
            pdf_links = driver.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
            for link in pdf_links:
                try:
                    href = link.get_attribute("href")
                    name = link.text.strip()
                    if href:
                        pdfs.append({
                            "path": path,
                            "name": name,
                            "url": href
                        })
                        print("  " * len(path) + name, flush=True)
                except StaleElementReferenceException:
                    continue

            folder_links = driver.find_elements(By.XPATH,
                "//a[starts-with(@id, 'ctl') and contains(@href, '__doPostBack') and img[contains(@src, 'folder')]]")
            folder_names = [f.text.strip() for f in folder_links if f.text.strip() and f.text.strip() != ".."]

            for name in folder_names:
                print("  " * len(path) + f"Entering: {name}", flush=True)
                if click_folder_by_name(name):
                    crawl_folder(path + [name])
                    go_back()

        except Exception as e:
            print(f"Error crawling folder {'/'.join(path)}: {e}", flush=True)

    try:
        print(f"Starting year: {year}", flush=True)
        if click_folder_by_name(str(year)):
            crawl_folder([str(year)])
        else:
            print(f"Year folder '{year}' not found, crawling root instead.", flush=True)
            crawl_folder([])

        os.makedirs("pdf_results", exist_ok=True)
        output_file = f"pdf_results/{year}_pdfs.json"
        with open(output_file, "w") as f:
            json.dump(pdfs, f, indent=2)

        print(f"Finished {year}: {len(pdfs)} PDFs collected.", flush=True)
        return year, len(pdfs)

    finally:
        driver.quit()

def main():
    os.makedirs("pdf_results", exist_ok=True)

    years = list(range(2010, 2025))  # 2010 to 2024

    with concurrent.futures.ThreadPoolExecutor(max_workers=min(5, len(years))) as executor:
        future_to_year = {executor.submit(crawl_year, year): year for year in years}
        for future in concurrent.futures.as_completed(future_to_year):
            year = future_to_year[future]
            try:
                y, count = future.result(timeout=1800)  # 30-minute timeout per year
                print(f"{y}: {count} PDFs collected", flush=True)
            except Exception as e:
                print(f"Error crawling {year}: {e}", flush=True)

if __name__ == '__main__':
    main()
