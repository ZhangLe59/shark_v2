import json


def save_to_local_file(dict):
    fname = '../raw_data.json'
    try:
        with open(fname, mode='r', encoding='utf-8') as feedsjson:
            feeds = json.load(feedsjson)

        feeds.append(dict)
        with open(fname, mode='w', encoding='utf-8') as f:
            f.write(json.dumps(feeds, indent=2))

    except Exception as file_exception:
        print(str(file_exception))
