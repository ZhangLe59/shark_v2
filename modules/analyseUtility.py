def analyse_trend(_dict):
    result = {}

    data = _dict['data']
    for stock in _dict['stock_pool']:

        marketPrice = data[stock]['regularMarketPrice']['raw']
        fifty_day_ma = data[stock]['50-Day Moving Average 3']
        twohundred_day_ma = data[stock]['200-Day Moving Average 3']

        display_name = data[stock]['shortName'] + ' (' + stock + ')'

        if twohundred_day_ma < fifty_day_ma < marketPrice:
            comment = 'AWESOME, Hold this stock! '
        elif fifty_day_ma < marketPrice:
            comment = 'Seems effective short-term rebounce. '
        elif marketPrice < fifty_day_ma < twohundred_day_ma:
            comment = 'This is really bad. '
        elif marketPrice < fifty_day_ma > twohundred_day_ma:
            comment = 'Watch out, it will be ok if it breakthrough. '
        else:
            comment = 'Need further investigation'

        result[display_name] = comment
        # print(comment + display_name)
    return result

