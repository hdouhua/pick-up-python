import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def get_drawdown(p):
    """
    计算净值回撤
    """
    T = len(p)
    hmax = [p[0]]
    for t in range(1, T):
        hmax.append(np.nanmax([p[t], hmax[t - 1]]))
    dd = [p[t] / hmax[t] - 1 for t in range(T)]

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

    annvol = np.nanstd(ret) * np.sqrt(242)

    sr = annret / annvol
    dd = get_drawdown(adjnav)
    mdd = np.nanmin(dd)
    calmar = annret / -mdd

    return [annret, annvol, sr, mdd, calmar]


def datestr2dtdate(datestr):
    """
    日期格式转换：'yyyy-mm-dd' 转为 datetime.date
    """
    return datetime.datetime.strptime(datestr, '%Y-%m-%d').date()


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
