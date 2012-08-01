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
        'tasks': {}
}


def read_data(f, *args, **kargs):
    '''Read data before action.'''
    def new_f(self, *args, **kargs):
        self._read_data()
        result = f(self, *args, **kargs)
        return result
    return new_f

def save_data(f, *args, **kargs):
    '''Save data after action.'''
    def new_f(self, *args, **kargs):
        result = f(self, *args, **kargs)
        self._save_data()
        return result
    return new_f


class DpClient(object):
    def __init__(self, data_file):
        self.data_file = data_file

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

    @read_data
    @save_data
    def set_config(self, setting, value):
        self.data[setting] = value
        return '%s saved in config' % setting

    @read_data
    def config(self, setting=None):
        if setting:
            return '%s: %s' % (setting, self.data[setting])
        else:
            settings = []
            for s in ['server', 'user', 'password']:
                settings.append('%s: %s' % (s, self.data[s]))
            return '\n'.join(settings)

    @read_data
    @save_data
    def add_task(self, task_id, task_name):
        if task_id not in self.data.tasks and \
           task_name not in self.data.tasks.values():
            self.data.tasks[task_id] = task_name

    @read_data
    def tasks(self):
        result = 'Tasks:\n'
        result += '\n'.join('%s:%s' % (t_id, t_name)
                            for t_id, t_name in self.data.tasks.items())
        return result

