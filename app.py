from bson import json_util
from flask import Flask
from modules.DBUtility import *
from flask import render_template
# https://codehandbook.org/creating-rest-api-using-python-mongodb/
app = Flask(__name__)


@app.route('/getResult')
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

    return render_template('index.html', geocode=result_json)
    # return str(result_json)


if __name__ == '__main__':
    app.run()
