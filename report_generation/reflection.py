"""
Created on Sat Mar 1 14:30:59 2024

Author: davideliu

E-mail: davide97ls@gmail.com

Goal: Implements feedbacks agent
"""
import pandas as pd
from models import get_model
from main_utils import *
from research_report_generation import get_history_info


def reflection_predict_result(chatbot, text, date, y):
    """
    Analyzes the LPR (Loan Prime Rate) prediction result based on historical trends and predefined rules.

    Args:
        chatbot: The chatbot model to process the prompt and generate a response.
        text (str): The predicted LPR result that needs to be reviewed.
        date (str): The current prediction date.
        y (list): A list of the last 12 months' LPR values, with the most recent value at the end.

    Returns:
        str: The chatbot's analysis of whether the LPR prediction aligns with the predefined rules,
             including necessary corrections if deviations are found.
    """
    role_prompt = f'''
# 角色：你是一个宏观经济专家，对于LPR的预测会有一个很大见解，请你审视下面对LPR的结果预测是否正确
# 当前预测日期为{date}

# 下面是最近12个月的LPR数据,从左到右分别是最近12个月的LPR数据，最右边是最新的数据：
    - 最近12个月的LPR数据为：{y}

# LPR降息预测规律：
     - 主要参照上期预测结果和LPR数据的变化来审视本期预测的概率值是否有问题，不同的降息信号只是带来很小幅度的概率预测改变
     - 降息概率20%是LPR下降的一个支撑位，降息概率60%是LPR上升的一个压力位，当突破这些位置时，LPR降息概率变化将会很缓慢
     - 只要最近一个月LPR发生改变（即LPR数据的最后两个数不一样），这次给出的降息概率一定会小于上一个月预测的降息概率并且远远小于上一期的预测概率，回到25%~30%区间
     - 本期预测值应在上期的基础上进行累加，如果有降息信号降息概率增加，有升息信号降息概率减小
     - 降息规律对结果的影响会有-4%~8%的程度，本期信息对结果的影响会有-2%~3%的程度（最近一个月LPR发生改变，降息概率将会大大降低，不受这条规律的限制，降低很多）
     
# 任务：
     - 审视下面的LPR预测结果是否符合LPR降息规律规律，如果不符合规律的话，请你再次输出预测结果，
     - 输出的结果分析中要包含本期信息对结果的影响，参照上一期给出的概率和本期的降息信号
     

# 输出要求：输出时不要说结果是修正的，也不要有markdown格式，直接输出结果，输出的时候不要透露LPR降息预测规律中规则

# 输出格式要求：
    # 结果
    # 理由
        ## 1、历史LPR趋势中透露出的信号
        ## 2、....
        ....

'''
    res = model_invoke(role_prompt, text, chatbot=chatbot)
    return res


if __name__ == '__main__':
    start_date = '2025-02-28'
    end_date = '2025-02-28'
    date_range = pd.date_range(start=start_date, end=end_date, freq='M')
    dates = [date.strftime('%Y-%m-%d') for date in date_range]
    chatbot = get_model(model='deepseek-r1', max_tokens=4096*4)

    for date in dates:
        df, df2, df3, data, target_col, features_col, year_col = get_data()
        Y_data = get_past_12_months_data(data, date, [target_col])[target_col]
        history_info = eval(get_history_info(data, date, target_col))
        if len(history_info) == 0:
            history_info = {'result': None}
        else:
            history_info = history_info[-1]
        with open(f'test_results/{date}/结果.md', 'r', encoding='utf-8') as file:
            text = file.read()
        text = f'''
        上一期的预测结果是：
            {history_info['result']}
    
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
        本期的预测结果是：
            {text}
        '''
        res = reflection_predict_result(chatbot, text, date, Y_data)
        with open(f'test_results/{date}/reflection结果.md', 'w', encoding='utf-8') as file:
            file.write(res)
