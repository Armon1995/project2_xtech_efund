"""
Created on Sat Mar 1 14:30:59 2024

Author: davideliu

E-mail: davide97ls@gmail.com

Goal: Do search on FAISS database
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import FakeEmbeddings
from typing import Optional, List
from langchain.schema import Document
from yifangda_news.retrieve_s3_news import download_news_from_s3


def filter_by_date(docs, start_date, end_date):
    """
    Filters documents by date range.

    Args:
        docs (list): List of document objects with 'metadata' attribute containing 'date' key.
        start_date (datetime): Start of the date range (inclusive).
        end_date (datetime): End of the date range (exclusive).

    Returns:
        list: List of documents with dates within the specified range.
    """
    filtered_by_date = []
    for doc in docs:
        doc_date = doc.metadata.get("date", "")
        try:
            doc_date = pd.to_datetime(doc_date)  # Convert to datetime
            if start_date <= doc_date < end_date:
                filtered_by_date.append(doc)
        except Exception as e:
            print(f"Skipping doc with invalid date: {doc_date} (Error: {e})")
    return filtered_by_date


def filter_by_similarity(query=None, start_date=None, end_date=None, top_kk=50, top_k=10, use_tfidf=True,
                         faiss_db=None, prod_env=False):
    """
    Filter documents first by similarity (using FAISS or TF-IDF) and then by date.

    Parameters:
    - query (str): Query for similarity search. If None, only date filtering is performed.
    - start_date (datetime): Start date for date filtering. If None, only similarity filtering is performed.
    - end_date (datetime): End date for date filtering. If None, only similarity filtering is performed.
    - top_kk (int): Number of top documents to retain after similarity filtering.
    - top_k (int): Number of top documents to retain after date filtering.
    - use_tfidf (bool): Whether to use TF-IDF instead of FAISS for similarity search.
    - prod_env (bool): if True use prod env to retrieve news.

    Returns:
    - List[Document]: Filtered documents.
    """
    assert faiss_db
    print('Loading news from FAISS db...')
    all_docs = list(faiss_db.docstore._dict.values())  # Retrieve all stored documents

    # Pre-Filter by date (if date range is provided)
    if start_date and end_date:
        all_docs = filter_by_date(all_docs, start_date, end_date)

    # Step 1: Filter by similarity
    if query:
        if use_tfidf:
            # Extract text content from documents
            doc_texts = [doc.page_content for doc in all_docs]

            # Compute TF-IDF similarity
            vectorizer = TfidfVectorizer()
            doc_vectors = vectorizer.fit_transform(doc_texts)
            query_vector = vectorizer.transform([query])

            # Compute cosine similarity
            similarities = cosine_similarity(query_vector, doc_vectors).flatten()
            top_indices = similarities.argsort()[-top_kk:][::-1]  # Get top_kk most relevant

            similarity_results = [all_docs[i] for i in top_indices]
        else:
            # FAISS similarity search
            similarity_results = faiss_db.similarity_search(query, k=top_kk)
    else:
        # If no query is provided, return all documents
        similarity_results = all_docs

    # Step 2: Re-Filter by date (if date range is provided)
    if start_date and end_date:
        similarity_results = filter_by_date(similarity_results, start_date, end_date)

    results = similarity_results[:top_k]

    for doc in results:
        if doc.metadata.get('s3_url', None):
            news_code = doc.metadata['s3_url'].split('/')[-1]
            content = download_news_from_s3(news_code, prod_env=prod_env)
            if content is None or content != "No news content found":
                doc.page_content = doc.metadata.get("title", "")

    return results


if __name__ == "__main__":
    save_path = "faiss_db_test"
    embedding_model = FakeEmbeddings(size=10)
    faiss_db = FAISS.load_local(save_path, embedding_model, allow_dangerous_deserialization=True)
    start_date = pd.to_datetime("2024-01-01")
    end_date = pd.to_datetime("2024-12-31")
    filtered_docs = filter_by_similarity(query="LPR", start_date=start_date, end_date=end_date, top_k=3, use_tfidf=True,
                                         faiss_db=faiss_db)
    for doc in filtered_docs:
        print(f"Date: {doc.metadata['date']}, URL: {doc.metadata['url']}")
        print(doc.page_content[:100])
