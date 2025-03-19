"""
Created on Sat Mar 1 14:30:59 2024

Author: davideliu

E-mail: davide97ls@gmail.com

Goal: Update FAISS database from news articles
"""
import os
from keys import openai_key
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import FakeEmbeddings
import pandas as pd
from faiss_db_generate import news_files, yifangda_news_files
from __init__ import fake_embedding_size


def update_faiss_db(data_path='data', no_embeddings=False, save_path="faiss_db", add_yifangda_news=False):
    """
    Updates an existing FAISS database with new documents from CSV files.

    Parameters:
    data_path (str): Path to the directory containing news CSV files.
    no_embeddings (bool): If True, uses fake embeddings instead of OpenAI embeddings.
    save_path (str): Path to the FAISS database to update.
    add_yifangda_news (bool): Add Yifangda news to DB

    Returns:
    list: A list of newly added Document objects.
    """
    if not no_embeddings:
        embedding_model = OpenAIEmbeddings(model="text-embedding-ada-002", openai_key=openai_key)
    else:
        embedding_model = FakeEmbeddings(size=fake_embedding_size)
    faiss_db = FAISS.load_local(save_path, embedding_model, allow_dangerous_deserialization=True)
    print("FAISS database loaded and ready to be updated")
    # Extract existing metadata (e.g., URLs) from the FAISS database
    existing_metadata = set(
        doc.metadata["url"] for doc in faiss_db.docstore._dict.values()
    )
    all_documents = []
    for file in news_files:
        file_path = os.path.join(data_path, file)
        if not os.path.exists(file_path):
            print(f"Skipping missing file: {file_path}")
            continue
        print(f"Processing file: {file_path}")
        df = pd.read_csv(file_path, index_col=0)
        added_docs = 0
        for index, row in df.iterrows():
            text = row['text']
            date = pd.to_datetime(index, errors='coerce')
            if pd.isna(date):
                # print(f"Skipping row with invalid date: {index}")
                continue
            url = row['url']
            category = file.split('.csv')[0]

            # Skip the document if it already exists in the FAISS database
            if url in existing_metadata:
                # print(f"Skipping duplicate document with URL: {url}")
                continue

            doc = Document(
                page_content=text,
                metadata={"date": date, "url": url, "category": category}
            )
            all_documents.append(doc)
            added_docs += 1
        print(f'Added new {added_docs} doc')

    if add_yifangda_news:
        for file_path in yifangda_news_files:
            if not os.path.exists(file_path):
                print(f"Skipping missing file: {file_path}")
                continue
            print(f"Processing file: {file_path}")
            df = pd.read_csv(file_path)
            df['news_publish_time'] = pd.to_datetime(df['news_publish_time'])
            df.set_index('news_publish_time', inplace=True)
            added_docs = 0
            category = ''
            for index, row in df.iterrows():
                text = row['news_title']
                date = pd.to_datetime(index, errors='coerce')
                if pd.isna(pd.to_datetime(date, errors='coerce')):
                    # print(f"Skipping row with invalid date: {index}")
                    continue
                url = row['news_url']
                s3_url = row['s3_url']
                category = file_path.split('.csv')[0]
                # Skip the document if it already exists in the FAISS database
                if url in existing_metadata:
                    # print(f"Skipping duplicate document with URL: {url}")
                    continue
                doc = Document(
                    page_content=text,
                    metadata={"date": date, "url": url, "category": category, "s3_url": s3_url}
                )
                all_documents.append(doc)
                added_docs += 1
            if added_docs > 0:
                print(f'Added new {added_docs} doc from {category}')

    # Add new documents to the existing FAISS database
    if all_documents:
        print('Adding new documents to FAISS database...')
        faiss_db.add_documents(all_documents)
        print(f'Added in total {len(all_documents)} new docs')
        print("FAISS database updated")
        faiss_db.save_local(save_path)
        print(f"Updated FAISS database saved to {save_path}")
    else:
        print("No new documents to add to the FAISS database.")

    return all_documents


if __name__ == '__main__':
    all_documents = update_faiss_db(no_embeddings=True, save_path="faiss_db_test", add_yifangda_news=True)
