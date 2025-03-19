"""
Created on Sat Mar 1 14:30:59 2024

Author: davideliu

E-mail: davide97ls@gmail.com

Goal: Generate images to put in report: LPR historical data, XY correlation, word cloud, sentiment analysis.
"""
import matplotlib.pyplot as plt
import platform
if platform.system() == 'Darwin':  # macOS
    plt.rcParams['font.sans-serif'] = ['Heiti TC']
elif platform.system() == 'Windows':  # Windows
    plt.rcParams['font.sans-serif'] = ['SimHei']
else:
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
from wordcloud import WordCloud
from collections import Counter
import re
import os
import json
from dateutil.relativedelta import relativedelta
from models import model_invoke
import pandas as pd
from datetime import datetime


x_dict = {
    'China_Inflation': '中国通货膨胀',
    'China_Consumer_Confidence': '中国消费者信心',
    'China_Public_Debt': '中国公共债务',
    'China_Gov_Lending': '中国政府贷款',
    'US_Interest_Rates': '美国利率',
    'US_Composite_Leading_Indicator': '美国综合领先指标',
    'China_Composite_Leading_Indicator': '中国综合领先指标',
    'China_Business_Confidence': '中国商业信心',
    'Shanghai_Composite': '上证综合指数',
    'CNYUSD': '人民币兑美元',
    'CNYEUR': '人民币兑欧元',
    'M1_MOM': '中国: M1',
    'M2_MOM': '中国: M2',
    '中国:国债到期收益率:1年': '国债到期收益率:1年',
    '中国:国债到期收益率:3年': '国债到期收益率:3年',
    '中国:国债到期收益率:10年': '国债到期收益率:10年',
    '中国银行:净息差': '中国银行净息差',
    '国民总储蓄率': '国民总储蓄率',
    '未来3个月准备增加"购房"支出的比例': '未来3个月准备增加“购房”支出的比例',
    '中债中国绿色债券指数(总值)净价指数': '中债中国绿色债券指数(总值)净价指数',
    '制造业PMI': '制造业采购经理人指数(PMI)',
    'CPI': '居民消费价格指数(CPI)',
    '房地产开发投资:当月值': '房地产开发投资',
    '规模以上工业增加值:定基指数': '规模以上工业增加值',
    '居民人均可支配收入': '居民人均可支配收入',
    '出口总值(人民币计价):当月值': '出口总值',
    '全国城镇调查失业率': '全国城镇调查失业率',
    'GDP:不变价:当季同比': '国内生产总值(GDP)',
    'ppi': '工业生产者价格指数(PPI)',
    'TR_Interest_Rate': '泰勒规则利率',
    'Bond_Spread': '债券利差',
    '中期借贷便利(MLF):操作利率:1年': '中期借贷便利(MLF):1年',
    '存款准备金率:中小型存款类金融机构': '存款准备金率:中小型存款类金融机构',
    'GDP:平减指数': 'GDP:平减指数',
    'DR007': 'DR007',
    '逆回购:7日:回购利率': '逆回购:7日:回购利率',
    '逆回购:7日:回购金额': '逆回购:7日:回购金额',
    '中国:贷款市场报价利率(LPR):1年': '中国:贷款市场报价利率(LPR):1年',
}
key_terms = [
    '贷款', '风险', '金融环境', '融资', '实体经济', '社会预期', '政策工具', '绿色金融', '结构性改革', '资本', '债务', '消费',
    '住房信贷政策', '基础设施建设', '经济增长', '中小银行', '制造业', '现代化产业体系', '碳中和', '社会融资成本', '外汇储备', '货币供应量',
    '政府投资', '私人投资', '宏观经济', '跨周期调节', '就业', '普惠金融', '数字经济', '科技创新', '区域协调发展', '平台经济', '房地产市场',
    '金融资源', '外部均衡', '现代化', '消费信心', '产业升级', '通货膨胀', '货币信贷政策', '国际经济', '经济复苏', '金融开放', '通胀预期',
    '价格稳定', '加息', '降息', '量化宽松', '量化紧缩', '财政与货币政策协调', '中性利率', '收益率曲线控制', '前瞻性指引', '核心通胀',
    '总体通胀', '经济闲置', '充分就业', '产出缺口', '政策正常化', '金融稳定', '劳动力市场', '工资价格', '生产率增长', '供应链中断',
    '外部冲击', '汇率稳定', '账户赤字', '资产负债表', '市场流动性', '财政可持续性', '中性政策立场', '全球溢出效应', '衰退压力', '通胀粘性',
    '期限溢价', '稳健的货币政策', '逆周期调节', '货币政策工具', '金融风险防控', '经济活力', '扩大内需战略', '人民币汇率', '高质量发展',
    '宏观政策', '稳健货币政策', '贷款市场', '双向浮动', '经济增长放缓', '通胀', '供给冲击', '需求收缩', '预期转弱', '结构性货币',
    '金融供给侧', '市场化利率', '汇率市场化改革', '稳就业', '社会融资规模', '产业链供应链', '宏观调控', '国内生产总值', '居民消费价格指数',
    '国民经济', '流动性', '中期借贷便利', '公开市场操作', '再贷款', '再贴现', '支农支小', '金融风险', '广义货币', '普惠小微贷款', '碳减排',
    '利率市场化', '外汇市场', '金融支持', '金融风险监测', '市场预期', '风险防范', '经济金融形势', '全球经济', '物价形势', '适度流动性',
    '货币信贷', '融资结构', '信贷结构', '汇率形成机制改革', '金融运行效率', '服务实体经济', '国际资本流动', '合理均衡水平', '经济金融运行',
    '改革创新', '稳中求进', '实体经济', '政策针对性', '政策灵活性', '政策前瞻性', '预调微调', '经济平稳较快发展', '经济结构调整',
    '管理通胀预期', '金融资源配置', '信贷资金供求结构性矛盾', '金融风险防范', '金融服务水平', '国民经济平稳较快发展', '直接融资', '多样化投融资需求', '金融市场规范发展', '利率市场化改革', '人民币汇率形成机制', '人民币汇率双向浮动弹性', '亚太经合组织',
    '领导人非正式会议', '二十国集团峰会', '亚太经济合作', '区域经济一体化', '亚太命运共同体', '多边主义', '全球经济治理', '经济全球化',
    '可持续发展', '服务贸易', '知识密集型服务', '旅行服务', '服务贸易逆差', '社会消费品零售总额', '网络购物', '消费潜力释放', '全民健身',
    '信息化', '互联网使用', '家务劳动', '时间利用调查', '居民生活质量', '社会民生福祉', '生产生活方式', '智能家居', '在线生活服务',
    '运动健身', '数字化', '互联网普及', '经济社会发展', '政策制定', '改革开放', '国内需求', '经济结构', '生产力', '民生保障', '经济韧性',
    '市场潜力', '经济形势', '财政货币政策', '存量政策', '增量政策', '存量房贷', '资本市场', '中长期资金', '并购重组', '公募基金',
    '中小投资者', '民营经济', '非公有制经济', '消费结构', '新型消费业态', '养老产业', '托育产业', '生育支持政策', '制造业改革', '外资准入',
    '市场化', '法治化', '国际化', '营商环境', '民生底线', '高校毕业生', '农民工', '脱贫人口', '零就业家庭', '就业困难群体', '低收入人口',
    '食品供应', '水电气热', '粮食生产', '农业生产', '粮食安全', '经济回升', '选人用人', '三方区分', '担当者', '全面深化改革'
    , '中国式现代化', '中共中央', '中央委员会', '党内民主', '中国特色社会主义制度', '国家治理体系', '治理能力现代化', '社会主义市场经济',
    '党总揽全局', '党中央权威', '党的全面领导', '顶层设计', '法治轨道', '人民主体地位', '制度建设', '创新', '法治', '经济与社会关系',
    '政府与市场', '效率与公平', '活力与秩序', '发展与安全', '改革成果', '法治统一', '改革落实', '党的自我革命', '学习思想', '报告事项',
    '教育工作', '主持会议', '党建设', '自我革命', '发展理念', '发展格局', '质量发展', '中国化', '先进性', '政治统一', '中心任务',
    '理论结合', '报告制度', '纪律规矩', '党性', '素质提升', '担当', '自律', '调查解决', '舆论氛围'
]
key_terms = list(dict.fromkeys(key_terms))
font_path = '../fonts/NotoSansSC-VariableFont_wght.ttf'


