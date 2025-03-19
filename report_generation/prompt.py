"""
Created on Sat Mar 1 14:30:59 2024

Author: davideliu

E-mail: davide97ls@gmail.com

Goal: Define prompts for data analysis
"""
import pandas as pd


def get_xdata_prompt(result, assist_result, month, year):
    """
    Generates a formatted string containing the explanation of X data for LPR analysis.

    Args:
        result (dict): A dictionary containing the X data values.
        assist_result (dict): A dictionary containing the assistive results (e.g., yoy, mom, zscore).
        month (list): A list of month dates.
        year (list): A list of year dates.

    Returns:
        str: A formatted string explaining the X data.
    """
    x_explain_prompt = f'''
    一、年度数据(时间区间为：{str(year[0])[:10]}~{str(year[-1])[:10]})
        1. 中国GDP实际值（美元计价）：如果中国GDP增长放缓，表明经济活动减弱，可能需要降低LPR以刺激经济活动。
            - 近五年中国GDP实际值（美元计价）数据 ：{result['中国GDP']}
        2. 中国GDP平减指数：GDP平减指数的变化会通过影响货币政策来间接影响LPR。当GDP平减指数下降，显示通缩压力时，央行可能采取宽松政策，促使LPR下降。
            - 近五年中国GDP平减指数数据：{result['中国GDP平减指数']}
        3. 中国公共债务：公共债务水平高可能会限制政府实施财政刺激的能力，可能需要通过货币政策来调节，如降低LPR以减轻债务负担和刺激经济。
            - 近五年中国公共债务数据 ：{result['中国公共债务']}
        4. 中国广义政府净贷款/借款：政府贷款增加可能会增加市场上的货币供应量，如果贷款增加过多，可能会导致通货膨胀，从而可能需要提高LPR以控制货币供应量。
            - 近五年中国政府贷款数据 ：{result['中国政府贷款']}
        5. 美国综合领先指标：如果美国综合领先指标下降，可能会降低全球利率水平，包括中国的LPR也会下降。
            - 近五年美国综合领先指标数据 ：{result['美国综合领先指标']}
        6. 中国综合领先指标：综合领先指标的下降可能反映国内经济的预期，影响货币政策和LPR，可能导致LPR下降。
            - 近五年中国综合领先指标数据 ：{result['中国综合领先指标']}
        7. 中国商业信心：商业信心指数反映了企业对未来经济活动的预期。如果商业信心下降，可能会降低LPR以支持企业投资和经济增长。
            - 近五年中国商业信心数据 ：{result['中国商业信心']}
        8. 泰勒利率：泰勒规则是一种货币政策规则，它建议中央银行根据通货膨胀率和产出缺口来调整名义利率。泰勒利率的下降可能会影响货币政策，进而可能导致LPR下降。
            - 近五年泰勒利率数据 ：{result['泰勒利率']}
    
    二、月度数据(时间区间为：{str(month[0])[:10]}~{str(month[-1])[:10]})
        1. 上证指数：股市的下跌可能反映市场对经济的信心下降，这可能会影响货币政策和LPR，可能导致LPR下降。
             -上证指数数据 ：{result['上证指数']}
             -上证指数数据同比、环比和当前值相较于过去半年均值的偏差是：{assist_result['上证指数_yoy'], assist_result['上证指数_mom'], assist_result['上证指数_zscore']}
        2. 人民币对美元汇率：人民币对美元汇率的贬值可能会增加出口竞争力，但如果贬值过快，可能会引起资本外流，影响流动性，可能导致LPR下降。
             -人民币对美元汇率数据 ：{result['人民币对美元汇率']}
             -人民币对美元汇率数据同比、环比和当前值相较于过去半年均值的偏差是：{assist_result['人民币对美元汇率_yoy'], assist_result['人民币对美元汇率_mom'], assist_result['人民币对美元汇率_zscore']}
        3. 人民币对欧元汇率：同上，人民币对欧元汇率的变化也可能影响出口和资本流动，进而影响LPR。
             -人民币对欧元汇率数据 ：{result['人民币对欧元汇率']}
             -人民币对欧元汇率数据同比、环比和当前值相较于过去半年均值的偏差是：{assist_result['人民币对欧元汇率_yoy'], assist_result['人民币对欧元汇率_mom'], assist_result['人民币对欧元汇率_zscore']}
        4. 中国：狭义货币供应量（M1）环比：M1环比的下降可能反映了市场流动性的减少，这可能会促使央行降低LPR以增加流动性。
             -中国M1环比数据 ：{result['中国：M1月度增长率']}
        5. 中国：广义货币供应量（M2）环比：M2环比的下降可能反映了市场流动性的减少，这可能会促使央行降低LPR以增加流动性。
             -中国M2环比数据 ：{result['中国：M2月度增长率']}
        6. 中国：国债到期收益率：1年：国债收益率的下降可能反映了市场对经济前景的悲观预期，这可能会影响货币政策，导致LPR下降。
             -中国1年期国债收益率数据 ：{result['国债到期收益率:1年']}
             -中国1年期国债收益率数据同比、环比和当前值相较于过去半年均值的偏差是：{assist_result['国债到期收益率:1年_yoy'], assist_result['国债到期收益率:1年_mom'], assist_result['国债到期收益率:1年_zscore']}
        7. 中国：国债到期收益率：3年：国债收益率的下降可能会影响货币政策，导致LPR下降。
             -中国3年期国债收益率数据 ：{result['国债到期收益率:3年']}
             -中国3年期国债收益率数据同比、环比和当前值相较于过去半年均值的偏差是：{assist_result['国债到期收益率:3年_yoy'], assist_result['国债到期收益率:3年_mom'], assist_result['国债到期收益率:3年_zscore']}
        8. 中国：国债到期收益率：10年：国债收益率的下降可能会影响货币政策，导致LPR下降。
             -中国3年期国债收益率数据 ：{result['国债到期收益率:10年']}
             -中国3年期国债收益率数据同比、环比和当前值相较于过去半年均值的偏差是：{assist_result['国债到期收益率:10年_yoy'], assist_result['国债到期收益率:10年_mom'], assist_result['国债到期收益率:10年_zscore']}
        9. 中国银行：净息差：银行净息差的缩小可能会影响银行的利润，进而影响银行的贷款利率政策，可能导致LPR下降。
             -中国银行净息差数据 ：{result['中国银行:净息差']}
             -中国银行净息差数据同比、环比和当前值相较于过去半年均值的偏差是：{assist_result['中国银行:净息差_yoy'], assist_result['中国银行:净息差_mom'], assist_result['中国银行:净息差_zscore']}
        10. 国民总储蓄率：国民总储蓄率的下降可能会减少银行的存款基础，从而可能迫使银行降低LPR以吸引存款。
             -国民总储蓄率数据 ：{result['国民总储蓄率']}
             -国民总储蓄率数据同比、环比和当前值相较于过去半年均值的偏差是：{assist_result['国民总储蓄率_yoy'], assist_result['国民总储蓄率_mom'], assist_result['国民总储蓄率_zscore']}
        11. 未来3个月准备增加“购房”支出的比例：如果这一比例下降，可能表明房地产市场需求减少，这可能会影响房地产市场和LPR，可能导致LPR下降。
             -未来3个月购房支出比例数据 ：{result['未来3个月准备增加"购房"支出的比例']}
             -未来3个月购房支出比例数据同比、环比和当前值相较于过去半年均值的偏差是：{assist_result['未来3个月准备增加"购房"支出的比例_yoy'], assist_result['未来3个月准备增加"购房"支出的比例_mom'], assist_result['未来3个月准备增加"购房"支出的比例_zscore']}
        12. 制造业PMI：制造业PMI的下降可能反映了制造业活动的减少，这可能会影响经济预期和货币政策，可能导致LPR下降。
             -制造业PMI数据 ：{result['制造业PMI']}
             -制造业PMI数据同比、环比和当前值相较于过去半年均值的偏差是：{assist_result['制造业PMI_yoy'], assist_result['制造业PMI_mom'], assist_result['制造业PMI_zscore']}
        13. CPI：消费者价格指数(CPI)的下降可能会直接影响通货膨胀预期和货币政策，可能导致LPR下降。
             -CPI数据 ：{result['CPI']}
             -CPI数据同比、环比和当前值相较于过去半年均值的偏差是：{assist_result['CPI_yoy'], assist_result['CPI_mom'], assist_result['CPI_zscore']}
        14. 房地产开发投资：如果房地产开发投资减少，表明房地产市场可能放缓，这可能促使政策制定者降低LPR以刺激房地产市场和经济增长。
            -房地产开发投资数据 ：{result['房地产开发投资:当月值']}
            -房地产开发投资数据同比、环比和当前值相较于过去半年均值的偏差是：{assist_result['房地产开发投资:当月值_yoy'], assist_result['房地产开发投资:当月值_mom'], assist_result['房地产开发投资:当月值_zscore']}
        15. 规模以上工业增加值：工业增加值的下降可能意味着工业生产放缓，这可能导致经济增速下降。为了提振经济，央行可能会降低LPR以降低企业融资成本，促进工业投资和生产。
            -规模以上工业增加值数据 ：{result['规模以上工业增加值:定基指数']}
            -规模以上工业增加值数据同比、环比和当前值相较于过去半年均值的偏差是：{assist_result['规模以上工业增加值:定基指数_yoy'], assist_result['规模以上工业增加值:定基指数_mom'], assist_result['规模以上工业增加值:定基指数_zscore']}   
        16. 居民人均可支配收入：居民人均可支配收入的减少可能意味着消费能力下降，这可能对经济增长产生负面影响。为了刺激消费和经济增长，央行可能会降低LPR以降低贷款成本，增加居民的可支配收入。
            -居民人均可支配收入数据 ：{result['居民人均可支配收入']}
            -居民人均可支配收入数据同比、环比和当前值相较于过去半年均值的偏差是：{assist_result['居民人均可支配收入_yoy'], assist_result['居民人均可支配收入_mom'], assist_result['居民人均可支配收入_zscore']}
        17. 出口总值：出口总值的下降可能意味着外部需求减少，对经济增长构成压力。为了缓解这种压力，央行可能会降低LPR以降低企业融资成本。
            -出口总值(人民币计价)数据 ：{result['出口总值(人民币计价):当月值']}
            -出口总值(人民币计价)数据同比、环比和当前值相较于过去半年均值的偏差是：{assist_result['出口总值(人民币计价):当月值_yoy'], assist_result['出口总值(人民币计价):当月值_mom'], assist_result['出口总值(人民币计价):当月值_zscore']}
        18. PPI：PPI的下降通常意味着生产成本降低，如果PPI持续下降，可能表明存在通缩风险。为了对抗通缩和刺激经济增长，央行可能会降低LPR以降低企业融资成本。
            -PPI数据 ：{result['ppi']}
            -PPI数据同比、环比和当前值相较于过去半年均值的偏差是：{assist_result['ppi_yoy'], assist_result['ppi_mom'], assist_result['ppi_zscore']}
        19. 利率：中期借贷便利(MLF)：1年：MLF利率的下降可能会直接影响LPR，因为LPR是在MLF利率基础上加点形成的。
            -中国1年期MLF利率数据 ：{result['中期借贷便利(MLF):操作利率:1年']}
            -中国1年期MLF利率数据同比、环比和当前值相较于过去半年均值的偏差是：{assist_result['中期借贷便利(MLF):操作利率:1年_yoy'], assist_result['中期借贷便利(MLF):操作利率:1年_mom'], assist_result['中期借贷便利(MLF):操作利率:1年_zscore']}
        20. 全国城镇调查失业率：失业率的上升可能意味着经济放缓和劳动力市场疲软。为了刺激经济增长和降低失业率，央行可能会降低LPR以降低企业融资成本。
            -全国城镇调查失业率数据 ：{result['中期借贷便利(MLF):操作利率:1年']}
            -全国城镇调查失业率数据同比、环比和当前值相较于过去半年均值的偏差是：{assist_result['中期借贷便利(MLF):操作利率:1年_yoy'], assist_result['中期借贷便利(MLF):操作利率:1年_mom'], assist_result['中期借贷便利(MLF):操作利率:1年_zscore']}
        21. 消费者信心指数：消费者信心指数的下降可能意味着消费者对未来经济前景持悲观态度，这可能会影响消费和经济增长。为了刺激消费和经济增长，央行可能会降低LPR以降低贷款成本。
            -消费者信心指数数据 ：{result['消费者信心指数']}
            -消费者信心指数数据同比、环比和当前值相较于过去半年均值的偏差是：{assist_result['消费者信心指数_yoy'], assist_result['消费者信心指数_mom'], assist_result['消费者信心指数_zscore']}
        22. DR007:DR007的变化通过影响银行资金成本和市场流动性，间接影响LPR的调整：当DR007下行时，银行资金成本降低，LPR下调的可能性增加。
            - DR007数据：{result['DR007']}
            - DR007数据同比、环比和当前值相较于过去半年均值的偏差是：{assist_result['DR007_yoy'], assist_result['DR007_mom'], assist_result['DR007_zscore']}
        23. 7天期逆回购利率:7天期逆回购利率作为中国货币政策的核心工具之一，其调整直接影响银行间市场资金成本（如DR007），进而传导至LPR（贷款市场报价利率）。当逆回购利率下调时，银行融资成本降低，为LPR下调创造空间，从而降低企业和居民的贷款成本。
            - 7天期逆回购利率数据：{result['7天期逆回购利率']}
            - 7天期逆回购利率数据同比、环比和当前值相较于过去半年均值的偏差是：{assist_result['7天期逆回购利率_yoy'], assist_result['7天期逆回购利率_mom'], assist_result['7天期逆回购利率_zscore']}
        24. 7天期逆回购数量:7天期逆回购数量的变化通过影响市场流动性和银行资金成本，间接影响LPR的调整：当逆回购数量增加时，市场流动性充裕，DR007等短期利率下行，为LPR下调创造条件。
            - 7天期逆回购数量数据：{result['7天期逆回购数量']}
            - 7天期逆回购数量数据同比、环比和当前值相较于过去半年均值的偏差是：{assist_result['7天期逆回购数量_yoy'], assist_result['7天期逆回购数量_mom'], assist_result['7天期逆回购数量_zscore']}

    '''
    return x_explain_prompt


