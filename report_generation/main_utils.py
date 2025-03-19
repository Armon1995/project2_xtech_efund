"""
Created on Sat Mar 1 14:30:59 2024

Author: davideliu

E-mail: davide97ls@gmail.com

Goal: Utils functions.
"""
import warnings
from prompt import get_x_prompt, PoliticalAnalysis, MonetaryAnalysis, MonetaryBoardMeetingsAnalysis
from models import model_invoke
import tiktoken
import pandas as pd
from datetime import timedelta
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar
import numpy as np
warnings.filterwarnings("ignore")


def get_data(target_col='中国:贷款市场报价利率(LPR):1年'):
    """
    Loads financial and policy-related datasets, processes them, and returns relevant columns.

    Args:
        target_col (str): The target column for analysis, defaulting to LPR 1-year rate.

    Returns:
        tuple: (df, df2, df3, data, target_col, features_col, year_col)
            - df: Monetary policy report data.
            - df2: Political bureau meeting data.
            - df3: Central bank meeting report data.
            - data: Processed dataset with financial indicators.
            - target_col: The selected target column.
            - features_col: List of feature column names.
            - year_col: List of yearly economic indicators.
    """
    # 读取数据
    df = pd.read_csv('../data_retrieval/data/政策货币报告.csv')
    df2 = pd.read_csv('../data_retrieval/data/政治局会议.csv')
    df3 = pd.read_csv('../data_retrieval/data/中央银行会议报告.csv')
    data = pd.read_csv('../data_retrieval/data/XY_aug_feat.csv').round(4)
    # 选取特征
    year_col = ['中国GDP', '中国通货膨胀率', '中国公共债务', '中国政府贷款', '美国综合领先指标', '中国综合领先指标', '中国商业信心', '泰勒利率']
    features_col = ['中国GDP', '中国通货膨胀率', '中国公共债务', '中国政府贷款',
                    '美国利率', '美国综合领先指标', '中国综合领先指标', '中国商业信心', '上证指数', '人民币对美元汇率',
                    '人民币对欧元汇率', 'DR007',
                    '中国：M1月度增长率', '中国：M2月度增长率',
                    '国债到期收益率:1年',
                    '国债到期收益率:3年', '国债到期收益率:10年', '中国银行:净息差', '国民总储蓄率',
                    '未来3个月准备增加"购房"支出的比例', '中债中国绿色债券指数(总值)净价指数', '制造业PMI', 'CPI',
                    '房地产开发投资:当月值', '规模以上工业增加值:定基指数', '居民人均可支配收入', '出口总值(人民币计价):当月值',
                    'ppi', '7天期逆回购利率', '7天期逆回购数量', '中国GDP平减指数',
                    '泰勒利率', '债券利差', '中期借贷便利(MLF):操作利率:1年',
                    'GDP:不变价:当季同比', '消费者信心指数']
    rename_dict = {
        '逆回购:7日:回购利率': '7天期逆回购利率',
        '逆回购:7日:回购金额': '7天期逆回购数量',
        'China_GDP': '中国GDP',
        'GDP:平减指数': '中国GDP平减指数',
        'China_Inflation': '中国通货膨胀率',
        'China_Public_Debt': '中国公共债务',
        'China_Gov_Lending': '中国政府贷款',
        'US_Interest_Rates': '美国利率',
        'US_Composite_Leading_Indicator': '美国综合领先指标',
        'China_Composite_Leading_Indicator': '中国综合领先指标',
        'China_Business_Confidence': '中国商业信心',
        'Shanghai_Composite': '上证指数',
        'CNYUSD': '人民币对美元汇率',
        'CNYEUR': '人民币对欧元汇率',
        'M1_MOM': '中国：M1月度增长率',
        'M2_MOM': '中国：M2月度增长率',
        'TR_Interest_Rate': '泰勒利率',
        'Bond_Spread': '债券利差',
        'Unnamed: 0': 'date',
        '消费者指数:信心指数': '消费者信心指数',
        'CPI:当月值': 'CPI'
    }
    data = data.rename(columns=rename_dict)
    data = data.dropna(subset=target_col)
    data = data.ffill()
    # 日期处理
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    df2['date'] = pd.to_datetime(df2['date'])
    df2 = df2.sort_values('date')
    df3['date'] = pd.to_datetime(df3['date'])
    df3 = df3.sort_values('date')
    data['datetime'] = pd.to_datetime(data['date'])
    data.set_index('datetime', inplace=True)
    return df, df2, df3, data, target_col, features_col, year_col


