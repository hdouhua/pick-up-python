# import ipywidgets as widgets
# widgets.interact(asset_predicition,
#     init_capital=widgets.FloatSlider(min=0, max=100, step=10, value=20),
#     start_age=widgets.FloatSlider(min=0, max=100, step=10, value=25),
#     salary_month=widgets.FloatSlider(min=0, max=100, step=10, value=20),
#     spend_month=widgets.FloatSlider(min=0, max=100, step=10, value=20),
#     rental_fee=widgets.FloatSlider(min=0, max=100, step=10, value=20),
#     retired_age=widgets.FloatSlider(min=0, max=100, step=10, value=65))

import pandas as pd
import random
import matplotlib.pyplot as plt

# init_capital = 30
# start_age = 25
# salary_month = 3
# expense_month = 1
# rental_fee = 1
# retiring_age = 60
# invest_start_age = 25
# invest_percentage = 50
# invest_return_ratio = 5
# total_house_price = 500
# buy_house_age = 45
# housing_first_payment = 100
# housing_loan_ratio = 4
# housing_loan_periods = 24
# age_range = (25, 90, 1)

# asset_predicition(
#     init_capital, 
#     start_age,
#     salary_month,
#     expense_month,
#     rental_fee,
#     retiring_age,
#     invest_start_age,
#     invest_percentage,
#     invest_return_ratio,
#     total_house_price,
#     buy_house_age,
#     housing_first_payment,
#     housing_loan_ratio,
#     housing_loan_periods)


def asset_predicition(
    init_capital, 
    start_age,
    salary_month,
    expense_month,
    rental_fee_month,
    retiring_age,
    invest_start_age,
    invest_percentage,
    invest_return_ratio,
    total_house_price,
    buy_house_age,
    housing_first_payment,
    housing_loan_ratio,
    housing_loan_periods
):

    predicition_range = range(start_age, 100)


    def compound_interest(arr, ratio, return_rate):
        ret = [arr.iloc[0]]
        for v in arr[1:]:
            ret.append(ret[-1] * ratio * (return_rate / 100 + 1) +ret[-1] * (1-ratio) + v)
        return pd.Series(ret, predicition_range)


    every_year_equity = pd.Series(0, index=predicition_range)
    every_year_equity.iloc[0] = init_capital
    every_year_equity.loc[:retiring_age] += salary_month * 12
    every_year_equity -= (expense_month + rental_fee_month) * 12

    expense_house = pd.Series(0, index=predicition_range)
    expense_house[buy_house_age] = housing_first_payment
    expense_house.loc[buy_house_age:buy_house_age+housing_loan_periods] += (total_house_price - housing_first_payment) / housing_loan_periods

    debt = pd.Series(0, index=predicition_range)
    debt[buy_house_age] = total_house_price
    debt = debt.cumsum()
    debt = debt - expense_house.cumsum()

    interest = debt.shift().fillna(0) * housing_loan_ratio / 100

    rental_fee_annual = pd.Series(rental_fee_month * 12, index=predicition_range)
    rental_fee_annual.loc[buy_house_age:] = 0

    every_year_equity_buy_house = pd.Series(0, index=predicition_range)
    every_year_equity_buy_house.iloc[0] = init_capital
    every_year_equity_buy_house.loc[:retiring_age] += salary_month * 12
    every_year_equity_buy_house -= (expense_month*12 + rental_fee_month + interest + expense_house)

    pd.DataFrame({
        'no invest, no house': every_year_equity.cumsum(),
        'invest, no house': compound_interest(every_year_equity, invest_percentage, invest_return_ratio),
        'no invest, house': every_year_equity_buy_house.cumsum(),
        'invest, house': compound_interest(every_year_equity_buy_house, invest_percentage, invest_return_ratio),
    }).plot()

    plt.ylim(0, None)
    print('housing loan / month', (total_house_price - housing_first_payment) / housing_loan_periods / 12)
    print('interest', interest.sum() / housing_loan_periods)
    print('')
