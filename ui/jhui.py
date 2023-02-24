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

    def run_main(self):
        projects = self.pepper.get_all_projects()
        print(projects)
        self.main_ui.lwg_projects.clear()
        self.main_ui.lwg_projects.addItems(projects)
        self.main_ui.lwg_projects.itemClicked.connect(
            lambda: self.assign_project(projects[self.main_ui.lwg_projects.currentRow()]))
        self.main_ui.lwg_templates.itemClicked.connect(
            lambda: self.castedshots_get(self.all_assets[self.main_ui.lwg_templates.currentRow()]))

    def assign_project(self, project_name):
        self.pepper.project = project_name
        self.all_assets = self.pepper.get_all_assets()
        print(self.all_assets)
        self.main_ui.lwg_templates.clear()
        self.main_ui.lwg_shots.clear()
        self.main_ui.lwg_templates.addItems(self.all_assets)

    def castedshots_get(self, template_name):
        self.pepper.asset = template_name
        all_shots, _, _ = self.pepper.get_casting_path_for_asset()
        print(all_shots)
        self.main_ui.lwg_shots.clear()
        for shot in all_shots:
            self.main_ui.lwg_shots.addItem(shot['shot_name'])


def main():
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QtWidgets.QApplication()
    p_login = pepper_login()
    p_login.setup_ui()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
