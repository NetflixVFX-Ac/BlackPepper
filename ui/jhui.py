import sys

import gazu.project
from PySide2 import QtWidgets, QtCore, QtUiTools
from hook.python.pepper.pepper import Houpub


class pepper_login(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.login_ui = QtUiTools.QUiLoader().load("/home/rapa/login.ui")
        self.main_ui = QtUiTools.QUiLoader().load("/home/rapa/main.ui")

    def setup_ui(self):
        self.setCentralWidget(self.login_ui)
        self.setWindowTitle("UI TEST")
        self.show()
        self.login_ui.login_btn.clicked.connect(lambda: self.check_id())

    def check_id(self):
        user_id = self.login_ui.input_id.text()
        user_pw = self.login_ui.input_pw.text()
        host = "http://192.168.3.116/api"
        pepper = Houpub()
        pepper.login(host, user_id, user_pw)
        print(gazu.project.get_project_by_name("PEPPER"))
        self.next_ui()

    def next_ui(self):
        self.setCentralWidget(self.main_ui)
        self.setWindowTitle("UI TEST")
        self.show()


def main():
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QtWidgets.QApplication()
    p_login = pepper_login()
    p_login.setup_ui()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
