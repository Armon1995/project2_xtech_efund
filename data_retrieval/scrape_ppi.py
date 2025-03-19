"""
Created on Sat Mar 1 14:30:59 2024

Author: davideliu

E-mail: davide97ls@gmail.com

Goal: Scrape ppi data
"""
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from utils import setup_chrome_driver, close_advertisement_eastmoney
import time


def scrape_ppi_data(url: str, total_pages: int) -> pd.DataFrame:
    """
    Scrapes PPI data from the specified URL across multiple pages.

    Args:
        url (str): The URL of the website to scrape data from.
        total_pages (int): The total number of pages to scrape.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the scraped PPI data.
    """
    driver = setup_chrome_driver()
    driver.get(url)

    # Wait for page to load
    sleep_time = 3
    time.sleep(sleep_time)

    all_dates = []
    all_data = []

    for page in range(1, total_pages + 1):
        close_advertisement_eastmoney(driver)  # Close adv if present
        try:
            # Get rows of data for the current page
            rows = driver.find_elements(By.XPATH, '//*[@id="cjsj_table"]/table/tbody/tr')

            for row in rows:
                date = row.find_element(By.XPATH, './td[1]').text
                data = row.find_element(By.XPATH, './td[2]').text

                # Convert the date to the last day of the month
                try:
                    date_str = date.replace('月份', '')
                    date_obj = pd.to_datetime(date_str, format='%Y年%m')
                    last_day_of_month = pd.Timestamp(year=date_obj.year, month=date_obj.month, day=1) + pd.DateOffset(months=1, days=-1)
                    formatted_date = last_day_of_month.strftime('%Y-%m-%d')
                except Exception as e:
                    print(f"Error converting date: {date}, Error: {e}")
                    formatted_date = None

                # Append the data to the list
                all_dates.append(formatted_date)
                all_data.append(data)

                # print(f"Date: {formatted_date}, Data: {data}")

            if page < total_pages:
                # Go to the next page
                page_input = driver.find_element(By.XPATH, '//*[@id="gotopageindex"]')
                page_input.clear()
                page_input.send_keys(str(page + 1))
                page_input.send_keys(Keys.RETURN)

                # Click the submit button
                driver.find_element(By.XPATH, '//*[@id="cjsj_table_pager"]/div[2]/form/input[2]').click()

                # Wait for the page to load
                time.sleep(sleep_time)

        except Exception as e:
            print(f"Error during scraping: {e}")
            break  # Exit loop on error

    driver.quit()

    # Convert the data to a pandas DataFrame
    df = pd.DataFrame({
        '日期': all_dates,
        'ppi': all_data
    })

    return df


def save_data_to_csv(df: pd.DataFrame, file_path: str = 'data/ppi_data.csv') -> None:
    """
    Saves the scraped PPI data to a CSV file.

    Args:
        df (pd.DataFrame): The DataFrame containing the scraped data.
        file_path (str): The file path where the data will be saved.
    """
    df.to_csv(file_path, index=False, encoding='utf-8')


def scrape_ppi():
    url = 'https://data.eastmoney.com/cjsj/ppi.html'
    total_pages = 12  # Adjust the total pages based on the website structure
    # Scrape the data
    scraped_data = scrape_ppi_data(url, total_pages)
    # Save the data to CSV
    save_data_to_csv(scraped_data)
    return scraped_data


if __name__ == "__main__":
    ppi_df = scrape_ppi()
    print(ppi_df)


