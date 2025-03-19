"""
Created on Sat Mar 1 14:30:59 2024

Author: davideliu

E-mail: davide97ls@gmail.com

Goal: Generates historical reports
"""
from prompt import generate_report_text, generate_summary_prompt
from plot_utils import *
from research_report_generation import *
from main_utils import *
from models import get_model
from generate_news_analysis import generate_news_analysis
from generate_LPR_analysis import generate_lpr_analysis
from generate_report_images import generate_report_images
from create_word import generate_word_doc
from reflection import reflection_predict_result
import argparse
warnings.filterwarnings("ignore")

# GLOBAL VARIABLES usually no need to change
load_result = False  # load cached results, only used for debugging specific parts
x_data_path = '../data_retrieval/data/XY_aug_feat.csv'
results_path = 'test_results'
target_col = '中国:贷款市场报价利率(LPR):1年'
no_news_embedding = True  # if False use tf-idf for news retrieval, otherwise use FAISS
model = 'gpt-4o-mini'
# 易方达 VARIABLES
# make sure use_efund_models = True to generate report on 易方达 machine
prod_env = False  # if True retrieve news from production env, else use test env
use_efund_models = True  # use yifangda efund model
if use_efund_models:
    no_news_embedding = True
    model = 'efund'

# select dates to generate report
dates_2018 = ['2018-08-01', '2018-09-01', '2018-10-01', '2018-11-01', '2018-12-01']
dates_2019 = ['2019-01-01', '2019-02-01', '2019-03-01', '2019-04-01', '2019-05-01', '2019-06-01', '2019-07-01', '2019-08-01', '2019-09-01', '2019-10-01', '2019-11-01', '2019-12-01']
dates_2020 = ['2020-01-01', '2020-02-01', '2020-03-01', '2020-04-01', '2020-05-01', '2020-06-01', '2020-07-01', '2020-08-01', '2020-09-01', '2020-10-01', '2020-11-01', '2020-12-01']
dates_2021 = ['2021-01-01', '2021-02-01', '2021-03-01', '2021-04-01', '2021-05-01', '2021-06-01', '2021-07-01', '2021-08-01', '2021-09-01', '2021-10-01', '2021-11-01', '2021-12-01']
dates_2022 = ['2022-01-01', '2022-02-01', '2022-03-01', '2022-04-01', '2022-05-01', '2022-06-01', '2022-07-01', '2022-08-01', '2022-09-01', '2022-10-01', '2022-11-01', '2022-12-01']
dates_2023 = ['2023-01-01', '2023-02-01', '2023-03-01', '2023-04-01', '2023-05-01', '2023-06-01', '2023-07-01', '2023-08-01', '2023-09-01', '2023-10-01', '2023-11-01', '2023-12-01']
dates_2024 = ['2024-01-01', '2024-02-01', '2024-03-01', '2024-04-01', '2024-05-01', '2024-06-01', '2024-07-01', '2024-08-01', '2024-09-01', '2024-10-01', '2024-11-01', '2024-12-01']
dates_2025 = ['2025-01-01', '2025-02-01']
all_dates = dates_2018 + dates_2019 + dates_2020 + dates_2021 + dates_2022 + dates_2023 + dates_2024 + dates_2025


