"""
Created on Sat Mar 1 14:30:59 2024

Author: davideliu

E-mail: davide97ls@gmail.com

Goal: Scrape Wind news articles
"""
import os
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils import setup_chrome_driver


def scrape_wind_news(n_pages=10, timeout_len=5, data_path='data', num_threads=5):
    """
    Scrapes news articles from Wind's Insights page.

    Args:
        n_pages (int): Number of times to load more news.
        timeout_len (int): Timeout duration for Selenium waits.
        data_path (str): Directory to save the scraped data.
        num_threads (int): Number of threads for parallel article scraping.

    Returns:
        pd.DataFrame: DataFrame containing the scraped news data.
    """

    base_url = "https://www.wind.com.cn/portal/zh/Insights/index.html"
    prefix_url = "https://www.wind.com.cn/portal/zh/Insights/"

    # Set up Selenium in headless mode for faster execution
    driver = setup_chrome_driver()
    driver.get(base_url)

    for page in tqdm(range(n_pages), desc="Loading More Pages"):
        try:
            load_more_button = WebDriverWait(driver, timeout_len / 2).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "insights-more"))
            )
            ActionChains(driver).move_to_element(load_more_button).perform()
            load_more_button.click()
            time.sleep(timeout_len / 2)  # Allow content to load
        except Exception:
            print(f"Failed to load more articles at page {page + 1}.")
            break

    # Extract article links and dates
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    news_items = soup.find_all("div", class_="focus-detail")
    all_articles = []

    for div in news_items:
        link_tag = div.find("a", class_="insights-subtitle")
        date_tag = div.find("div", class_="focus-date")

        if link_tag and date_tag:
            url = f"{prefix_url.rstrip('/')}/{link_tag['href'].lstrip('./')}"
            date_text = date_tag.text.strip()
            try:
                date_obj = datetime.strptime(date_text, "%Y.%m.%d").date()
            except ValueError:
                date_obj = None

            all_articles.append((url, date_obj))

    print(f"Found {len(all_articles)} articles. Fetching content in parallel...")

    meeting_data = {}

    def fetch_article(url, date_obj):
        """Fetch article content in parallel."""
        try:
            driver = setup_chrome_driver()
            driver.get(url)
            time.sleep(timeout_len/2)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            target_div = soup.find('div', class_='news-content-container')
            article_text = target_div.get_text(strip=True) if target_div else ""
            if len(article_text) > 5:
                print({"date": date_obj, "text": article_text, "url": url})
                return url, {"date": date_obj, "text": article_text, "url": url}
            driver.quit()
        except requests.exceptions.RequestException:
            pass
        return url, None

    # Parallel fetching using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_to_url = {executor.submit(fetch_article, url, date): url for url, date in all_articles}

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
    csv_file_path = os.path.join(data_path, "news_wind.csv")
    df.to_csv(csv_file_path, encoding="utf-8-sig")

    print(f"Data saved to {csv_file_path}")
    return df


if __name__ == "__main__":
    df = scrape_wind_news(n_pages=1)
    print(df.head())
