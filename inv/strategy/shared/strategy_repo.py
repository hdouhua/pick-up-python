import datetime
import numpy as np
import pandas as pd
from tools import date_count_in_month, get_trading_dates, datestr2dtdate


def calendar_stgy(data, start_date, end_date, params):
    """
    日历策略
    开盘前调用，返回目标组合权重
    Input:
        data: df(date*, index1, index2, ...), basic data
        start_date, end_date: 'yyyy-mm-dd' or datetime.date
        params: dict, format {'index_id':'hs300', 't1':1, 't2':5}
    Output: 
        target_wgt: df(trade_date*, index1, index2, ...) 目标权重
    """
    if isinstance(start_date) is str:
        start_date = datestr2dtdate(start_date)
    if isinstance(end_date) is str:
        end_date = datestr2dtdate(end_date)
    index_id = params['index_id']
    t1 = params['t1']
    t2 = params['t2']

    start_date0 = start_date - datetime.timedelta(31)
    dates0 = get_trading_dates(start_date0, end_date)
    dates0_rank = date_count_in_month(dates0)
    target_wgt = pd.DataFrame(data=0, index=dates0, columns=data.columns)
    target_wgt[index_id] = [1 if (e >= t1 and e <= t2) else 0 for e in dates0_rank]
    target_wgt = target_wgt.loc[start_date:end_date]
    return target_wgt


def rotation_stgy(data, start_date, end_date, params):
    """
    轮动策略
    开盘前调用，返回目标组合权重
    Input:
        data: df(date*, index1, index2, ...), basic data
        start_date, end_date: 'yyyy-mm-dd' or datetime.date
        params: dict, format {'index_list':['N':20}
    Output: 
        target_wgt: df(trade_date*, index1, index2, ...) 目标权重
    """
    if isinstance(start_date) is str:
        start_date = datestr2dtdate(start_date)
    if isinstance(end_date) is str:
        end_date = datestr2dtdate(end_date)
    n_day = params['N']

    start_date0 = start_date - datetime.timedelta(n_day) * 2
    dates0 = get_trading_dates(start_date0, end_date)
    data0 = data.reindex(index=dates0)
    n_day_ret = data0.shift(1) / data0.shift(n_day + 1) - 1    # 截止昨收的最近N个交易日涨幅
    target_wgt = pd.DataFrame(index=data0.index, columns=data0.columns)
    target_wgt['hs300'] = [1 if e > 0 else 0 if e <= 0 else np.nan for e in n_day_ret['hs300'] - n_day_ret['csi500']]
    target_wgt['csi500'] = 1 - target_wgt['hs300']
    target_wgt = target_wgt.loc[start_date:end_date].fillna(0)

    return target_wgt


def rotation_stgy1(data, start_date, end_date, params):
    """
    轮动策略（可以空仓版）
    开盘前调用，返回目标组合权重
    Input:
        data: df(date*, index1, index2, ...), basic data
        start_date, end_date: 'yyyy-mm-dd' or datetime.date
        params: dict, format {'index_list':['N':20}
    Output: 
        target_wgt: df(trade_date*, index1, index2, ...) 目标权重
    """
    if isinstance(start_date) is str:
        start_date = datestr2dtdate(start_date)
    if isinstance(end_date) is str:
        end_date = datestr2dtdate(end_date)
    n_day = params['N']

    start_date0 = start_date - datetime.timedelta(n_day) * 2
    dates0 = get_trading_dates(start_date0, end_date)
    data0 = data.reindex(index=dates0)
    n_day_ret = data0.shift(1) / data0.shift(n_day + 1) - 1    # 截止昨收的最近N个交易日涨幅
    target_wgt = pd.DataFrame(0, index=data0.index, columns=data0.columns)
    for i in range(1, len(target_wgt)):
        t2 = target_wgt.index[i]
        t1 = target_wgt.index[i - 1]
        if n_day_ret.loc[t1, 'hs300'] >= n_day_ret.loc[t1, 'csi500'] and n_day_ret.loc[t1, 'hs300'] > 0:
            target_wgt.loc[t2, 'hs300'] = 1
        elif n_day_ret.loc[t1, 'hs300'] < n_day_ret.loc[t1, 'csi500'] and n_day_ret.loc[t1, 'csi500'] > 0:
            target_wgt.loc[t2, 'csi500'] = 1
    target_wgt = target_wgt.loc[start_date:end_date].fillna(0)

    return target_wgt
