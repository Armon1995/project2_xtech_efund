"""
Created on Sat Mar 1 14:30:59 2024

Author: davideliu

E-mail: davide97ls@gmail.com

Goal: Generate FAISS database from news articles
"""
import os
from keys import openai_key
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import FakeEmbeddings
import pandas as pd
from collections import defaultdict
from __init__ import fake_embedding_size

news_files = ['news_xinhua_政策执行.csv', 'news_xinhua_银行.csv', 'news_xinhua_LPR.csv', 'news_xinhua_债券.csv',
              'news_xinhua_利率.csv', 'news_xinhua_general.csv', 'news_wind.csv', 'news_eastmoney.csv']
yifangda_news_files = ['yifangda_news/通联宏观类舆情的表.csv']


def create_faiss_db(data_path='data', no_embeddings=False, save_path="faiss_db", add_yifangda_news=False):
    """
    Creates a FAISS database from news article CSV files.

    Parameters:
    data_path (str): Path to the directory containing news CSV files.
    no_embeddings (bool): If True, uses fake embeddings instead of OpenAI embeddings.
    save_path (str): Path to save the FAISS database.
    add_yifangda_news (bool): Add Yifangda news to DB

    Returns:
    list: A list of Document objects processed from the input files.
    """
    if not no_embeddings:
        embedding_model = OpenAIEmbeddings(model="text-embedding-ada-002", openai_key=openai_key)
    else:
        embedding_model = FakeEmbeddings(size=fake_embedding_size)
    all_documents = []
    for file in news_files:
        file_path = os.path.join(data_path, file)
        if not os.path.exists(file_path):
            print(f"Skipping missing file: {file_path}")
            continue
        print(f"Processing file: {file_path}")
        df = pd.read_csv(file_path, index_col=0)
        for index, row in df.iterrows():
            text = row['text']
            date = pd.to_datetime(index, errors='coerce')
            if pd.isna(pd.to_datetime(date, errors='coerce')):
                # print(f"Skipping row with invalid date: {index}")
                continue
            url = row['url']
            category = file.split('.csv')[0]
            doc = Document(
                page_content=text,
                metadata={"date": date, "url": url, "category": category}
            )
            all_documents.append(doc)
    if add_yifangda_news:
        for file_path in yifangda_news_files:
            if not os.path.exists(file_path):
                print(f"Skipping missing file: {file_path}")
                continue
            print(f"Processing file: {file_path}")
            df = pd.read_csv(file_path, index_col=0)
            df['news_publish_time'] = pd.to_datetime(df['news_publish_time'])
            df.set_index('news_publish_time', inplace=True)
            for index, row in df.iterrows():
                text = row['news_title']
                date = pd.to_datetime(index, errors='coerce')
                if pd.isna(pd.to_datetime(date, errors='coerce')):
                    # print(f"Skipping row with invalid date: {index}")
                    continue
                url = row['news_url']
                s3_url = row['s3_url']
                category = file_path.split('.csv')[0]
                doc = Document(
                    page_content=text,
                    metadata={"date": date, "url": url, "category": category, "s3_url": s3_url}
                )
                all_documents.append(doc)

    if all_documents:
        print('Generating FAISS database...')
        faiss_db = FAISS.from_documents(all_documents, embedding_model)
        print("FAISS database generated")
    else:
        print("No documents found. FAISS database not created.")
        return None

    faiss_db.save_local(save_path)
    print(f"FAISS database saved to {save_path}")
    return all_documents


if __name__ == "__main__":
    all_documents = create_faiss_db(no_embeddings=True, save_path="faiss_db_test")
    category_count = defaultdict(int)
    yearly_category_count = defaultdict(lambda: defaultdict(int))

    for doc in all_documents:
        category = doc.metadata["category"]
        date = doc.metadata["date"]
        category_count[category] += 1
        year = pd.to_datetime(date).year
        yearly_category_count[category][year] += 1

    for category, total_count in category_count.items():
        print(f"{category}: {total_count} docs")
        yearly_counts = yearly_category_count[category]
        for year, year_count in sorted(yearly_counts.items()):
            print(f"  {year}: {year_count}")