def wordcloud_prompt(term_counts, report):
    """
    Generates a prompt for analyzing the relationship between key financial terms
    and a potential future Loan Prime Rate (LPR) decrease based on a given financial report.

    Args:
        term_counts (dict): A dictionary where keys are financial terms and values are their frequency of occurrence in the report.
        report (str): The full financial report text, which provides context for the term frequency analysis.

    Returns:
        str: A formatted string prompt that instructs an AI agent to analyze the most frequently occurring terms
        and their potential relationship to an LPR decrease. The response is expected to be a concise analysis (2-3 sentences)
        without making any direct predictions about a rate cut.
    """
    prompt = f"""
根据给定财务报告中关键术语的频率词典，结合报告内容，分析最常出现的术语与未来潜在的贷款市场报价利率(LPR)下调有何关联。
仅提供分析，不对潜在降息做出任何预测。
请保持分析简洁，限制在2-3句以内。
关键术语频率：{term_counts}
报告内容：{report}
总结分析和建议：
"""
    return prompt


def terms_sentiment_score_prompt(term_list, report):
    """
    Generates a prompt for sentiment analysis of key terms within an economic conference report.

    Args:
        term_list (list of str): A list of key terms extracted from the report that need to be analyzed for sentiment.
        report (str): The full text of the economic conference report providing context for sentiment evaluation.

    Returns:
        str: A formatted string prompt instructing an AI agent to assign sentiment scores (1 to 10) to each term
        based on its context in the report. The output should be a JSON object containing:
        - Sentiment scores for each term.
        - Brief explanations justifying the assigned scores.

    The scoring criteria:
    - 1 represents a very negative sentiment.
    - 10 represents a very positive sentiment.
    - The score is based on the positivity/negativity of statements associated with the term and the tone of its context.
    """
    prompt = f"""
您正在分析一份经济会议报告：
{report}

以下是与会议相关的关键术语：{term_list}。

您的任务是为每个术语关联一个情感分数，评分范围为1到10：
- 分数为1表示非常负面的情感或关联。
- 分数为10表示非常正面的情感或关联。

该评分应基于：
1. 与每个术语相关的陈述的积极性或消极性。
2. 术语出现的语气和上下文（例如，乐观、悲观、中立）。

另外，提供简洁的理由，解释为何给出该分数。
将结果输出为有效的JSON对象，结构如下：
{'{'}
    "term_1": sentiment_score_1,
    "term_2": sentiment_score_2,
    ...
    "term_N": sentiment_score_N,
    "reasons": {'{'}
        "term_1": "term_1分数的原因",
        "term_2": "term_2分数的原因",
        ...
        "term_N": "term_N分数的原因"
    {'}'}
{'}'}

确保包含所有术语，并且只提供JSON输出，不包含其他内容。
"""
    return prompt