# 计算辅助特征
def calculate_auxiliary_features(data, features_col):
    """
    Computes additional statistical features for financial data.

    Args:
        data (pd.DataFrame): The dataset containing financial indicators.
        features_col (list): List of feature column names.

    Returns:
        tuple: (results, data)
            - results (dict): Summary statistics for the features.
            - data (pd.DataFrame): Updated dataset with additional computed features.
    """
    results = {}
    for col in features_col:
        if '同比' not in col and '环比' not in col:
            # 环比 (MoM)
            data[f'{col}_mom'] = data[col].pct_change()
            # 同比 (YoY)
            data[f'{col}_yoy'] = data[col].pct_change(12)
            # 当前值相较于过去6个月均值的偏差 (z-score)
            data[f'{col}_zscore'] = (
                    (data[col] - data[col].rolling(window=6, min_periods=6).mean()) /
                    data[col].rolling(window=6, min_periods=6).std()
            )
            # 统计环比、同比的均值
            results[col] = {
                'mom_mean': data[f'{col}_mom'].mean(),
                'yoy_mean': data[f'{col}_yoy'].mean(),
                'current_zscore': data[f'{col}_zscore'].iloc[-1]  # 取当前最新的偏差值
            }
    return results, data


def get_x_data_prompt(date, data, features_col, target_col, year_col):
    """
    Generates a data prompt for model input using past trends.

    Args:
        date (str): The reference date for retrieving historical data.
        data (pd.DataFrame): The dataset containing financial indicators.
        features_col (list): List of feature column names.
        target_col (str): The target column for analysis.
        year_col (list): List of yearly economic indicators.

    Returns:
        str: The generated prompt containing financial trends.
    """
    reference_date = date
    result = get_past_12_months_data(data, reference_date, features_col + [target_col])
    result.update(get_past_5_years_data(data, reference_date, year_col))
    assist_col = [col for col in data.columns if any(keyword in col for keyword in ['mom', 'yoy', 'zscore'])]
    assist_result = get_data_for_specific_month(data, reference_date, assist_col)
    assist_result = {feature: value if not np.isnan(value) else 0 for feature, value in assist_result.items()}
    x_prompt = get_x_prompt(reference_date, result, assist_result, target_col)
    return x_prompt


def get_monetary_board_meetings_prompt(df3, reference_date):
    """
    Retrieves and formats monetary board meeting reports.

    Args:
        df3 (pd.DataFrame): Central bank meeting data.
        reference_date (str): The reference date for extracting relevant reports.

    Returns:
        tuple: (monetary_board_meetings_news_info, role_prompt)
            - monetary_board_meetings_news_info (str): Formatted meeting report content.
            - role_prompt (str): Model prompt template for analysis.
    """
    df3['last_news'] = df3['text'].shift(1)
    df3['last_date'] = df3['date'].shift(1)
    monetary_board_meetings_current_data = df3[df3['date'] <= pd.to_datetime(reference_date)].tail(1)
    monetary_board_meetings_news1, monetary_board_meetings_news2 = \
        monetary_board_meetings_current_data['text'].values[0], \
        monetary_board_meetings_current_data['last_news'].values[0]
    date1, date2 = str(monetary_board_meetings_current_data['date'].values[0])[:10], str(
        monetary_board_meetings_current_data['last_date'].values[0])[:10]
    monetary_board_meetings_news_info = f'''
    第一篇新闻，发布日期为{date1}:
    {monetary_board_meetings_news1}

    第二篇新闻,发布日期为{date2}:
    {monetary_board_meetings_news2}

    '''
    role_prompt = MonetaryBoardMeetingsAnalysis.role_prompt
    return monetary_board_meetings_news_info, role_prompt


