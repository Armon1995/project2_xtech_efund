"""
Created on Sat Mar 1 14:30:59 2024

Author: davideliu

E-mail: davide97ls@gmail.com

Goal: Analyze news DB
"""
import pandas as pd
from retrieve_s3_news import download_news_from_s3


def process_news_data(file_path, start_date, end_date):
    """
    Load news data from a CSV file, filter it by date, and print the news content.

    :param file_path: The path to the CSV file containing news data.
    :param start_date: The start date for filtering news data (inclusive).
    :param end_date: The end date for filtering news data (inclusive).
    """
    # Load the CSV file into a DataFrame
    df = pd.read_csv(file_path)

    # Ensure the 'news_publish_time' column is in datetime format
    df['news_publish_time'] = pd.to_datetime(df['news_publish_time'])

    # Set the 'news_publish_time' column as the index
    df.set_index('news_publish_time', inplace=True)
    df = df.sort_index()

    # Keep only the year, month, and day
    df.index = df.index.strftime('%Y-%m-%d')

    # Filter rows within the date range
    filtered_df = df[(df.index >= start_date) & (df.index <= end_date)]

    # Display the updated DataFrame
    print("Filtered DataFrame:")
    print(filtered_df.head())

    # Read some news
    i = 0
    for index, row in filtered_df.iterrows():
        print(f"Index: {index}, {row['s3_url']}, {row['news_title']}")
        news_code = row['s3_url'].split('/')[-1]
        content = download_news_from_s3(news_code)
        print(content)
        print("\n")  # Add a newline for better readability
        i += 1
        if i == 5:
            break


if __name__ == '__main__':
    # Define the file path and date range
    file_path = '通联宏观类舆情的表.csv'  # Replace with your CSV file path
    start_date = '2024-12-01'
    end_date = '2024-12-31'

    # Process the news data
    process_news_data(file_path, start_date, end_date)
