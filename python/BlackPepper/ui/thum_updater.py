import sys
import re
from PySide2 import QtWidgets, QtCore
import os
import glob
import subprocess
import gazu
import random


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

    def upload_thumnail(self):
        # Gazu 서버에 로그인합니다.
        # gazu.login("http://192.168.3.116/login", "pipeline@rapa.org", "netflixacademy")
        gazu.set_host("http://192.168.3.116/api")
        gazu.log_in("pipeline@rapa.org", "netflixacademy")

        project_name = "hoon"

        asset_name = "groot"

        shot_name = "0020"

        image_path = "/home/rapa/thumbnail.jpg"

        project = gazu.project.get_project_by_name(project_name)
        print("1111", project["name"], project["id"])

        asset = gazu.asset.get_asset_by_name(project["id"], asset_name)
        print("2222", asset["name"], asset["id"])

        shot = next((s for s in gazu.asset.all_shot(asset["id"]) if s["name"] == shot_name), None)
        print("3333", shot)

        if shot is None:
            print(f"No shot named {shot_name} found for asset {asset_name}")
            exit(1)

        image = gazu.files.update_preview(image_path)

        gazu.shots.attach_image(shot["id"], image["id"])

    def find_jpg(self):

        folder_path = "/home/rapa/"

        # 폴더 내에 있는 파일 중 JPG 파일만 리스트로 가져옵니다.
        file_list = [f for f in os.listdir(folder_path) if f.endswith(".jpg")]

        if len(file_list) == 0:
            print(f"No JPG files found in {folder_path}")
            exit(1)

        # 파일 리스트에서 랜덤으로 선택합니다.
        random_file = random.choice(file_list)

        # 선택된 파일의 전체 경로를 출력합니다.
        random_file_path = os.path.join(folder_path, random_file)
        print(random_file_path)


def main():
    m = thumnail_pusher()
    m.find_jpg()
    m.upload_thumnail()


if __name__ == "__main__":
    main()
