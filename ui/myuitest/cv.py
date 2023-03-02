import sys
from PySide2 import QtCore, QtWidgets
from PySide2.QtUiTools import QUiLoader
from hook.ui.myuitest import model
from hook.ui.myuitest.view import PepperView
from hook.python.pepper.pepper import Houpub

# class ProjectView(QtWidgets.QListView):
#     def __init__(self, parent):
#         super(ProjectView, self).__init__(parent=None)
#
#     def get_selected_project(self):
#         if not self.model():
#             return
#         return self.model().selectedIndexes()[-1]


class MainWindow:
    def __init__(self):
        self.project_model = model.PepperModel()
        self.template_model = model.PepperModel()
        self.shot_model = model.PepperModel()
        self.render_model = model.PepperModel()
        self.pepper = Houpub()

        self.projects_listview = PepperView(self)
        self.templates_listview = PepperView(self)
        self.shots_listview = PepperView(self)
        self.renderlists_listview = PepperView(self)
        self.shots_listview.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.shots_listview.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.projects_selection = None
        self.templates_selection = None

        login_ui_path = '/home/rapa/login.ui'
        self.login_ui = QtCore.QFile(login_ui_path)
        self.login_ui.open(QtCore.QFile.ReadOnly)
        self.login_ui_loader = QUiLoader()

        main_ui_path = '/home/rapa/main.ui'
        self.main_ui = QtCore.QFile(main_ui_path)
        self.main_ui.open(QtCore.QFile.ReadOnly)
        self.main_ui_loader = QUiLoader()

        self.window = self.login_ui_loader.load(self.login_ui)
        self.window.show()
        self.window.login_btn.clicked.connect(lambda: self.login())

        self.my_projects = []
        self.all_assets = []
        self.all_shots = []

        # self.window = self.main_ui_loader.load(self.main_ui)
        # self.window.lv_proj.setModel(self.project_model)
        # self.window.lv_temp.setModel(self.template_model)
        # self.window.lv_shot.setModel(self.shot_model)
        # self.window.lv_rend.setModel(self.render_model)
        # self.pepper = Houpub()
        # self.pepper.login("http://192.168.3.116/api", "pipeline@rapa.org", "netflixacademy")
        # ppp = self.pepper.get_self.my_projects()
        # for i in ppp:
        #     self.project_model.projects.append(i)
        #     self.template_model.templates.append(i)
        #     self.shot_model.shots.append(i)
        #     self.render_model.renders.append(i)
        # self.window.addButton.pressed.connect(self.add)

    def login(self):
        user_id = self.window.input_id.text()
        user_pw = self.window.input_pw.text()
        user_software = self.window.hipbox.currentText()[1:]
        host = "http://192.168.3.116/api"

        self.pepper.login(host, user_id, user_pw)
        self.pepper.software = user_software
        self.main()

    def main(self):
        self.window = self.main_ui_loader.load(self.main_ui)

        self.window.gridLayout_3.addWidget(self.projects_listview, 2, 0)
        self.window.gridLayout_3.addWidget(self.templates_listview, 2, 1)
        self.window.gridLayout_3.addWidget(self.shots_listview, 2, 2)
        self.window.gridLayout_3.addWidget(self.renderlists_listview, 2, 5)

        self.projects_listview.setModel(self.project_model)
        self.projects_selection = self.projects_listview.selectionModel()
        self.templates_listview.setModel(self.template_model)
        self.templates_selection = self.templates_listview.selectionModel()
        self.shots_listview.setModel(self.shot_model)
        self.renderlists_listview.setModel(self.render_model)

        self.my_projects = self.pepper.get_my_projects()
        for my_project in self.my_projects:
            self.project_model.pepperlist.append(my_project)

        self.window.show()
        self.projects_listview.clicked.connect(self.project_selected)
        self.templates_listview.clicked.connect(self.template_selected)
        self.shots_listview.clicked.connect(self.shot_selected)
        self.window.reset_btn.clicked.connect(self.clear_list)

        # slot -> clicked, connect
        # signal -> emit
        # self.window.lwg_templates.itemClicked.connect(s
        #     lambda: self.assign_template(self.all_assets[self.window.lwg_templates.currentRow()]))
        # self.window.lwg_shots.itemClicked.connect(
        #     lambda: self.assign_shots(self.all_shots[self.window.lwg_shots.currentRow()]))

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

    def template_selected(self, event):
        template_name = self.all_assets[event.row()]
        self.pepper.asset = template_name
        self.all_shots = self.pepper.get_casting_path_for_asset()
        self.shot_model.pepperlist.clear()
        for shot in self.all_shots:
            self.shot_model.pepperlist.append(shot['sequence_name'] + '_' + shot['shot_name'])
        self.shot_model.layoutChanged.emit()

    def shot_selected(self, event):
        shot_dict = self.all_shots[event.row()]
        print(shot_dict)
        self.pepper.make_precomp_dict(shot_dict)
        self.render_model.pepperlist.clear()
        for render in self.pepper.precomp_list:
            self.render_model.pepperlist.append(render['name'])
        self.render_model.layoutChanged.emit()

    def clear_list(self):
        self.pepper.precomp_list = []
        self.render_model.pepperlist.clear()
        self.render_model.layoutChanged.emit()


QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
app.exec_()

