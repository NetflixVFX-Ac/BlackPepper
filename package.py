# -*- coding: utf-8 -*-

name = 'BlackPepper'

version = '0.0.1'

authors = ['Sunjun Park', 'Sungwoo Park', 'Jinkwang Park', 'Yeolhoon Yoon', 'Wongyu Lee', 'Jaehyuk Lee']

requires = [
    'gazu', 'PySide2'
]
variants = [
    ['platform-linux', 'python-3.9', 'houdini-19.5.493'],
]


def commands():
    env.PATH.append("{root}/bin")
    env.PYTHONPATH.prepend("{root}/python")


format_version = 1