def get_x_prompt(date, result, assist_result, target_col):
    """
    Generates a formatted string containing the X data prompt for LPR analysis.

    Args:
        date (str): The date for which the analysis is being performed.
        result (dict): A dictionary containing the X data values.
        assist_result (dict): A dictionary containing the assistive results (e.g., yoy, mom, zscore).
        target_col (str): The target column name.

    Returns:
        str: A formatted string containing the X data prompt.
    """
    reference_date = pd.to_datetime(date)
    year_dates = pd.date_range(end=reference_date, periods=5, freq='Y')
    month_dates = pd.date_range(end=reference_date, periods=12, freq='M')
    x_explain_prompt = get_xdata_prompt(result, assist_result, month_dates, year_dates)
    x_prompt = f'''

    # 下面是X数据，分为年度数据和月度数据，月度数据我还会计算同比、环比和当前值相较于过去半年均值的偏差,我会给出各个因素变化会导致LPR下降的原因和过往数据：
        {x_explain_prompt}

    # 这是过往12个月的Y数据，
        - LPR数据：{result[target_col]}
        - LPR数据的同比、环比和当前值相较于过去半年均值的偏差是：{assist_result[f'{target_col}_yoy'], assist_result[f'{target_col}_mom'], assist_result[f'{target_col}_zscore']}

    '''
    role_prompt = f'''
    角色：你是一个宏观政策分析师，你会从历史数据中提取信息预测LPR下降的概率,请记住输出的时候输出每一个X数据的分析
    
    # 思考方向
    - 如果X数据长期在下降/上升，Y数据没有下降，那么Y数据下降的压力将会增大，会更倾向于下降。
    - 通常LPR一年只会下降1-3次,思考的时候也要考虑当前时间点，当前日期是{date}。
    - 距离上一次改变的时间越长，下降的概率越大。
    - 在思考每个X导致LPR下降的概率时，需要参考过往LPR变化幅度和X变化幅度，根据X变化幅度和与LPR的关系来估计概率。
    - 在思考LPR变化的时候，也要考虑LPR的同比环比和偏差，这些数据会影响LPR的变化。
    - 思考的时候也要参考数据过去的同比环比和偏差作为一个依据。
    - 给出的降息预测概率在50%左右波动，上限为60%，下限为40%，当有很强烈切明确的降息信号时，概率为60%,当没有任何降息信号时，概率为40%，请给出确切的值而不是一个区间，给出的值尽量在50%波动，而不是50%，例如51%,52%,48%等
    - 如果LPR在最近一个月内有变化，那么这次给出的降息概率会大大减小!!!!!
        
    # 任务
        - 请你根据这些历史数据来判断，下一个月LPR是否会下降.
        - 思考的时候一定要参考思考方向，不要单纯依赖数据，这是很重要的一点。
        - 最后需要输出LPR的历史数据并分析LPR数据趋势。
        - 记住每一个X数据都要分析并输出

    # 输出格式如下
    一、年度数据(时间区间为:...)(请记住要分析每一个X数据)
        1. 中国GDP数据对LPR的影响
            - 过往中国GDP数据是：...
            - 过往中国GDP数据的趋势是：...
            - 过往中国GDP变化对LPR的影响是：...
            - 可能导致LPR下降的概率是：...
        2. 中国通货膨胀率对LPR的影响
            - ...
            - ....
        （全部的年度X数据分析） 
        ......
        
    二、月度数据(时间区间为:...)(请记住要分析每一个X数据)
        1、MLF数据对LPR的影响
            - 过往MLF数据是：...
            - 过往MLF的同比、环比和偏差分别是：...
            - 过往MLF数据的趋势是：...
            - 过往MLF变化对LPR的影响是：...
            - 过往MLF同比环比和偏差对其的影响是：...（月度数据分析不要忘记这点）
            - 可能导致LPR下降的概率是：...
        2、中国通货膨胀率对LPR的影响
            - ...
            - ....
        （全部的月度X数据分析）    
            
    三、LPR数据分析
        - LPR数据趋势是....
        - LPR数据的同比环比和偏差是：...,影响是...

    总的分析，给出结果。
    '''

    return x_prompt, role_prompt


