"""

Controller.py

View : "login.ui, main.ui"

"""

"""

pepper@hook.com
pepperpepper

pipeline@rapa.org
netflixacademy
"""



import sys


from PySide2.QtUiTools import QUiLoader
from PySide2 import QtWidgets, QtCore
from PySide2.QtGui import QStandardItem, QStandardItemModel


import Model


class PepC(QtWidgets.QListView):

    def __init__(self, loginUi_file, mainUi_file):
        super(PepC, self).__init__()
        self.setup_ui(loginUi_file, mainUi_file)

    def setup_ui(self, loginUi_file, mainui_file):
        loginUi = QtCore.QFile(loginUi_file)
        loginUi.open(QtCore.QFile.ReadOnly)

        loader = QUiLoader()
        self.login_ui = loader.load(loginUi)
        self.main_ui = loader.load(mainui_file)
        # loginUi.close()

        # set login UI
        self.login_ui.login_btn.clicked.connect(self.set_login)
        self.login_ui.setWindowTitle("Pepper Login v0.0.1 SW")
        self.login_ui.show()

        # set main UI
        self.main_ui.setWindowTitle("Pepper Main v0.0.1 SW")
        self.main_ui.show()

        self.main_ui.project_list.itemClicked.connect(self.set_temp)
        # self.main_ui.project_list.currentItem()
    def set_login(self):
        # get login data
        email = self.login_ui.input_id.text()
        pw = self.login_ui.input_pw.text()
        software_ext = self.login_ui.hipbox.currentText()[1:]
        pepm = Model.PepM()
        pepm.login_data(email, pw, sel_software=software_ext)

        # login 하면 로그인창 close 되고 로그인정보에 어사인된 프로젝트리스트가져오는 함수 까지 작동
        self.login_ui.close()
        self.set_project()

    def set_project(self):
        pepm = Model.PepM()
        project_list = pepm.get_project()
        model = QStandarditemModel()

        for item in project_list:
            model.appendRow(QStandardItem(item))
        self.main_ui.list.listView_proj.setModel(model)



        # self.main_ui.project_list.clear()
        # self.main_ui.project_list.addItems(proj_list)

        # temp_list = pepm.get_temp(project_name)
        # self.main_ui.temp_list.clear()
        # self.main_ui.temp_list.addItems(temp_list)
        # self.main_ui.show()

    def set_clear(self):
        pass



    def set_temp(self, projects=None):
        pepm = Model.PepM()
        project_name = projects[self.main_ui.project_list.currentRow()]
        print(project_name)
        # temps = pepm.get_temp(project_name)
        # print(temps)



    #
    #     self.main_ui.temp_list.clear()
    #     self.main_ui.temp_list.addItems(temp_list)
    #     # self.main_ui.show()

    def set_shot(self):
        pass


def main():
    #   QApplication을 생성하기 전에 AA_ShareOpenGLContexts를 설정하여 수정
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QtWidgets.QApplication(sys.argv)
    myapp = PepC("login.ui", "main.ui")
    # mymain = PepC("main.ui")
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()