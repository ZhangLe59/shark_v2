from bson import json_util
from flask import Flask
from modules.DBUtility import *

# https://codehandbook.org/creating-rest-api-using-python-mongodb/
app = Flask(__name__)


@app.route('/')
def start():
    db_config = {'URI': 'mongodb+srv://root:root@cluster0-50fxe.mongodb.net/admin?retryWrites=true'}
    shark_db = Mongodb(db_config, 'sharkDB')
    # shark_db.output_rows('stocks')
    result_cursor = shark_db.find_all('stocks', )
    # cursor_list = list(result_cursor)
    # result_json = json.dumps(cursor_list)
    result_json = [json.dumps(doc, default=json_util.default) for doc in result_cursor]

    return str(result_json)


if __name__ == '__main__':
    app.run()
