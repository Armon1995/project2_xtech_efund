"""
Created on Sat Mar 1 14:30:59 2024

Author: davideliu

E-mail: davide97ls@gmail.com

Goal: Prompts for report generation
"""
from main_utils import num_tokens_from_string, find_last_unchanged_date
import os
import json
from models import model_invoke


def report_part_y_data(model, text):
    """
    Converts the analysis of LPR historical data into a research report.

    This function takes the analysis text of LPR historical data and converts it into a structured research report.
    It uses a predefined role prompt to guide the chatbot in generating the report.

    Args:
        model: The chatbot model used for generating the report.
        text (str): The analysis text of LPR historical data.

    Returns:
        str: The generated research report.

    Raises:
        Exception: If the chatbot fails to generate a valid response.
    """
    role_prompt = '''
    角色，你是一位宏观政策分析师，会分析历史的LPR数据来进行解读和预测

    # 任务
        - 阅读下面的数据分析过程，然后将其改写转化为一篇研报
        - 输出结果要遵守格式，#代表一级标题，## 代表二级标题以此类推

    # 要求
        - 语言准确无误，不能有错别字
        - 以客观的角度分析，不要出现‘我’这种主观的语气词
        - 多使用专业术语来描述，让结果看起来很专业
        - 分析每一部分的时候都要保持这一部分在150字以上
    
    # 输出格式例子如下：
        # 一、LPR概述及其重要性
            介绍什么是LPR，LPR的改变会影响什么东西，LPR的重要性...
        
        # 二、LPR历史数据解读
            LPR历史数据的时间区间是:...
            LPR历史数据是:.....
            通过统计摘要进行分析，LPR历史数据的趋势，统计量
            LPR历史数据的趋势，统计量，可能会导致什么影响，LPR可能会受到什么因素的影响
        
        # 三、LPR趋势分析
            ...
        
        # 四、经济洞察与政策影响
            通过历史LPR可以洞察出什么，使用宏观经济角度来解说...
    '''
    res = model_invoke(role_prompt, text, chatbot=model)
    return res


def report_part_x_data(model, text):
    """
    Converts the analysis of economic factors affecting LPR into a research report.

    This function takes the analysis text of economic factors and converts it into a structured research report.
    It uses a predefined role prompt to guide the chatbot in generating the report.

    Args:
        model: The chatbot model used for generating the report.
        text (str): The analysis text of economic factors.

    Returns:
        str: The generated research report.

    Raises:
        Exception: If the chatbot fails to generate a valid response.
    """
    role_prompt = '''
    角色，你是一位宏观政策分析师，精通LPR的预测，你需要分析下面的数据分析过程，然后将其改写转化为一篇研报，请参考任务和要求

    # 任务
        - 阅读下面的数据分析过程，然后将其改写转化为一篇研报
        - 我会给出月度数据和年度数据的分析过程，解读主要影响因素时，在年度数据选概率最高的1条，月度数据选概率最高的的4条，相同概率下选择趋势比较明显的！！！！！
        - 输出结果要遵守格式，#代表一级标题，## 代表二级标题以此类推
        - 以客观的角度分析，不要出现‘我’这种主观的语气词
    
    # 要求
        - 语言准确无误，不能有错别字
        - 多使用专业术语来描述，让结果看起来很专业
        - 记得任务要求里面对数据详细分析时要在年度数据选择一条下降概率最高的，月度数据选择四条下降概率最高的
        - 分析每一部分的时候都要保持这一部分在三百字以上
        - 格式必须标准，不要随便换行乱输出

    # 输出格式例子如下：
    
        # 一、相关经济因素对LPR的影响
            （说明相关的这些经济因素分析对预测LPR的重要性和必要性。首先介绍有哪些相关因素，之后说明这些因素对预测LPR的重要性和必要性）
            ......

        # 二、主要因素分析
            （解读主要影响因素(参照给你的任务第二条，在年度数据选出一个，月度数据选出四个，一共要选出五个数据)）
            ## 1. 中国GDP实际值（美元计价）数据对LPR的影响
            - 中国GDP实际值（美元计价）是什么：
            - 中国GDP实际值（美元计价）对LPR的影响：
            - 过往中国GDP实际值（美元计价）数据的趋势是：整体呈现上升趋势，但最近两年增速放缓。
            - 过往中国GDP实际值（美元计价）变化对LPR的影响是：GDP增长放缓通常会促使央行降低LPR以刺激经济。
            - 可能导致LPR下降的概率是：中等偏高，约60%。这个概率是怎么来的：....
            
            ..........
            
            ## 5. 中国M1月度增长率对LPR的影响
            - 中国M1是什么：
            - 中国M1对LPR的影响：
            - 过往M1的同比、环比和偏差分别是：(-0.6708, -1.1697, 0.482)
            - 过往M1的趋势是：波动较大，近期有所下降。
            - 过往M1的同比、环比和偏差对LPR的影响是：.....（月度数据分析不要忘记这点）
            - 过往M1变化对LPR的影响是：M1增长率下降可能促使央行降低LPR以增加流动性。
            - 可能导致LPR下降的概率是：中等偏高，约65%。这个概率是怎么来的：....
            
            针对上面五个因素总的分析和总结。....

        # 三、其余因素分析
            （分析除了主要影响因素外的其他因素，分析的时候记得要数值的说明，历史趋势是什么，通过这个趋势的变化体现了什么）
            说说除了第二部分分析的最主要的因素外，其他年度和月度因素对LPR造成的影响，这里要举例具体数值来说明，
            例如：M2数据偏差是多少，预示着什么，每一个例子都要有数据支撑，
            M2过往月度数据是什么样的，对LPR变化的影响等,每次说明都要列举历史数据

        # 四、总结
            （总结分析结果，并提出自己对未来LPR变化的预测，说出哪些原因导致的,并说一下未来LPR发展的展望）
        

    '''
    res = model_invoke(role_prompt, text, chatbot=model)
    return res