def detailed_analysis(chatbot, date):
    """
    Performs a detailed analysis of LPR data and generates a comprehensive report.

    This function orchestrates the entire analysis process, including data loading, feature calculation,
    LPR analysis, X data analysis, policy report analysis, news analysis, and summary generation.
    It also handles the creation of necessary directories and saving of intermediate results.

    Args:
        chatbot: The chatbot instance used for generating analysis and reports.
        date (str): The date for which the analysis is being performed, in the format "YYYY-MM-DD".

    Returns:
        None

    Raises:
        Exception: If any part of the analysis process fails.
    """
    print('Generating report for date:', date, type(date))

    # 判断保存路径是否存在
    log_dir = os.path.join(results_path, date)
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    print(f'Saving log in: {log_dir}')

    # 读取数据
    # df is monetary_policy_reports
    # df2 is political_bureau_reports
    # df3 is monetary_board_meetings_reports
    # data is timeseries data
    df, df2, df3, data, target_col, features_col, year_col = get_data()
    print('Data loaded successfully')

    # 计算辅助特征
    # compute yoy, mom, zscore
    results, data = calculate_auxiliary_features(data, features_col+[target_col])
    y_data = get_past_12_months_data(data, date, [target_col])[target_col]

    # 计算历史降息幅度和当年降息幅度
    historical_avg_decline, decline_from_year_start = calculate_average_decline(data, date, target_col)
    historical_avg_decline, decline_from_year_start = round(historical_avg_decline, 4),\
                                                      round(decline_from_year_start, 4)
    print('Data preprocess completed')

    # retrieve previous reports
    print('Retrieving historical reports...')
    history_info = eval(get_history_info(data, date, target_col))
    if len(history_info) == 0:
        print('No historical reports found. Review agent not used.')
    else:
        print(f'Retrieved {len(history_info)} historical reports used for review agent.')

    # 0: 生成保存引言
    if not load_result:
        print('Part 0: Generating introduction...')
        intro_file_name = f"test_results/{date}/引言.md"
        response_introduction = introduction(chatbot)
        with open(intro_file_name, 'w', encoding='utf-8') as file:
            file.write(response_introduction)
        print(f"Part 0: Introduction generated and saved to {intro_file_name}")

    # 1: 进行LPR数据的详细分析
    if not load_result:
        print('Part 1: Generating LPR analysis...')
        generate_lpr_analysis(date, x_data_path, target_col, results_path, model=model)
        lpr_analysis_file_name = f'test_results/{date}/LPR分析报告.md'
        with open(lpr_analysis_file_name, 'r', encoding='utf-8')as f:
            analysis_y_data = f.read()
        generate_report(report_part_y_data, chatbot, analysis_y_data, date, 'LPR数据分析研报部分')
        lpr_analysis_file_name = f'test_results/{date}/LPR数据分析研报部分.md'
        print(f"Part 1: LPR analysis generated and saved to {lpr_analysis_file_name}")

    # 2: 进行X数据的详细分析
    if not load_result:
        print('Part 2: Generating X data analysis...')
        x_prompt, role_prompt = get_x_data_prompt(date, data, features_col, target_col, year_col)
        res_xdata = analysis(role_prompt, x_prompt, date, chatbot, 'X数据分析')
        # with open(f'test_results/{date}/X数据分析.md', 'r', encoding='utf-8')as f:
        #    res_xdata = f.read()
        # 生成X数据的研报部分
        res_xdata_report = generate_report(report_part_x_data, chatbot, res_xdata, date, 'X数据分析研报部分')
        x_data_analysis_file_name = f'test_results/{date}/X数据分析研报部分.md'
        # with open(x_data_analysis_file_name, 'r', encoding='utf-8')as f:
        #    res_xdata_report = f.read()
        print(f'Part 2: X data analysis generated and saved to {x_data_analysis_file_name}')

        # Generate figures
        print('Part 2 figures: generating X data analysis figures...')
        plot_factors(date, chatbot, data, target_col,
                     f'-数据分析报告：{res_xdata} \n\n -重要性分析报告：{res_xdata_report}', 'top')  # 绘制最重要的几个X数据
        print('- X historical data image generated.')
        plot_prob(date, chatbot, res_xdata)  # 绘制概率热图
        print('- X prob data image generated.')
        # 绘制降息压力图
        if len(history_info) > 0:
            plot_pressure(history_info, chatbot, data, date, target_col)
            print(f'- Generated LPR pressure plot with {len(history_info)} previous events.')
        print("Part 2 figures: X data analysis figures generated")

    # 3: 进行政治局会议的详细分析
    if not load_result:
        print("Part 3: Generating policy reports analysis...")
        # 货币政策执行报告prompt
        monetary_policy_news_info, monetary_policy_role_prompt = get_monetary_policy_prompt(df, date)
        # 政治局会议prompt
        political_bureau_news_info, political_bureau_role_prompt = get_political_bureau_prompt(df2, date)
        # 货币委员会会议prompt
        monetary_board_meetings_news_info, monetary_board_meetings_role_prompt =\
            get_monetary_board_meetings_prompt(df3, date)
        response_political = analysis(political_bureau_role_prompt, political_bureau_news_info, date, chatbot,
                                      '政治局会议分析')
        file_name = f"test_results/{date}/政治局会议分析.md"
        print(f'- 政治局会议分析 analysis generated and saved to {file_name}')
        response_monetary = analysis(monetary_policy_role_prompt, monetary_policy_news_info, date, chatbot,
                                     '货币政策分析')
        file_name = f"test_results/{date}/货币政策分析.md"
        print(f'- 货币政策分析 analysis generated and saved to {file_name}')
        response_monetary_board_meetings = analysis(monetary_board_meetings_role_prompt,
                                                    monetary_board_meetings_news_info, date, chatbot,
                                                    '货币政策委员会会议分析')
        file_name = f"test_results/{date}/货币政策委员会会议分析.md"
        print(f'- 货币政策委员会会议分析 analysis generated and saved to {file_name}')
        report_text = generate_report_text(response_monetary, response_monetary_board_meetings, response_political)
        generate_report(report_part_compare, chatbot, report_text, date, '报告对比分析研报部分')  # 生成报告数据的研报部分
        file_name = f"test_results/{date}/报告对比分析研报部分.md"
        print(f'- Policy comparison analysis generated and saved to {file_name}')
        print("Part 3: Policy reports analysis generated.")

    # 4: 进行新闻分析
    if not load_result:
        print("Part 4: News analysis...")
        generate_news_analysis(date, x_data_path, target_col, results_path, model=model,
                               no_news_embedding=no_news_embedding)
        with open(f'test_results/{date}/新闻数据分析.md', 'r', encoding='utf-8') as f:
            analysis_news = f.read()
        generate_report(report_part_news, chatbot, analysis_news, date, '新闻数据分析研报部分')
        file_name = f"test_results/{date}/新闻数据分析研报部分.md"
        print(f'Part 4: News analysis generated and saved to {file_name}')

    # Generate other images
    if not load_result:
        print('Generating supplement images...')
        meeting_report = df['text'].values[0]  # choose from df, df1, df2
        generate_report_images(date, x_data_path, target_col, results_path, meeting_report, model=model)
        print('Supplement images generated.')

    # 5: Generate conclusions part
    if not load_result:
        print('Part 5: Generating conclusions...')
        with open(f'test_results/{date}/X数据分析研报部分.md', 'r', encoding='utf-8')as f:
            res_x = f.read()
        with open(f'test_results/{date}/LPR数据分析研报部分.md', 'r', encoding='utf-8')as f:
            res_y = f.read()
        with open(f'test_results/{date}/报告对比分析研报部分.md', 'r', encoding='utf-8')as f:
            res_report = f.read()
        with open(f'test_results/{date}/新闻数据分析研报部分.md', 'r', encoding='utf-8')as f:
            res_news = f.read()
        summary_prompt = generate_summary_prompt(res_y, res_x, res_report, res_news, history_info)
        res = report_part_summary(chatbot, summary_prompt, date, (historical_avg_decline, decline_from_year_start), y_data)
        conclusions_file_name = f'test_results/{date}/结果.md'
        with open(conclusions_file_name, 'w', encoding='utf-8') as file:
            file.write(res)
        print(f"Part 5: Conclusions generated and saved to {conclusions_file_name}.")