def get_political_bureau_prompt(df2, reference_date):
    """
    Retrieves and formats political bureau meeting reports.

    Args:
        df2 (pd.DataFrame): Political bureau meeting data.
        reference_date (str): The reference date for extracting relevant reports.

    Returns:
        tuple: (news_info, role_prompt)
            - news_info (str): Formatted political bureau meeting content.
            - role_prompt (str): Model prompt template for analysis.
    """
    df2['last_news'] = df2['text'].shift(1)
    df2['last_date'] = df2['date'].shift(1)
    political_bureau_current_data = df2[df2['date'] <= pd.to_datetime(reference_date)].tail(1)
    political_bureau_news1, political_bureau_news2 = political_bureau_current_data['text'].values[0],\
        political_bureau_current_data['last_news'].values[0]
    date1, date2 = str(political_bureau_current_data['date'].values[0])[:10], \
        str(political_bureau_current_data['last_date'].values[0])[:10]
    news_info = f'''
    第一篇新闻，发布日期为{date1}:
    {political_bureau_news1}
    
    第二篇新闻,发布日期为{date2}:
    {political_bureau_news2}
    '''
    role_prompt = PoliticalAnalysis.role_prompt
    return news_info, role_prompt


def get_monetary_policy_prompt(df, reference_date):
    """
    Retrieves and formats monetary policy reports.

    Args:
        df (pd.DataFrame): Monetary policy report data.
        reference_date (str): The reference date for extracting relevant reports.

    Returns:
        tuple: (monetary_policy_news_info, role_prompt)
            - monetary_policy_news_info (str): Formatted monetary policy report content.
            - role_prompt (str): Model prompt template for analysis.
    """
    df['last_news'] = df['text'].shift(1)
    df['last_date'] = df['date'].shift(1)
    monetary_policy_current_data = df[df['date'] <= pd.to_datetime(reference_date)].tail(1)
    monetary_policy_news1, monetary_policy_news2 = monetary_policy_current_data['text'].values[0], \
        monetary_policy_current_data['last_news'].values[0]
    date1, date2 = str(monetary_policy_current_data['date'].values[0])[:10], str(
        monetary_policy_current_data['last_date'].values[0])[:10]
    monetary_policy_news_info = f'''
    第一篇新闻，发布日期为{date1}:
    {monetary_policy_news1}

    第二篇新闻,发布日期为{date2}:
    {monetary_policy_news2}

    '''
    role_prompt = MonetaryAnalysis.role_prompt
    return monetary_policy_news_info, role_prompt


def last_day_of_current_month(date):
    """
    Computes the last day of the month for a given date.

    Args:
        date (str or datetime): Input date.

    Returns:
        datetime: The last day of the given month.
    """
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d')
    next_month = date.replace(day=28) + timedelta(days=4)  # this will never fail
    last_day = next_month - timedelta(days=next_month.day)
    return last_day


def analysis(role_prompt, prompt, date, chatbot, filename, load_result=False):
    """
    Performs analysis using a given role prompt and input prompt.

    Args:
        role_prompt (str): The role-specific prompt for the model.
        prompt (str): The input prompt for generating analysis.
        date (str): The date for saving the analysis results.
        chatbot (str): The chatbot model to use.
        filename (str): The filename to save results.
        load_result (bool, optional): Whether to load previous results instead of running new analysis.

    Returns:
        str: The generated analysis result.
    """
    if load_result:
        with open(f'test_results/{date}/{filename}.md', 'r', encoding='utf-8') as file:
            response = file.read()
    else:
        response = model_invoke(role_prompt, prompt, chatbot=chatbot)
    log_token_usage(role_prompt+prompt, response)
    file_name = f"test_results/{date}/{filename}.md"
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(response)
    # print(f"{filename} generated and saved to {file_name}")
    return response