def report_part_compare(model, text):
    """
    Converts the comparison analysis of policy reports into a research report.

    This function takes the comparison analysis text of policy reports and converts it into a structured research
     report.
    It uses a predefined role prompt to guide the chatbot in generating the report.

    Args:
        model: The chatbot model used for generating the report.
        text (str): The comparison analysis text of policy reports.

    Returns:
        str: The generated research report.
    """
    role_prompt = '''
    角色:你是一个宏观政策分析师，擅长对一些报告的对比总结进行二次分析

    # 任务
        - 阅读三篇不同的报告对比，然后写一个整体的研报
        - 在三篇对比报告中选出对LPR下降预测最重要的一篇，重点分析，其余两篇只做大概总结
        - 输出结果要遵守格式，#代表一级标题，## 代表二级标题以此类推
        - 以客观的角度分析，不要出现‘我’这种主观的语气词

    # 要求
        - 语言准确无误，不能有错别字
        - 多使用专业术语来描述，让结果看起来很专业
        - 保持报告原有的格式
        - 分析每一部分的时候都要保持这一部分在三百字以上

    # 输出格式例子如下：
        # 一、宏观政策对LPR的影响
            （通过三篇报告说明，说明这三篇报告分别对预测LPR的重要性）
            ## 1、首先说一下引入报告文本数据的必要性和重要性，弥补结构数据的缺点
            ## 2、介绍三篇报告分别是什么，对预测LPR下降有什么作用（这里需要重点说一下，多说一点）

        # 二、重点报告分析    
            ## 1、选出对LPR下降预测最重要的一篇保持原本格式输出，之后进行重点分析
                政治局报告：(这里直接用原本的对比报告，不要更改格式)
                | 类型 | date1 | date2 | date1原文 | date2原文 | 原文差异 | 原文关键字差异 | 降准降息概率 |
                |对未来经济形式的判断 | 第一篇对未来经济形式的判断 | 第二篇对未来经济形式的判断 | 第一篇涉及未来经济形式判断的原文 | 第二篇涉及未来经济形式判断的原文 |两篇对未来经济判断的差异 | 两篇文中这一关键词不同可能导致的差异 |这种差异可能导致下一个月降准降息的概率(给出具体的概率值) |
                | ... | ... | ... | ... | ... | ... |
                ......
                报告总结....

        # 三、其余报告分析
            (说明其他两篇报告分析对预测LPR的关联和重要性)
            xx报告的对比分析对预测LPR下降的指示作用（整体因素分析一下）
            xx报告的对比分析对预测LPR下降的指示作用（整体因素分析一下）
            总结两篇报告透露LPR下降的信息
        
        # 四、总结
            （分析结果，输出本章小结，说出哪些原因会导致LPR下降,并说一下未来LPR发展的展望和报告透露出来的未来经济信息）
'''
    res = model_invoke(role_prompt, text, chatbot=model)
    return res


