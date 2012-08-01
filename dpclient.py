#!/usr/bin/python
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
BASIC_HELP = 'usage: dp <action> <params>'
ACTIONS_HELP = 'actions: help, config, task, log'


def read_data(f, *args, **kargs):
    '''Read data before action.'''
    def new_f(self, *args, **kargs):
        self._read_data()
        result = f(self, *args, **kargs)
        return result
    new_f.__doc__ = f.__doc__
    return new_f

def save_data(f, *args, **kargs):
    '''Save data after action.'''
    def new_f(self, *args, **kargs):
        result = f(self, *args, **kargs)
        self._save_data()
        return result
    new_f.__doc__ = f.__doc__
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
    def config(self, setting=None, value=None):
        if setting:
            if value:
                self.data[setting] = value
                return '%s saved in config' % setting
            else:
                return '%s: %s' % (setting, self.data[setting])
        else:
            result = []
            result.extend('%s: %s' % (s, self.data[s])
                          for s in ['server', 'user', 'password'])
            return '\n'.join(result)

    @read_data
    @save_data
    def task(self, task_id=None, name=None):
        if task_id:
            if name:
                self.data.tasks[task_id] = name
                return 'task saved'
            else:
                return '%s: %s' % (task_id, self.data.tasks[task_id])
        else:
            result = ['tasks:', ]
            result.extend('%s: %s' % (t_id, t_name)
                          for t_id, t_name in self.data.tasks.items())
            return '\n'.join(result)

    @read_data
    def log(self, date, hours, task_id, description):
        raise NotImplementedError()

    def help(self, action=None):
        if action and action != 'help':
            if self._is_action(action):
                return 'usage: dp %s' % getattr(self, action).__doc__
            else:
                return 'unknown action "%s"' % action
                print ACTIONS_HELP
        else:
            return 'usage: dp help <action>\n' + ACTIONS_HELP

    def _is_action(self, action):
        return action in dir(self) and callable(getattr(self, action))

if __name__ == '__main__':
    dpc = DpClient(DEFAULT_DATA_FILE)

    if len(sys.argv) == 1:
        print BASIC_HELP
        print ACTIONS_HELP
    else:
        action = sys.argv[1]
        if dpc._is_action(action):
            action_method = getattr(dpc, action)
            print action_method(*sys.argv[2:])
        else:
            print 'unknown action "%s"' % action
            print BASIC_HELP
            print ACTIONS_HELP
