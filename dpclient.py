import os
import sys
import json
from bunch import bunchify
from browser import DotProjectBot

DEFAULT_DATA_FILE = os.path.expanduser('~/.dpclient')
INITIAL_DATA = {
        'user': '',
        'password': '',
        'server': '',
        'tasks': []
}


class DpClient(object):
    def __init__(self, data_file):
        self.data_file = data_file

    def read_data(self):
        '''Read stored data.'''
        if not os.path.exists(self.data_file):
            self.save_data(INITIAL_DATA)
        json_data = json.loads(open(self.data_file).read())
        return bunchify(json_data)

    def save_data(self, data):
        '''Save data.'''
        with open(self.data_file, 'w') as f:
            f.write(json.dumps(data))

