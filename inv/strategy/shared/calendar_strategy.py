import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from os.path import exists
from ipywidgets import DatePicker, IntSlider, Select, Checkbox, Box, HBox, VBox

from shared.tools import get_drawdown, cal_period_perf_indicator, datestr2dtdate, date_count_in_month, \
    SymbolCategry, get_symbols_by_categry


def get_widgets(symbol_type=SymbolCategry.Default):
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

    if symbol_type == SymbolCategry.SmallCap:
        symbols = [
            Select(options=get_symbols_by_categry(SymbolCategry.SmallCap),
                   value='000905',
                   rows=7,
                   description='Symbol:',
                   disabled=False),
        ]
    elif symbol_type == SymbolCategry.LargeCap:
        symbols = [
            Select(options=get_symbols_by_categry(SymbolCategry.LargeCap),
                   value='000300',
                   rows=7,
                   description='Symbol:',
                   disabled=False),
        ]
    elif symbol_type == SymbolCategry.Divident:
        symbols = [
            Select(options=get_symbols_by_categry(SymbolCategry.Divident),
                   value='30269',
                   rows=7,
                   description='Symbol:',
                   disabled=False),
        ]
    elif symbol_type == SymbolCategry.Specialization:
        symbols = [
            Select(options=get_symbols_by_categry(SymbolCategry.Specialization),
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