"""
Created on Sat Mar 1 14:30:59 2024

Author: davideliu

E-mail: davide97ls@gmail.com

Goal: Create full dataset
"""
import os.path
from create_X_dataset import merge_csv_files
from scrape_fred import update_data_fred
from scrape_ifind import update_data_ifind
from utils import retry
from scrape_political_bureau_reports import scrape_political_bureau_meetings
from scrape_pboc_reports import scrape_pboc_meetings
from scrape_monetary_policy_reports import scrape_monetary_policy_meetings
from scrape_news_xinhua_general import scrape_xinhua_news_general
from scrape_news_xinhua_filter import scrape_xinhua_news_filter
from scrape_news_wind import scrape_wind_news
from scrape_news_eastmoney import scrape_eastmoney_news
from faiss_db_update import update_faiss_db
from scrape_M1_M2 import scrape_m1_m2
from scrape_ppi import scrape_ppi
from faiss_db_generate import create_faiss_db
from yifangda_news.retrieve_news_db import download_yifangda_news
from __init__ import *


def scrape_all_data(start_date='2016-01-01', end_date=None, use_yifangda_news=False):
    """
    Scrapes and updates all required data, including time-series (TS) data,
    policy reports, and news articles. It also updates the FAISS database.

    Parameters:
    start_date (str): The starting date for time-series data scraping.
    end_date (str, optional): The ending date for time-series data scraping. Defaults to None.
    use_yifangda_news (str, optional): Retrieve news from yifangda database.
    """
    # TS data
    retry(update_data_fred, max_attempts=5, wait_seconds=10, start_date=start_date, end_date=end_date)
    print('Data Fred retrieved')
    retry(update_data_ifind, max_attempts=5, wait_seconds=10, start_date=start_date, end_date=end_date)
    print('Data Ifind retrieved')
    retry(scrape_m1_m2, max_attempts=5, wait_seconds=10)
    print('M1, M2 data retrieved')
    retry(scrape_ppi, max_attempts=5, wait_seconds=10)
    print('PPI data retrieved')
    merge_csv_files('data/X_data_Fred.csv', 'data/X_data_iFind.csv', 'data/M1_M2_data.csv', 'data/ppi_data.csv',
                    'data/XY_aug_feat.csv')
    print('TS dataset created')

    # Policy Reports data
    retry(scrape_political_bureau_meetings, max_attempts=5, wait_seconds=10)
    print('Political Bureau Meetings data retrieved')
    retry(scrape_pboc_meetings, max_attempts=5, wait_seconds=10)
    print('PBOC Meeting data retrieved')
    retry(scrape_monetary_policy_meetings, max_attempts=5, wait_seconds=10)
    print('Monetary Policy data retrieved')

    # News data
    retry(scrape_wind_news, max_attempts=5, wait_seconds=10, n_pages=n_wind_pages)
    print('Wind News retrieved')
    retry(scrape_xinhua_news_general, max_attempts=5, wait_seconds=10, n_pages=n_xinhua_pages)
    print('Xinhua General News retrieved')
    retry(scrape_xinhua_news_filter, max_attempts=5, wait_seconds=10, n_pages=n_xinhua_pages, keyword='利率')
    retry(scrape_xinhua_news_filter, max_attempts=5, wait_seconds=10, n_pages=n_xinhua_pages, keyword='政策执行')
    retry(scrape_xinhua_news_filter, max_attempts=5, wait_seconds=10, n_pages=n_xinhua_pages, keyword='债券')
    retry(scrape_xinhua_news_filter, max_attempts=5, wait_seconds=10, n_pages=n_xinhua_pages, keyword='LPR')
    retry(scrape_xinhua_news_filter, max_attempts=5, wait_seconds=10, n_pages=n_xinhua_pages, keyword='银行')
    print('Xinhua News with Keyword Filter retrieved')
    retry(scrape_eastmoney_news, max_attempts=5, wait_seconds=10, n_pages=n_eastmoney_pages)
    print('Eastmoney News retrieved')

    # Yifangda news
    if use_yifangda_news:
        try:
            download_yifangda_news()
        except Exception as e:
            print(f'Failed to connect to Yifangda database. Error: {e}')
            print(f'Yifangda news NOT downloaded')

    # Create FAISS db if not exist
    if not os.path.exists('faiss_db/index.faiss'):
        print('FAISS db not found')
        create_faiss_db(no_embeddings=False, add_yifangda_news=True, save_path="faiss_db")
    else:
        # Update FAISS database
        update_faiss_db(no_embeddings=True, save_path="faiss_db", add_yifangda_news=True)
        print('FAISS database updated')


if __name__ == "__main__":
    use_yifangda_news = True
    scrape_all_data(use_yifangda_news=use_yifangda_news)

