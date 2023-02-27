"""

Controller.py

View : "login.ui, main.ui"

"""

"""
email:
pepper@hook.com
pw :
pepperpepper
"""



import sys
from PySide2.QtUiTools import QUiLoader
from PySide2 import QtWidgets, QtCore

import Model


class PepC(QtWidgets.QMainWindow):

    def __init__(self, loginUi_file, mainUi_file):
        super(PepC, self).__init__()
        self.setup_ui(loginUi_file, mainUi_file)

    def setup_ui(self, loginUi_file, mainui_file):
        loginUi = QtCore.QFile(loginUi_file)
        loginUi.open(QtCore.QFile.ReadOnly)

        loader = QUiLoader()
        self.login_ui = loader.load(loginUi)
        self.main_ui = loader.load(mainui_file)
        loginUi.close()

        # setUI
        # login UI
        self.login_ui.login_btn.clicked.connect(self.set_login)
        self.login_ui.setWindowTitle("Pepper Login v0.0.1 SW")
        self.login_ui.show()

        # main UI

        self.main_ui.setWindowTitle("Pepper Main v0.0.1 SW")
        self.main_ui.show()

    def set_login(self):

        email = self.login_ui.input_id.text()
        pw = self.login_ui.input_pw.text()
        software_ext = self.login_ui.hipbox.currentText()[1:]
        pepm = Model.PepM()
        pepm.login_model(email, pw, sel_software=software_ext)

        self.set_main()


    def set_main(self):
        pepm = Model.PepM()
        proj_list = pepm.main_model()


def main():
    #   QApplication을 생성하기 전에 AA_ShareOpenGLContexts를 설정하여 수정
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QtWidgets.QApplication(sys.argv)
    myapp = PepC("login.ui", "main.ui")
    # mymain = PepC("main.ui")
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()