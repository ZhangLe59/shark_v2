import pymongo
import pytz
from flask import Flask, g, render_template, jsonify
from json2table import json2table
import schedule
import time
import threading

from modules.crawler import *

# https://codehandbook.org/creating-rest-api-using-python-mongodb/
# https://cloud.mongodb.com/v2/5be630d0cf09a2a588b0055e#clusters
# from modules.news import get_news_from_API


app = Flask(__name__)

logger = logging.getLogger(__name__)


@app.route("/")
def hello():
    # return "Welcome to Shark V2, The Quick Analytics Platform for Global Stocks"
    return render_template('index.html')


@app.route('/analysis')
def show_analysis():
    shark_db = get_db()

    all_data = {}
    result_cursor = shark_db.find_all('analysis').sort([('key', pymongo.DESCENDING)]).limit(4)
    for doc in result_cursor:
        doc.pop('_id')
        all_data[doc['key']] = doc

    return json2table.convert(all_data, "LEFT_TO_RIGHT", {'border': 1})


@app.route('/data')
def show_data():
    shark_db = get_db()

    all_data = {}
    result_cursor = shark_db.find_all('stocks').sort([('key', pymongo.DESCENDING)]).limit(7)
    for doc in result_cursor:
        doc.pop('_id')
        all_data[doc['key']] = doc

    return json2table.convert(all_data, "LEFT_TO_RIGHT", {'border': 1})


@app.route('/snapshot')
def show_today_snapshot():
    today = datetime.now(pytz.timezone('Singapore')).strftime('%Y-%m-%d')

    analyse_result = get_db().find_one('analysis', {'key': today})

    if analyse_result is None:
        return 'Analysis result is not ready yet.'

    analyse_result.pop('_id')
    print(type(analyse_result))
    # html_string = json2table.convert(analyse_result, "LEFT_TO_RIGHT", {'border': 1})
    # return html_string

    # json_data = jsonify(json.dumps(analyse_result))

    # json_data = jsonify(analyse_result) #Returns full response with status

    return render_template('snapshot.html', content=analyse_result)

@app.route('/backtest')
def backtest():
    all_analyse_result = []
    for x in get_db().find_all('analysis'):
        x.pop('_id')
        logger.info(x)
        all_analyse_result.append(x)

    all_analyse_result.pop(0)
    # html_string = json2table.convert(all_analyse_result, "LEFT_TO_RIGHT", {'border': 1})
    return 'ok'

    # json_data = jsonify(json.dumps(analyse_result))

    # json_data = jsonify(analyse_result) #Returns full response with status

    # return render_template('snapshot.html', content=analyse_result)

@app.route('/crawl')
def crawl_today_raw():
    try:
        logger.info('Started crawling')
        shark_db = get_db()
        result = get_data_yahoo(shark_db)
        analyse_trend(shark_db, result)
        return 'Data has been crawled and analysed.'
    except Exception as e:
        print(e)
        return e


@app.route('/rerun')
def analyse_all():
    logger.info('Re-run all analysis from today')
    shark_db = get_db()

    count = 0
    current_day = datetime.now(pytz.timezone('Singapore'))
    current_day_key = current_day.strftime('%Y-%m-%d')

    start_date = '2018-11-27'

    while (start_date < current_day_key):
        stock_data = get_db().find_one('stocks', {'key': current_day_key})
        if stock_data is not None:
            print('Stock data found on ', current_day_key)
            analyse_trend(shark_db, stock_data)
            count = count + 1

        current_day = current_day - timedelta(1)
        current_day_key = current_day.strftime('%Y-%m-%d')

    return 'Re-run completed for ' + str(count) + ' days data since ' + start_date
# @app.route('/news')
# def get_news():
#     try:
#         logger.info('Retriving news')
#         result = get_news_from_API()
#
#         html_string = json2table.convert(result, "LEFT_TO_RIGHT", {'border': 1})
#         return html_string
#
#     except Exception as e:
#         print(e)
#         return e


def get_db():
    if 'db' not in g:
        db_config = {'URI': 'mongodb+srv://root:root@cluster0-50fxe.mongodb.net/admin?retryWrites=true'}
        g.db = Mongodb(db_config, 'sharkDB')
    return g.db


@app.teardown_appcontext
def teardown_db(error):
    db = g.pop('db', None)

    if db is not None:
        db.close_conn()


def start_scheduler():
    # schedule.every().day.at("10:30").do(crawl_today_raw)
    # schedule.every(1).minutes.do(crawl_today_raw)
    # schedule.run_pending()

    logger.info('Started scheduler')


if __name__ == '__main__':
    start_scheduler()
    app.run()
