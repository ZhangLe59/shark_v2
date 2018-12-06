from modules.DBUtility import *
from datetime import date, timedelta


def analyse_trend(_dict):
    logger = logging.getLogger(__name__)
    collection = connect_to_mongoDB('analysis')
    raw_data_collection = connect_to_mongoDB('stocks')

    # Get previous analysis data for status change which will trigger buy/sell action
    yesterday = date.today() - timedelta(1)
    logger.info('The date used for previous day is ' + str(yesterday))
    yesterday__strftime = yesterday.strftime('%Y-%m-%d')

    yesterday_analysis = collection.find_one({'key': yesterday__strftime})
    yesterday_raw_data = raw_data_collection.find_one({'key': yesterday__strftime})

    while (yesterday_analysis is None or yesterday_raw_data is None):
        print('There is gap in data, pushing 1 more day back')
        yesterday = yesterday - timedelta(1)
        yesterday__strftime = yesterday.strftime('%Y-%m-%d')
        yesterday_analysis = collection.find_one({'key': yesterday__strftime})
        yesterday_raw_data = raw_data_collection.find_one({'key': yesterday__strftime})

    print('Found previous data for analysing!')

    full_result = {}
    result = {}

    data = _dict['data']
    for stock in _dict['stock_pool']:
        individual_result = {}

        marketPrice = data[stock]['regularMarketPrice']['raw']
        fifty_day_ma = data[stock]['50-Day Moving Average 3']
        twohundred_day_ma = data[stock]['200-Day Moving Average 3']

        yest_fifty_day_ma = yesterday_raw_data['data'][stock]['50-Day Moving Average 3']
        yest_twohundred_day_ma = yesterday_raw_data['data'][stock]['200-Day Moving Average 3']

        yearly_chg = data[stock]['52-Week Change 3']
        sp500_yearly_chg = data[stock]['S&P500 52-Week Change 3']

        display_name = data[stock]['shortName'] + ' (' + stock + ')'

        comment = {}
        if twohundred_day_ma < fifty_day_ma < marketPrice \
                and fifty_day_ma > yest_fifty_day_ma and twohundred_day_ma > yest_twohundred_day_ma:
            comment['conclusion'] = 'AWESOME, Hold this stock! '
        elif fifty_day_ma < marketPrice:
            comment['conclusion'] = 'Seems effective short-term rebounce. But you have to check Trend_1'
        elif marketPrice < fifty_day_ma < twohundred_day_ma \
                and fifty_day_ma < yest_fifty_day_ma:
            comment['conclusion'] = 'This is really bad. '
        elif marketPrice < fifty_day_ma > twohundred_day_ma \
                and fifty_day_ma > yest_fifty_day_ma:
            comment['conclusion'] = 'Watch out, it will be Awesome if it breakthrough ' + str(fifty_day_ma)
        else:
            comment['conclusion'] = 'Need further investigation'

        if not yesterday_analysis is None:
            if comment['conclusion'][0:10] != yesterday_analysis['data'][stock]['comment']['conclusion'][0:10]:
                comment['HIGH_ALERT'] = 'Previous Conclusion: ' + \
                                        yesterday_analysis['data'][stock]['comment'][
                                            'conclusion'] + '\n' + 'Current Conclusion: ' + comment['conclusion']

            if fifty_day_ma < yest_fifty_day_ma:
                comment['TREND_1'] = 'Middle Term Downward Trending, SELL Fast'
            else:
                comment['TREND_1'] = 'Middle Term turned Upward/Flat Trending, Start BUYing'

            if twohundred_day_ma < yest_twohundred_day_ma \
                    and marketPrice < twohundred_day_ma:
                comment['TREND_2'] = "Long Term Downward Trending. This stock is DOOMED!!"
            else:
                comment['TREND_2'] = 'Long Term Upward/Flat Trending. Watch closely'

        comment['vsSP500'] = 'Outperformed S&P 500' if yearly_chg > sp500_yearly_chg else 'Under performed S&P 500'

        individual_result['short_name'] = display_name
        individual_result['comment'] = comment
        full_result[stock] = individual_result
        # print(comment + display_name)

    today__strftime = date.today().strftime('%Y-%m-%d')
    result['key'] = today__strftime
    result['data'] = full_result
    save_to_mongo_db(collection, result)

    return result
