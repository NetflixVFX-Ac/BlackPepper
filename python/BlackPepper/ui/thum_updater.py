import sys
import re
from PySide2 import QtWidgets, QtCore
import os
import glob
import subprocess
import os
import random

def find_mov():
    dir_path = '/home/rapa'

    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith('.mov'):
                file_path = os.path.join(root, file)
                file_path = '"' + file_path + '"'
                print(file_path)



def thumnail_machine():
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



def select_jpg():
    folder_path = "/home/rapa"

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


select_jpg()