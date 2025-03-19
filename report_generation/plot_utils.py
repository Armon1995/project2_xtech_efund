"""
Created on Sat Mar 1 14:30:59 2024

Author: davideliu

E-mail: davide97ls@gmail.com

Goal: Visualize X factors trends and influence.
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates
import re
from pylab import mpl
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
from adjustText import adjust_text
from models import model_invoke

mpl.rcParams['font.sans-serif'] = ['STZhongsong']
mpl.rcParams['axes.unicode_minus'] = False


def plot_factors(date, chatbot, ydata, target, text, fig_name):
    """
    Extracts and plots the trends of key factors affecting LPR from the provided analysis text.

    This function processes the analysis text to extract key factors, their historical data, and
    the probability of their impact on LPR. It then plots the trends of these factors and the LPR
    over time, normalizing the data for comparison.

    Args:
        date (str): The date for which the analysis is being performed, in the format "YYYY-MM-DD".
        chatbot: The chatbot instance used for generating analysis and reports.
        ydata (pd.DataFrame): The DataFrame containing the LPR data.
        target (str): The column name for the LPR data in the DataFrame.
        text (str): The analysis text containing information about key factors and their impact.
        fig_name (str): The base name for the figures to be saved.

    Returns:
        str: The processed analysis text.
    """
    role_prompt = '''
    角色：信息提取师，我会将一份关于LPR的分析报告给你，请你将主要因素的数据趋势和影响概率提取出来

    # 任务描述：我会提供一份包含lpr数据的分析报告，还有一份对lpr主要因素分析的报告，我希望你将参考数据分析报告将lpr主要因素的数据输出出来

    # 输出格式
        主要因素是：中国GDP、历史数据是：[13.8949, 14.28, 14.6877, 17.8205, 17.8818]，可能导致LPR下降的概率是：65%
        主要因素是：制造业PMI、历史数据是：[50.2, 49.5, 47.4, 49.6, 50.2, 49.0, 49.4, 50.1, 49.2, 48.0, 47.0, 50.1]，可能导致LPR下降的概率是：65%
        ....
        ....

'''
    text = model_invoke(role_prompt, text, chatbot=chatbot)
    # 提供的基准日期
    reference_date = date
    # 使用正则表达式提取数据
    pattern = r"主要因素是：(.*?)、历史数据是：\[(.*?)\]，可能导致LPR下降的概率是：(\d+)%"
    matches = re.findall(pattern, text)

    # 处理提取的数据
    factors = []
    historical_data = []
    probabilities = []

    for match in matches:
        factors.append(match[0])
        historical_data.append(list(map(float, match[1].split(", "))))
        probabilities.append(float(match[2]) / 100)

    # 构建DataFrame
    data = pd.DataFrame({"Factor": factors, "Historical Data": historical_data, "Probability": probabilities})

    # 转换趋势数据为时间序列
    reference_date = pd.to_datetime(reference_date)
    trend_data = {}

    for factor, values in zip(data["Factor"], data["Historical Data"]):
        if len(values) <= 6:
            # 年度数据
            dates = pd.date_range(end=reference_date, periods=len(values), freq='Y')
        else:
            # 月度数据
            dates = pd.date_range(end=reference_date, periods=len(values), freq='M')
        trend_data[factor] = pd.Series(data=values, index=dates)
    scaler = MinMaxScaler(feature_range=(0.4, 0.6))  # 设置范围为 0.4-0.6
    data["Normalized"] = scaler.fit_transform(data[["Probability"]])
    # 热图数据
    heatmap_data = pd.DataFrame({"Factor": factors, "Probability": probabilities}).set_index("Factor")

    # 归一化并绘制趋势图和热图
    for i, factor in enumerate(factors):
        fig, axes = plt.subplots(1, 1, figsize=(12, 4))
        plt.suptitle(f"Analysis of {factor}", fontsize=14, weight='bold')
        # # 获取当前的子图
        ax_trend = axes

        # 趋势图（归一化）
        series = trend_data[factor]
        x = series.index.astype(np.int64) // 10**9  # 转换为时间戳
        y = series.values

        # 归一化
        scaler = MinMaxScaler()
        y_normalized = scaler.fit_transform(y.reshape(-1, 1)).flatten()

        ax_trend.plot(series.index, y_normalized, marker="o", label=factor, color="steelblue", linewidth=2)

        # 设置纵坐标为归一化范围，但显示原始数据的刻度
        ax_trend.set_ylim(-0.3, 1.3)  # 归一化后的范围
        ax_trend.set_yticks(np.linspace(0, 1, 5))  # 归一化后的刻度
        ax_trend.set_yticklabels([f"{y.min():.2f}", f"{(y.max() - y.min()) * 0.25 + y.min():.2f}",
                                  f"{(y.max() - y.min()) * 0.5 + y.min():.2f}",
                                  f"{(y.max() - y.min()) * 0.75 + y.min():.2f}", f"{y.max():.2f}"])  # 显示原始数据范围
        # 美化轴标签
        # ax_trend.set_title(f"Trend of {factor}", fontsize=12, weight='bold')
        ax_trend.set_ylabel("Value", fontsize=10)
        ax_trend.set_xlabel("Date", fontsize=10)
        ax_trend.grid(True, linestyle="--", alpha=0.6)
        ax_trend.set_xticks(series.index)
        ax_trend.set_xticklabels(series.index.strftime('%Y-%m'), rotation=45, ha='right')
        ax_trend.legend(loc="upper left", fontsize=10)
        # 创建第二个 y 轴
        ax2 = ax_trend.twinx()
        if len(series) < 6:
            y2 = ydata.resample('Y').last().loc[series.index, target]
        else:
            y2 = ydata.loc[series.index, target]
        scaler = MinMaxScaler()
        y2_normalized = scaler.fit_transform(np.array(y2.values).reshape(-1, 1)).flatten()

        # 绘制归一化后的曲线
        ax2.plot(series.index, y2_normalized, marker="x", label="LPR", color="orange", linewidth=2)
        ax2.set_ylim(-0.3, 1.3)  # 保持与第一个 y 轴一致
        ax2.set_ylabel("LPR", fontsize=10)

        # 设置第二个 y 轴显示原始 LPR 数据刻度
        ax2.set_yticks(np.linspace(0, 1, 5))
        ax2.set_yticklabels([f"{y2.min():.2f}", f"{(y2.max() - y2.min()) * 0.25 + y2.min():.2f}",
                             f"{(y2.max() - y2.min()) * 0.5 + y2.min():.2f}",
                             f"{(y2.max() - y2.min()) * 0.75 + y2.min():.2f}", f"{y2.max():.2f}"])
        ax2.legend(loc="upper right", fontsize=10)

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig(f"test_results/{date}/{fig_name}{i}相关因素分析.png", dpi=300)
        plt.clf()
    return text


def plot_prob(date, chatbot, text):
    """
    Extracts the probability of LPR reduction due to different factors
    from an analysis report and plots a heatmap.

    Args:
    - date (str): Reference date for saving the plot.
    - chatbot: Chatbot instance for extracting probabilities.
    - text (str): LPR analysis report.

    Returns:
    - None (Saves the probability heatmap as an image).
    """
    role_prompt = '''
    角色：信息提取师，我会将一份关于LPR的分析报告给你，请你将每个因素的影响概率提取出来

    # 输出格式
        主要因素是：中国GDP、可能导致LPR下降的概率是：48%
        主要因素是：制造业PMI、可能导致LPR下降的概率是：51%
        ....
        ....

'''
    text = model_invoke(role_prompt, text, chatbot=chatbot)

    # 使用正则表达式提取数据
    pattern = r"主要因素是：(.*?)、可能导致LPR下降的概率是：(\d+)%"
    matches = re.findall(pattern, text)
    # 处理提取的数据
    factors = []
    probabilities = []

    for match in matches:
        factors.append(match[0])
        probabilities.append(float(match[1]) / 100)
    data = pd.DataFrame({"Factor": factors, "Probability": probabilities})

    # 归一化 Probability 值到 [0, 1]，用于控制热图颜色
    scaler = MinMaxScaler(feature_range=(0.4, 0.6))  # 设置范围为 0.4-0.6
    data["Normalized"] = scaler.fit_transform(data[["Probability"]])

    # 转为矩阵形式
    heatmap_data = data.pivot_table(index="Factor", values="Normalized")

    # 设置绘图尺寸
    plt.figure(figsize=(10, 16))

    # 绘制热度图，使用归一化后的数据，但标注原始值
    sns.heatmap(
        heatmap_data,
        annot=data.pivot_table(index="Factor", values="Probability"),
        cmap="YlGnBu",  # 设置颜色图谱
        cbar_kws={"label": "Probability"}  # 颜色条标签
    )

    # 设置标题
    plt.title("各经济因素导致LPR下降的概率")
    plt.xlabel("概率")
    plt.ylabel("经济因素")

    # 显示图形
    plt.tight_layout()
    plt.savefig(f"test_results/{date}/各经济因素导致LPR下降的概率.png", dpi=300)
    # plt.show()
    plt.clf()


def plot_ydata(date, chatbot):
    """
    Extracts and plots historical LPR data with a trend line.

    Args:
    - date (str): The last date in the historical series.
    - chatbot: Chatbot instance for extracting LPR historical data.

    Returns:
    - None (Displays the LPR historical trend plot).
    """
    text = '''
'''
    role_prompt = '''
    角色：信息提取师，我会将一份关于LPR的分析报告给你，请你将LPR历史数据提取出来

    # 输出格式
        LPR历史数据是：[13.8949, 14.28, 14.6877, 17.8205, 17.8818]
'''
    text = model_invoke(role_prompt, text, chatbot=chatbot)

    # 提取数据
    start_index = text.find('[')
    end_index = text.find(']')
    data_list_str = text[start_index + 1:end_index]
    data_list = [float(item) for item in data_list_str.split(', ')]

    # 指定最后一个日期（格式为 'YYYY-MM-DD'）
    specified_date = date  

    # 生成月份列表
    def generate_months(end_date, num_months):
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        months = [(end_date - timedelta(days=30 * i)).strftime('%Y-%m') for i in range(num_months - 1, -1, -1)]
        return months

    months = generate_months(specified_date, len(data_list))

    # 线性回归分析
    x = np.arange(len(data_list)).reshape(-1, 1)
    y = np.array(data_list)
    model = LinearRegression()
    model.fit(x, y)
    trend = model.predict(x)

    # 绘制图表
    plt.figure(figsize=(10, 5))
    plt.plot(months, data_list, marker='o', linestyle='-', color='b', label='LPR')
    plt.plot(months, trend, linestyle='--', color='r', label='趋势线')
    plt.title('LPR历史数据与趋势预测')
    plt.xlabel('月份')
    plt.ylabel('LPR')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)  # 旋转 x 轴标签以便更好地显示
    plt.tight_layout()  # 调整布局
    plt.show()


def pressure_extract(chatbot, text):
    """
    Extracts the main pressure factors leading to LPR decline
    from a historical prediction report.

    Args:
    - chatbot: Chatbot instance for extracting pressure factors.
    - text (str): LPR historical prediction report.

    Returns:
    - Extracted text with summarized pressure factors.
    """
    role_prompt = '''
    # 角色：信息提取师，我会将一份关于LPR的历史预测给你，请你将主要导致LPR下降的压力总结

    # 任务
        - 给出导致LPR下降的因素分析，按照贡献值从高到低排序之后输出
        - 每条原因简洁一点，最好几个字总结
        - 只用输出贡献度最高的一个
        - 每输出10个字都要使用\n换行
    
    # 输出结果格式如下
        根据历史xxx的分析，\n什么原因，可能导致LPR下降，\n重要度为：（这里用贡献度作重要度）
        .......

'''
    text = model_invoke(role_prompt, text, chatbot=chatbot)
    return text


def plot_pressure(text, chatbot, data, date, target):
    """
    Plots LPR historical trends and marks the periods where past
    predictions indicated downward pressure.

    Args:
    - text (list): List of extracted historical prediction records.
    - chatbot: Chatbot instance for extracting factors.
    - data (DataFrame): Historical LPR data.
    - date (str): Reference date for trend visualization.
    - target (str): Column name in data for LPR values.

    Returns:
    - None (Saves the pressure visualization as an image).
    """
    plot_date = date
    reference_date = pd.to_datetime(date)
    df = data.loc[reference_date - pd.DateOffset(months=11):reference_date, target]
    for idx, item in enumerate(text):
        t = text[idx]['result']
        text[idx]['result'] = pressure_extract(chatbot, t)

    forecast_df = pd.DataFrame(text)
    forecast_df['date'] = pd.to_datetime(forecast_df['date'])

    # 创建图表
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.plot(df.index, df.values, marker='o', linestyle='-', color='#1f77b4', label='LPR', linewidth=2, markersize=8)

    # 在每个时间点画一条垂直线
    for date in forecast_df['date']:
        ax.axvline(x=date, color='gray', linestyle='--', alpha=0.5)

    # 添加文本标注
    texts = []
    pre = [180, 140, 100, 50, 0]
    for _, row in forecast_df.iterrows():
        text = ax.annotate(
            row['result'],
            xy=(row['date'], df[df.index == row['date']].values[0]),
            xycoords='data',
            xytext=(0, pre[_]),  # 初始偏移量（水平方向）
            textcoords='offset points',
            arrowprops=dict(arrowstyle="->", lw=1.5, color='#d62728'),
            fontsize=12, color='#d62728', bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
            rotation=0  # 旋转文本为垂直方向
        )
        texts.append(text)

    adjust_text(texts)

    # 设置日期格式
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.MonthLocator())

    # 设置标题和标签
    ax.set_title('LPR与历史未兑现的降息压力', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('日期', fontsize=14, labelpad=10)
    ax.set_ylabel('LPR', fontsize=14, labelpad=10)

    # 设置网格线
    ax.grid(True, linestyle='--', alpha=0.7)

    # 旋转日期标签
    plt.xticks(rotation=45, ha='right')

    # 设置图例
    ax.legend(loc='upper left', fontsize=12)

    # 调整布局
    plt.tight_layout()
    plt.savefig(f"test_results/{plot_date}/LPR与历史未兑现的降息压力.png", dpi=300)
    # 显示图表
    # plt.show()
    plt.clf()
