import sys
import re
from PySide2 import QtWidgets, QtCore
import os
import glob
import subprocess


def find_mov():
    dir_path = '/home/rapa'

    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith('.mov'):
                file_path = os.path.join(root, file)
                file_path = '"' + file_path + '"'
                print(file_path)


find_mov()


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


thumnail_machine()

def upload_thumnail_to_kitsu():
