import sys

import gazu
from PySide2 import QtWidgets, QtCore, QtUiTools
from hook.python.pepper.pepper import Houpub


class pepper_login(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.pepper = Houpub()
        self.login_ui = QtUiTools.QUiLoader().load("/home/rapa/login.ui")
        self.main_ui = QtUiTools.QUiLoader().load("/home/rapa/main.ui")

    def setup_ui(self):
        self.setCentralWidget(self.login_ui)
        self.setWindowTitle("pepper v0.0.1")
        self.show()
        self.login_ui.login_btn.clicked.connect(lambda: self.check_id())

    def check_id(self):
        user_id = self.login_ui.input_id.text()
        user_pw = self.login_ui.input_pw.text()
        user_software = self.login_ui.hipbox.currentText()[1:]
        host = "http://192.168.3.116/api"

        self.pepper.login(host, user_id, user_pw)
        self.pepper.software = user_software
        print(self.pepper.software)
        self.open_main_ui()

    def open_main_ui(self):
        self.setCentralWidget(self.main_ui)
        self.setWindowTitle("pepper v0.0.1")
        self.show()
        self.run_main()

    # def run_main(self):
    #     all_projects = self.pepper.get_all_projects()
    #     self.main_ui.listwidget


def main():
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QtWidgets.QApplication()
    p_login = pepper_login()
    p_login.setup_ui()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
