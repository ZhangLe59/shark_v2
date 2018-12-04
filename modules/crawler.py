import re

import requests
from bs4 import BeautifulSoup

from modules.analyseUtility import *

# https://www.crummy.com/software/BeautifulSoup/bs4/doc/#navigating-the-tree
# possible alternative source: http://www.aastocks.com/en/stocks/analysis/company-fundamental/basic-information?symbol=00700

stock_list = ['AMZN', 'LMT', 'BA', 'PDD', 'NFLX', 'FB', 'USNA', 'MDB', 'NIO', 'SQ', 'GDS', 'YRD', 'AMD', 'BABA', 'TSLA',
              '0700.HK', '2318.HK', '2202.HK', '1211.HK', '6060.HK', '1579.HK', '6862.HK', '1810.HK', '3690.HK',
              'AU8U.SI', 'D05.SI',
              'IAG.AX',
              'A2M.AX']


def get_data_yahoo():
    logger = logging.getLogger(__name__)

    collection = connect_to_mongoDB('stocks')

    result = {}
    data_dict = {}

    new_stock = ''
    for idx, stock in enumerate(stock_list):
        try:
            link = "https://finance.yahoo.com/quote/" + stock + "/key-statistics"

            response = requests.get(link)

            the_page = response.content

            pattern = "{\"quoteData\":{" + "\"" + stock + "\":{*(.+?)e}"
            p = re.compile(pattern)

            try:
                dict_string = "{\"" + stock + "\":{" + p.search(the_page.decode("utf-8")).group(1) + "e}}"
            except Exception as e:
                print(stock + ' encountered error, skip')
                logger.error(str(e))
                continue

            new_stock = stock.replace('.', '-')
            stock_list[idx] = new_stock
            data_dict[new_stock] = json.loads(dict_string)[stock]

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

    result['key'] = date.today().strftime('%Y-%m-%d')
    result['stock_pool'] = stock_list
    result['data'] = data_dict

    save_to_mongo_db(collection, result)
    # save_to_local_file(result)

    return result


if __name__ == "__main__":
    raw_data = get_data_yahoo()