class PoliticalAnalysis:
    role_prompt = '''
    角色：经验丰富的政策解读专家，你擅长对比两篇新闻的关键点不同并将其差异总结，当两篇新闻中的点一致时，不会产生什么影响

    ## 总结时需要注意保留和提炼新闻中的这些相关的主题，包括：
     - 对未来经济形式的判断
     - 这篇新闻的政策基调
     - 涉及的宏观政策
     - 涉及的财政政策
     - 涉及的货币政策
     - 涉及的产业政策
     - 对房地产发展的态度
     - 未来的投资趋势
     - 未来的民生消费趋势
     - 涉及民营经济外资外贸的点
     - 涉及产业相关的点
     - 涉及社会民生相关的点
     - 涉及防风险的相关的点

    ## 任务
     - 对两篇新闻进行总结，总结时请注意要求保留和提炼的主题
     - 未直接提及的点可以不总结
     - 如果提及的点记得把两篇中对应的原文也输出出来（输出原文时记得把相关的原文都输出，不要省略）
     - 对两篇新闻在这些关键点进行对比，并总结出差异
     - 从这些差异分析这两篇新闻后的下一个月会降准降息的概率，每一点进行比较时都给出一个差异会导致发布两篇新闻后会降息的概率
     - 请记住核心目标是分析两篇新闻的差异然后预测下一个月是否会降准降息，不是两篇新闻分别给出预测概率
     - 给出的降息预测概率在50%左右波动，上限为60%，下限为40%，当有很强烈切明确的降息信号时，概率为60%,当没有任何降息信号时，概率为40%，请给出确切的值而不是一个区间，给出的值尽量在50%波动，而不是50%，例如51%,52%,48%等
     - 如果观点是比较片面的语言且一致，则降息的概率是一种特殊情况，概率为0
     - 在进行原文差异对比时，也要着重注意原本关键词的顺序或者语气等不同（例如：全面深入和深入全面代表的意义不同，积极和推动意义也不同，这些也可能预示着LPR下降）

    ## 输出格式
    | 类型 | {date1} | {date2} | {date1}原文 | {date2}原文 | 原文差异 | 原文关键字差异 | 降准降息概率 |
    |对未来经济形式的判断 | 第一篇对未来经济形式的判断 | 第二篇对未来经济形式的判断 | 第一篇涉及未来经济形式判断的原文 | 第二篇涉及未来经济形式判断的原文 | 两篇对未来经济判断的差异 | 两篇文中这一关键词不同可能导致的差异 | 这种差异可能导致下一个月降准降息的概率(给出具体的概率值，同时也要考虑关键词对其的影响) |
    | ... | ... | ... | ... | ... | ... |

    '''


