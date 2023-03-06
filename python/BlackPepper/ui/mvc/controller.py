import sys
import os
from PySide2 import QtCore, QtWidgets
from PySide2.QtUiTools import QUiLoader
from BlackPepper.ui.mvc.model import PepperModel
from BlackPepper.ui.mvc.view import PepperView
from BlackPepper.pepper import Houpub


class PepperWindow:
    def __init__(self):
        """이 모듈은 pepper를 통해 얻어 온 kitsu 상의 template asset과 casting 된 shot들의 정보들을 UI를 통해 보여준다.
        UI 모듈은 controller, model, view로 분리되어 있고, mvc_login, mvc_main의 .ui 파일이 UI 데이터를 가지고 있다. \n
        메인 UI의 4개 model은 PepperModel에서 가져오며, ListView는 PepperView에서 가져온다.
        여러 개의 shot들을 한번에 선택해 조정할 수 있도록 shots와 rendelistes의 view는 ExtendedSelection으로 설정했다. \n
        PepperWindow 실행 시 self.login_ui가 우선 실행된다.
        """
        QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
        self.app = QtWidgets.QApplication(sys.argv)
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

        script_path = os.path.dirname(os.path.realpath(__file__))
        self.login_ui = QtCore.QFile(os.path.join(script_path, 'mvc_login.ui'))
        self.login_ui.open(QtCore.QFile.ReadOnly)
        self.login_ui_loader = QUiLoader()

        self.main_ui = QtCore.QFile(os.path.join(script_path, 'mvc_main.ui'))
        self.main_ui.open(QtCore.QFile.ReadOnly)
        self.main_ui_loader = QUiLoader()

        self.login_window = self.login_ui_loader.load(self.login_ui)
        self.login_window.show()
        self.login_window.login_btn.clicked.connect(self.user_login)
        self.login_window.input_id.returnPressed.connect(self.user_login)
        self.login_window.input_pw.returnPressed.connect(self.user_login)

        self.window = self.main_ui_loader.load(self.main_ui)
        self.my_projects = []
        self.all_assets = []
        self.all_shots = []

        self.app.exec_()

    def user_login(self):
        """mvc_login.ui를 디스플레이 해주는 메소드. 유저의 로그인 페이지 UI에서 Login 버튼 클릭, Enter 입력 시 실행된다. \n
        UI에서는 id, password를 입력받고, combobox를 통해 Houdini의 license 종류를 입력받는다. \n
        host는 http://192.168.3.116/api 로 고정되어 있다.
        입력받은 id, password 값을 pepper의 login 메소드를 통해 kitsu에 로그인한다.
        로그인 성공 시 입력받은 Houdini license 종류가 pepper의 self.software에 set 된다.
        이후 self.main_window가 바로 실행되어 pepper의 메인 UI가 디스플레이 된다.
        """
        user_id = self.login_window.input_id.text()
        user_pw = self.login_window.input_pw.text()
        user_software = self.login_window.hipbox.currentText()[1:]
        host = "http://192.168.3.116/api"

        self.pepper.login(host, user_id, user_pw)
        self.pepper.software = user_software
        self.main_window()

    # def enter_login(self, event):
    #     user_id = self.window.input_id.text()

    def main_window(self):
        """mvc_main.ui를 디스플레이 해주는 메소드. 로그인 성공 시 실행된다. \n
        projects, templates, shots, render_lists의 네 가지 부분으로 나뉘어 있다. \n
        projects 에서는 로그인 된 유저가 assign 되어있는 project들을 projects_listview에 디스플레이 해준다.
        templates 에서는 선택된 project 안의 fx templates를 templates_listview에 디스플레이 해준다.
        shots 에서는 선택된 fx template가 casting 된 shots를 shots_listview에 디스플레이 해준다.
        renderlists 에서는 Houdini로 넘겨 precomp를 진행할 shot들을 renderlists_listview에 디스플레이 해준다. \n
        renderlists는 pepper.precomp_list에 담긴 shot 들의 name의 value 값만 보여주는 것이고,
        render 버튼 클릭 시 pepper.precomp_list 속 dict를 Houdini로 전달한다.
        """
        self.login_window.close()

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
        """projects_listview 클릭 시 실행되는 메소드. \n
        선택한 project의 fx template들을 pepper.project에 set 한 뒤, self.all_assets에 fx template 들을 받아온다.
        가져온 fx template들을 templates_listview에 디스플레이 해준다.
        다른 project 클릭 시 templates_listview를 clear 한 뒤 같은 방법으로 templates_listview에 fx templates들을 디스플레이 해준다.
        template가 설정되어 있을 경우에는 shots_listview도 clear 해준다.

        Args:
            event: Listview click event
        """
        # self.pepper.project = event.data()
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
        """templates_listview 클릭 시 실행되는 메소드. \n
        선택한 template이 casting된 shot들을 self.all_shots에 받아온다.
        가져온 shot들을 shots_listview에 디스플레이 해준다.
        다른 template 클릭 시 shots_listview를 clear 한 뒤 같은 방법으로 shots_listview에 shot들을 디스플레이 해준다.

        Args:
            event: Listview click event
        """
        # self.pepper.asset = event.data()
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
    window = PepperWindow()


if __name__ == "__main__":
    main()
