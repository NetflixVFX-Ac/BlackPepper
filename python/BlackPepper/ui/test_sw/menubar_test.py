import os
import glob
from PySide2.QtWidgets import QMainWindow, QApplication, QAction, QMenuBar

class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 메뉴바 생성
        menu_bar = self.menuBar()

        # 파일 메뉴 생성
        file_menu = menu_bar.addMenu('File')

        # 디렉토리 경로 설정
        directory_path = '/BlackPepper/ui/ui_sw'

        # 디렉토리에 있는 JSON 파일 경로를 생성일 기준으로 정렬
        json_files = sorted(glob.glob(os.path.join(directory_path, '*.json')), key=os.path.getmtime, reverse=True)[:5]

        # 최신 파일 5개만 선택
        # latest_files = json_files[-5:]

        # 선택된 파일들을 순서대로 QAction로 추가
        for file_path in json_files:
            action = QAction(os.path.basename(file_path), self)
            action.triggered.connect(lambda _, path=file_path: self.handle_file(path))
            file_menu.addAction(action)

    def handle_file(self, file_path):
        # TODO: 파일 내용 처리하기

        pass

if __name__ == '__main__':
    app = QApplication([])
    main_window = MyMainWindow()
    main_window.show()
    app.exec_()