class MonetaryBoardMeetingsAnalysis:
    role_prompt = '''
    角色：经验丰富的政策解读专家，你擅长对比两篇新闻的关键点不同并将其差异总结，当两篇新闻中的点一致时，不会产生什么影响

    ## 请你在原文中帮我找到涉及下面点的内容，包括：
     - 对未来经济形式的判断
     - 未来货币政策总体基调
     - 通货膨胀
     - 结构性货币政策工具
     - 金融稳定
     - 利率内容
     - 汇率内容
     - 实体经济
     - 房地产
     - 平台企业
     - 金融开放
    
    ## 任务
     - 在两篇文章中找到涉及的点的原文,只要涉及的原文都要输出，不要省略
     - 未涉及的点可以输出无
     - 对两篇新闻在这些关键点进行对比，并说出文本不同体现出的边际变化
     - 从这些边际变化分析这两篇新闻后的下一个月会降准降息的概率，每一点进行比较时都给出一个边际变化会导致发布两篇新闻后的下一个月会降息的概率
     - 请记住核心目标是分析两篇新闻的差异然后预测下一个月是否会降准降息，不是两篇新闻分别给出预测概率
     - 给出的降息预测概率在50%左右波动，上限为60%，下限为40%，当有很强烈切明确的降息信号时，概率为60%,当没有任何降息信号时，概率为40%，请给出确切的值而不是一个区间，给出的值尽量在50%波动，而不是50%，例如51%,52%,48%等
     - 如果观点是比较片面的语言且一致，则降息的概率是一种特殊情况，概率为0
     - 在进行原文差异对比时，也要着重注意原本关键词的顺序或者语气等不同（例如：全面深入和深入全面代表的意义不同，积极和推动意义也不同，这些也可能预示着LPR下降）

    
    ## 输出格式
    | 类型 | {date1}原文 | {date2}原文 | 边际变化 | 原文关键词差异 | 降准降息概率 |
    |对未来经济形式的判断 | 第一篇涉及未来经济形式判断的原文 | 第二篇涉及未来经济形式判断的原文 |两篇涉及未来经济形式判断的原文进行对比的边际变化 | 两篇文中这一关键词不同可能导致的差异 | 这种差异可能导致下一个月降准降息的概率(给出具体的概率值，同时也要考虑关键词对其的影响) |
    | ... | ... | ... | ... | ... | ... | ... |
    
    '''


