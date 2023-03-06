import sys
from PySide2 import QtCore, QtWidgets
from PySide2.QtUiTools import QUiLoader
from model import PepperModel
from view import PepperView
from pepper import Houpub


class PepperWindow:
    def __init__(self):
        self.project_model = PepperModel()
        self.template_model = PepperModel()
        self.shot_model = PepperModel()
        self.render_model = PepperModel()
        self.pepper = Houpub()

        self.projects_listview = PepperView(self)
        self.templates_listview = PepperView(self)
        self.shots_listview = PepperView(self)
        self.renderlists_listview = PepperView(self)
        self.shots_listview.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.renderlists_listview.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.projects_selection = None
        self.templates_selection = None
        self.shots_selection = None
        self.renderlists_selection = None

        self.login_ui = QtCore.QFile('mvc_login.ui')
        self.login_ui.open(QtCore.QFile.ReadOnly)
        self.login_ui_loader = QUiLoader()

        self.main_ui = QtCore.QFile('mvc_main.ui')
        self.main_ui.open(QtCore.QFile.ReadOnly)
        self.main_ui_loader = QUiLoader()

        self.window = self.login_ui_loader.load(self.login_ui)
        self.window.show()
        self.window.login_btn.clicked.connect(self.user_login)
        # self.window.input_id.returnPressed.connect(self.window.login_btn.clicked.connect(self.user_login))
        # self.window.input_pw.returnPressed.connect(self.window.login_btn.clicked.connect(self.user_login))

        self.my_projects = []
        self.all_assets = []
        self.all_shots = []

    def user_login(self):
        user_id = self.window.input_id.text()
        user_pw = self.window.input_pw.text()
        user_software = self.window.hipbox.currentText()[1:]
        host = "http://192.168.3.116/api"

        self.pepper.login(host, user_id, user_pw)
        self.pepper.software = user_software
        self.main_window()

    def main_window(self):
        self.window = self.main_ui_loader.load(self.main_ui)

        self.window.gridLayout_3.addWidget(self.projects_listview, 2, 0)
        self.window.gridLayout_3.addWidget(self.templates_listview, 2, 1)
        self.window.gridLayout_3.addWidget(self.shots_listview, 2, 2)
        self.window.gridLayout_3.addWidget(self.renderlists_listview, 2, 5)

        self.projects_listview.setModel(self.project_model)
        self.templates_listview.setModel(self.template_model)
        self.shots_listview.setModel(self.shot_model)
        self.renderlists_listview.setModel(self.render_model)
        self.projects_selection = self.projects_listview.selectionModel()
        self.templates_selection = self.templates_listview.selectionModel()
        self.shots_selection = self.shots_listview.selectionModel()
        self.renderlists_selection = self.renderlists_listview.selectionModel()

        self.my_projects = self.pepper.get_my_projects()
        for my_project in self.my_projects:
            self.project_model.pepperlist.append(my_project)

        self.window.show()
        self.projects_listview.clicked.connect(self.project_selected)
        self.templates_listview.clicked.connect(self.template_selected)
        self.shots_listview.clicked.connect(self.shot_selected)
        self.window.reset_btn.clicked.connect(self.clear_list)
        self.window.render_btn.clicked.connect(self.render_execute)
        self.window.append_btn.clicked.connect(self.append_render_list)
        self.window.del_btn.clicked.connect(self.delete_render_list)

        # slot -> clicked, connect
        # signal -> emit

    def project_selected(self, event):
        project_name = self.my_projects[event.row()]
        self.pepper.project = project_name
        self.all_assets = self.pepper.get_all_assets()
        self.template_model.pepperlist.clear()
        self.shot_model.pepperlist.clear()
        for asset in self.all_assets:
            self.template_model.pepperlist.append(asset)
        self.template_model.layoutChanged.emit()
        self.shot_model.layoutChanged.emit()
        self.templates_selection.clear()
        self.shots_selection.clear()
        self.renderlists_selection.clear()

    def template_selected(self, event):
        template_name = self.all_assets[event.row()]
        self.pepper.asset = template_name
        name, time, rev = self.pepper.get_working_file_data('simulation', 'asset')
        self.window.template_info_label.setText(f"Artist : {name}, Created Time : {time}, Revision : {rev}")
        self.all_shots = self.pepper.get_casting_path_for_asset()
        self.shot_model.pepperlist.clear()
        for shot in self.all_shots:
            self.shot_model.pepperlist.append(shot['sequence_name'] + '_' + shot['shot_name'])
        self.shot_model.layoutChanged.emit()
        self.shots_selection.clear()
        self.renderlists_selection.clear()

    def shot_selected(self, event):
        shot_dict = self.all_shots[event.row()]
        self.pepper.sequence = shot_dict['sequence_name']
        self.pepper.shot = shot_dict['shot_name']
        name, time, rev = self.pepper.get_output_file_data('camera_cache', 'layout', 'shot')
        self.window.shot_info_label.setText(f"Artist : {name}, Created Time : {time}, Revision : {rev}")
        self.renderlists_selection.clear()

    def append_render_list(self):
        for idx in self.shots_selection.selectedRows():
            shot_dict = self.all_shots[idx.row()]
            self.pepper.make_precomp_dict(shot_dict)
        self.render_model.pepperlist.clear()
        for render in self.pepper.precomp_list:
            self.render_model.pepperlist.append(render['name'])
        self.render_model.layoutChanged.emit()
        self.shots_selection.clear()
        self.renderlists_selection.clear()

    def delete_render_list(self):
        for idx in self.renderlists_selection.selectedRows():
            self.pepper.delete_precomp_dict(idx.data())
        self.render_model.pepperlist.clear()
        for render in self.pepper.precomp_list:
            self.render_model.pepperlist.append(render['name'])
        self.render_model.layoutChanged.emit()
        self.renderlists_selection.clear()

    def clear_list(self):
        self.pepper.precomp_list = []
        self.render_model.pepperlist.clear()
        self.render_model.layoutChanged.emit()

    def render_execute(self):
        print(self.pepper.precomp_list)
        return self.pepper.precomp_list



def main():
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QtWidgets.QApplication(sys.argv)
    window = PepperWindow()
    app.exec_()


if __name__ == "__main__":
    main()