def generate_sentiment_score_caption(score_rationality):
    """
    Generates a caption summarizing sentiment scores and their reasoning for key economic terms.

    Args:
        score_rationality (dict): A dictionary where keys are economic terms and values are
                                  explanations for their assigned sentiment scores.

    Returns:
        str: A formatted caption that provides an overview of the sentiment scores, explaining
             how each term's score was derived based on its role and context in the report.

    The output structure:
    - An introduction explaining the purpose of the sentiment analysis.
    - A list of terms with their corresponding explanations.
    """
    intro = (
        "本分析突出了关键经济术语，并提供了对它们情感的洞察 (1 到 10），"
        "这些情感来源于会议报告。每个术语都根据其在报告中的角色和背景进行了解释。"
    )
    result = intro + '\n\n'
    for key, value in score_rationality.items():
        result += f"- {key}: {value}\n"
    return result


def generate_report_images_lpr_hist(df, cur_date, history_len=12, y='中国:贷款市场报价利率(LPR):1年',
                                    save_folder=None):
    """
    Generates a historical LPR (Loan Prime Rate) trend plot based on the given dataframe.

    Args:
        df (pd.DataFrame): A pandas DataFrame containing historical LPR data with a datetime index.
        cur_date (datetime): The reference date for generating the historical trend.
        history_len (int, optional): The number of months of historical data to include in the plot. Defaults to 12.
        y (str, optional): The column name in `df` that contains the LPR data. Defaults to '中国:贷款市场报价利率(LPR):1年'.
        save_folder (str, optional): The directory where the generated plot will be saved.
                                     If None, the plot is displayed but not saved. Defaults to None.

    Returns:
        None: The function generates and displays a plot, and optionally saves it to the specified folder.

    Plot Details:
    - The x-axis represents months, formatted as "YYYY-MM".
    - The y-axis represents the LPR values.
    - The LPR values are plotted as a blue line with markers.
    - The grid is included for better readability.
    - The x-axis labels are rotated for better visibility.

    If `save_folder` is provided, the plot is saved in a subdirectory named after `cur_date`
    in the format "YYYY-MM-DD" within the given folder.
    """
    title = "LPR历史数据"
    xlabel = "月"
    ylabel = "利率"
    line_color = "blue"
    y_start_period = cur_date - relativedelta(months=history_len)
    df = df[(df.index >= y_start_period) & (df.index < cur_date)]
    series = df[y]

    plt.figure(figsize=(10, 6))
    plt.plot(series.index, series.values, marker="o", color=line_color, label="LPR")
    plt.title(title, fontsize=14)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)

    # Format x-axis to show only year and month
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%Y-%m"))
    plt.gca().xaxis.set_major_locator(plt.matplotlib.dates.MonthLocator(interval=1))
    plt.xticks(rotation=45, fontsize=10)

    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend()
    plt.tight_layout()

    if save_folder is not None:
        os.makedirs(f'{save_folder}/{cur_date.strftime("%Y-%m-%d")}/', exist_ok=True)
        file_name = f"LPR历史数据.png"
        file_path = os.path.join(f'{save_folder}/{cur_date.strftime("%Y-%m-%d")}/', file_name)
        plt.savefig(file_path, dpi=300)
        print(f"- LPR history image saved to: {file_path}")


