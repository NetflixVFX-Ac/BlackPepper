import sys
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import QWidget
from PySide2.QtCore import Qt, QFile
from PySide2.QtUiTools import QUiLoader

from pepper import Houpub
from Model import MainModel


class MainWindow:
    def __init__(self):
        super().__init__()

        self.pepper = Houpub()
        # model loader
        self.model_proj = MainModel()
        self.model_temp = MainModel()
        self.model_shot = MainModel()
        self.model_render = MainModel()




        # login Ui loader
        login_ui_file = "login.ui"
        loginUi = QtCore.QFile(login_ui_file)
        loginUi.open(QtCore.QFile.ReadOnly)
        loader = QUiLoader()
        self.window_login = loader.load(loginUi)
        self.window_login.show()

        # main Ui loder
        main_ui_file = "main.ui"
        mainUi = QtCore.QFile(main_ui_file)
        mainUi.open(QtCore.QFile.ReadOnly)
        loader = QUiLoader()
        self.window_main = loader.load(mainUi)
        self.window_main.show()

        # set connect Ui

        self.window_login.login_btn.clicked.connect(self.set_login)

    def set_login(self):
        host = "http://192.168.3.116/api"
        email = self.window_login.input_id.text()
        pw = self.window_login.input_pw.text()
        software_ext = self.window_login.hipbox.currentText()[1:]
        self.get_login(email, pw, sel_software=software_ext)

    def get_login(self, email, pw, sel_software):
        self.host = "http://192.168.3.116/api"
        self.email = email
        self.pw = pw

        self.pepper.login(self.host, email, pw)
        self.pepper.software = sel_software
        print(f"login id : {email} , seleted software : {sel_software}")
        self.window_login.close()
        self.set_main()

    def set_main(self):
        self.window_main.lv_proj.setModel(self.model_proj)
        get_projects = self.pepper.get_my_projects()
        print(get_projects)
        for get_project in get_projects:
            self.model_proj.append(get_project)
        self.window_main.show()


QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
app.exec_()
