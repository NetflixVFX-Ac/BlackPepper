# -*- coding: utf-8 -*-

name = 'H O O K'

version = '0.0.1'

authors = ['Sunjun Park', 'Sungwoo Park', 'Jinkwang Park', 'Yeolhoon Yoon', 'Wongyu Lee', 'Jaehyuk Lee']

requires = [
    'gazu', 'hou', 'ffmpeg'
]
variants = [
    ['platform-linux', 'pyhton-3.9', 'houdini 19.5'],
]

tools = ['Black Pepper']


def commands():
    env.PATH.append("{root}/bin")
    env.PYTHONPATH.prepend("{root}/python")


format_version = 1
