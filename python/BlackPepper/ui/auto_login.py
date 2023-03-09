from BlackPepper.log.login_log import Logger
from BlackPepper.pepper import Houpub
import os
import json
import gazu


class Auto_log:
    def __init__(self):
        self.hklog = Logger()
        self.pr = Houpub()

        self.user_dict = None

        self._user = None
        self._host = None
        self._user_id = None
        self._user_pw = None
        self._user_ext = None
        self._valid_host = False
        self._valid_user = False

        self._auto_login = False

        self.dir_path = os.path.expanduser('~/.config/Hook/')
        self.user_path = os.path.join(self.dir_path, 'user.json')

        self.access_setting()

    @property
    def valid_host(self):
        return self._valid_host

    @valid_host.setter
    def valid_host(self, value):
        self._valid_host = value

    @property
    def valid_user(self):
        return self._valid_user

    @valid_user.setter
    def valid_user(self, value):
        self._valid_user = value

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, hos):
        self._host = hos

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, uid):
        self._user_id = uid

    @property
    def user_pw(self):
        return self._user_pw

    @user_pw.setter
    def user_pw(self, upw):
        self._user_pw = upw

    @property
    def user_ext(self):
        return self._user_ext

    @user_ext.setter
    def user_ext(self, ext):
        self._user_ext = ext

    @property
    def user(self):
        return self._user

    @property
    def auto_login(self):
        return self._auto_login

    @auto_login.setter
    def auto_login(self, value):
        self._auto_login = value

    def connect_login(self):
        self.pr.login(self.host, self.user_id, self.user_pw)
        self.pr.software = self.user_ext
        self.hklog.set_logger(self.user_id)
        if not gazu.client.host_is_valid():
            self.hklog.failed_log()
            raise ValueError('Invalid host URL.')
        self.save_setting()
        self.hklog.connect_log(self.host)
        self._valid_host = True
        self.save_setting()
        try:
            log_in = self.pr.user
        except gazu.AuthFailedException:
            raise ValueError('Invalid user ID or password.')
        self._user = log_in['user']
        self._valid_user = True
        self.save_setting()
        self.hklog.enter_log(self.user['full_name'])
        return True

    def log_out(self):
        gazu.log_out()
        self._user = None
        self.reset_setting()
        return True

    def access_setting(self):
        if not os.path.exists(self.dir_path):
            try:
                os.makedirs(self.dir_path)
            except OSError:
                raise ValueError("Failed to create the directory.")
        try:

            if os.path.exists(self.user_path):
                self.load_setting()
                if self.user_id != self.user_dict['user_id'] or self.user_pw != self.user_dict['user_pw'] or self.user_ext != self.user_dict['user_ext']:
                    self.reset_setting()
            if not os.path.exists(self.user_path):
                self.reset_setting()
        except OSError:
            raise ValueError("Failed to create user.json file.")
        return True

    def load_setting(self):
        with open(self.user_path, 'r') as json_file:
            self.user_dict = json.load(json_file)
        return self.user_dict

    def save_setting(self):
        self.user_dict = {
            'host': self.host,
            'user_id': self.user_id,
            'user_pw': self.user_pw,
            'user_ext': self.user_ext,
            'valid_host': self.valid_host,
            'valid_user': self.valid_user,
            'auto_login': self.auto_login
        }
        with open(self.user_path, 'w') as json_file:
            json.dump(self.user_dict, json_file)

    def reset_setting(self):
        self.host = ''
        self.user_id = ''
        self.user_pw = ''
        self.valid_host = False
        self.valid_user = False
        self.auto_login = False

        self.save_setting()
