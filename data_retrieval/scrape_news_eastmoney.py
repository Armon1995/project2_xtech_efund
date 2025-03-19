"""
Created on Sat Mar 1 14:30:59 2024

Author: davideliu

E-mail: davide97ls@gmail.com

Goal: Scrape Eastmoney news articles
"""
import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from utils import setup_chrome_driver
import time


def scrape_eastmoney_news(n_pages=10, data_path='data', max_retries=3, timeout_len=2, num_threads=5):
    """
    Scrapes news articles related to interest rates from Eastmoney with improved performance.

    Args:
        n_pages (int): Number of pages to scrape.
        data_path (str): Path to save the scraped data.
        max_retries (int): Maximum retries for loading pages and fetching articles.
        timeout_len (int): Timeout length for waiting for elements.
        num_threads (int): Number of threads for parallel article scraping.

    Returns:
        pd.DataFrame: DataFrame containing the scraped data.
    """

    base_url = 'https://so.eastmoney.com/news/s?keyword=%E5%88%A9%E7%8E%87&sort=score&type=title'

    # Set up Selenium in headless mode
    driver = setup_chrome_driver()
    driver.get(base_url)

    all_urls = []
    snippets = []

    print('Fetching news...')
    for page in tqdm(range(n_pages), desc="Scraping Pages"):
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        news_items = soup.find_all('div', class_='news_item')

        for div in news_items:
            link_tag = div.find('a')
            if link_tag and 'href' in link_tag.attrs:
                url = link_tag['href']
                if url not in all_urls:
                    all_urls.append(url)
                    text = div.find('div', class_='news_item_c').get_text(strip=True)
                    snippets.append(text)

        # Try clicking the "Next Page" button
        retries = 0
        while retries < max_retries:
            try:
                next_button = WebDriverWait(driver, timeout_len).until(
                    EC.element_to_be_clickable((By.XPATH, '//a[@title="下一页"]'))
                )
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(timeout_len / 2)
                break  # Exit retry loop if successful
            except Exception as e:
                retries += 1
                print(f"Retry {retries}/{max_retries} - Could not click '下一页': {e}")
                if retries == max_retries:
                    print("Max retries reached. Stopping pagination.")

    driver.quit()
    print(f'Fetched {len(all_urls)} news articles. Starting parallel scraping...')
    meeting_data = {}

    def fetch_article(url, snippet):
        """ Fetch individual articles in parallel """
        for _ in range(max_retries):
            try:
                response = requests.get(url, timeout=timeout_len)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')

                target_div = soup.find('div', class_='mainleft')
                meeting_text = target_div.get_text(strip=True) if target_div else snippet

                date_str = url.split("/")[-1][:8]
                meeting_date = datetime.strptime(date_str, "%Y%m%d")

                return url, {'date': meeting_date, 'text': meeting_text, 'url': url}
            except requests.exceptions.RequestException:
                pass
        return url, None  # Return None if all retries fail

    # Use ThreadPoolExecutor for parallel fetching
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_to_url = {executor.submit(fetch_article, url, snippets[j]): url for j, url in enumerate(all_urls)}

        for future in tqdm(as_completed(future_to_url), total=len(future_to_url), desc="Downloading Articles"):
            url, result = future.result()
            if result:
                meeting_data[url] = result

    df = pd.DataFrame.from_dict(meeting_data, orient='index').reset_index(drop=True)
    df.set_index('date', inplace=True)

    os.makedirs(data_path, exist_ok=True)
    csv_file_path = os.path.join(data_path, "news_eastmoney.csv")
    df.to_csv(csv_file_path, encoding="utf-8-sig")

    print(f"Data has been saved to {csv_file_path}")
    return df


if __name__ == "__main__":
    df = scrape_eastmoney_news(n_pages=10)
    if not df.empty:
        print(df.head())
