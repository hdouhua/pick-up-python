import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from enum import Enum

import ipywidgets as widgets
from ipywidgets import DatePicker, Select, Layout, Box, VBox

from tools import get_drawdown, cal_period_perf_indicator, datestr2dtdate


def get_widgets():
    datePickers = [
        DatePicker(value=datetime.date(2020, 1, 1),
                   description='Start:',
                   disabled=False,
                   layout=Layout(flex='1 1 auto', width='auto')),
        DatePicker(value=datetime.date(2022, 12, 16),
                   description='End:',
                   disabled=False,
                   layout=Layout(flex='1 1 auto', width='auto')),
        widgets.IntSlider(value=21,
                          min=5,
                          max=100,
                          step=1,
                          description='N days:',
                          disabled=False,
                          continuous_update=False,
                          orientation='horizontal',
                          readout=True,
                          readout_format='d'),
    ]
    symbols = [
        Select(options=[
            ('中证500', '000905'),
            ('500质量', '930939'),
            ('沪港深500', '30455'),
            ('500SNLV', '930782'),
            ('500成长估值', '930938'),
            ('创成长', '930938'),
            ('创业板指', '399006'),
            ('中小板指', '399005'),
        ],
               value='000905',
               rows=10,
               description='Small-Cap:',
               disabled=False),
        Select(options=[
            ('沪深300', '000300'),
            ('300价值', '000919'),
            ('沪港深300', '931395'),
            ('300质量', '931155'),
            ('300成长', '000918'),
            ('深证300', '399007'),
            ('300消费', '000912'),
        ],
               value='000300',
               rows=10,
               description='Large-Cap:',
               disabled=False),
    ]

    box1 = Box(children=datePickers)
    box2 = Box(children=symbols)

    return (VBox(children=(box1, box2)), datePickers, symbols)


def _get_T_dates():
    # T 值的区间
    return [
        datetime.date(2010, 10, 11),
        datetime.date(2012, 8, 31),
        datetime.date(2015, 4, 7),
        datetime.date(2016, 1, 14),
        datetime.date(2017, 10, 30),
        datetime.date(2019, 1, 2),
        datetime.date(2021, 2, 9),
        datetime.date(2022, 3, 14),
    ]


def _read_csv(csv_file, cols=None):
    df = pd.read_csv(csv_file).set_index('datetime')
    df.index = [datestr2dtdate(e) for e in df.index]
    df.drop(['acc_close', 'pe', 'pe_pct80', 'pe_pct20', 'pe_pct50'], axis=1, inplace=True)
    if cols:
        df.rename(columns=cols, inplace=True)

    # print(df.head(50))
    return df


class RotationType(Enum):
    """
    1 - 满仓
    2- 可空仓
    3 - 增强
    """
    Full = 1
    Nullable = 2
    Enhanced = 3


def load_data(small_index, large_index):
    small_price = _read_csv(f'../res/small/{small_index}.csv', cols={
        'close': 'small',
        'pe_pct': 'small_pe_pct',
    })
    large_price = _read_csv(f'../res/large/{large_index}.csv', cols={
        'close': 'large',
        'pe_pct': 'large_pe_pct',
    })

    return pd.merge(large_price, small_price, left_index=True, right_index=True)


def run_strategy(index_price, rotation_type, params):
    N = params['N']
    start_date = params['start_date']
    end_date = params['end_date']

    df = index_price.copy()
    df = df.loc[start_date:end_date]
    df['ret_large'] = df['large'].pct_change()
    df['ret_small'] = df['small'].pct_change()
    df['N_day_ret_large'] = df['large'] / df['large'].shift(N) - 1
    df['N_day_ret_small'] = df['small'] / df['small'].shift(N) - 1

    # 设置仓位：在 large OR small

    df['momentum_large_vs_small'] = df['N_day_ret_large'] - df['N_day_ret_small']
    df['pos_large'] = [1 if e > 0 else 0 for e in df['momentum_large_vs_small'].shift(1)]
    df['pos_small'] = 1 - df['pos_large']

    if rotation_type == RotationType.Full:
        pass
    elif rotation_type == RotationType.Nullable:
        df['pos_large'] = 0
        df['pos_small'] = 0
        for i in range(1, len(df)):
            t = df.index[i]
            t0 = df.index[i - 1]
            if df.loc[t0, 'N_day_ret_large'] >= df.loc[t0, 'N_day_ret_small'] and df.loc[t0, 'N_day_ret_large'] > 0:
                df.loc[t, 'pos_large'] = 1
            elif df.loc[t0, 'N_day_ret_small'] > df.loc[t0, 'N_day_ret_large'] and df.loc[t0, 'N_day_ret_small'] > 0:
                df.loc[t, 'pos_small'] = 1
    elif rotation_type == RotationType.Enhanced:
        t_date_range = _get_T_dates()
        # 可空仓区间：T <= 1.8
        for i in range(1, len(df)):
            t = df.index[i]
            if t <= t_date_range[1] or (t >= t_date_range[2] and t <= t_date_range[3]) \
                or (t >= t_date_range[4] and t <= t_date_range[5]) \
                or (t >= t_date_range[6] and t <= t_date_range[7]):
                t0 = df.index[i - 1]
                if df.loc[t0, 'N_day_ret_large'] >= df.loc[t0, 'N_day_ret_small'] and df.loc[t0, 'N_day_ret_large'] > 0:
                    df.loc[t, 'pos_large'] = 1
                elif df.loc[t0, 'N_day_ret_small'] > df.loc[t0, 'N_day_ret_large'] and df.loc[t0,
                                                                                              'N_day_ret_small'] > 0:
                    df.loc[t, 'pos_small'] = 1
                else:
                    df.loc[t, 'pos_large'] = 0
                    df.loc[t, 'pos_small'] = 0
    else:
        raise NotImplemented(f'not supported rotation_type [{rotation_type}]')

    # 计算获利
    df['ret_stgy'] = df['ret_large'] * df['pos_large'] + df['ret_small'] * df['pos_small']
    df['large'] = (1 + df['ret_large']).cumprod().fillna(1)
    df['small'] = (1 + df['ret_small']).cumprod().fillna(1)
    df['stgy'] = (1 + df['ret_stgy']).cumprod().fillna(1)

    return df


def backtest_result(df, title):
    ret_df = df.loc[:, ['large', 'small', 'stgy']]

    fig = plt.figure(figsize=(20, 10))
    ax1 = fig.add_subplot(2, 1, 1)
    ax1.set_title(title)
    ret_df.plot(ax=ax1, grid=True)
    plt.xlim(df.index[0], df.index[-1])

    ax2 = fig.add_subplot(2, 1, 2)
    df[['pos_large', 'pos_small']].plot(ax=ax2, kind='area', stacked=True, grid=True)
    plt.xlim(df.index[0], df.index[-1])

    res = cal_period_perf_indicator(ret_df)
    res['TotalRet'] = ret_df.iloc[-1] - 1
    print(res)
