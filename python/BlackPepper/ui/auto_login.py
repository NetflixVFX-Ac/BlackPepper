from BlackPepper.log.moduler_log import Logger
from BlackPepper.pepper import Houpub
import os
import json
import gazu


class Auto_log:
    def __init__(self):
        """
        이 모듈은 precomp를 하기 위한 login을 할 때 전에 login한 기록이 있다면 자동으로 로그인을 도와준다. \n
        login 정보의 경우 json파일에 'auto'라는 이름의 key값으로 저장되며 해당 값에는 host, id, password, auto login이력의 정보가 적혀있다.
        해당모듈은 ui가 실행하면 작동한다.
        """
        self.hklog = Logger()
        self.pr = Houpub()

        self.user_dict = {}

        self._user = None
        self._host = None
        self._user_id = None
        self._user_pw = None
        self._user_ext = None
        self._valid_host = False
        self._valid_user = False

        self._auto_login = False

        self.dir_path = ''
        self.user_path = ''

        self.home_json_path()

        self.access_setting()

    @property
    def valid_host(self):
        return self._valid_host

    @valid_host.setter
    def valid_host(self, value):
        """웹에 연결된 host에 대한 연결상태를 True, False로 기록한다. True의 경우 연결이 된 것이고, False의 경우는 연결이 되지 않은 것이다.

        Examples:
            Auto_log.valid_host = Ture

        Args:
            value: True or False

        Returns:
            True or False

        """
        self._valid_host = value

    @property
    def valid_user(self):
        return self._valid_user

    @valid_user.setter
    def valid_user(self, value):
        """host를 연결하고 ui에서 적은 id와 password의 연결 된 적이 있는지 파악하는 역할을 한다. 이력이 있으면 True를 가지고
        없다면 False를 가진다.

        Examples:
            Auto_log.valid_user = True

        Args:
            value: True or False

        Returns:
            True or False
        """
        self._valid_user = value

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, hos):
        """ host의 정보를 받아온다.

        Auto_log.host = "http://192.168.3.116/api"

        Args:
            hos(str): host url

         Raises:
            ConnectionError: Host ip에 다른 값이 있을 때
            ServerErrorException: Host의 주소가 맞지 않을 때

        """
        self._host = hos

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, uid):
        """ id 정보를 받아온다.

        Examples:
            Auto_log.user_id = "pipeline@rapa.org"

        Args:
            uid(str): user id

        Raises:
            AuthFailedException: id가 맞지 않을 때
        """
        self._user_id = uid

    @property
    def user_pw(self):
        return self._user_pw

    @user_pw.setter
    def user_pw(self, upw):
        """password 정보를 받아온다.

        Examples:
            Auto_log.user_pw = "netflixacademy"

        Args:
            upw(str): user password

        Raises:
            AuthFailedException: password가 맞지 않을 때
        """
        self._user_pw = upw

    @property
    def user_ext(self):
        return self._user_ext

    @user_ext.setter
    def user_ext(self, ext):
        """houdini의 extension을 hip, hipnc, hiplc타입을 가져온다.

        Examples:
            Auto_log.user_ext = 'hip'

        Args:
            ext(str): 'hip', 'hipnc', or 'hiplc'

        Raises:
            Exception: If software_name is not hip, hipnc, or hiplc.
        """
        self._user_ext = ext

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, us):
        """user의 id의 full_name정보를 가져오기 위해 사용한다.

        Examples:
            Auto_log.user = Hou_pub.user['user']

        Args:
            us(dict): user information

        Returns:
            user information dict

        Raises:
            AuthFailedException: id나 password가 맞지 않을 때
        """
        self._user = us

    @property
    def auto_login(self):
        return self._auto_login

    @auto_login.setter
    def auto_login(self, tr):
        """auto login의 성공여부를 True 혹은 False로 나타낸다.

        Args:
            tr: True or False

        Returns:
            True or False
        """
        self._auto_login = tr

    def home_json_path(self):
        """auto login을 할 수 있는 json 파일의 생성경로를 지정한다. 파일의 root는 현재 python 파일이 위치한 곳으로 한다.

        Examples:
            home_json_path()
        """
        now_path = os.path.realpath(__file__)
        split_path = now_path.split('/')[:-2]
        self.dir_path = os.path.join('/'.join(split_path), '.config')
        self.user_path = os.path.join(self.dir_path, 'user.json')

    def connect_login(self):
        """


        """
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
        self.user = log_in['user']
        self._valid_user = True
        self.save_setting()
        self.hklog.enter_log(self.user['full_name'])
        return True

    def log_out(self):
        gazu.log_out()
        self.user = None
        self.reset_setting()
        return True

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
            if 'auto' not in self.user_dict:
                self.save_setting()
                return
            else:
                for auto_value in self.user_dict['auto']:
                    return auto_value

    def save_setting(self):
        self.user_dict['auto'] = []
        self.user_dict['auto'].append({
            'host': self.host,
            'user_id': self.user_id,
            'user_pw': self.user_pw,
            'user_ext': self.user_ext,
            'valid_host': self.valid_host,
            'valid_user': self.valid_user,
            'auto_login': self.auto_login
        })
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
