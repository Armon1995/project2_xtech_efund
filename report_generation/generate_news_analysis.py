"""
Created on Sat Mar 1 14:30:59 2024

Author: davideliu

E-mail: davide97ls@gmail.com

Goal: News Analysis based on historical data and statistics.
"""
from keys import openai_key
import json
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from datetime import datetime
from dateutil.relativedelta import relativedelta
from models import model_invoke
from tqdm import tqdm
import pandas as pd
from typing import Optional
import sys
import os
import warnings
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../data_retrieval")))
from data_retrieval.faiss_db_utils import filter_by_similarity


embedding_model = OpenAIEmbeddings(model="text-embedding-ada-002", api_key=openai_key)
try:
    faiss_db = FAISS.load_local("../data_retrieval/faiss_db", embedding_model, allow_dangerous_deserialization=True)
    print("FAISS database loaded")
except FileNotFoundError as e:
    warnings.warn(f"FAISS database not found: {e}", UserWarning)
    faiss_db = None  # Optionally set faiss_db to None if you want to handle it later
except Exception as e:
    faiss_db = None


def generate_news_prompt(doc, y_history, cur_date):
    """
    Generates a prompt for analyzing the impact of a news article on LPR (Loan Prime Rate).

    Args:
        doc: The news document containing metadata and content.
        y_history (list): Historical LPR values in chronological order.
        cur_date (datetime): The current date for prediction.

    Returns:
        str: The generated prompt for the AI model.
    """
    news_prompt = f"""
你是一位专门研究新闻对贷款市场报价利率（LPR）影响的经济分析专家。
预测日期为 {cur_date.strftime("%Y-%m-%d")}。
LPR历史数据为：{y_history}（按时间顺序从过去到现在列出，最右侧的值表示当前的LPR）。
在 {doc.metadata['date']} 日期，新闻内容为：{doc.page_content}。
分析该新闻对下个月LPR的影响。
影响你决策的因素包括：
- LPR的历史趋势及其分析。
- 新闻对下个月LPR值的影响。
同时请考虑以下关于LPR降息的提示：
- 降息连续发生的可能性较小，但并非不可能。
- 离上次LPR降息的时间越长，降息的概率越大。
- 降息预测的概率通常在40%到60%之间波动，上限为60%，下限为40%。
- 当有强烈且明确的降息信号时，概率为60%；当没有降息信号时，概率为40%。
输出一个有效的JSON格式：
{'{'}
    "prob_decrease": (float, 新闻发布后，LPR降息的概率，范围在40%到60%之间),
    "impact_on_LPR": (str, 新闻可能对下个月LPR产生的影响)
{'}'}
"""
    return news_prompt


def generate_summary_prompt(doc):
    """
    Generates a summary prompt for a news document.

    Args:
        doc: The news document containing metadata and content.

    Returns:
        str: The formatted summary prompt.
    """
    summary_prompt = f"""
请对以下新闻内容进行总结，用简洁明确的语言呈现，并确保涵盖所有关键信息，避免遗漏任何重要细节。
新闻内容: {doc.page_content}
仅输出您生成的新闻总结，以文本形式呈现。
"""
    return summary_prompt


def generate_news_report(news_df):
    """
    Generates a report analyzing the impact of recent news on LPR.

    Args:
        news_df (pd.DataFrame): A DataFrame containing summarized news articles with their impact on LPR.

    Returns:
        str: A formatted report analyzing the impact of news on LPR trends.
    """
    n_news = len(news_df)
    report_template1 = f"""
# 第四部分：新闻对LPR的影响分析

本部分分析了近期新闻对LPR未来走势的潜在影响。
共分析了{n_news}篇新闻文章，以评估其与LPR相关性及对下个月LPR走势的潜在影响。
"""
    report_template2 = ""
    i = 0
    for index, row in news_df.iterrows():
        news_template = f"""
## 新闻 {i+1}
新闻内容总结: {row['summary']}
新闻对LPR的影响: {row['impact_on_LPR']}
LPR降息概率: {row['prob_decrease']}%
来源: {row['source']}
发布日期: {row['date'].strftime("%Y-%m-%d")}
"""
        i += 1
        report_template2 += news_template
    return report_template1 + report_template2


def generate_news_report_with_conclusions(news_report, news_conclusions, decrease_prob):
    """
    Appends a conclusion section to the given news report.

    Args:
        news_report (str): The main body of the news report.
        news_conclusions (str): The conclusion derived from the analysis.
        decrease_prob (float or str): The probability of an LPR decrease.

    Returns:
        str: The final report with conclusions appended.
    """
    news_report = f"""
{news_report}
## 总结

根据对收集的新闻及其对下个月LPR总体影响的分析，得出以下结论：
最终结果: {news_conclusions}
降息概率: {decrease_prob}%
"""
    return news_report