def generate_report_images_x(df, cur_date, y, corr_history_len=12, save_folder=None):
    """
    Generates correlation visualizations for a given target variable (y) and other features over a specified time period.

    Args:
        df (pd.DataFrame): A pandas DataFrame containing historical data with a datetime index.
        cur_date (datetime): The reference date for computing correlations.
        y (str): The target variable whose correlation with other features is analyzed.
        corr_history_len (int, optional): The number of months of historical data to include in the correlation analysis. Defaults to 12.
        save_folder (str, optional): The directory where the generated plots will be saved.
                                     If None, the plots are displayed but not saved. Defaults to None.

    Returns:
        None: The function generates and displays two correlation plots:
        1. A bar chart showing the correlation of each feature with `y`.
        2. A heatmap of the correlation matrix for all included features.

    Functionality:
    - The function filters the dataset to only include columns that are present in `x_dict.values()`.
    - Computes correlations between `y` and other features within the given `corr_history_len` months.
    - The first plot visualizes the correlation of all features with `y` as a sorted bar chart.
    - The second plot generates a heatmap of the correlation matrix among all features.
    - If `save_folder` is provided, the plots are saved in a subdirectory named after `cur_date`
      in the format "YYYY-MM-DD" within the given folder.
    """
    y_start_period = cur_date - relativedelta(months=corr_history_len)
    df = df.rename(columns=x_dict)
    columns_to_include = set(x_dict.values())
    df = df[df.columns.intersection(columns_to_include)]
    df = df[(df.index >= y_start_period) & (df.index <= cur_date)]
    correlation_with_y = df.corr()[y]

    # Plot correlation of X with Y
    plt.figure(figsize=(10, 6))
    plt.title(f'过去{corr_history_len}个月指标与{y}的相关性')
    correlation_with_y.drop(y, errors='ignore').sort_values(ascending=False).plot(kind='bar', colormap='coolwarm')
    plt.ylabel('相关系数')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    if save_folder is not None:
        os.makedirs(f'{save_folder}/{cur_date.strftime("%Y-%m-%d")}/', exist_ok=True)
        file_name = f"Xy_correlation_report.png"
        file_path = os.path.join(f'{save_folder}/{cur_date.strftime("%Y-%m-%d")}/', file_name)
        plt.savefig(file_path, dpi=300)
        print(f"- Xy_correlation image saved to: {file_path}")

    correlation_matrix = df.corr()
    plt.figure(figsize=(20, 12))
    plt.title(f'过去{corr_history_len}个月所有特征的相关性')
    cax = plt.imshow(correlation_matrix, cmap='coolwarm', interpolation='none')
    plt.colorbar(cax)
    plt.xticks(range(len(correlation_matrix)), correlation_matrix.columns, rotation=45, ha='right')
    plt.yticks(range(len(correlation_matrix)), correlation_matrix.columns)
    plt.tight_layout()

    if save_folder is not None:
        os.makedirs(f'{save_folder}/{cur_date.strftime("%Y-%m-%d")}/', exist_ok=True)
        file_name = f"Xx_correlation_report.png"
        file_path = os.path.join(f'{save_folder}/{cur_date.strftime("%Y-%m-%d")}/', file_name)
        plt.savefig(file_path, dpi=300)
        print(f"- Xx_correlation image saved to: {file_path}")


