from flask import Flask, g
from json2table import json2table

from modules.DBUtility import *
from flask import render_template
from modules.crawler import *
from modules.analyseUtility import *

# https://codehandbook.org/creating-rest-api-using-python-mongodb/
# https://cloud.mongodb.com/v2/5be630d0cf09a2a588b0055e#clusters
app = Flask(__name__)


@app.route("/")
def hello():
    return "Welcome to Shark V2, The Quick Analytics Platform for Global Stocks"


@app.route('/showall')
def start():
    db_config = {'URI': 'mongodb+srv://root:root@cluster0-50fxe.mongodb.net/admin?retryWrites=true'}
    shark_db = Mongodb(db_config, 'sharkDB')
    # shark_db.output_rows('stocks')
    result_cursor = shark_db.find_all('stocks', )
    result_json = []
    for doc in result_cursor:
        doc.pop('_id')
        result_json.append(json.dumps(doc))

    return json2table.convert(doc, "LEFT_TO_RIGHT", {'border': 1})
    # return render_template('index.html', content=result_json)
    # return str(result_json)


@app.route('/snapshot')
def show_today_snapshot():
    today = datetime.datetime.today().strftime('%Y-%m-%d')

    result = get_db().find_one('stocks', {'key': today})

    if result is None:
        result = get_data_yahoo()

    analyse_result = analyse_trend(result)

    html_string = json2table.convert(analyse_result)
    # return render_template('index.html', content=analyse_result)
    return html_string


@app.route('/crawl')
def crawl_today_raw():
    get_data_yahoo()


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
