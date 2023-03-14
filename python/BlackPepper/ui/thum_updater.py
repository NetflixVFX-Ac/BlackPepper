import sys
import re
from PySide2 import QtWidgets, QtCore
import os
import glob
import subprocess
import gazu

class thumnail_pusher():

    def find_mov(self):
        dir_path = '/home/rapa'

        for root, dirs, files in os.walk(dir_path):
            for file in files:
                if file.endswith('.mov'):
                    file_path = os.path.join(root, file)
                    file_path = '"' + file_path + '"'
                    print(file_path)


    def thumnail_machine(self):
        input = "/home/rapa/dog_convert.mov"
        output = "/home/rapa/thumbnail_004.jpg"
        ffmpeg_path = "/mnt/pipeline/app/ffmpeg-5.1.1-i686-static/ffmpeg"

        command = [
            ffmpeg_path,
            "-i", input,
            "-ss 00:00:10",
            "-vframes 1",
            "-y",
            "-loglevel", "debug",
            output
        ]

        cmd = (' '.join(str(s) for s in command))
        result = subprocess.run(cmd, shell=True, check=True)


    def upload_thumnail_to_kitsu(self):
        # Gazu 서버에 로그인합니다.
        # gazu.login("http://192.168.3.116/login", "pipeline@rapa.org", "netflixacademy")
        self.set_auto_login()

        project_name = "hoon"

        asset_name = "groot"

        shot_name = "0020"

        image_path = "/home/rapa/thumbnail.jpg"

        project = gazu.project.get_by_name(project_name)

        asset = gazu.asset.get_by_name(project["id"], asset_name)
        print(asset)

        shot = next((s for s in gazu.asset.get_shots(asset["id"]) if s["name"] == shot_name), None)

        if shot is None:
            print(f"No shot named {shot_name} found for asset {asset_name}")
            exit(1)

        image = gazu.files.upload(image_path)

        gazu.shots.attach_image(shot["id"], image["id"])



    def set_auto_login(self):
        log_path = self.login_log.user_path
        self.login_log.host = "http://192.168.3.116/api"
        log_id = self.login_window.input_id.text()
        log_pw = self.login_window.input_pw.text()
        log_sfw = self.login_window.hipbox.currentText()[1:]
        log_value = self.login_log.load_setting()
        log_dict = self.login_log.user_dict
        if os.path.exists(log_path) and (not log_dict['auto'] or log_id != log_value['user_id']
                                         or log_pw != log_value['user_pw'] or log_sfw != log_value['user_ext']):
            self.login_log.user_id = log_id
            self.login_log.user_pw = log_pw
            self.login_log.user_ext = log_sfw
            self.login_log.valid_host = True
            self.login_log.valid_user = True
            self.login_log.auto_login = True
            self.login_log.save_setting()
            return
        if log_value['valid_host'] and log_value['valid_user']:
            self.login_log.host = log_value['host']
            self.login_log.user_id = log_value['user_id']
            self.login_log.user_pw = log_value['user_pw']
            self.login_log.user_ext = log_value['user_ext']
            self.pepper.login(self.login_log.host, self.login_log.user_id, self.login_log.user_pw)
            self.pepper.software = self.login_log.user_ext
            self.login_window.close()
            self.open_main_window()
        else:
            pass


thumnail_pusher.upload_thumnail_to_kitsu()