def generate_report(generate_func, chatbot, prompt, date, filename, load_result=False):
    """
    Generates and saves a report using a specified function.

    Args:
        generate_func (function): The function used to generate the report.
        chatbot (str): The chatbot model to use.
        prompt (str): The input prompt for the report.
        date (str): The date for saving the report.
        filename (str): The filename to save results.
        load_result (bool, optional): Whether to load a previous report instead of generating a new one.

    Returns:
        str: The generated report content.
    """
    file_name = f"test_results/{date}/{filename}.md"
    if load_result:
        with open(file_name, 'r', encoding='utf-8') as file:
            response = file.read()
    else:
        response = generate_func(chatbot, prompt)
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(response)
    # print(f"{filename} generated and saved to {file_name}")
    return response


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """
    Computes the number of tokens in a given string using a specified encoding.

    Args:
        string (str): The input string to be tokenized.
        encoding_name (str): The encoding type to use for tokenization.

    Returns:
        int: The number of tokens in the string.
    """
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def log_token_usage(input_message, output_message, log_file='token_usage_log.txt'):
    """
    Logs token usage for input and output messages to a specified file.

    Args:
        input_message (str): The input message string.
        output_message (str): The output message string.
        log_file (str): The file to store the log. Default is 'token_usage_log.txt'.
    """
    input_tokens = num_tokens_from_string(input_message, 'cl100k_base')
    output_tokens = num_tokens_from_string(output_message, 'cl100k_base')
    # Append the updated token counts to the log file
    with open(log_file, 'a', encoding='utf-8') as file:
        file.write(f"Input tokens: {input_tokens}, Output tokens: {output_tokens}\n")


def get_past_12_months_data(df, reference_date, feature_list):
    """
    Retrieves data for the past 12 months from a given reference date.

    Args:
        df (pd.DataFrame): The input dataframe containing time series data.
        reference_date (str): The reference date (YYYY-MM-DD format).
        feature_list (list): The list of features to extract.

    Returns:
        dict: A dictionary where keys are feature names and values are lists of past 12-month values.
    """
    reference_date = pd.to_datetime(reference_date)
    filtered_df = df.loc[reference_date - pd.DateOffset(months=11):reference_date, feature_list]
    result = {feature: filtered_df[feature].tolist() for feature in feature_list}
    return result


def get_past_5_years_data(df, reference_date, feature_list):
    """
    Retrieves data from the first available date in each of the past five years.

    Args:
        df (pd.DataFrame): The input dataframe containing time series data.
        reference_date (str): The reference date (YYYY-MM-DD format).
        feature_list (list): The list of features to extract.

    Returns:
        dict: A dictionary where keys are feature names and values are lists of first values from past five years.
    """
    reference_date = pd.to_datetime(reference_date)
    df['date'] = pd.to_datetime(df['date'])
    df = df[df['date'] <= reference_date]
    df['year'] = df['date'].dt.year
    first_value_per_year = df.groupby('year').first().reset_index().tail(6).iloc[:-1, :]
    result = {}
    for feature in feature_list:
        feature_values = first_value_per_year[feature].tolist()
        result[feature] = feature_values
    return result


def get_data_for_specific_month(df, reference_date, feature_list):
    """
    Retrieves data for a specific month from the dataframe.

    Args:
        df (pd.DataFrame): The input dataframe containing time series data.
        reference_date (str): The reference date (YYYY-MM-DD format).
        feature_list (list): The list of features to extract.

    Returns:
        dict: A dictionary where keys are feature names and values are rounded values for the given month.
    """
    reference_date = pd.to_datetime(reference_date)
    filtered_df = df.loc[reference_date, feature_list]
    result = {feature: round(filtered_df[feature], 4) for feature in feature_list}
    return result


def last_day_of_previous_month(date):
    """
    Finds the last day of the previous month given a specific date.

    Args:
        date (str): The input date in YYYY-MM-DD format.

    Returns:
        datetime: The last day of the previous month.
    """
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d')
    first_day_of_current_month = date.replace(day=1)
    last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
    return last_day_of_previous_month


