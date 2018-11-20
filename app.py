from flask import Flask, jsonify
from json2table import json2table

from modules.DBUtility import *
from flask import render_template
from modules.crawler import *
from modules.analyseUtility import *

# https://codehandbook.org/creating-rest-api-using-python-mongodb/
app = Flask(__name__)


@app.route('/showall')
def start():
    db_config = {'URI': 'mongodb+srv://root:root@cluster0-50fxe.mongodb.net/admin?retryWrites=true'}
    shark_db = Mongodb(db_config, 'sharkDB')
    # shark_db.output_rows('stocks')
    result_cursor = shark_db.find_all('stocks', )
    # cursor_list = list(result_cursor)
    # result_json = json.dumps(cursor_list)
    result_json = []
    for doc in result_cursor:
        doc.pop('_id')
        result_json.append(json.dumps(doc))

    return json2table.convert(doc, "LEFT_TO_RIGHT", {'border': 1})
    # return render_template('index.html', content=result_json)
    # return str(result_json)

@app.route('/snapshot')
def show_today_snapshot():
    today_data = get_data_yahoo()

    today = datetime.datetime.today().strftime('%Y-%m-%d')
    analyse_result = analyse_trend(today_data[today])

    html_string = json2table.convert(analyse_result)
    # return render_template('index.html', content=analyse_result)
    return html_string



if __name__ == '__main__':
    app.run()
