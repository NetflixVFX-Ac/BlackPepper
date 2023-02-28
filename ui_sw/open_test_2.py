import sys
from PySide2 import QtWidgets, QtUiTools, QtCore
from pepper import Houpub

"""
id :
pepper@hook.com
pw :
pepperpepper
"""

loader = QtUiTools.QUiLoader()
host = "http://192.168.3.116/api"
login_path = "/ui_sw/ui_test/login.ui"
main_path = "/ui_sw/ui_test/main.ui"


class Pepi(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.login_ui = loader.load(login_path)
        self.main_ui = loader.load(main_path)

    def setup_ui(self):
        self.setWindowTitle("pepper v0.0.1 sw")
        self.show()
        self.login_ui.login_btn.clicked.connect(self.set_login)

    def set_login(self):

        email = self.login_ui.input_id.text()
        pw = self.login_ui.input_pw.text()
        sel_software = self.login_ui.hipbox.currentText()[1:]

        pepper = Houpub()
        pepper.login(host, email, pw)
        pepper.software = sel_software
        print("login 성공")
        self.main_ui()

    def main_ui(self):
        self.login_ui = loader.load(main_path)
        self.set_project()
        self.login_ui.show()

    def set_project(self):
        # self.listWidget = []
        pepper = Houpub()
        self.project_list = pepper.get_my_projects()
        print(self.project_list)
        # self.ui.listWidget.setText(self.project_list)
        # self.listWidget.textSet(self.project_list)
        # line_edit text 값 가져오기
        # self.ui.listWidget.setText(self.project_list)  # label에 text 설정하기


def main():
    app = QtWidgets.QApplication()
    # app.setWindowIcon(QtGui.QIcon(':/icon/counter.ico'))
    main = Pepi()
    main.set_login()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

