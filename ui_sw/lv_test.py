import sys
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import QWidget
from PySide2.QtCore import Qt, QFile
from PySide2.QtUiTools import QUiLoader

import Model



class TodoModel(QtCore.QAbstractListModel):
    def __init__(self, *args, todos=None, **kwargs):
        super(TodoModel, self).__init__(*args, **kwargs)
        self.todos = todos or []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            text = self.todos[index.row()]
            return text

        # if role == Qt.DecorationRole:
        #     text = self.todos[index.row()]
        #     if text:
        #         return text

    def rowCount(self, index):
        return len(self.todos)


# second open main ui
class MainWindow():
    def __init__(self):
        super().__init__()

        self.model = TodoModel()

        # main Ui loder
        main_ui_file = "main.ui"
        mainUi = QtCore.QFile(main_ui_file)
        mainUi.open(QtCore.QFile.ReadOnly)
        loader = QUiLoader()
        self.window_main = loader.load(mainUi)
        self.window_main.show()


        # self.window_main.lv_proj.setModel(self.model)

# first open login ui
class LoginWindow():
    def __init__(self):
        super().__init__()
        self.model = TodoModel()

        # login Ui loder
        login_ui_file = "login.ui"
        loginUi = QtCore.QFile(login_ui_file)
        loginUi.open(QtCore.QFile.ReadOnly)
        loader = QUiLoader()
        self.window_login = loader.load(loginUi)
        self.window_login.show()

        # get login data
        email = self.window_login.input_id.text()
        pw = self.window_login.input_pw.text()
        software_ext = self.window_login.hipbox.currentText()[1:]
        pepm = Model.PepM()
        pepm.login_data(email, pw, sel_software=software_ext)

        # view connect
        # self.window_login.login_btn.clicked.connect(self.second_window)
        self.show()

        # self.window_login.login_btn.pressed.connect(self.set_project)


        # self.window_main.login_btn.pressed.connect(self.delete)

    def second_window(self):


        # login 하면 로그인창 close 되고 로그인정보에 어사인된 프로젝트리스트가져오는 함수 까지 작동
        # self.window_login.close()
        # self.set_project()
        # pepm = Model.PepM()
        # project_list = pepm.get_project()
        # for list in project_list:
        #     self.model.todos.append(list)
            # self.model.layoutChanged.emit()
            # self.window_main.lv_proj.clearSelection()

        window_2 = MainWindow()
        window_2.exec_()



    # def set_project(self):
    #     pepm = Model.PepM()
    #     project_list = pepm.get_project()
    #     for list in project_list:
    #         self.model.todos.appendRow(list)
    #         self.model.layoutChanged.emit()
    #         self.window_main.lv_proj.clearSelection()
        # self.window_main.lv_proj.setModel(self.model)


# QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
app = QtWidgets.QApplication(sys.argv)
window = LoginWindow()

app.exec_()
