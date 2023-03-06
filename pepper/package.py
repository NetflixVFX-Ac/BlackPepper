# -*- coding: utf-8 -*-

name = 'Hook'
version = '0.0.1'
authors = ['Sunjun Park', 'Sungwoo Park', 'Jinkwang Park', 'Yeolhoon Yoon', 'Jaehyuk Lee', 'Wongyu Lee']
requires = [
    'pepper', 'gazu', 'hou'
]
variants = [
    ['platform-linux', 'pepper'],
]

def commands():
    env.PYTHONPATH.prepend("{root}/pepper")


format_version = 1