def generate_final_news_pred_prompt(news_report, y_history, cur_date):
    """
    Generates a prediction prompt based on economic news for the potential impact on the Loan Prime Rate (LPR).

    Args:
        news_report (str): A string containing the summary of economic news articles to be analyzed. This will be evaluated for its potential impact on the LPR.
        y_history (list of float): A list of historical LPR values, ordered chronologically. The most recent value is the last item in the list.
        cur_date (datetime): The current date for which the LPR prediction is being made. It is used to format the prediction date in the prompt.

    Returns:
        str: A formatted string to be used as an input to an AI agent for generating a prediction on the likelihood of an LPR decrease based on the provided news and historical data.
    """
    news_prompt = f'''
角色：你是一位专门研究新闻对利率影响的经济分析专家。你的任务是分析一组新闻如何可能影响下个月的贷款市场报价利率（LPR）。

分析背景：
- 预测日期：{cur_date.strftime("%Y-%m-%d")}
- 历史LPR数据：{y_history}（按时间顺序从过去到现在列出，最右侧的值表示当前的LPR）。

提供的信息：
- 经济新闻摘要。
- 每条新闻对LPR潜在影响的评估。

你的目标：
1. 全面分析：
   - 分析所有提供的新闻对下个月LPR的综合影响。
   - 结合新闻条目之间的关键洞察和关系。
   - 基于历史LPR趋势及其背景进行分析。

2. 概率预测：
   - 根据以下因素预测下个月LPR降息的可能性：
     - 历史趋势和上次降息的时间。
     - 提供的新闻的影响。
   - 考虑以下因素：
     - 连续降息不太常见，但有可能。
     - 自上次降息以来，时间越长，降息的概率越大。
     - 降息预测的概率通常在50%左右波动，上限为60%，下限为40%。
     - 当有强烈且明确的降息信号时，概率为60%，没有降息信号时，概率为40%。
     - 尝试给出一个在50%左右波动的值，而不是正好50%。

输出格式：
返回一个有效的JSON对象，其结构如下：
{'{'}
    "prob_decrease": (float, 下个月LPR降息的概率，范围在40%到60%，不少于40%，不超过60%),
    "impact_on_LPR": (str, 对新闻可能对下个月LPR产生的影响的详细分析，报告所有新闻条目的洞察及其影响).
{'}'}

下面是所有新闻报告：
{news_report}
'''
    return news_prompt