def generate_report_images_terms_analysis(meeting_report, cur_date, key_terms, save_folder=None, analyze_top_k=10,
                                          generate_caption=False, verbose=False, model="gpt-4o-mini"):
    """
    Generates word cloud and sentiment analysis visualizations for a given financial meeting report.

    Args:
        meeting_report (str): The full text of the financial meeting report.
        cur_date (datetime): The reference date used for saving generated files.
        key_terms (list): A list of key economic terms to analyze.
        save_folder (str, optional): The directory where generated images and captions will be saved.
                                     If None, the images are displayed but not saved. Defaults to None.
        analyze_top_k (int, optional): The number of most frequent terms to analyze for sentiment. Defaults to 10.
        generate_caption (bool, optional): Whether to generate a textual summary for the word cloud. Defaults to False.
        verbose (bool, optional): If True, prints debug information during execution. Defaults to False.
        model (str, optional): The AI model used for generating text-based insights. Defaults to "gpt-4o-mini".

    Returns:
        None: The function generates and displays two visualizations:
        1. A word cloud representing term frequencies within the report.
        2. A bar chart showing sentiment scores for the most frequent key terms.

    Additional Outputs:
        - If `save_folder` is provided, the function saves:
          - "report_wordcloud.png": Word cloud image.
          - "terms_sentiment_bar_chart.png": Sentiment score bar chart.
          - Captions summarizing insights (if enabled).
    """
    # WORD CLOUD
    # Remove non-Chinese characters and make the text lowercase
    cleaned_text = re.sub(r'[^\w\s\u4e00-\u9fff]', '', meeting_report)
    captions = None
    term_counts = Counter()
    for term in key_terms:
        term_counts[term] = cleaned_text.count(term)
    if verbose:
        print(term_counts)
    if generate_caption:
        top_terms = sorted(term_counts.items(), key=lambda x: x[1], reverse=True)[:analyze_top_k]
        prompt = wordcloud_prompt(top_terms, meeting_report)
        system_prompt = "You are an helpful assistant"
        captions = model_invoke(system_prompt, prompt, model=model)
        if verbose:
            print(captions)

    wordcloud = WordCloud(background_color="white", font_path=font_path, width=800, height=400).\
        generate_from_frequencies(term_counts)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')

    if save_folder is not None:
        os.makedirs(f'{save_folder}/{cur_date.strftime("%Y-%m-%d")}/', exist_ok=True)
        file_name = "report_wordcloud.png"
        image_path = os.path.join(f'{save_folder}/{cur_date.strftime("%Y-%m-%d")}/', file_name)
        text_path = os.path.join(f'{save_folder}/{cur_date.strftime("%Y-%m-%d")}/', file_name.replace(".png", ".txt"))
        plt.savefig(image_path, dpi=300)
        print(f"- Word cloud image saved to: {image_path}")
        if captions:
            with open(text_path, "w", encoding="utf-8") as text_file:
                text_file.write(captions)
            print(f"- Word cloud caption saved to: {text_path}")

    # SENTIMENTS SCORE
    top_terms = sorted(term_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    term_list = [term for term, count in top_terms]
    if verbose:
        print(top_terms)
    prompt = terms_sentiment_score_prompt(term_list, meeting_report)
    system_prompt = "You are an helpful assistant, your output must be in Chinese language"
    response = model_invoke(system_prompt, prompt, model=model)
    response = response[response.find("{"):response.rfind("}") + 1]  # extract in json format
    terms_sentiment_dict = json.loads(response)
    score_rationality = terms_sentiment_dict.pop("reasons", None)
    if verbose:
        print(terms_sentiment_dict)
        print(score_rationality)

    # Create the bar chart
    terms = list(terms_sentiment_dict.keys())
    scores = list(terms_sentiment_dict.values())
    plt.figure(figsize=(10, 6))
    plt.bar(terms, scores, color='skyblue', edgecolor='black')
    plt.xlabel("关键经济术语", fontsize=12)
    plt.ylabel("情感评分", fontsize=12)
    plt.title("关键经济术语的情感评分", fontsize=14)
    plt.xticks(rotation=45, fontsize=10, ha="right")
    plt.tight_layout()

    caption = generate_sentiment_score_caption(score_rationality)
    if verbose:
        print(caption)

    if save_folder is not None:
        os.makedirs(f'{save_folder}/{cur_date.strftime("%Y-%m-%d")}/', exist_ok=True)
        file_name = "terms_sentiment_bar_chart.png"
        text_path = os.path.join(f'{save_folder}/{cur_date.strftime("%Y-%m-%d")}/', file_name.replace(".png", ".md"))
        image_path = os.path.join(f'{save_folder}/{cur_date.strftime("%Y-%m-%d")}/', file_name)
        plt.savefig(image_path, dpi=300)
        print(f"- Terms sentiment bar chart image saved to: {image_path}")
        with open(text_path, "w", encoding="utf-8") as text_file:
            text_file.write(caption)
        print(f"- Terms sentiment caption saved to: {text_path}")


def generate_report_images(date, csv_file_path, y, save_folder, meeting_report, model="gpt-4o-mini"):
    """
    Generates multiple financial report visualizations, including LPR trends, feature correlations, and term analysis.

    Args:
        date (str): The reference date for the report in the format "YYYY-MM-DD".
        csv_file_path (str): The path to the CSV file containing historical financial data.
        y (str): The target variable for correlation analysis and historical trends.
        save_folder (str): The directory where generated images and captions will be saved.
        meeting_report (str): The full text of the financial meeting report for term analysis.
        model (str, optional): The AI model used for text-based insights. Defaults to "gpt-4o-mini".

    Returns:
        None: The function generates and saves the following visualizations:
        1. "LPR历史数据.png" - A line chart of the historical Loan Prime Rate (LPR).
        2. "Xy_correlation_report.png" - A bar chart of feature correlations with the target variable.
        3. "Xx_correlation_report.png" - A heatmap of feature correlations.
        4. "report_wordcloud.png" - A word cloud of key terms from the meeting report.
        5. "terms_sentiment_bar_chart.png" - A sentiment score bar chart for key economic terms.

    Additional Outputs:
        - If `generate_caption` is enabled, captions summarizing key insights are saved alongside images.
        - All files are stored in a subfolder named after `date` within `save_folder`.
    """
    year, month, day = map(int, date.split('-'))
    cur_date = datetime(year, month, day)
    start_date = datetime(2019, 8, 31)
    history_len = (cur_date.year * 12 + cur_date.month) - (start_date.year * 12 + start_date.month)
    df = pd.read_csv(csv_file_path, index_col=0, parse_dates=True)
    df = df.loc[:, ~df.columns.str.startswith('y_')]
    analyze_top_k = 10
    generate_caption = True
    generate_report_images_lpr_hist(df, cur_date, history_len=history_len, y=y, save_folder=save_folder)
    generate_report_images_x(df, cur_date, y, corr_history_len=60, save_folder=save_folder)
    generate_report_images_terms_analysis(meeting_report, cur_date, key_terms, save_folder=save_folder,
                                          analyze_top_k=analyze_top_k, generate_caption=generate_caption,
                                          model=model)


if __name__ == '__main__':
    csv_file_path = '../data_retrieval/data/XY_aug_feat.csv'
    y = '中国:贷款市场报价利率(LPR):1年'
    df = pd.read_csv(csv_file_path)
    df.set_index(df.columns[0], inplace=True)
    df.index = pd.to_datetime(df.index)
    df = df.loc[:, ~df.columns.str.startswith('y_')]
    cur_date = datetime(2023, 1, 31)
    start_date = datetime(2019, 8, 1)
    history_len = (cur_date.year - start_date.year) * 12 + (cur_date.month - start_date.month)
    analyze_top_k = 10
    save_folder = 'test_results'
    generate_caption = True
    meeting_report = '''中国人民银行货币政策委员会2023年第四季度（总第103次）例会于12月27日在北京召开。
    会议分析了国内外经济金融形势。会议认为，今年以来宏观政策坚持稳字当头、稳中求进，稳健的货币政策精准有力，强化逆周期和跨周期调节，综合运用利率、准备金、再贷款等工具，切实服务实体经济，有效防控金融风险，为经济回升向好创造适宜的货币金融环境。贷款市场报价利率改革成效显著，存款利率市场化调整机制作用有效发挥，货币政策传导效率增强，社会融资成本明显下降。外汇市场供求基本平衡，经常账户顺差稳定，外汇储备充足，人民币汇率双向浮动、预期趋稳，在合理均衡水平上保持基本稳定，发挥了宏观经济稳定器功能。
    会议指出，稳健的货币政策要灵活适度、精准有效。当前外部环境更趋复杂严峻，国际经济贸易投资放缓，通胀出现高位回落趋势，发达国家利率保持高位。我国经济回升向好、动力增强，高质量发展扎实推进，但仍面临有效需求不足、社会预期偏弱等挑战。要稳中求进、以进促稳，加大宏观政策调控力度，不断巩固稳中向好的基础。精准有效实施稳健的货币政策，更加注重做好逆周期和跨周期调节，更好发挥货币政策工具的总量和结构双重功能，着力扩大内需、提振信心，推动经济良性循环。
    会议认为，要加大已出台货币政策实施力度。保持流动性合理充裕，引导信贷合理增长、均衡投放，保持社会融资规模、货币供应量同经济增长和价格水平预期目标相匹配。增强政府投资和政策激励的引导作用，提高乘数效应，有效带动激发更多民间投资。促进物价低位回升，保持物价在合理水平。完善市场化利率形成和传导机制，发挥央行政策利率引导作用，释放贷款市场报价利率改革和存款利率市场化调整机制效能，推动企业融资和居民信贷成本稳中有降。积极盘活被低效占用的金融资源，提高资金使用效率。深化汇率市场化改革，引导企业和金融机构坚持“风险中性”理念，综合施策、校正背离、稳定预期，坚决对顺周期行为予以纠偏，坚决防范汇率超调风险，防止形成单边一致性预期并自我强化，保持人民币汇率在合理均衡水平上的基本稳定。
    会议指出，要深化金融供给侧结构性改革，构建金融有效支持实体经济的体制机制。引导大银行服务重心下沉，推动中小银行聚焦主责主业，支持银行补充资本，共同维护金融市场的稳定发展。做好科技金融、绿色金融、普惠金融、养老金融、数字金融“五篇大文章”，实施好存续结构性货币政策工具，落实好再贷款再贴现额度，继续加大对普惠金融、绿色转型、科技创新、数字经济、基础设施建设等支持力度，综合施策支持区域协调发展。落实好加大力度支持科技型企业融资行动方案，引导金融机构增加制造业中长期贷款，支持加快建设现代化产业体系。坚持“两个毫不动摇”，持续做好支持民营经济发展壮大的金融服务。以促进实现碳达峰、碳中和为目标完善绿色金融体系。优化大宗消费品和社会服务领域消费金融服务，继续加大对企业稳岗扩岗和重点群体创业就业的金融支持力度。因城施策精准实施差别化住房信贷政策，更好支持刚性和改善性住房需求，一视同仁满足不同所有制房地产企业合理融资需求，促进房地产市场平稳健康发展。加大对保障性住房建设、“平急两用”公共基础设施建设、城中村改造的金融支持力度，推动加快构建房地产发展新模式。落实促进平台经济健康发展的金融政策措施。切实推进金融高水平双向开放，提高开放条件下经济金融管理能力和防控风险能力。
    会议强调，要以习近平新时代中国特色社会主义思想为指导，全面贯彻落实党的二十大、中央经济工作会议和中央金融工作会议精神，按照党中央、国务院的决策部署，坚持稳中求进工作总基调，牢牢把握高质量发展首要任务，扎实推进中国式现代化，完整、准确、全面贯彻新发展理念，加快构建新发展格局。把实施扩大内需战略同深化供给侧结构性改革有机结合起来，进一步加强部门间政策协调配合，强化政策统筹，充分发挥货币信贷政策效能，兼顾好内部均衡和外部均衡。切实增强经济活力、防范化解风险、改善社会预期，巩固和增强经济回升向好态势，持续推动经济实现质的有效提升和量的合理增长。
    本次会议由中国人民银行行长兼货币政策委员会主席潘功胜主持，货币政策委员会委员廖岷、张青松、李云泽、易会满、康义、朱鹤新、刘世锦、蔡昉、王一鸣出席会议。徐守本、李春临、刘国强、田国立因公务请假。中国人民银行北京市分行、山西省分行、海南省分行、四川省分行、西藏自治区分行负责同志列席会议.
    '''

    generate_report_images_lpr_hist(df, cur_date, history_len=history_len, y=y, save_folder=save_folder)
    generate_report_images_x(df, cur_date, y, corr_history_len=60, save_folder=save_folder)
    generate_report_images_terms_analysis(meeting_report, cur_date, key_terms, save_folder=save_folder,
                                          analyze_top_k=analyze_top_k, generate_caption=generate_caption, model='g4f')