class MonetaryAnalysis:
    # 货币政策执行总结prompt
    role_prompt = '''
    角色：经验丰富的政策解读专家，你擅长对比两篇新闻的关键点不同并将其差异总结，当两篇新闻中的点一致时，不会产生什么影响

    ## 总结时需要注意保留和提炼新闻中的这些相关的主题，包括：
     - 分析国内经济展望
     - 国外经济形势分析
     - 对中国来说海外值得关注的问题
     - 中国未来的工作总基调与要求
     - 未来政策展望，包括：
         1、对未来货币政策的展望
         2、为未来货币政策工具运用的展望
         3、对利率的展望
         4、对汇率的展望
         5、对物价水平的展望
         6、对金融风险防范的展望
         7、对房地产的展望


    ## 任务
     - 对两篇新闻进行总结，总结时请注意要求保留和提炼的主题
     - 未直接提及的点可以不总结
     - 如果提及的点记得把两篇中对应的原文也输出出来（输出原文时记得把相关的原文都输出，不要省略）
     - 对两篇新闻在这些关键点进行对比，并总结出差异
     - 从这些差异分析这两篇新闻后的下一个月会降准降息的概率，每一点进行比较时都给出一个差异会导致发布两篇新闻后会降息的概率
     - 请记住核心目标是分析两篇新闻的差异然后预测下一个月是否会降准降息，不是两篇新闻分别给出预测概率
     - 给出的降息预测概率在50%左右波动，上限为60%，下限为40%，当有很强烈切明确的降息信号时，概率为60%,当没有任何降息信号时，概率为40%，请给出确切的值而不是一个区间，给出的值尽量在50%波动，而不是50%，例如51%,52%,48%等
     - 如果观点是比较片面的语言且一致，则降息的概率是一种特殊情况，概率为0
     - 在进行原文差异对比时，也要着重注意原本关键词的顺序或者语气等不同（例如：全面深入和深入全面代表的意义不同，积极和推动意义也不同，这些也可能预示着LPR下降）


    ## 输出格式
    | 类型 | {date1} | {date2} | {date1}原文 | {date2}原文 | 原文差异 | 原文关键词差异 | 降准降息概率 |
    |分析国内经济展望 | 第一篇分析国内经济展望 | 第二篇分析国内经济展望 | 第一篇涉及分析国内经济展望的原文 | 第二篇涉及分析国内经济展望的原文 |两篇对分析国内经济展望的差异 | 两篇文中这一关键词不同可能导致的差异 | 这种差异可能导致下一个月降准降息的概率(给出具体的概率值，同时也要考虑关键词对其的影响) |
    | ... | ... | ... | ... | ... | ... |
    '''


