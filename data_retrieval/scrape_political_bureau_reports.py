"""
Created on Sat Mar 1 14:30:59 2024

Author: davideliu

E-mail: davide97ls@gmail.com

Goal: Scrape political bureau meetings reports
"""
import pandas as pd
from selenium.webdriver.common.by import By
import time
from __init__ import *
from utils import setup_chrome_driver
import os


def scrape_political_bureau_meetings():
    """
    Scrapes political bureau meeting reports from the Chinese government website.
    Extracts meeting dates, titles, and content, then saves the data to a CSV file.

    Returns:
        pd.DataFrame: DataFrame containing the scraped data.
    """
    driver = setup_chrome_driver()
    url = "https://www.gov.cn/toutiao/zyzzjhy/home.htm"
    driver.get(url)
    driver.implicitly_wait(timeout_len)  # Reduce need for sleep
    all_contents = []

    for page in range(n_pages_bureau_reports):
        print('Retrieving elements...')
        titles = driver.find_elements(By.XPATH, "//a[@href and @target='_blank']")
        links = [title.get_attribute("href") for title in titles if 'content' in title.get_attribute("href") and 'home' not in title.get_attribute("href")]
        print(f"Found {len(links)} links on page {page + 1}")

        for link in links:
            driver.get(link)
            time.sleep(timeout_len)  # Allow page to load

            try:
                # Extract news content
                paragraphs = driver.find_elements(By.XPATH, "//p[@style='text-indent: 2em;']")
                news_title = driver.find_element(By.XPATH, "//*[@id='ti']").text
                date_time = driver.find_element(By.XPATH, "/html/body/div[3]/div[1]/div/div[1]").text.split('来源')[0]

                content = "\n".join([p.text for p in paragraphs])

                # If content is too short, try a different method
                if len(content) < 20:
                    parent_element = driver.find_element(By.ID, "UCAP-CONTENT")
                    content = "\n".join([p.text for p in parent_element.find_elements(By.TAG_NAME, "p")])

                all_contents.append({
                    "date": date_time.strip(),
                    "url": link,
                    "title": news_title.strip(),
                    "text": content.strip()
                })
                print(f"Fetched: {news_title} ({date_time.strip()})")

            except Exception as e:
                print(f"Error fetching {link}: {e}")

        # Handle pagination
        try:
            print('Discovering new pages...')
            driver.get(url)
            next_button = driver.find_element(By.XPATH, f'/html/body/div[3]/div/div/div[2]/div[2]/a[{page + 2}]')

            if "disabled" in next_button.get_attribute("class"):
                print("No more pages to fetch.")
                break
            else:
                next_button.click()
                time.sleep(timeout_len)

        except Exception as e:
            print(f"Error clicking next page: {e}")
            break

    # Save data to CSV
    if all_contents:
        df = pd.DataFrame(all_contents)
        os.makedirs(data_path, exist_ok=True)
        csv_file_path = os.path.join(data_path, "政治局会议.csv")
        df.to_csv(csv_file_path, index=False, encoding="utf-8-sig")
        print(f"Data saved to {csv_file_path}")
    else:
        df = None

    driver.quit()
    return df


if __name__ == "__main__":
    df = scrape_political_bureau_meetings()
    print(df.head())
