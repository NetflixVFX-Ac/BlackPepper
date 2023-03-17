import logging
import os


class Logger:
    """
    이 모듈은 BlackPepper를 사용해서 발생할 수 있는 문제나 사용자의 접속, 퍼플리싱에 대한 정보를 기록하는 역할을 한다.
    모든 정보는 .config의 log파일로 저장된다.
    """

    def __init__(self):
        self.log = None
        self.dir_path = ''
        self.home_path()

    def home_path(self):
        """ log정보가 저장될 root path를 설정해준다. 만약 없을 경우 생성도 해준다.

        Examples:
            Logger.home_json_path()

        Raises:
            OSError: 'Failed to create the directory.'
        """
        now_path = os.path.realpath(__file__)
        split_path = now_path.split('/')[:-2]
        self.dir_path = os.path.join('/'.join(split_path), '.config')
        if not os.path.exists(self.dir_path):
            try:
                os.makedirs(self.dir_path)
            except OSError:
                raise ValueError('Failed to create the directory.')

    def set_logger(self, ident):
        """id를 root log로 설정하고 Log에 대한 기본 handler를 만든다. log파일에 나올 정보의 format을 정해주고 stream handler,
        file handler에 log의 레벨을 부여해서 기록되도록한다.

        Examples:
            Looger.set_logger("pipeline@rapa.org")

        Args:
            ident(str): user id
        """
        self.log = logging.getLogger(ident)
        if len(self.log.handlers) == 0:
            formatting = logging.Formatter('%(asctime)s - %(name)s %(levelname)s : %(message)s')
            self.log.setLevel(logging.DEBUG)

            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatting)
            stream_handler.setLevel(logging.INFO)
            self.log.addHandler(stream_handler)

            file_handler = logging.FileHandler(os.path.join(self.dir_path, 'hook_login.log'))
            file_handler.setFormatter(formatting)
            file_handler.setLevel(logging.DEBUG)
            self.log.addHandler(file_handler)

    def connect_log(self, host_url):
        """host가 존재할 경우, host에 잘 연결이 되었는가에 대한 정보를 기록한다.

        Examples:
            Logger.connect_log("http://192.168.3.116/api")

        Args:
            host_url(str): host url
        """
        if host_url:
            self.log.debug(f"successful connection to {host_url}")
        else:
            raise Exception(f'{host_url} not exists')

    def enter_log(self, user_name):
        """id가 존재하고 해당 id의 연결성공을 기록한다.

         Examples:
             Logger.enter_log("pipeline@rapa.org")

        Args:
            user_name(str):  user id
        """
        if user_name:
            self.log.debug(f"{user_name}: log-in succeed")
        else:
            self.exists_error(user_name)

    def failed_log(self):
        """kitsu에 host가 잘 연결됐는지 확인하고 실패시 로그를 남긴다.

        Examples:
            Logger.failed_log()
        """
        self.log.debug("Failed Connection")

    def tree_log(self, pro):
        """projec의 tree가 update됐을 경우 로그를 남긴다.

        Examples:
            Logger.tree_log(project)

        Args:
            pro(dict): project dict
        """
        project_name = pro['name']
        if project_name:
            self.log.debug(f"File Tree of {project_name}updated")
        else:
            self.exists_error(project_name)

    def publish_working_file_log(self, task_type_name):
        """working file을 publish했을 경우 로그를 남긴다.

        Examples:
            Logger.publish_working_file_log('FX')

        Args:
            task_type_name(str): 'FX', 'layout'....
        """
        if task_type_name:
            self.log.debug(f"publish {task_type_name} working file, last revision up")
        else:
            self.exists_error(task_type_name)

    def publish_output_file_log(self, task_type_name, output_type_name):
        """output file을 publish 할 경우 log를 남긴다.

        Examples:
            Logger.publish_output_file_log('layout', 'abc')

        Args:
            task_type_name(str): 'FX', 'layout'....
            output_type_name(str):  'Movie_file', 'mpeg-4', 'jpeg', ...
        """
        if task_type_name and output_type_name:
            self.log.debug(f'publish {task_type_name}, {output_type_name} output file, last revision up')
        else:
            self.exists_error(task_type_name, output_type_name)

    @staticmethod
    def exists_error(*names):
        """name의 존재 유무에 대해 물어본다.

        Examples:
            Logger.exists_error('PEPPER')

        Args:
            *names(str): exists information
        """
        if len(names) >= 2:
            for name in names:
                raise Exception(f'{name}not exists.')
        else:
            raise Exception(f'{names}not exists.')