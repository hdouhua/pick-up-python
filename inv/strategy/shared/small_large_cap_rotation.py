from enum import Enum
import datetime
import pandas as pd
import matplotlib.pyplot as plt

from ipywidgets import DatePicker, IntSlider, Select, Checkbox, Layout, Box, VBox

from tools import cal_period_perf_indicator, datestr2dtdate, SymbolCategry, get_symbols_by_categry


class RotationType(Enum):
    """
    1 - 满仓
    2- 可空仓
    3 - 增强
    """
    FULL = 1
    NULLABLE = 2
    ENHANCED = 3


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
        IntSlider(value=20,
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
        Select(options=get_symbols_by_categry(SymbolCategry.SMALL_CAP),
               rows=10,
               description='Small-Cap:',
               disabled=False),
        Checkbox(value=False, description='Fund ?', disabled=False, indent=False),
        Select(options=get_symbols_by_categry(SymbolCategry.LARGE_CAP),
               rows=10,
               description='Large-Cap:',
               disabled=False),
        Checkbox(value=False, description='Fund ?', disabled=True, indent=False),
    ]

    box1 = Box(children=date_pickers)
    box2 = Box(children=symbols)

    return (VBox(children=(box1, box2)), date_pickers, symbols)


def _get_t_dates():
    """
    T 值的区间
    """
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

    try:
        df.drop(['acc_close', 'pe', 'pe_pct80', 'pe_pct20', 'pe_pct50'], axis=1, inplace=True)
    except Exception as ex:
        print(f'{ex} ignored')

    if cols:
        df.rename(columns=cols, inplace=True)

    # print(df.head(50))
    return df


def run_strategy(index_price, rotation_type, params):
    n_day = params['N']
    start_date = params['start_date']
    end_date = params['end_date']
    long_spread = params['long_spread'] if 'long_spread' in params else 0
    short_spread = params['short_spread'] if 'short_spread' in params else 0

    df = index_price.copy()
    df = df.loc[start_date:end_date]
    df['ret_large'] = df['large'].pct_change()
    df['ret_small'] = df['small'].pct_change()
    df['N_day_ret_large'] = df['large'] / df['large'].shift(n_day) - 1
    df['N_day_ret_small'] = df['small'] / df['small'].shift(n_day) - 1

    # 设置仓位：在 large OR small
    df['momentum_large_vs_small'] = df['N_day_ret_large'] - df['N_day_ret_small']
    df['pos_large'] = [1 if e > 0 else 0 for e in df['momentum_large_vs_small'].shift(1)]
    df['pos_small'] = 1 - df['pos_large']
    if rotation_type == RotationType.FULL:
        pass
    elif rotation_type == RotationType.NULLABLE:
        df['pos_large'] = 0
        df['pos_small'] = 0

        for i in range(1, len(df)):
            t1 = df.index[i - 1]
            t2 = df.index[i]
            if df.loc[t1, 'N_day_ret_large'] >= df.loc[t1,'N_day_ret_small'] \
                and df.loc[t1,'N_day_ret_large'] > long_spread:
                df.loc[t2, 'pos_large'] = 1
            elif df.loc[t1, 'N_day_ret_small'] > df.loc[t1, 'N_day_ret_large'] \
                and df.loc[t1, 'N_day_ret_small'] > long_spread:
                df.loc[t2, 'pos_small'] = 1
            else:
                if df.loc[t1, 'N_day_ret_large'] < short_spread:
                    df.loc[t2, 'pos_large'] = 0
                if df.loc[t1, 'N_day_ret_small'] < short_spread:
                    df.loc[t2, 'pos_small'] = 0
    elif rotation_type == RotationType.ENHANCED:
        t_date_range = _get_t_dates()
        # 可空仓区间：T <= 1.8
        for i in range(1, len(df)):
            t1 = df.index[i - 1]
            t2 = df.index[i]
            if t2 <= t_date_range[1] or (t2 >= t_date_range[2] and t2 <= t_date_range[3]) \
                or (t2 >= t_date_range[4] and t2 <= t_date_range[5]) \
                or (t2 >= t_date_range[6] and t2 <= t_date_range[7]):
                if df.loc[t1, 'N_day_ret_large'] >= df.loc[t1, 'N_day_ret_small'] \
                    and df.loc[t1, 'N_day_ret_large'] > long_spread:
                    df.loc[t2, 'pos_large'] = 1
                elif df.loc[t1, 'N_day_ret_small'] > df.loc[t1, 'N_day_ret_large'] \
                    and df.loc[t1, 'N_day_ret_small'] > long_spread:
                    df.loc[t2, 'pos_small'] = 1
                else:
                    if df.loc[t1, 'N_day_ret_large'] < short_spread:
                        df.loc[t2, 'pos_large'] = 0
                    if df.loc[t1, 'N_day_ret_small'] < short_spread:
                        df.loc[t2, 'pos_small'] = 0
    else:
        raise NotImplementedError(f'not supported rotation_type [{rotation_type}]')

    # 计算获利
    df['ret_stgy'] = df['ret_large'] * df['pos_large'] + df['ret_small'] * df['pos_small']
    df['large'] = (1 + df['ret_large']).cumprod().fillna(1)
    df['small'] = (1 + df['ret_small']).cumprod().fillna(1)
    df['stgy'] = (1 + df['ret_stgy']).cumprod().fillna(1)

    return df


def backtest_result(df, title):
    ret_df = df.loc[:, ['small', 'large', 'stgy']]

    fig = plt.figure(figsize=(20, 10))
    ax1 = fig.add_subplot(2, 1, 1)
    ax1.set_title(title)
    ret_df.plot(ax=ax1, grid=True)
    plt.xlim(df.index[0], df.index[-1])

    ax2 = fig.add_subplot(2, 1, 2)
    df[['pos_small', 'pos_large']].plot(ax=ax2, kind='area', stacked=True, grid=True)
    plt.xlim(df.index[0], df.index[-1])

    res = cal_period_perf_indicator(ret_df)
    res['TotalRet'] = ret_df.iloc[-1] - 1
    print(res)


def load_data(small_index, large_index, small_is_fund, large_is_fund):
    if small_is_fund:
        small_cols = {
            'nav': 'small',
            'pe_pct': 'small_pe_pct',
        }
    else:
        small_cols = {
            'close': 'small',
            'pe_pct': 'small_pe_pct',
        }

    if large_is_fund:
        large_cols = {
            'nav': 'large',
            'pe_pct': 'large_pe_pct',
        }
    else:
        large_cols = {
            'close': 'large',
            'pe_pct': 'large_pe_pct',
        }

    small_price = _read_csv(f'../res/small/{small_index}.csv', cols=small_cols)
    large_price = _read_csv(f'../res/large/{large_index}.csv', cols=large_cols)

    return pd.merge(large_price, small_price, left_index=True, right_index=True)
