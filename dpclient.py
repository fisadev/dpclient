import os
import json
from bunch import bunchify
from browser import DotProjectBot

DATA_FILE = os.path.expanduser('~/.dpclient')
INITIAL_DATA = {
        'user': '',
        'password': '',
        'server': '',
        'tasks': []
}


def read_data():
    '''Read stored data.'''
    if not os.path.exists(DATA_FILE):
        save_data(INITIAL_DATA)
    json_data = json.loads(open(DATA_FILE).read())
    return bunchify(json_data)


def save_data(data):
    '''Save data.'''
    with open(DATA_FILE, 'w') as f:
        f.write(json.dumps(data))
