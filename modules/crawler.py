import datetime

from bs4 import BeautifulSoup
import re
import json
import requests
import pymongo

# https://www.crummy.com/software/BeautifulSoup/bs4/doc/#navigating-the-tree

stock_list = ['AMZN', 'LMT', 'BA', 'PDD', 'NFLX', 'FB', 'USNA', 'MDB', 'NIO', 'SQ', 'GDS', 'YRD', 'AMD', 'BABA', 'TSLA',
              '0700.HK', '2318.HK', '2202.HK', '1211.HK', '6060.HK', '1579.HK', '6862.HK', '1810.HK', '3690.HK',
              'AU8U.SI', 'D05.SI',
              'IAG.AX',
              'A2M.AX']


def get_data_yahoo():
    collection = connect_to_mongoDB()

    result = {}
    data_dict = {}

    for idx, stock in enumerate(stock_list):
        try:
            link = "https://finance.yahoo.com/quote/" + stock + "/key-statistics"

            response = requests.get(link)

            the_page = response.content

            pattern = "{\"quoteData\":{" + "\"" + stock + "\":{*(.+?)e}"
            p = re.compile(pattern)
            dict_string = "{\"" + stock + "\":{" + p.search(the_page.decode("utf-8")).group(1) + "e}}"
            # print(dict_string)

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

            print(stock + ' loaded')

        except Exception as crawl_exception:
            print(str(crawl_exception))

    result['key'] = datetime.datetime.today().strftime('%Y-%m-%d')
    result['stock_pool'] = stock_list
    result['data'] = data_dict

    save_to_mongo_db(collection, result)
    # save_to_local_file(result)

    return result


def connect_to_mongoDB():
    try:
        client = pymongo.MongoClient("mongodb+srv://root:root@cluster0-50fxe.mongodb.net/admin?retryWrites=true")
        collection = client.sharkDB.stocks
        return collection
    except Exception as db_exception:
        print(str(db_exception))


def save_to_mongo_db(collection, dict):
    try:
        old_document = collection.find_one({'key': dict['key']})
        if old_document is None:
            _id = collection.insert_one(dict).inserted_id

            print('Insertion successful')
            return _id
        else:
            _id = old_document['_id']
            collection.replace_one({'_id': _id}, dict)
            new_document = collection.find_one({'_id': _id})
            print('Existing document has been replaced %s', new_document['_id'])
    except Exception as db_exception:
        print(str(db_exception))


if __name__ == "__main__":
    get_data_yahoo()
