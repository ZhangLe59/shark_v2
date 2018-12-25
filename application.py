import pymongo
from flask import Flask, g, render_template, jsonify
from json2table import json2table

from modules.crawler import *

# https://codehandbook.org/creating-rest-api-using-python-mongodb/
# https://cloud.mongodb.com/v2/5be630d0cf09a2a588b0055e#clusters
from modules.news import get_news_from_API

app = Flask(__name__)

logger = logging.getLogger(__name__)


@app.route("/")
def hello():
    return "Welcome to Shark V2, The Quick Analytics Platform for Global Stocks"


@app.route('/showrecent')
def all_saved_data():
    shark_db = get_db()

    all_data = {}
    result_cursor = shark_db.find_all('analysis').sort([('key', pymongo.DESCENDING)]).limit(7)
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
        # crawl_today_raw()


@app.route('/news')
def get_news():
    try:
        logger.info('Retriving news')
        result = get_news_from_API()

        html_string = json2table.convert(result, "LEFT_TO_RIGHT", {'border': 1})
        return html_string

    except Exception as e:
        print(e)
        return e


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


if __name__ == '__main__':
    app.run()
