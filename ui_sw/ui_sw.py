import sys
# import os
from PySide2 import QtWidgets, QtUiTools, QtCore
# from pepper import Houpub

"""
id :
pepper@hook.com
pw :
pepperpepper

M V C class 로 나눠보기

"""



class PepperModel(QtWidgets.QWidget):

    def __init__(self, data):
        super().__init__()
        self._data = data

        # path
        login_path = "/home/rapa/git/hook/ui_sw/login.ui"
        main_path = "/home/rapa/git/hook/ui_sw/main.ui"

        # Load UI file login & main
        loader = QtUiTools.QUiLoader()
        self.login_ui = loader.load(login_path)
        # self.main_ui = loader.load(main_path)
        # get UI elements
        # self.setCentralWidget(login_ui)
        # self.setWindowTitle("login_tset")
        # self.show()

    def openLogin(self):
        self.setCentralWidget(self.login_ui)
        self.setWindowTitle("login_tset")
        self.show()

# class PepperVeiw(QtWidgets.QListView):
#
#
#
#
#
#
#
# class PepperController():
#     pass



def main():
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QtWidgets.QApplication()
    a = PepperModel()
    a.openLogin()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

