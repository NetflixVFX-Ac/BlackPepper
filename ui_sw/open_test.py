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
login_path = "/home/rapa/git/hook/ui_sw/login.ui"
main_path = "/home/rapa/git/hook/ui_sw/main.ui"


class Pepi(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super(Pepi, self).__init__()
        self.ui = loader.load(login_path)
        self.ui.show()
        self.setup_ui()

    def setup_ui(self):
        # self.ui.action_Quit.triggered.connect(app.quit)
        self.ui.login_btn.clicked.connect(self.login_ui)
        # self.ui.comboBox.clicked.connect(self.hipbox)
        # self.ui.listWidget.setText(self.project_list)


    def login_ui(self):
        email = self.ui.input_id.text()
        pw = self.ui.input_pw.text()
        pepper = Houpub()
        pepper.login(host, email, pw)
        print("login 성공")
        self.main_ui()

    def main_ui(self):
        self.ui = loader.load(main_path)
        self.set_project()
        self.ui.show()

    def set_project(self):
        self.listWidget = []
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
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

