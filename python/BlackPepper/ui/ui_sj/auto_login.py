from BlackPepper.log.login_log import Logger
from BlackPepper.pepper import Houpub as hp
import logging
import os
import json
import gazu


class Autolog:
    def __init__(self):
        self.hklog = Logger()
        self.pr = hp()

        self.user_dict = None

        self._user = None
        self._host = None
        self._user_id = None
        self._user_pw = None
        self._valid_host = False
        self._valid_user = False

        self.dir_path = os.path.expanduser('~/.config/Hook/')
        self.user_path = os.path.join(self.dir_path, 'user.json')

        if self.access_setting():
            self.load_setting()

    @property
    def valid_host(self):
        return self._valid_host

    @property
    def valid_user(self):
        return self._valid_user

    @property
    def host(self):
        return self._host

    @property
    def user(self):
        return self._user

    def connect_gazu(self, try_host, try_id, try_pw):
        if not gazu.client.host_is_valid():
            raise ValueError('Invalid host URL.')
        if not self._valid_host:
            raise ValueError('Host to login is not connected.')
        self.pr.login(try_host, try_id, try_pw)
        self._host = gazu.get_host()
        self._valid_host = True
        self.save_setting()
        self.hklog.connect_log(self.host)
        log_in = gazu.log_in(try_id, try_pw)
        self._user = log_in['user']
        self._user_id = try_id
        self._user_pw = try_pw
        self._valid_user = True
        self.save_setting()
        self.hklog.enter_log(self.user['full_name'])
        return True

    def log_out(self):
        gazu.log_out()
        self._user = None
        self.reset_setting()

    def access_setting(self):
        if not os.path.exists(self.dir_path):
            try:
                os.makedirs(self.dir_path)
            except OSError:
                raise ValueError("Failed to create the directory.")
        try:
            if not os.path.exists(self.user_path):
                self.reset_setting()
        except OSError:
            raise ValueError("Failed to create user.json file.")
        return True

    def load_setting(self):
        with open(self.user_path, 'r') as json_file:
            self.user_dict = json.load(json_file)
        if self.user_dict['valid_host'] and self.user_dict['valid_user']:
            self.connect_gazu(self.user_dict['host'], self.user_dict['user_id'], self.user_dict['user_pw'])

    def save_setting(self):
        self.user_dict = {
            'host': self.host,
            'user_id': self._user_id,
            'user_pw': self._user_pw,
            'valid_host': self.valid_host,
            'valid_user': self.valid_user,
        }
        with open(self.user_path, 'w') as json_file:
            json.dump(self.user_dict, json_file)

    def reset_setting(self):
        self._host = ''
        self._user_id = ''
        self._user_pw = ''
        self._valid_host = False
        self._valid_user = False

        self.save_setting()
