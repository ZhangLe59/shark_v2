from bs4 import BeautifulSoup
import re
import json
import requests
import pymongo
from modules.analyseUtility import *

# https://www.crummy.com/software/BeautifulSoup/bs4/doc/#navigating-the-tree

stock_list = ['0700.HK', 'AMZN', 'LMT', 'BA', 'NFLX', 'FB', 'USNA', 'SQ', 'GDS', 'YRD', 'AMD', 'BABA', 'TSLA', '2318.HK', '2202.HK', '1357.HK',
              '1211.HK', '2120.HK', 'AU8U.SI', 'CWP.AX', 'IAG.AX', 'A2M.AX']


def get_data_yahoo():
    collection = connect_to_mongoDB()

    for stock in stock_list:
        try:
            link = "https://finance.yahoo.com/quote/" + stock + "/key-statistics"

            response = requests.get(link)

            the_page = response.content

            pattern = "{\"quoteData\":{" + "\"" + stock + "\":{*(.+?)e}"
            p = re.compile(pattern)
            dict_string = "{\"" + stock + "\":{" + p.search(the_page.decode("utf-8")).group(1) + "e}}"
            # print(dict_string)

            _dict = json.loads(dict_string)

            soup = BeautifulSoup(the_page, features="html.parser")

            for header in soup.findAll('h2'):
                if header.text == 'Trading Information':
                    stock_price_hist_tb = header.next_sibling.find('h3').next_sibling
                    for row in stock_price_hist_tb.findAll('tr'):
                        key = row.contents[0].text
                        _text = row.contents[1].text.rstrip("%").replace(',', '')

                        value = float(_text if _text != 'N/A' else '10000000')
                        _dict[stock][key] = value

            _dict[stock.replace('.', '-')] = _dict.pop(stock)
            stock = stock.replace('.', '-')

            analyse_trend(_dict, stock)

            # save_to_mongoDB(collection, _dict)

            # print(stock + ' loaded')

        except Exception as crawl_exception:
            print(str(crawl_exception))
            # time.sleep(2)

def connect_to_mongoDB():
    try:
        client = pymongo.MongoClient("mongodb+srv://root:root@cluster0-50fxe.mongodb.net/admin?retryWrites=true")
        collection = client.sharkDB.stocks
        return collection
    except Exception as db_exception:
        print(str(db_exception))


def save_to_mongoDB(collection, dict):
    try:
        _id = collection.insert_one(dict).inserted_id
        print('Insertion successful')
        return _id
    except Exception as db_exception:
        print(str(db_exception))


get_data_yahoo()
# save_to_mongoDB()
