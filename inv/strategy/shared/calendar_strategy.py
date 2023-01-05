import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from os.path import exists
from enum import Enum
from ipywidgets import DatePicker, IntSlider, Select, Checkbox, Box, HBox, VBox

from shared.tools import get_drawdown, cal_period_perf_indicator, datestr2dtdate, date_count_in_month


class SymbolType(Enum):
    Default = 0
    Divident = 1
    SmallCap = 2
    LargeCap = 3
    Specialization = 4


def get_widgets(symbol_type=SymbolType.Default):
    datePickers = [
        DatePicker(
            value=datetime.date(2020, 1, 1),
            description='Start:',
            disabled=False,
        ),
        DatePicker(
            value=datetime.date(2022, 12, 31),
            description='End:',
            disabled=False,
        ),
    ]
    dayRange = [
        IntSlider(value=1,
                  min=1,
                  max=22,
                  step=1,
                  description='t1:',
                  disabled=False,
                  continuous_update=False,
                  orientation='horizontal',
                  readout=True,
                  readout_format='d'),
        IntSlider(value=5,
                  min=5,
                  max=23,
                  step=1,
                  description='t2:',
                  disabled=False,
                  continuous_update=False,
                  orientation='horizontal',
                  readout=True,
                  readout_format='d'),
    ]

    if symbol_type == SymbolType.SmallCap:
        symbols = [
            Select(options=[
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
            ],
                   value='000905',
                   rows=7,
                   description='Symbol:',
                   disabled=False),
        ]
    elif symbol_type == SymbolType.LargeCap:
        symbols = [
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
                   rows=7,
                   description='Symbol:',
                   disabled=False),
        ]
    elif symbol_type == SymbolType.Divident:
        symbols = [
            Select(options=[
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
                ('上证消费', '000036'),
                ('中证消费', '000932'),
                ('基金 - 泰达消费红利指数A', '008928'),
                ('深证红利', '399324'),
                ('深证红利ETF', '159905'),
            ],
                   value='30269',
                   rows=7,
                   description='Symbol:',
                   disabled=False),
        ]
    elif symbol_type == SymbolType.Specialization:
        symbols = [
            Select(options=[
                ('医药100', '000978'),
                ('基金 - 医药100', '000059'),
                ('300医药ETF', '512010'),
                ('广发中证全指医药卫生ETF', '159938'),
                ('中证生科', '930743'),
                ('中证白酒', '399997'),
                ('基金 - 招商中证白酒指数A', '161725'),
            ],
                   value='000978',
                   rows=7,
                   description='Symbol:',
                   disabled=False),
        ]
    else:
        symbols = None

    box1 = Box(children=datePickers)
    box2 = Box(children=dayRange)
    vbox1 = VBox(children=(box1, box2))

    if symbols is not None:
        symbols.append(Checkbox(value=False, description='Fund ?', disabled=False, indent=False))
        box3 = Box(children=symbols)
    else:
        box3 = Box()

    return (HBox((vbox1, box3)), datePickers, dayRange, symbols)


def run_strategy(index_data, index_id, start_date, end_date, calendard_range, fee_rate):
    df = index_data.loc[start_date:end_date, [index_id]]
    df['index_ret'] = df[index_id].pct_change()
    # 设置仓位
    df['date_count_in_month'] = date_count_in_month(df.index)
    df['pos'] = [1 if (e >= calendard_range[0] and e <= calendard_range[1]) else 0 for e in df['date_count_in_month']]
    # df['pos']= df.pos.shift(-1, fill_value=0)

    df['stgy_ret'] = df['pos'] * df['index_ret']
    rebalancing_rows = df[df['date_count_in_month'] == 1].index
    df.loc[rebalancing_rows, 'stgy_ret'] = df.loc[rebalancing_rows, 'stgy_ret'] - fee_rate
    df['stgy'] = (1 + df['stgy_ret']).cumprod().fillna(1)
    df['index'] = (1 + df['index_ret']).cumprod().fillna(1)
    # df.fillna({'index': 1, 'stgy': 1}, inplace=True)

    return df


def backtest_result(df, title):
    # 回测结果展示
    fig = plt.figure(figsize=(16, 8))

    ret_df = df.loc[:, ['index', 'stgy']]
    ax1 = fig.add_subplot(2, 1, 1)
    ret_df.plot(ax=ax1, grid=True, title=title, legend=True)

    ax2 = fig.add_subplot(2, 1, 2)
    df.loc[:, ['pos']].plot(ax=ax2, grid=True)

    res = cal_period_perf_indicator(ret_df)
    res['TotalRet'] = ret_df.iloc[-1] - 1
    print(res)

    plt.show()


def load_hist_data(symbol_id, col_mappings=None, folder='../res'):
    csv_file = f'{folder}/{symbol_id}.csv'
    if exists(csv_file):
        index_data = pd.read_csv(csv_file).set_index('datetime')
        index_data.index = [datestr2dtdate(e) for e in index_data.index]
        if col_mappings:
            index_data.rename(columns=col_mappings, inplace=True)
        return index_data
    return None