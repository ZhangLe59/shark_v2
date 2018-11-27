from modules.DBUtility import *
import datetime


def analyse_trend(_dict):
    collection = connect_to_mongoDB('analysis')
    full_result = {}
    result = {}

    data = _dict['data']
    for stock in _dict['stock_pool']:
        individual_result = {}

        marketPrice = data[stock]['regularMarketPrice']['raw']
        fifty_day_ma = data[stock]['50-Day Moving Average 3']
        twohundred_day_ma = data[stock]['200-Day Moving Average 3']

        yearly_chg = data[stock]['52-Week Change 3']
        sp500_yearly_chg = data[stock]['S&P500 52-Week Change 3']

        display_name = data[stock]['shortName'] + ' (' + stock + ')'

        comment = {}
        if twohundred_day_ma < fifty_day_ma < marketPrice:
            comment['conclusion'] = 'AWESOME, Hold this stock! '
        elif fifty_day_ma < marketPrice:
            comment['conclusion'] = 'Seems effective short-term rebounce. '
        elif marketPrice < fifty_day_ma < twohundred_day_ma:
            comment['conclusion'] = 'This is really bad. '
        elif marketPrice < fifty_day_ma > twohundred_day_ma:
            comment['conclusion'] = 'Watch out, it will be Awesome if it breakthrough ' + str(fifty_day_ma)
        else:
            comment['conclusion'] = 'Need further investigation'

        comment['vsSP500'] = 'Outperformed S&P 500' if yearly_chg > sp500_yearly_chg else 'Under performed S&P 500'

        individual_result['short_name'] = display_name
        individual_result['comment'] = comment
        full_result[stock] = individual_result
        # print(comment + display_name)

    result['key'] = datetime.datetime.today().strftime('%Y-%m-%d')
    result['data'] = full_result
    save_to_mongo_db(collection, result)

    return result
