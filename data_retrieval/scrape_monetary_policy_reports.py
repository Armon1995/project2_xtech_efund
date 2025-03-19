"""
Created on Sat Mar 1 14:30:59 2024

Author: davideliu

E-mail: davide97ls@gmail.com

Goal: Scrape monetary policy meetings reports
"""
import requests
from bs4 import BeautifulSoup
import os
import pandas as pd
import fitz  # PyMuPDF for PDF processing
import re
import io
import time
from datetime import datetime
from __init__ import *


def scrape_monetary_policy_meetings():
    """
    Scrapes monetary policy meeting reports from the People's Bank of China website.
    Extracts meeting dates and content, handling both HTML and PDF formats, then saves the data to a CSV file.

    Returns:
        pd.DataFrame: DataFrame containing the scraped data.
    """
    base_url = 'http://www.pbc.gov.cn/zhengcehuobisi/125207/125227/125957/index.html'
    prefix = 'http://www.pbc.gov.cn'
    reports_url = []

    response = requests.get(base_url, timeout=timeout_len)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract report URLs
    for link in soup.find_all('a', href=True):
        href = link['href']
        if prefix in href:
            href = href.replace(prefix, "")
        if href.startswith('/zhengcehuobisi/') and href.endswith('index.html') and len(href.split('/')) == 8:
            reports_url.append(prefix + href)

    meeting_data = {}
    finish = False
    for index, url in enumerate(reports_url):
        if index == 0:  # Skip the first item (explanation page)
            continue
        if finish:
            break

        retries = 0
        while retries < max_retries:
            try:
                print(f"Fetching URL: {url}, Attempt {retries + 1}")
                response = requests.get(url, timeout=timeout_len)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')

                # Extract the meeting date
                date_tag = soup.find('span', {'id': 'shijian'}) or soup.find('td', {'class': 'hui12', 'align': 'right'})
                meeting_date = date_tag.text.strip() if date_tag else 'No Date Available'
                print(f"Meeting date: {meeting_date}")

                parsed_date = datetime.strptime(meeting_date, "%Y-%m-%d %H:%M:%S")
                if parsed_date.year < 2018:
                    print(f"Stopping scraping: Found report from {parsed_date.year}")
                    finish = True
                    break  # Exit from the loop

                # Extract the meeting text
                zoom_div = soup.find('div', {'id': 'zoom'})
                meeting_text = zoom_div.text.strip() if zoom_div else 'No Meeting Text Available'

                # Check if additional content needs to be extracted from a PDF
                extracted_text = []
                pdf_tag = soup.find('a', href=lambda href: href and href.endswith('.pdf'))
                pdf_link = pdf_tag['href'] if pdf_tag else None

                if pdf_link:
                    pdf_url = pdf_link if pdf_link.startswith(prefix) else prefix + pdf_link
                    print(f"Found report PDF: {pdf_url}")

                    pdf_retries = 0
                    while pdf_retries < max_retries:
                        try:
                            pdf_response = requests.get(pdf_url, timeout=timeout_len)
                            pdf_response.raise_for_status()

                            with io.BytesIO(pdf_response.content) as pdf_data:
                                pdf_doc = fitz.open(stream=pdf_data, filetype="pdf")
                                start_extraction = False

                                for page_num in range(pdf_doc.page_count):
                                    page = pdf_doc.load_page(page_num)
                                    text = page.get_text("text")

                                    if '内容摘要' in text:
                                        start_extraction = True
                                    if re.search(r'目\s*\n*\s*录', text):
                                        start_extraction = False
                                        break
                                    if start_extraction:
                                        extracted_text.append(text)

                            break  # PDF downloaded and processed successfully

                        except requests.exceptions.RequestException as e:
                            pdf_retries += 1
                            print(f"Error fetching PDF: {pdf_url}, Attempt {pdf_retries}. Error: {e}")
                            if pdf_retries == max_retries:
                                print(f"Max retries reached for PDF: {pdf_url}. Skipping.")
                            else:
                                time.sleep(timeout_len)  # Exponential backoff

                # Use extracted text if PDF extraction was successful
                if extracted_text:
                    meeting_text = "\n".join(extracted_text)
                elif '内容摘要' in meeting_text:
                    meeting_text = meeting_text.replace('内容摘要', '')
                else:
                    print('Skipped due to bad format')
                    break

                # Store the meeting data
                meeting_data[url] = {
                    'date': meeting_date,
                    'text': meeting_text.strip(),
                    'url': url
                }
                break  # Exit retry loop on success

            except requests.exceptions.RequestException as e:
                retries += 1
                print(f"Error fetching URL: {url}, Attempt {retries}. Error: {e}")
                if retries == max_retries:
                    print(f"Max retries reached for URL: {url}. Skipping.")
                else:
                    time.sleep(2 ** retries)  # Exponential backoff

    # Convert to DataFrame
    df = pd.DataFrame.from_dict(meeting_data, orient='index').reset_index(drop=True)
    df.set_index('date', inplace=True)

    # Ensure data directory exists
    os.makedirs(data_path, exist_ok=True)

    # Save to CSV
    csv_file_path = os.path.join(data_path, "政策货币报告.csv")
    df.to_csv(csv_file_path, encoding="utf-8-sig")

    print(f"Data has been saved to {csv_file_path}")
    return df


if __name__ == '__main__':
    df = scrape_monetary_policy_meetings()
    print(df.head())
