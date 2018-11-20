def analyse_trend(_dict):
    result = {}

    data = _dict['data']
    for stock in _dict['stock_code']:

        marketPrice = data[stock]['regularMarketPrice']['raw']
        fifty_day_ma = data[stock]['50-Day Moving Average 3']
        twohundred_day_ma = data[stock]['200-Day Moving Average 3']

        display_name = data[stock]['shortName'] + ' (' + stock + ')'

        if twohundred_day_ma < fifty_day_ma < marketPrice:
            comment = 'Hold this stock! '
        elif fifty_day_ma < marketPrice:
            comment = 'Seems effective short-term rebounce. '
        elif marketPrice < fifty_day_ma < twohundred_day_ma:
            comment = 'This is really bad. '
        elif fifty_day_ma > twohundred_day_ma:
            comment = 'Watch out, it will be ok if it breakthrough. '
        else:
            comment = 'Need further investigation'

        result[display_name] = comment
        print(comment + display_name)
    return result


def analyse_data(dict_list):
    stock_list = dict_list
    for _dict in dict_list:
        stock = [_dict.keys()][0]

        marketPrice = _dict['regularMarketPrice']['raw']
        fifty_day_ma = _dict['50-Day Moving Average 3']
        twohundred_day_ma = _dict['200-Day Moving Average 3']

        display_name = _dict['shortName'] + ' (' + stock + ')'
        if twohundred_day_ma < fifty_day_ma < marketPrice:
            print('Hold this stock! ' + display_name)
        elif fifty_day_ma < marketPrice:
            print('Seems effective short-term rebouncing. ' + display_name)
        elif marketPrice < fifty_day_ma < twohundred_day_ma:
            print('This is really bad. ' + display_name)
        elif fifty_day_ma > twohundred_day_ma:
            print('Watch out, it will be ok if it breakthrough. ' + display_name)
