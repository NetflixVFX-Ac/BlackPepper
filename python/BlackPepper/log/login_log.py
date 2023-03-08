import logging
import os


class Logger:
    def __init__(self):
        self.log = None
        self.dir_path = os.path.expanduser('~/.config/Hook')
        if not os.path.exists(self.dir_path):
            try:
                os.makedirs(self.dir_path)
            except OSError:
                raise ValueError('Failed to create the directory.')

        self.set_logger()

    def set_logger(self):
        self.log = logging.getLogger('hook')

        if len(self.log.handlers) == 0:
            formatting = logging.Formatter('%(asctime)s - %(levelname)s : %(message)s')
            self.log.setLevel(logging.DEBUG)

            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatting)
            stream_handler.setLevel(logging.INFO)
            self.log.addHandler(stream_handler)

            file_handler = logging.FileHandler(os.path.join(self.dir_path, 'hook_log.log'))
            file_handler.setFormatter(formatting)
            file_handler.setLevel(logging.DEBUG)
            self.log.addHandler(file_handler)

    def connect_log(self, host_url):
        if host_url:
            self.log.debug(f"successful connection to {host_url}")

    def enter_log(self, user_name):
        if user_name:
            self.log.debug(f"{user_name}: log-in succeed")

    def failed_log(self):
        self.log.debug("Failed Connection")

    def tree_log(self, pro):
        if pro:
            self.log.debug(f"{pro}'s File Tree updated")

    def publish_working_file_log(self, task_type_name):
        if task_type_name:
            self.log.debug()

    # def create_working_file_log(self, user_name, working_file):
    #     if os.path.exists(working_file):
    #         self.log.debug("\"%s\" create houdini file in \"%s\"" % (user_name, working_file))
    #         else:
    #         self.log.warning("\"%s\" failed to create Maya file" % user_name)

    # def load_output_file_log(self, user_name, output_file_path):
    #     return self.log.debug("\"%s\" load output file from \"%s\"" % (user_name, output_file_path))