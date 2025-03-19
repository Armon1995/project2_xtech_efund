import requests
from bs4 import BeautifulSoup
import os
"""
Created on Sat Mar 1 14:30:59 2024

Author: davideliu

E-mail: davide97ls@gmail.com

Goal: Scrape PBOC meetings reports
"""
import pandas as pd
import time
from __init__ import *


def scrape_pboc_meetings():
    """
    Scrapes monetary policy meeting reports from the People's Bank of China website.
    Extracts meeting dates and content, then saves the data to a CSV file.

    Returns:
        pd.DataFrame: DataFrame containing the scraped data.
    """
    base_url = 'http://www.pbc.gov.cn/zhengcehuobisi/125207/3870933/3870936/af7dde41/index{}.html'
    prefix = 'http://www.pbc.gov.cn'
    reports_url = []

    # Scrape multiple pages for report links
    for page in range(1, n_pages_pboc_reports + 1):
        url = base_url.format(page)
        print(f'Scraping reports page {page}: {url}')

        retries = 0
        while retries < max_retries:
            try:
                response = requests.get(url, timeout=timeout_len)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')

                # Extract valid report links
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if prefix in href:
                        href = href.replace(prefix, "")
                    if (
                            (href.startswith('/zhengcehuobisi/') and href.endswith('index.html') and len(href.split('/')) == 7) or
                            (href.startswith('/goutongjiaoliu/') and href.endswith('index.html') and len(href.split('/')) == 6)
                    ):
                        reports_url.append(prefix + href)
                        print(f"Found report URL: {prefix + href}")

                break  # Exit retry loop if successful

            except requests.exceptions.RequestException as e:
                retries += 1
                print(f"Error fetching page {page}, Attempt {retries}. Error: {e}")
                if retries == max_retries:
                    print(f"Max retries reached for page {page}. Skipping.")
                else:
                    time.sleep(2 ** retries)  # Exponential backoff

    # Scrape data from extracted report URLs
    meeting_data = {}

    for url in reports_url:
        retries = 0
        while retries < max_retries:
            try:
                print(f"Fetching report: {url}")
                response = requests.get(url, timeout=timeout_len)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')

                # Extract meeting date
                date_tag = soup.find('span', {'id': 'shijian'}) or soup.find('td', {'class': 'hui12', 'align': 'right'})
                meeting_date = date_tag.text.strip() if date_tag else 'No Date Available'
                print(f"Meeting Date: {meeting_date}")

                # Extract meeting text
                zoom_div = soup.find('div', {'id': 'zoom'})
                meeting_text = zoom_div.text.strip() if zoom_div else 'No Meeting Text Available'

                # Store the meeting data
                meeting_data[url] = {
                    'date': meeting_date,
                    'text': meeting_text,
                    'url': url
                }
                break  # Exit retry loop on success

            except requests.exceptions.RequestException as e:
                retries += 1
                print(f"Error fetching report {url}, Attempt {retries}. Error: {e}")
                if retries == max_retries:
                    print(f"Max retries reached for report {url}. Skipping.")
                else:
                    time.sleep(2 ** retries)  # Exponential backoff

    # Convert to DataFrame
    df = pd.DataFrame.from_dict(meeting_data, orient='index').reset_index(drop=True)
    df.set_index('date', inplace=True)

    # Ensure data directory exists
    os.makedirs(data_path, exist_ok=True)

    # Save to CSV
    csv_file_path = os.path.join(data_path, "中央银行会议报告.csv")
    df.to_csv(csv_file_path, encoding="utf-8-sig")

    print(f"Data has been saved to {csv_file_path}")
    return df


if __name__ == "__main__":
    df = scrape_pboc_meetings()
    print(df.head())
