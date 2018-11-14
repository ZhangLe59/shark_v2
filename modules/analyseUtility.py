def analyse_trend(_dict, stock):
    marketPrice = _dict[stock]['regularMarketPrice']['raw']
    fifty_day_ma = _dict[stock]['50-Day Moving Average 3']
    twohundred_day_ma = _dict[stock]['200-Day Moving Average 3']

    display_name = _dict[stock]['shortName'] + ' (' + stock + ')'

    if twohundred_day_ma < fifty_day_ma < marketPrice:
        print('Hold this stock! ' + display_name)
    elif fifty_day_ma < marketPrice:
        print('Seems effective short-term rebouncing. ' + display_name)
    elif marketPrice < fifty_day_ma < twohundred_day_ma:
        print('This is really bad. ' + display_name)
    elif fifty_day_ma > twohundred_day_ma:
        print('Watch out, it will be ok if it breakthrough. ' + display_name)
