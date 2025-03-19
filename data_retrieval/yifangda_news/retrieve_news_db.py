"""
Created on Sat Mar 1 14:30:59 2024

Author: davideliu

E-mail: davide97ls@gmail.com

Goal: Retrieve all news from DB
"""
import pandas as pd
from sqlalchemy import create_engine
import os


def get_infodb_wind_data(sql):
    """
    Retrieve data from the INFODB database using the given SQL query.

    Args:
        sql (str): SQL query to execute.

    Returns:
        pd.DataFrame: Retrieved data as a Pandas DataFrame.
    """
    config = {'user': 'jrkjb', 'password': 'jrkjb#1112', 'host': '192.1.61.119', 'port': 1521, 'db': 'INFODB'}
    con = create_engine("oracle+cx_oracle://{user}:{password}@{host}:{port}/{db}".format(**config))
    data = pd.read_sql(sql, con)
    return data


def download_yifangda_news():
    """
    Retrieve data from the Yifangda database.

    Returns:
        pd.DataFrame: Retrieved data as a Pandas DataFrame.
    """
    sql_news1 = '''
    SELECT t1.*, t2.s3_url
    FROM HERMES.VNEWS_CONTENT_V1 t1
    JOIN HERMES.VNEWS_BODY_V1_S3 t2
    ON t1.NEWS_ID = t2.NEWS_ID
    WHERE t1.NEWS_PUBLISH_TIME >= DATE '2019-07-01'
    AND t1.NEWS_PUBLISH_SITE IN (
        SELECT NEWS_SITE_NAME FROM HERMES.NEWS_POLICY_CLASSIFICATION_V1
        WHERE NEWS_INDUSTRY_NAME = '宏观'
        GROUP BY NEWS_SITE_NAME )
    '''
    print(f'Downloading news from Yifangda database. The process may take a few minutes...')
    news = get_infodb_wind_data(sql_news1)

    # Define the directory and file path
    directory = 'yifangda_news'
    file_name = '通联宏观类舆情的表.csv'
    file_path = os.path.join(directory, file_name)

    # Create the directory if it does not exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Save the DataFrame to the specified path
    news.to_csv(file_path, index=False)
    print(f'Yifangda news csv saved to {file_path}')
    return news


if __name__ == "__main__":
    news = download_yifangda_news()
    print(news)