def report_part_news(model, text):
    """
    Converts the analysis of news data into a research report.

    This function takes the analysis text of news data and converts it into a structured research report.
    It uses a predefined role prompt to guide the chatbot in generating the report.

    Args:
        model: The chatbot model used for generating the report.
        text (str): The analysis text of news data.

    Returns:
        str: The generated research report.
    """
    role_prompt = '''
    角色:你是一个宏观政策分析师，擅长通过新闻分析LPR是否会下降

    # 任务
        - 阅读通过新闻分析LPR是否会下降的报告，然后写一个整体的研报
        - 输出结果要遵守格式，#代表一级标题，## 代表二级标题以此类推
        - 以客观的角度分析，不要出现‘我’这种主观的语气词

    # 要求
        - 语言准确无误，不能有错别字
        - 多使用专业术语来描述，让结果看起来很专业
        - 分析每一部分的时候都要保持这一部分在三百字以上
        - 给出的降息预测概率在50%左右波动，上限为60%，下限为40%，当有很强烈切明确的降息信号时，概率为60%,当没有任何降息信号时，概率为40%，请给出确切的值而不是一个区间，给出的值尽量在50%波动，而不是50%

    # 输出格式例子如下：
        # 一、新闻重要性
            讨论加入新闻数据对预测未来LPR下降的重要性，弥补了结构化数据和报告数据的不足等
        
        # 二、新闻总结
            逐一输出每个新闻的新闻总结（完全输出不要删减）
            新闻一分析:......(原文链接)
            新闻二分析:......(原文链接)
            .......
        
        # 三、总结分析结果，输出本章小结，说出哪些原因会导致LPR下降，并说一下未来LPR发展的展望和新闻透露出来的未来经济信息
        
        '''
    res = model_invoke(role_prompt, text, chatbot=model)
    return res


def report_part_summary(model, text, date, arg, y):
    """
    Generates a summary report based on the analysis of various parts.

    This function takes the analysis text and generates a summary report.
    It uses a predefined role prompt to guide the chatbot in generating the report.

    Args:
        model: The chatbot model used for generating the report.
        text (str): The analysis text.
        date (str): The date for which the summary is being generated.
        arg (tuple): A tuple containing historical average decline and decline from year start.
        y (list): A list of the most recent 12 LPR data points.

    Returns:
        str: The generated summary report.
    """
    reference_date = date
    historical_avg_decline, decline_from_year_start = arg

    role_prompt = f'''
    角色:你是一个宏观政策分析师，擅长对多维度的信息进行解读，然后总结预测LPR下降

    # 要求
        - 语言准确无误，不能有错别字
        - 多使用专业术语来描述，让结果看起来很专业
        - 输出结果要遵守格式，#代表一级标题，## 代表二级标题以此类推
        - 以客观的角度分析，不要出现‘我’这种主观的语气词

    # 最近12个月的LPR数据为：{y},从左到右分别是最近12个月的LPR数据，最右边是最新的数据，如果LPR在最近一个月有变化，这次给出的降息概率一定会小于上一个月预测的降息概率。

    # 注意  
        1. 参考历史预测结果：  
            - 如果历史预测有降息信号累积，但LPR未变化，则本次降息概率会增加，需将累积的降息因素纳入考虑。  
            - 如果历史预测降息，且LPR确实下降，则无需考虑累积降息信号，但需评估降息幅度是否达到历史平均（{historical_avg_decline}）。若未达到，本次仍可能有降息概率。截至目前，降息幅度为{decline_from_year_start}。  
        2. 降息概率与时间关系：  
            - LPR一年通常下降1-3次，距离上次调整的时间越长，降息概率越大。年初降息概率应参考历史数据并设定为极低值。当前预测日期为{date}。  
        3. LPR变化的影响：  
            - 如果最近一个月LPR发生变化，累积的降息信号已兑现，本次降息概率会显著下降，并一定小于上个月的预测值。  
        4. 降息幅度接近性：  
            - 若今年降息幅度已接近或达到历史平均值，下个月降息概率会大幅降低。  
        5. 因素重要性排序：  
            - 综合考虑因素时，优先级为：报告 > 历史累积降息信号 > 其他因素 > 新闻 > LPR趋势。  
        6. 每一部分给出的下降概率都是在50%左右波动，当有很强烈切明确的降息信号时，概率为60%,当没有任何降息信号时，概率为40%，现在输出综合概率的时候，如果有很多强信号，那么概率会大于60%，同理很多弱信号时概率会小于40%，每次变动以1%为单位。

    # 任务
        - 通过给出的历史LPR分析部分，判断未来是否会降准降息，如果会的话，请说出是哪一类型的对比给出的提示
        - 通过给出的历史其他因素分析部分，判断未来是否会降准降息，如果会的话，请说出是哪些数据变化给出的提示
        - 通过给出的报告对比分析部分，判断未来时候是否会降准降息，如果会的话，请说出是哪些因素给出的提示
        - 通过给出的新闻总结部分，判断未来是否会降准降息，如果会的话，请说出是哪些新闻导致的
        - 通过历史的预测结果参与判断，如果历史预测结果内有降息信号没有兑现，那么本期预测时将会考虑上一期的降息信号积累，降息概率会增大
        - 输出未来LPR是否会降息的分析，输出结果的时候要注意输出格式，每一条理由都要在给的报告总结或者数据总结当中找，不能给出总的概括
        - 输出理由时要注意，预测LPR下降的概率是多少，如果会降息，是哪些关键点导致的，给出这些关键因素的贡献值，贡献值在0-1之间，总和为1
        - 输出下一个月如果降息，降息幅度是多少，可以参考历史降息幅度和当年降息幅度
        - 输出结果要遵守格式，#代表一级标题，## 代表二级标题以此类推

    # 输出结果格式如下，请遵守格式
        # 结果
            在{reference_date}预测下一个月LPR下降的概率是多少，降息幅度是多少bp(单位是bp)，是哪些关键点导致的，给出这些关键因素的重要性，重要性在0-1之间，总和为1。

        # 理由
            ## 一、历史LPR趋势中透露出的信号
                1、通过对LPR历史数据分析，出现...现象，有可能会降息
                2、通过对LPR历史数据分析，出现...现象，有可能不会降息
                3、....

            ## 二、相关数据中透露出的信号
                1、通过对中国GDP的分析，出现...现象，有可能会降息
                2、通过对中国PMI分析，出现...现象，有可能不会降息
                3、....
            
            ## 三、报告总结中透露出的信号
                1、通过利率内容分析，出现...现象，有可能会降息
                2、通过汇率内容分析，出现...现象，有可能不会降息
                3、...

            ## 四、新闻总结中透露出的信号
                1、根据xx新闻可以看出，出现...现象，有可能不会降息
                2、根据xx新闻可以看出，出现...现象，有可能会降息
                3、...

            ## 五、历史预测结果中透露出的没有兑现的降息信号(如果LPR在最近一个月内有变化，那么这些信号已经兑现，整体给出的概率将会下降很多)
                1、根据历史预测结果中的房地产展望分析可以看出，会出现降息现象，上期没有兑现，这一期降息概率将会增大
                2、...
'''
    res = model_invoke(role_prompt, text, chatbot=model)
    return res