def generate_news_report_analysis(
        df: pd.DataFrame,
        date: datetime,
        query: str,
        y: str,
        meeting_day: int = 20,
        history_len: int = 12,
        news_history_len: int = 3,
        top_kk: int = 500,
        top_k: int = 5,
        max_len_news: int = 10000,
        save_folder: Optional[str] = None,
        verbose: bool = False,
        model: str = "gpt-4o-mini",
        no_news_embedding: bool = False,
        prod_env: bool = False,
) -> str:
    """
    Generates a news report analysis by retrieving relevant financial news, summarizing them,
    and predicting their impact on LPR.

    Args:
        df (pd.DataFrame): Dataframe containing historical financial data.
        date (datetime): The reference date for analysis.
        query (str): Query string for retrieving relevant news.
        y (str): Target variable column name in the dataframe.
        meeting_day (int): The day of the month used for financial meeting alignment.
        history_len (int): Length of historical data to consider.
        news_history_len (int): Length of historical news period to consider (in months).
        top_kk (int): Number of top documents to retain after similarity filtering.
        top_k (int): Number of top documents to retain after date filtering.
        max_len_news (int): Maximum length of news content to process.
        save_folder (Optional[str]): Path to save the final news report.
        verbose (bool): Whether to print detailed logs.
        model (str): The model used for text generation.
        no_news_embedding (bool): If True, disables news embedding-based similarity search.
        prod_env (bool): if True use prod env to retrieve news.
    Returns:
        str: The final news report with conclusions.
    """

    system_prompt = (
        "You are a helpful assistant. When generating JSON, output string values in Chinese."
    )

    y_series = df[y]
    cur_date = date.replace(day=meeting_day)
    news_start_period = date - relativedelta(months=news_history_len)
    y_history = y_series.loc[:cur_date].iloc[-history_len:].values

    # Retrieve relevant news
    docs = filter_by_similarity(
        query=query,
        start_date=news_start_period,
        end_date=cur_date,
        top_kk=top_kk,
        top_k=top_k,
        use_tfidf=no_news_embedding,
        faiss_db=faiss_db,
        prod_env=prod_env,
    )

    json_responses = []
    for doc in tqdm(docs, desc="Processing News Articles"):
        if verbose:
            print(doc.metadata.get('url', 'Unknown URL'), 'Doc len:', len(doc.page_content))

        # Truncate long documents
        doc.page_content = doc.page_content[:max_len_news]

        # Generate news analysis prompt
        prompt = generate_news_prompt(doc, y_history, cur_date)
        response = model_invoke(system_prompt, prompt, model=model)
        response = response[response.find("{"):response.rfind("}") + 1]  # Extract JSON format

        try:
            json_response = json.loads(response)
        except json.JSONDecodeError:
            print("Failed to parse response JSON:", response)
            continue

        # Generate news summary
        summary_prompt = generate_summary_prompt(doc)
        summary_response = model_invoke(system_prompt, summary_prompt, model=model)

        json_response["summary"] = summary_response
        json_response["source"] = doc.metadata.get("url", "Unknown")
        json_response["date"] = doc.metadata.get("date", "Unknown")
        json_responses.append(json_response)

    news_df = pd.DataFrame(json_responses)
    news_report = generate_news_report(news_df)

    # Generate final prediction
    final_news_pred_prompt = generate_final_news_pred_prompt(news_report, y_history, cur_date)
    response = model_invoke(system_prompt, final_news_pred_prompt, model=model)
    response = response[response.find("{"):response.rfind("}") + 1]  # Extract JSON format

    try:
        final_response = json.loads(response)
    except json.JSONDecodeError:
        print("Failed to parse final prediction response:", response)
        return news_report

    final_news_report = generate_news_report_with_conclusions(
        news_report, final_response.get('impact_on_LPR'), final_response.get('prob_decrease')
    )

    # Save report if requested
    if save_folder:
        save_path = os.path.join(save_folder, date.strftime("%Y-%m-%d"), "新闻数据分析.md")
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        with open(save_path, "w", encoding="utf-8") as text_file:
            text_file.write(final_news_report)

        if verbose:
            print(f"新闻数据分析保存在: {save_path}")

    return final_news_report


def generate_news_analysis(
        date: str,
        csv_file_path: str,
        y: str,
        save_folder: str,
        model: str = "gpt-4o-mini",
        no_news_embedding: bool = False,
        prod_env: bool = False
) -> str:
    """
    Loads financial data, processes news reports, and generates a financial analysis report.

    Args:
        date (str): The analysis date in 'YYYY-MM-DD' format.
        csv_file_path (str): Path to the CSV file containing financial data.
        y (str): Target variable column name in the dataset.
        save_folder (str): Directory to save the generated news report.
        model (str): The model used for text generation.
        no_news_embedding (bool): If True, disables news embedding-based similarity search.
        prod_env (bool): if True use prod env to retrieve news.
    Returns:
        str: The final news report.
    """

    year, month, day = map(int, date.split('-'))
    cur_date = datetime(year, month, day)
    df = pd.read_csv(csv_file_path, index_col=0, parse_dates=True)

    return generate_news_report_analysis(
        df=df,
        date=cur_date,
        query="货币政策、利率、经济、贷款、央行",
        y=y,
        save_folder=save_folder,
        model=model,
        no_news_embedding=no_news_embedding,
        prod_env=prod_env
    )


if __name__ == '__main__':
    cur_date = datetime(2024, 12, 31)
    csv_file_path = '../data_retrieval/data/XY_aug_feat.csv'
    y = '中国:贷款市场报价利率(LPR):1年'
    df = pd.read_csv(csv_file_path, index_col=0, parse_dates=True)
    prod_env = False
    history_len = 12
    meeting_day = 20
    news_history_len = 3
    top_kk = 100
    top_k = 5
    max_len_news = 10000
    save_folder = 'test_results'
    query = "货币政策、利率、经济、贷款、央行"

    news_report = generate_news_report_analysis(
        df,
        cur_date,
        meeting_day=meeting_day,
        history_len=history_len,
        news_history_len=news_history_len,
        query="货币政策、利率、经济、贷款、央行",
        y='中国:贷款市场报价利率(LPR):1年',
        save_folder=save_folder,
        top_k=top_k,
        top_kk=top_kk,
        max_len_news=max_len_news,
        model='g4f',
        no_news_embedding=True,
        prod_env=prod_env
    )

    print(news_report)
