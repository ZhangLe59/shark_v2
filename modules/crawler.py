import re

import pytz
import requests
from bs4 import BeautifulSoup

from modules.analyseUtility import *


# https://www.crummy.com/software/BeautifulSoup/bs4/doc/#navigating-the-tree
# possible alternative source: http://www.aastocks.com/en/stocks/analysis/company-fundamental/basic-information?symbol=00700

def get_data_yahoo(shark_db):
    logger = logging.getLogger(__name__)

    CONSTANT_STOCK_POOL = [
        'AMZN', 'LMT', 'BA', 'PDD', 'FB', 'MDB', 'GDS', 'YRD', 'AMD', 'BABA', 'TSLA', 'MO', 'VIPS', 'TCEHY',
        '0700.HK', '2318.HK', '2202.HK', '1211.HK', '6060.HK', '1579.HK', '6862.HK', '1810.HK', '3690.HK', '1093.HK',
        '2382.HK', '1833.HK', '0981.HK', '3087.HK', '2827.HK',
        'AU8U.SI', 'D05.SI', 'A2M.AX',
        '600030.SS', '002415.SZ', '000725.SZ', '601138.SS'
    ]

    stock_list = CONSTANT_STOCK_POOL[:]

    result = {}
    data_dict = {}

    new_stock = ''
    for idx, stock in enumerate(CONSTANT_STOCK_POOL):
        get_technical_data_yahoo(idx, stock, data_dict, stock_list)

    result['key'] = datetime.now(pytz.timezone('Singapore')).strftime('%Y-%m-%d')
    result['stock_pool'] = stock_list
    result['data'] = data_dict

    save_to_mongo_db(shark_db, 'stocks', result)
    # save_to_local_file(result)

    return result


def get_technical_data_yahoo(idx, stock, data_dict, stock_list):
    try:
        link = "https://finance.yahoo.com/quote/" + stock + "/key-statistics"
        the_page = requests.get(link).content

        pattern = "{\"quoteData\":{" + "\"" + stock + "\":{*(.+?)e}"
        p = re.compile(pattern)

        try:
            dict_string = "{\"" + stock + "\":{" + p.search(the_page.decode("utf-8")).group(1) + "e}}"
        except Exception as e:
            print(stock + ' encountered error, skip')
            logger.error(str(e))
            return

        new_stock = stock.replace('.', '-')
        stock_list[idx] = new_stock
        data_dict[new_stock] = json.loads(dict_string)[stock]
        data_dict[new_stock]['stock_code'] = new_stock

        soup = BeautifulSoup(the_page, features="html.parser")

        for header in soup.findAll('h2'):
            if header.text == 'Trading Information':
                stock_price_hist_tb = header.next_sibling.find('h3').next_sibling
                for row in stock_price_hist_tb.findAll('tr'):
                    key = row.contents[0].text
                    _text = row.contents[1].text.rstrip("%").replace(',', '')
                    try:
                        value = float(_text)
                    except Exception as e:
                        value = 999999999
                    data_dict[new_stock][key] = value
                break

        print(stock + ' loaded')

    except Exception as crawl_exception:
        data_dict.pop(new_stock)
        print(str(crawl_exception))


def get_technical_data_aastock():
    link = "http://www.aastocks.com/en/usq/quote/quote.aspx?symbol=AMZN"
    the_page = requests.get(link).content

    return


def get_earning_dates(idx, stock):
    # https://finance.yahoo.com/calendar/earnings/?symbol=BABA

    return
