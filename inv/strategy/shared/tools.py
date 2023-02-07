import datetime
from enum import Enum
import numpy as np
import pandas as pd
from matplotlib import font_manager, pyplot as plt


class SymbolCategry(Enum):
    """
    Default is None
    """
    Default = 0
    Divident = 1
    SmallCap = 2
    LargeCap = 3
    Specialization = 4


def get_symbols_by_categry(categry):
    symbols = None
    if categry == SymbolCategry.SmallCap:
        symbols = [
            ('中证500', '000905'),
            ('中证500ETF', '510500'),
            ('基金 - 富国500', '161017'),
            ('基金 - 南方500', '160119'),
            ('500质量', '930939'),
            ('鹏扬中证500质量成长ETF', '560500'),
            ('沪港深500', '30455'),
            ('500SNLV', '930782'),
            ('基金 - 景顺长城中证500行业中性低波', '003318'),
            ('500成长估值', '930938'),
            ('创成长', '399296'),
            ('华夏创成长ETF', '159967'),
            ('创业板指', '399006'),
            ('深创100', '399088'),
            ('中小板指', '399005'),
        ]
    elif categry == SymbolCategry.LargeCap:
        symbols = [
            ('沪深300', '000300'),
            ('300价值', '000919'),
            ('沪港深300', '931395'),
            ('300质量', '931155'),
            ('300成长', '000918'),
            ('深证300', '399007'),
            ('300消费', '000912'),
            ('消费红利', '30094'),
            ('上证消费', '000036'),
            ('中证消费', '000932'),
            ('消费龙头', '931068'),
        ]
    elif categry == SymbolCategry.Divident:
        symbols = [
            ('红利低波', '30269'),
            ('红利LV', '512890'),
            ('红利低波100', '930955'),
            ('红利低波100ETF', '515100'),
            ('红利指数', '000015'),
            ('华泰柏瑞上证红利ETF', '510880'),
            ('300 红利', '000821'),
            ('建信沪深300红利ETF', '512530'),
            ('国企红利', '000824'),
            ('国企红利LOF', '501059'),
            ('中证红利', '000922'),
            ('招商中证红利ETF', '515080'),
            ('易方达中证红利ETF', '515180'),
            ('红利潜力', '30089'),
            ('基金 - 红利潜力', '007671'),
            ('消费红利', '30094'),
            ('基金 - 泰达消费红利指数A', '008928'),
            ('上证消费', '000036'),
            ('中证消费', '000932'),
            ('深证红利', '399324'),
            ('深证红利ETF', '159905'),
        ]
    elif categry == SymbolCategry.Specialization:
        symbols = [
            ('医药100', '000978'),
            ('基金 - 医药100', '000059'),
            ('300医药ETF', '512010'),
            ('广发中证全指医药卫生ETF', '159938'),
            ('中证生科', '930743'),
            ('中证白酒', '399997'),
            ('基金 - 招商中证白酒指数A', '161725'),
        ]
    return symbols


def set_plot_font(font_file):
    # add font file
    font_manager.fontManager.addfont(font_file)

    # set font
    # plt.rc('font', family='Microsoft YaHei')
    # or
    plt.rcParams['font.family'] = 'Microsoft YaHei'


def get_drawdown(p):
    """
    计算净值回撤
    """
    # T = len(p)
    # hmax = [p[0]]
    # for t in range(1, T):
    #     hmax.append(np.nanmax([p[t], hmax[t - 1]]))
    # dd = [p[t] / hmax[t] - 1 for t in range(T)]

    # yet, another way
    hmax = p.cummax()
    dd = p / hmax - 1

    return dd


def cal_period_perf_indicator(adjnav):
    """
    计算区间业绩指标: 输入必须是日频净值
    """

    if type(adjnav) == pd.DataFrame:
        res = pd.DataFrame(index=adjnav.columns, columns=['AnnRet', 'AnnVol', 'SR', 'MaxDD', 'Calmar'])
        for col in adjnav:
            res.loc[col] = cal_period_perf_indicator(adjnav[col])

        return res

    ret = adjnav.pct_change()

    # annret = np.nanmean(ret) * 242    # 单利
    annret = (adjnav[-1] / adjnav[0])**(242 / len(adjnav)) - 1    # 复利
    # annret = (adjnav[-1] / 1)**(242 / len(adjnav)) - 1

    annvol = np.nanstd(ret) * np.sqrt(242)

    sr = annret / annvol
    dd = get_drawdown(adjnav)
    mdd = np.nanmin(dd)
    calmar = annret / -mdd

    return [annret, annvol, sr, mdd, calmar]


def datestr2dtdate(datestr, format='%Y-%m-%d'):
    """
    日期格式转换：'yyyy-mm-dd' 转为 datetime.date
    """
    return datetime.datetime.strptime(datestr, format).date()


def date_count_in_month(dates):
    """
    计算日期序列中每个日期在所在月中的序数
    """
    cur_count = 1
    counts = [cur_count]
    for i in range(1, len(dates)):
        if dates[i].month == dates[i - 1].month:
            cur_count = cur_count + 1
        else:
            cur_count = 1
        counts.append(cur_count)
    return counts


def get_trading_dates(start_date=None, end_date=None):
    """
    读取指定起止日期之间的交易日序列
    """
    dates = pd.read_csv('../res/trading_date.csv')['trade_date'].to_list()
    # dates = [datestr2dtdate(e, '%Y/%m/%d') for e in dates]
    dates = [datestr2dtdate(e) for e in dates]
    if start_date is not None:
        dates = [e for e in dates if e >= start_date]
    if end_date is not None:
        dates = [e for e in dates if e <= end_date]
    return dates


def get_hist_data(data_file, index_ids=None, end_date=None):
    """
    读取指数历史数据到指定截止日
    Input:
        data_file: string
        index_ids: list of str, 指数代码列表, like ['hs300', 'csi500']
        end_date: datetime.date, 截止日期
    Output:
        data: df(date*, index1, index2, ...), 多个指数的历史收盘价序列
    """
    # 从csv文件获取指数价格数据
    data = pd.read_csv(data_file).set_index('datetime')
    data.index = [datestr2dtdate(e) for e in data.index]
    print('基础数据起止日期：%s，%s' % (data.index[0], data.index[-1]))
    if index_ids is not None:
        data = data.loc[:, index_ids]
    if end_date is not None:
        data = data.loc[:end_date, :]
    return data
