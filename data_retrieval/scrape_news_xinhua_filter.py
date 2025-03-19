"""
Created on Sat Mar 1 14:30:59 2024

Author: davideliu

E-mail: davide97ls@gmail.com

Goal: Scrape Xinhua news articles with specific keywords
"""
import os
import re
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils import setup_chrome_driver


# Define search URLs for different keywords
SEARCH_CONFIG = {
    "利率": ("http://mrdx.xinhuanet.com/search.htm?channelid=11148&searchword=%E5%88%A9%E7%8E%87", 270),
    "政策执行": ("http://mrdx.xinhuanet.com/search.htm?channelid=11148&searchword=%E6%94%BF%E7%AD%96%E6%89%A7%E8%A1%8C", 500),
    "债券": ("http://mrdx.xinhuanet.com/search.htm?channelid=11148&searchword=%E5%80%BA%E5%88%B8", 182),
    "LPR": ("http://mrdx.xinhuanet.com/search.htm?channelid=11148&searchword=LPR", 10),
    "银行": ("http://mrdx.xinhuanet.com/search.htm?channelid=11148&searchword=%E9%93%B6%E8%A1%8C", 500),
}


def scrape_xinhua_news_filter(keyword="利率", timeout_len=5, data_path="data", n_pages=None, num_threads=5):
    """
    Scrapes news articles from Xinhua based on a keyword.

    Args:
        keyword (str): The keyword to search for.
        timeout_len (int): Timeout duration for Selenium waits.
        data_path (str): Directory to save the scraped data.
        n_pages (int): Number of pages to scrape.
        num_threads (int): Number of threads for parallel article scraping.

    Returns:
        pd.DataFrame: DataFrame containing the scraped news data.
    """

    if keyword not in SEARCH_CONFIG:
        raise ValueError(f"Keyword '{keyword}' is not supported. Choose from: {list(SEARCH_CONFIG.keys())}")

    base_url, default_pages = SEARCH_CONFIG[keyword]
    n_pages = n_pages or default_pages

    # Setup headless Selenium driver
    driver = setup_chrome_driver()
    driver.get(base_url)

    print(f"Scraping Xinhua News for keyword: {keyword}")

    all_urls = []
    snippets = []

    for page in tqdm(range(n_pages), desc="Loading More Pages"):
        time.sleep(timeout_len / 2)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Extract URLs
        url_pattern = r"(http[s]?://[^\s]+?)(?=\d{4}-\d{2}-\d{2}|$)"
        urls = [match.group(1) for match in re.finditer(url_pattern, soup.text)]
        all_urls.extend(urls)

        # Extract snippets from <div class="tex">
        tex_divs = soup.find_all("div", class_="tex")
        snippets.extend(div.get_text(strip=True) for div in tex_divs)

        # Try to click the "Next Page" button
        try:
            next_button = WebDriverWait(driver, timeout_len / 2).until(
                EC.element_to_be_clickable((By.XPATH, '//a[@data-type="next"]'))
            )
            next_button.click()
        except Exception:
            print(f"Failed to load next page at {page + 1}. Stopping pagination.")
            break

    driver.quit()

    print(f"Found {len(all_urls)} articles. Fetching content in parallel...")

    meeting_data = {}

    def fetch_article(url, snippet):
        """Fetch article content in parallel."""
        try:
            response = requests.get(url, timeout=timeout_len)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            target_div = soup.find("div", class_="main")
            article_text = target_div.get_text(strip=True) if target_div else snippet

            date_obj = extract_date_from_url(url)

            return url, {"date": date_obj, "text": article_text, "url": url}
        except requests.exceptions.RequestException:
            return url, None

    def extract_date_from_url(url):
        """Extract the date from the article URL."""
        date_pattern = r'/(\d{8})/|/(\d{4}-\d{2}-\d{2})/'
        match = re.search(date_pattern, url)
        if match and match.group(1):
            date_str = match.group(1)
            meeting_date = datetime.strptime(date_str, '%Y%m%d')
        else:
            date_match = re.search(r"/(\d{4}-\d{2}/\d{2})/", url)
            if date_match:
                date_str = date_match.group(1).replace('/', '-')
                meeting_date = datetime.strptime(date_str, "%Y-%m-%d")
            else:
                return None
        return meeting_date

    # Parallel fetching using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_to_url = {executor.submit(fetch_article, url, snippet): url for url, snippet in zip(all_urls, snippets)}

        for future in tqdm(as_completed(future_to_url), total=len(future_to_url), desc="Downloading Articles"):
            url, result = future.result()
            if result:
                meeting_data[url] = result

    # Convert dictionary to DataFrame
    df = pd.DataFrame.from_dict(meeting_data, orient="index").reset_index(drop=True)
    df.set_index("date", inplace=True)

    # Ensure data directory exists
    os.makedirs(data_path, exist_ok=True)

    # Save DataFrame to CSV
    csv_file_path = os.path.join(data_path, f"news_xinhua_{keyword}.csv")
    df.to_csv(csv_file_path, encoding="utf-8-sig")

    print(f"Data saved to {csv_file_path}")
    return df


if __name__ == "__main__":
    keywords = ["利率", "政策执行", "债券", "LPR", "银行"]
    for keyword in keywords:
        df = scrape_xinhua_news_filter(keyword=keyword, n_pages=5)
        print(df.head())