def introduction(model):
    """
    Generates an introduction for the LPR analysis report.

    This function generates an introduction for the LPR analysis report.
    It uses a predefined role prompt to guide the chatbot in generating the introduction.

    Args:
        model: The chatbot model used for generating the introduction.

    Returns:
        str: The generated introduction.
    """
    text = '''
    # 任务：说一下预测LPR是什么，研究LPR的下降有什么意义，常规的人工研究方法是什么样的，常规方法的局限性，写下面的引言部分，每一小点都要在500字以上，格式为
    
    # 参考资料
        1、贷款市场报价利率（Loan Prime Rate，简称LPR）是指由各报价行根据其对最优质客户执行的贷款利率，按照公开市场操作利率加点形成的方式报价，由中国人民银行授权全国银行间同业拆借中心计算得出并发布的利率。各银行实际发放的贷款利率可根据借款人的信用情况，考虑抵押、期限、利率浮动方式和类型等要素，在贷款市场报价利率基础上加减点确定。
        2、LPR报价行现由18家商业银行组成，报价行应于每月20日（遇节假日顺延）9时前，按公开市场操作利率（主要指中期借贷便利利率）加点形成的方式，向全国银行间同业拆借中心报价。全国银行间同业拆借中心按去掉最高和最低报价后算术平均的方式计算得出贷款市场报价利率。目前，LPR包括1年期和5年期以上两个期限品种。

    # 要求：
        - 输出的时候要专业一点，不要首先其次然后，请以专业的ai学者的角度来写，语言学术化一点
        - 输出结果要遵守格式，#代表一级标题，## 代表二级标题以此类推
        - 以客观的角度分析，不要出现‘我’这种主观的语气词
        - 输出的时候对LPR介绍不要太宏大叙事和泛泛而谈，要根据参考资料写一些很具体的介绍
        - 不要输出伪造的数据，只是介绍不要捏造数据，要遵守实事求是
        
    # 输出格式：
        # 一、引言
        ## 1、研究背景
        ## 2、人工分析师的局限性
        ## 3、人工智能分析的优势
    '''
    res = model_invoke('', text, chatbot=model, temperature=0.7)
    return res


def get_history_info(data, date, target_col):
    """
    Retrieves historical information for LPR analysis.

    This function retrieves historical information for LPR analysis by finding the last unchanged date
    and collecting results from previous analyses stored in files.

    Args:
        data (pd.DataFrame): The DataFrame containing historical data.
        date (str): The date for which the historical information is being retrieved.
        target_col (str): The column name for the target variable in the DataFrame.

    Returns:
        str: A JSON string containing historical information.
    """
    time_series = find_last_unchanged_date(data, target_col, date)
    results = []  

    for date_str in time_series:
        file_path = f'test_results/{date_str}/结果.md'
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                results.append({
                    "date": date_str,
                    "result": content
                })
        else:
            # print(f"文件 {file_path} 不存在。")
            pass

    return json.dumps(results, ensure_ascii=False, indent=4)
