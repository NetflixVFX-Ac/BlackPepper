# -*- coding: utf-8 -*-

name = 'Hook'
version = '0.0.1'
authors = ['Sunjun Park', 'Sungwoo Park', 'Jinkwang Park', 'Yeolhoon Yoon', 'Jaehyuk Lee', 'Wongyu Lee']
requires = [
    'python', 'gazu', 'hou'
]
variants = [
    ['platform-linux', 'python'],
]

def commands():
    env.PYTHONPATH.prepend("{root}/python")


format_version = 1
