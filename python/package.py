# -*- coding: utf-8 -*-

name = 'Black Pepper'
version = '0.0.1'
authors = ['Sunjun Park', 'Sungwoo Park', 'Jinkwang Park', 'Yeolhoon Yoon', 'Jaehyuk Lee', 'Wongyu Lee']
requires = [
    'gazu', 'hou', 'ffmpeg', 'houdini',
]
variants = [
    ['platform-linux', 'Pyhton3.9', 'houdini 19.5'],
]


def commands():
    env.PYTHONPATH.prepend("{root}/BlackPepper")


format_version = 1
