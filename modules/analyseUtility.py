from datetime import timedelta

import pytz

from modules.DBUtility import *


def analyse_trend(shark_db, _dict):
    logger = logging.getLogger(__name__)

    # Get previous analysis data for status change which will trigger buy/sell action
    yesterday = datetime.now(pytz.timezone('Singapore')) - timedelta(1)
    logger.info('The date used for previous day is ' + str(yesterday))
    yesterday__strftime = yesterday.strftime('%Y-%m-%d')

    yesterday_analysis = shark_db.find_one('analysis', {'key': yesterday__strftime})
    yesterday_raw_data = shark_db.find_one('stocks', {'key': yesterday__strftime})

    while (yesterday_analysis is None or yesterday_raw_data is None):
        print('There is gap in data, pushing 1 more day back')
        yesterday = yesterday - timedelta(1)
        yesterday__strftime = yesterday.strftime('%Y-%m-%d')
        yesterday_analysis = shark_db.find_one('analysis', {'key': yesterday__strftime})
        yesterday_raw_data = shark_db.find_one('stocks', {'key': yesterday__strftime})

    print('Found previous data for analysing!')

    full_result = {}
    result = {}

    data = _dict['data']
    for stock in _dict['stock_pool']:

        comment = {}

        display_name, fifty_day_ma = analyse_today_data(comment, data, stock)
        if stock in yesterday_analysis['data'] and stock in yesterday_raw_data['data']:
            analyse_rolling_2_day(comment, fifty_day_ma, stock, yesterday_analysis, yesterday_raw_data)

        individual_result = {}
        individual_result['short_name'] = display_name
        individual_result['comment'] = comment
        full_result[stock] = individual_result

    today__strftime = datetime.now(pytz.timezone('Singapore')).strftime('%Y-%m-%d')
    result['key'] = today__strftime
    result['data'] = full_result
    save_to_mongo_db(shark_db, 'analysis', result)

    return result


def analyse_rolling_2_day(comment, fifty_day_ma, stock, yesterday_analysis, yesterday_raw_data):
    yest_fifty_day_ma = yesterday_raw_data['data'][stock]['50-Day Moving Average 3']
    yest_twohundred_day_ma = yesterday_raw_data['data'][stock]['200-Day Moving Average 3']
    if comment['conclusion'][0:10] != yesterday_analysis['data'][stock]['comment']['conclusion'][0:10]:
        comment['HIGH_ALERT'] = 'Previous Conclusion: ' + \
                                yesterday_analysis['data'][stock]['comment'][
                                    'conclusion'] + ' ' + 'Current Conclusion: ' + comment['conclusion']
    if fifty_day_ma < yest_fifty_day_ma:
        comment['TREND_1'] = 'Downward Middle Term Trending.'
    else:
        comment['TREND_1'] = 'Upward/Flat Middle Term Trending.'


def analyse_today_data(comment, data, stock):
    marketPrice = data[stock]['regularMarketPrice']['raw']
    fifty_day_ma = data[stock]['50-Day Moving Average 3']
    twohundred_day_ma = data[stock]['200-Day Moving Average 3']

    yearly_chg = data[stock]['52-Week Change 3']
    sp500_yearly_chg = data[stock]['S&P500 52-Week Change 3']

    display_name = data[stock]['shortName'] + ' (' + str(marketPrice) + ')'

    if twohundred_day_ma < fifty_day_ma < marketPrice:
        comment['conclusion'] = '1_1_AWESOME, Hold this stock! '
    elif fifty_day_ma < marketPrice:
        comment['conclusion'] = '1_2_Seems effective short-term rebounce.'
    elif marketPrice < fifty_day_ma < twohundred_day_ma:
        comment['conclusion'] = '3_1_This is really bad. '
    elif marketPrice < fifty_day_ma > twohundred_day_ma:
        comment['conclusion'] = '2_1_Watch out, it will be Awesome if it breakthrough ' + str(fifty_day_ma)
    else:
        comment['conclusion'] = 'Need further investigation'
    if twohundred_day_ma <= fifty_day_ma:
        comment['TREND_2'] = "Upward Long Term Trending."
    else:
        comment['TREND_2'] = 'Downward Long Term Trending.'

    comment['vsSP500'] = 'Outperformed S&P 500' if yearly_chg > sp500_yearly_chg else 'Under performed S&P 500'

    return display_name, fifty_day_ma
