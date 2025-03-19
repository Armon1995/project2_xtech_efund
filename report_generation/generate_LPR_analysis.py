"""
Created on Sat Mar 1 14:30:59 2024

Author: davideliu

E-mail: davide97ls@gmail.com

Goal: LPR analysis report generation based on historical data and statistics.
"""
import os
import pandas as pd
from datetime import datetime
from models import model_invoke


def analyze_series(series):
    """
    Analyzes a Pandas Series with a datetime index to compute basic statistics and identify changes.

    Args:
        series (pd.Series): The input series with a datetime index.

    Returns:
        dict: A dictionary containing the analysis results, including mean, mode, standard deviation,
              number of increases and decreases, dates of changes, and time since the last change.

    Raises:
        ValueError: If the input is not a Pandas Series or if the index is not a datetime index.
    """
    if not isinstance(series, pd.Series):
        raise ValueError("Input must be a Pandas Series.")
    if not isinstance(series.index, pd.DatetimeIndex):
        raise ValueError("The index of the series must be a datetime index.")

    # Compute basic statistics
    mean = series.mean()
    mode = series.mode().tolist()[0]  # Mode can have multiple values
    std_dev = series.std()

    # Identify increases and decreases
    changes = series.diff().dropna()  # Compute differences
    increases = changes[changes > 0]
    decreases = changes[changes < 0]

    # Determine the time since the last change
    last_change = changes[changes != 0].last_valid_index()
    months_since_last_change = None if last_change is None else (series.index[-1] - last_change).days // 30

    results = {
        "mean": mean,
        "mode": mode,
        "standard_deviation": std_dev,
        "num_increases": len(increases),
        "increase_dates": increases.index.strftime("%Y-%m").tolist(),
        "num_decreases": len(decreases),
        "decrease_dates": decreases.index.strftime("%Y-%m").tolist(),
        "months_since_last_change": months_since_last_change,
        "last_change_date": last_change.strftime("%Y-%m") if last_change else None,
    }
    return results


def generate_lpr_prompt(y_history, cur_date, y_stats):
    """
    Generates a prompt for LPR analysis based on historical data and statistics.

    Args:
        y_history (list): A list of historical LPR values.
        cur_date (datetime): The current date.
        y_stats (dict): A dictionary containing statistics about the LPR data.

    Returns:
        str: A formatted prompt for LPR analysis.
    """
    stats = y_stats
    prompt = f"""
你提供了一份包含2019年至今的中国贷款市场报价利率（LPR）时间序列数据，数据按月记录。
数据如下：{y_history}，其中最左侧的值代表2019年8月的LPR，而最右侧的值则对应于最新的一个月。
当前日期是 {cur_date.strftime("%Y-%m-%d")}，与最新LPR数据点的日期一致。
请对这份时间序列数据进行全面分析，内容包括以下几个部分：
1. 引言：提供关于中国贷款市场报价利率（LPR）及其重要性的概述。
2. 统计摘要：
- 显示关键统计数据，如均值：{stats['mean']:.2f}，众数：{stats['mode']:.2f}（浮动型），标准差：{stats['standard_deviation']:.2f}。
- 显示在该数据周期内发生了多少次利率上调和下调，以及发生的时间点。
    利率上调次数：{stats['num_increases']}，发生时间：{stats['increase_dates']}，若无上调，则不显示日期。
    利率下调次数：{stats['num_decreases']}，发生时间：{stats['decrease_dates']}，若无下调，则不显示日期。
    使内容更加文字化，而不仅仅是列出清单。
- 显示自上次LPR变动以来已过去了多少个月：{stats['months_since_last_change']}，发生日期：{stats['last_change_date']}。
3. 趋势分析：
- 检查LPR的总体趋势，突出显示任何稳定期、上调、下调或显著波动期。
- 识别数据中的任何重复模式或显著异常。
4. 经济洞察：
- 讨论趋势和模式的含义，提供关于可能影响LPR变动的经济或政策因素的见解。

确保报告的各个部分有清晰的子标题（如1.1，1.2等），并使用Markdown格式进行适当的标题标注。
在报告中提供可操作的见解。
在第2和第3部分添加日期以提供更清晰的上下文。
避免在最后包含总结或结论。
整个部分的标题为 "# 第一部分：LPR历史数据分析"。
"""
    return prompt


