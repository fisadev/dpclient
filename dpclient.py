#!/usr/bin/python
import os
import sys
import json
from datetime import datetime
from bunch import bunchify
from browser import DotProjectBot

DEFAULT_DATA_FILE = os.path.expanduser('~/.dpclient')
DATE_FORMAT = '%d/%m/%Y'
INITIAL_DATA = {
        'user': '',
        'password': '',
        'server': '',
        'tasks': {}
}
BASIC_HELP = 'usage: dp <action> <params>'
ACTIONS_HELP = 'actions: help, config, task, log'
SETTINGS = ('server', 'user', 'password')


def strip_lines(text):
    return '\n'.join(l.strip() for l in text.strip().split('\n'))


def read_data(f, *args, **kargs):
    '''Read data before action decorator.'''
    def new_f(self, *args, **kargs):
        self._read_data()
        result = f(self, *args, **kargs)
        return result
    new_f.__doc__ = f.__doc__
    return new_f


def save_data(f, *args, **kargs):
    '''Save data after action decorator.'''
    def new_f(self, *args, **kargs):
        result = f(self, *args, **kargs)
        self._save_data()
        return result
    new_f.__doc__ = f.__doc__
    return new_f


class DpClient(object):
    '''Dot Project command line client.'''

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
        '''
        config                   : show all settings
        config <setting>         : show single setting
        config <setting> <value> : save value into a setting

        settings: server, user, password
        '''
        if setting:
            if setting not in SETTINGS:
                return 'unknown setting "%s", see: dp help config' % setting
            if value:
                self.data[setting] = value.strip()
                return 'setting "%s" saved' % setting
            else:
                return '%s: %s' % (setting, self.data[setting])
        else:
            result = []
            result.extend('%s: %s' % (s, self.data[s])
                          for s in SETTINGS)
            return '\n'.join(result)

    @read_data
    @save_data
    def task(self, name=None, dot_project_id=None):
        '''
        task                         : show all known tasks
        task <name>                  : show single task
        task <name> <dot_project_id> : save task to known tasks
        '''
        if name:
            if dot_project_id:
                self.data.tasks[name.strip()] = dot_project_id.strip()
                return 'task "%s" saved' % name
            else:
                if name in self.data.tasks:
                    return '%s: %s' % (name, self.data.tasks[name])
                else:
                    return 'unknown task "%s", see: dp task' % name
        else:
            result = ['tasks:', ]
            result.extend('%s: %s' % (name, dp_id)
                          for name, dp_id in self.data.tasks.items())
            return '\n'.join(result)

    @read_data
    def log(self, date, hours, task, description):
        '''
        log <date> <hours> <task> <description>

        date is in dd/MM/yyyy format
        hours is in decimal unit (example: 1:15 hours would be 1.25)
        task is a known task name (see: dp help task)
        '''
        try:
            date = datetime.strptime(date, DATE_FORMAT)
        except ValueError:
            return 'wrong formated date "%s", see: dp help log' % date
        if task not in self.data.tasks:
            return 'unknown task "%s", see: dp task' % task
        if any(not bool(self.data[s]) for s in SETTINGS):
            return 'not all settings configured, see: dp config'
        bot = DotProjectBot(self.data.server)
        bot.login(self.data.user, self.data.password)
        bot.log_task(self.data.tasks[task],
                     date,
                     hours,
                     description)
        return 'Log created'

    def help(self, action=None):
        '''You really like recursion, don't you?'''
        if action:
            if self._is_action(action):
                return strip_lines(getattr(self, action).__doc__)
            else:
                return 'unknown action "%s"' % action
                print ACTIONS_HELP
        else:
            return 'help <action>\n' + ACTIONS_HELP

    def _is_action(self, action):
        '''Find if an action exists.'''
        return action in dir(self) and \
               not action.startswith('_') and \
               callable(getattr(self, action))


if __name__ == '__main__':
    dpc = DpClient(DEFAULT_DATA_FILE)

    if len(sys.argv) == 1:
        print BASIC_HELP
        print ACTIONS_HELP
    else:
        action = sys.argv[1]
        if dpc._is_action(action):
            action_method = getattr(dpc, action)
            try:
                print action_method(*sys.argv[2:])
            except TypeError as err:
                if 'arguments' in err.message:
                    print 'wrong parameters, see: dp help %s' % action
                else:
                    raise err
        else:
            print 'unknown action "%s"' % action
            print BASIC_HELP
            print ACTIONS_HELP