def calculate_average_decline(data, target_time, target_col):
    """
    Calculates the historical average decline and year-to-date decline for a financial series.

    Args:
        data (pd.DataFrame): The dataframe containing financial data.
        target_time (str): The target date for analysis (YYYY-MM-DD format).
        target_col (str): The column representing the financial metric.

    Returns:
        tuple: (historical_avg_decline, decline_from_year_start)
    """
    df = data.copy()[['date', target_col]]
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    year_start_lpr = df.groupby('year')['中国:贷款市场报价利率(LPR):1年'].transform('first')
    df['decline_from_year_start'] = year_start_lpr - df['中国:贷款市场报价利率(LPR):1年']
    yearly_stats = df.groupby('year')['decline_from_year_start'].last().reset_index()
    yearly_stats['historical_avg_decline'] = yearly_stats['decline_from_year_start'].expanding().mean().shift()
    df = df.merge(yearly_stats[['year', 'historical_avg_decline']], on='year', how='left')
    historical_avg_decline, decline_from_year_start \
        = df.loc[df['date'] == target_time, ['historical_avg_decline', 'decline_from_year_start']].values[0]
    return historical_avg_decline, decline_from_year_start


def find_last_unchanged_date(df, column_name, target_date):
    """
    Find the last date when the values in the specified column of the dataframe
    did not change, up until the given target date.

    Args:
        df (pd.DataFrame): The input DataFrame with a datetime index.
        column_name (str): The name of the column to analyze for changes.
        target_date (str or pd.Timestamp): The date before which to find the last unchanged date.

    Returns:
        list of str: A list of string dates (in 'YYYY-MM-DD' format) representing the monthly time range
                     from the last unchanged date until the target date.
    """
    if not isinstance(target_date, pd.Timestamp):
        target_date = pd.to_datetime(target_date)
    df_filtered = df[df.index < target_date]
    end_date = df_filtered.index[-1]
    changes = df_filtered[column_name] != df_filtered[column_name].shift(1)
    last_change_index = changes[changes].index[-1] if any(changes) else df_filtered.index[0]
    time_series = pd.date_range(start=last_change_index, end=end_date, freq='M')
    return time_series.strftime('%Y-%m-%d').tolist()


def extract_numeric(value):
    """
    Extracts the numeric part from a string.

    Args:
        value (str): The input string.

    Returns:
        str: The numeric value as a string, or None if not found.
    """
    match = re.match(r"([-+]?\d*\.?\d+)", value)
    return match.group(0) if match else None


def replace_in_text(text):
    """ Replace unwanted characters in the given text. """
    replacements = {
        "```": "",
        "json": "",
        "**": "",
        ': no': ':"no"',
        "\n": "",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def add_months(dt: datetime, n: int) -> datetime:
    """
    Adds a specified number of months to a datetime object.

    Args:
        dt (datetime): The input date.
        n (int): The number of months to add.

    Returns:
        datetime: The resulting date after adding months.
    """
    if n == 0:
        return dt
    return dt + relativedelta(months=n)


def months_difference(dt1: datetime, dt2: datetime) -> int:
    """
    Calculate the number of months between two dates.

    Parameters:
        dt1 (datetime): The first date.
        dt2 (datetime): The second date.

    Returns:
        int: The number of months between the two dates.
    """
    return (dt2.year - dt1.year) * 12 + (dt2.month - dt1.month)


def last_day_of_month(dt: datetime) -> int:
    """
    Get the last day of the month for a given date.

    Parameters:
        dt (datetime): The input date.

    Returns:
        int: The last day of the month.
    """
    return calendar.monthrange(dt.year, dt.month)[1]


def compare_previous(arr):
    """
    Compares each element in an array to the previous one and assigns 1 if the value decreases, otherwise 0.

    Args:
        arr (list): The input list of numeric values.

    Returns:
        np.ndarray: A binary array where 1 indicates a decrease from the previous value.
    """
    arr = np.asarray(arr)
    result = np.zeros_like(arr, dtype=int)
    result[1:] = (arr[1:] < arr[:-1]).astype(float)
    return result
