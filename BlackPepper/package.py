# -*- coding: utf-8 -*-

name = 'Hook'
version = '0.0.1'
authors = ['Sunjun Park', 'Sungwoo Park', 'Jinkwang Park', 'Yeolhoon Yoon', 'Jaehyuk Lee', 'Wongyu Lee']
requires = [
    'BlackPepper', 'gazu', 'hou'
]
variants = [
    ['platform-linux', 'BlackPepper'],
]

def commands():
    env.PYTHONPATH.prepend("{root}/BlackPepper")


format_version = 1
