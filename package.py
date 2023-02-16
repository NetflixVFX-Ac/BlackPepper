# -*- coding: utf-8 -*-

name = 'Hook'
version = '1.0.0'
authors = ['Sungwoo Park', 'Sunjun Park', '진광 박', '열훈 윤', '재혁 이', '원규 리', '수경 유']
requires = [
    'python', 'gazu',
]
variants = [
    ['platform-linux', 'python'],
]

def commands():
    env.PATH.append("{root}/bin")
    env.PYTHONPATH.prepend("{root}/python")


format_version = 1