def generate_report_text(response_monetary, response_monetary_board_meetings, response_political):
    """
    Generates a comprehensive report text by combining responses from different analyses.

    This function takes the analysis results from monetary policy, monetary board meetings, and political meetings,
    and formats them into a single report text.

    Args:
        response_monetary (str): The analysis result from monetary policy.
        response_monetary_board_meetings (str): The analysis result from monetary board meetings.
        response_political (str): The analysis result from political meetings.

    Returns:
        str: A formatted report text combining all the analysis results.
    """
    report_text = f'''
货币政策对比报告如下：
{response_monetary}


货币政策委员会会议如下：
{response_monetary_board_meetings}


政治局会议如下：
{response_political}

# '''
    return report_text


def generate_summary_prompt(res_y, res_xdata, res_report, res_news, history_info):
    """
    Generates a summary prompt by combining various analysis results and historical information.

    This function takes the results from LPR data analysis, X data analysis, report comparison, news summary,
    and historical prediction results, and formats them into a summary prompt.

    Args:
        res_y (str): The result from LPR data analysis.
        res_xdata (str): The result from X data analysis.
        res_report (str): The result from report comparison analysis.
        res_news (str): The result from news summary analysis.
        history_info (str): The historical prediction results.

    Returns:
        str: A formatted summary prompt combining all the analysis results and historical information.
    """
    summary_prompt = f'''
# 下面是历史LPR数据分析:
    - {res_y}

# 下面是相关数据分析:
    - {res_xdata}

# 下面是报告总结对比:
    - {res_report}

# 下面是新闻总结:
    - {res_news}
-
# 下面是历史预测结果:
    - {history_info}
'''
    return summary_prompt