def main():
    global prod_env
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run financial report generation for specific dates.")
    parser.add_argument("dates", nargs="*",
                        help="List of dates (YYYY-MM-DD) to generate reports for. Default: 2023-01-01",
                        default=["2023-01-01"])
    parser.add_argument("--use_prod_env", action="store_true",
                        help="Flag to indicate whether to use prod env to retrieve news S3.", default=False)
    args = parser.parse_args()
    prod_env = args.use_prod_env

    # load default models in ['efund', 'gf4', 'deepseek-r1', 'gpt-4o-mini']
    if not use_efund_models:
        chatbot = get_model(model=model, max_tokens=4096*4)
        chatbot_reflection = get_model(model='deepseek-r1', max_tokens=4096*4)
    else:
        # model_name in ['gpt-4o', 'deepseek-chat', 'o1-mini', 'deepseek-r1']
        chatbot = get_model(model='efund', max_tokens=4096*4, model_name='gpt-4o')
        chatbot_reflection = get_model(model='efund', max_tokens=4096*4, model_name='deepseek-r1')
    print('Model loaded successfully')

    if args.dates == 'all':
        args.dates = all_dates

    for date in args.dates:
        try:
            # Validate date format
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            print(f"Invalid date format: {date}. Skipping.")
            continue

        date = last_day_of_current_month(date).strftime('%Y-%m-%d')
        detailed_analysis(chatbot, date)
        df, df2, df3, data, target_col, features_col, year_col = get_data()
        y_data = get_past_12_months_data(data, date, [target_col])[target_col]
        history_info = eval(get_history_info(data, date, target_col))
        if len(history_info) == 0:
            history_info = {'result': None}
        else:
            print(f'Generating feedback with {len(history_info)} historical reports...')
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
        res = reflection_predict_result(chatbot_reflection, text, date, y_data)
        reflection_file_name = f'test_results/{date}/reflection结果.md'
        with open(f'test_results/{date}/reflection结果.md', 'w', encoding='utf-8') as file:
            file.write(res)
        print(f'Conclusions updated and saved to {reflection_file_name}')

        print(f'Creating Word doc date {date}...')
        generate_word_doc(date)
        print(f"Word doc {date} completed.")
        print(f"Processing date: {date} completed.")


# example: python main.py 2024-01-01 2024-02-01 2024-03-01
if __name__ == '__main__':
    main()
