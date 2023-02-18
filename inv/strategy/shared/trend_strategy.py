from os.path import exists
import datetime
import pandas as pd
import matplotlib.pyplot as plt

from ipywidgets import DatePicker, IntSlider, FloatSlider, Select, Checkbox, Layout, Box, HBox
from tools import cal_period_perf_indicator, datestr2dtdate, SymbolCategry, get_symbols_by_categry


def get_widgets():
    date_pickers = [
        DatePicker(value=datetime.date(2020, 1, 1),
                   description='Start:',
                   disabled=False,
                   layout=Layout(flex='1 1 auto', width='auto')),
        DatePicker(value=datetime.date(2022, 12, 31),
                   description='End:',
                   disabled=False,
                   layout=Layout(flex='1 1 auto', width='auto')),
    ]

    symbol_list = get_symbols_by_categry(SymbolCategry.SMALL_CAP) \
        + get_symbols_by_categry(SymbolCategry.LARGE_CAP) \
        + get_symbols_by_categry(SymbolCategry.DIVIDENT) \
        + get_symbols_by_categry(SymbolCategry.SPECIALIZATION)
    symbols = [
        Select(options=symbol_list, rows=10, description='Target:', disabled=False),
        Checkbox(value=False, description='Fund ?', disabled=False, indent=False),
    ]

    box1 = Box(children=date_pickers)
    box2 = Box(children=symbols)

    return (HBox(children=(box1, box2)), date_pickers, symbols)


def get_widgets_for_memontun():
    sliders = [
        IntSlider(value=20,
                  min=5,
                  max=200,
                  step=1,
                  description='N1:',
                  disabled=False,
                  continuous_update=False,
                  orientation='horizontal',
                  readout=True,
                  readout_format='d'),
        FloatSlider(
            value=0.05,
            min=0.01,
            max=0.50,
            step=0.01,
            description='Long:',
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='.2f',
        ),
        FloatSlider(
            value=-0.05,
            min=-0.50,
            max=-0.01,
            step=0.01,
            description='Short:',
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='.2f',
        ),
    ]
    return (HBox(sliders), sliders)


def get_widgets_for_dual_mv():
    sliders = [
        IntSlider(value=10,
                  min=5,
                  max=60,
                  step=1,
                  description='N1:',
                  disabled=False,
                  continuous_update=False,
                  orientation='horizontal',
                  readout=True,
                  readout_format='d'),
        IntSlider(value=30,
                  min=10,
                  max=200,
                  step=1,
                  description='N2:',
                  disabled=False,
                  continuous_update=False,
                  orientation='horizontal',
                  readout=True,
                  readout_format='d'),
        FloatSlider(
            value=1.05,
            min=1.01,
            max=1.5,
            step=0.01,
            description='Long:',
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='.2f',
        ),
        FloatSlider(
            value=0.97,
            min=0.50,
            max=1,
            step=0.01,
            description='Short:',
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='.2f',
        ),
    ]
    return (HBox(sliders), sliders)


def get_widgets_for_bolling_band():
    sliders = [
        IntSlider(value=10,
                  min=5,
                  max=60,
                  step=1,
                  description='N1:',
                  disabled=False,
                  continuous_update=False,
                  orientation='horizontal',
                  readout=True,
                  readout_format='d'),
    ]
    return (HBox(sliders), sliders)


def backtest_result(df, title):
    ret_df = df.loc[:, ['asset', 'stgy']]

    fig = plt.figure(figsize=(16, 8))
    ax1 = fig.add_subplot(2, 1, 1)
    ret_df.plot(ax=ax1, grid=True, title=title)
    ax2 = fig.add_subplot(2, 1, 2)
    df.loc[:, ['pos']].plot(ax=ax2, grid=True)

    res = cal_period_perf_indicator(ret_df)
    res['TotalRet'] = ret_df.iloc[-1, :] - 1
    print(res)


def load_hist_data(symbol_id, col_mappings=None, folder='../res'):
    csv_file = f'{folder}/{symbol_id}.csv'
    if exists(csv_file):
        index_data = pd.read_csv(csv_file).set_index('datetime')
        index_data.index = [datestr2dtdate(e) for e in index_data.index]
        if col_mappings:
            index_data.rename(columns=col_mappings, inplace=True)
        return index_data
    return None


def memontun(df, symbol_id, n_day=20, long_threshold=0.05, short_threshold=-0.05):
    if df.size == 0:
        return

    df['ret'] = df[symbol_id].pct_change()
    df['asset'] = (1 + df['ret']).cumprod().fillna(1)
    df['N_day_ret'] = df['asset'] / df['asset'].shift(n_day) - 1
    df['pos'] = [1 if e > long_threshold else 0 if e < short_threshold else 0.5 for e in df['N_day_ret'].shift(1)]
    df['stgy_ret'] = df['ret'] * df['pos']
    df['stgy'] = (1 + df['stgy_ret']).cumprod().fillna(1)


def mv_cross(df, symbol_id, n_day1=22, n_day2=55, long_threshold=1.05, short_threshold=0.95):
    if df.size == 0:
        return
    df['ret'] = df[symbol_id].pct_change()
    df['asset'] = (1 + df['ret']).cumprod().fillna(1)
    df['ret'] = df['asset'].pct_change()
    df['MA1'] = df['asset'].rolling(window=n_day1).mean()
    df['MA2'] = df['asset'].rolling(window=n_day2).mean()
    df['MA1/MA2'] = df['MA1'] / df['MA2']
    df['pos'] = [1 if e > long_threshold else 0 if e < short_threshold else 0.5 for e in df['MA1/MA2'].shift(1)]

    df['stgy_ret'] = df['ret'] * df['pos']
    df['stgy'] = (1 + df['stgy_ret']).cumprod().fillna(1)


def bolling_band(df, symbol_id, n_day=20):
    df['ret'] = df[symbol_id].pct_change()
    df['asset'] = (1 + df['ret']).cumprod().fillna(1)
    df['ret'] = df['asset'].pct_change()
    df['MA'] = df['asset'].rolling(window=n_day).mean()
    df['std'] = df['asset'].rolling(window=n_day).std()
    df['up'] = df['MA'] + 2 * df['std']
    df['down'] = df['MA'] - 2 * df['std']

    df['pos'] = 0
    for i in range(1, len(df)):
        t2 = df.index[i]
        t1 = df.index[i - 1]
        if df.loc[t1, 'asset'] > df.loc[t1, 'up']:
            df.loc[t2, 'pos'] = 1
        elif df.loc[t1, 'asset'] < df.loc[t1, 'down']:
            df.loc[t2, 'pos'] = 0
        elif df.loc[t1, 'pos'] == 1 and df.loc[t1, 'asset'] < df.loc[t1, 'MA']:
            df.loc[t2, 'pos'] = 0.5
        elif df.loc[t1, 'pos'] == 0 and df.loc[t1, 'asset'] > df.loc[t1, 'MA']:
            df.loc[t2, 'pos'] = 0.5
        else:
            df.loc[t2, 'pos'] = df.loc[t1, 'pos']

    df['stgy_ret'] = df['ret'] * df['pos']
    df['stgy'] = (1 + df['stgy_ret']).cumprod().fillna(1)
