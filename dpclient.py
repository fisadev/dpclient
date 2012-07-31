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


def data_operation(f, *args, **kargs):
    '''Data operation, read data before and saves data after.'''
    def new_f(self, *args, **kargs):
        self._read_data()
        result = f(self, *args, **kargs)
        self._save_data()
        return result
    return new_f


class DpClient(object):
    def __init__(self, data_file):
        self.data_file = data_file
        self._read_data()

    def _read_data(self):
        '''Read stored data.'''
        if not os.path.exists(self.data_file):
            self.data = INITIAL_DATA
            self._save_data()
        json_data = json.loads(open(self.data_file).read())
        self.data = bunchify(json_data)

    def _save_data(self):
        '''Save data.'''
        with open(self.data_file, 'w') as f:
            f.write(json.dumps(self.data))

    @data_operation
    def config(self, server, user, password):
        self.data.server = server
        self.data.user = user
        self.data.password = password
        return 'Config saved'

