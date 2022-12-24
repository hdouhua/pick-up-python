import datetime
import numpy as np
import pandas as pd


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
    dates = [datestr2dtdate(e, '%Y/%m/%d') for e in dates]
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