def generate_lpr_report_analysis(df, date, y, meeting_day=20, history_len=12, save_folder=None, verbose=False,
                                 model="gpt-4o-mini"):
    """
    Generates an LPR report analysis based on historical data.

    Args:
        df (pd.DataFrame): The input DataFrame containing the historical data.
        date (datetime): The current date.
        y (str): The column name for the LPR data in the DataFrame.
        meeting_day (int, optional): The day of the month for the meeting. Defaults to 20.
        history_len (int, optional): The length of the history to consider. Defaults to 12.
        save_folder (str, optional): The folder to save the report. Defaults to None.
        verbose (bool, optional): Whether to print verbose messages. Defaults to False.
        model (str, optional): The model to use for analysis. Defaults to "gpt-4o-mini".

    Returns:
        str: The generated report.
    """
    system_prompt = '''
角色: 你是一个宏观政策分析师，擅长从LPR的历史数据中提取有用的信息并解读
'''
    cur_date = date.replace(day=meeting_day)
    y_series = df[y]
    y_history = y_series.loc[:cur_date].iloc[-history_len:].values
    y_stats = analyze_series(y_series.loc[:cur_date].iloc[-history_len:])
    prompt = generate_lpr_prompt(y_history, cur_date, y_stats)
    response = model_invoke(system_prompt, prompt, model=model)
    if save_folder is not None:
        os.makedirs(f'{save_folder}/{date.strftime("%Y-%m-%d")}/', exist_ok=True)
        file_name = f"LPR分析报告.md"
        text_path = os.path.join(f'{save_folder}/{date.strftime("%Y-%m-%d")}/', file_name)
        with open(text_path, "w", encoding="utf-8") as text_file:
            text_file.write(response)
        if verbose:
            print(f"LPR报告保存在： {text_path}")

    return response


def generate_lpr_analysis(date, csv_file_path, y, save_folder, model="gpt-4o-mini"):
    """
    Generates an LPR analysis for a given date based on historical data from a CSV file.

    Args:
        date (str): The date in the format "YYYY-MM-DD".
        csv_file_path (str): The path to the CSV file containing the historical data.
        y (str): The column name for the LPR data in the CSV file.
        save_folder (str): The folder to save the report.
        model (str, optional): The model to use for analysis. Defaults to "gpt-4o-mini".

    Returns:
        str: The generated LPR report.
    """
    year, month, day = map(int, date.split('-'))
    cur_date = datetime(year, month, day)
    df = pd.read_csv(csv_file_path, index_col=0, parse_dates=True)
    start_date = datetime(2019, 8, 31)
    history_len = (cur_date.year * 12 + cur_date.month) - (start_date.year * 12 + start_date.month)
    # history_len = 12
    meeting_day = 20

    lpr_report = generate_lpr_report_analysis(
        df,
        cur_date,
        meeting_day=meeting_day,
        history_len=history_len,
        y=y,
        save_folder=save_folder,
        model=model,
    )
    return lpr_report


if __name__ == '__main__':
    cur_date = datetime(2023, 1, 31)
    start_date = datetime(2019, 8, 31)
    csv_file_path = '../data_retrieval/data/XY_aug_feat.csv'
    y = '中国:贷款市场报价利率(LPR):1年'
    df = pd.read_csv(csv_file_path, index_col=0, parse_dates=True)
    history_len = (cur_date.year - start_date.year) * 12 + (cur_date.month - start_date.month)
    meeting_day = 20
    save_folder = 'test_results'

    lpr_report = generate_lpr_report_analysis(
        df,
        cur_date,
        meeting_day=meeting_day,
        history_len=history_len,
        y='中国:贷款市场报价利率(LPR):1年',
        save_folder=save_folder,
        model='g4f'
    )

    print(lpr_report)

