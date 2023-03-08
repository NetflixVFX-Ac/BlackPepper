import sys
import os
from PySide2 import QtCore, QtWidgets
from PySide2.QtUiTools import QUiLoader
from BlackPepper.ui.model import PepperModel
from BlackPepper.ui.view import PepperView
from BlackPepper.pepper import Houpub
from BlackPepper.houpepper import HouPepper
from BlackPepper.ui.ui_sj.auto_login import Auto_log


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
        self.pepper = Houpub()
        self.login_log = Auto_log()
        self.projects_selection = None
        self.templates_selection = None
        self.shots_selection = None
        self.renderlists_selection = None
        self.my_projects = []
        self.all_assets = []
        self.all_shots = []
        # model instance
        self.project_model = PepperModel()
        self.template_model = PepperModel()
        self.shot_model = PepperModel()
        self.render_model = PepperModel()
        # listview instance
        self.projects_listview = PepperView(self)
        self.templates_listview = PepperView(self)
        self.shots_listview = PepperView(self)
        self.renderlists_listview = PepperView(self)
        self.shots_listview.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.renderlists_listview.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        # setModel
        self.projects_listview.setModel(self.project_model)
        self.templates_listview.setModel(self.template_model)
        self.shots_listview.setModel(self.shot_model)
        self.renderlists_listview.setModel(self.render_model)
        self.projects_selection = self.projects_listview.selectionModel()
        self.templates_selection = self.templates_listview.selectionModel()
        self.shots_selection = self.shots_listview.selectionModel()
        self.renderlists_selection = self.renderlists_listview.selectionModel()
        # get script_path
        # __file__ (전역변수) : 현재 열려있는 파일의 위치와 이름을 가지고 있는 문자열 변수
        # path.realpath(파일이름) : 현재 파일의  표준 경로+이름 을 반환
        script_path = os.path.dirname(os.path.realpath(__file__))
        # login Ui loader
        login_ui = QtCore.QFile(os.path.join(script_path, 'mvc_login.ui'))
        login_ui.open(QtCore.QFile.ReadOnly)
        self.login_ui_loader = QUiLoader()
        self.login_window = self.login_ui_loader.load(login_ui)
        self.login_window.show()
        # main Ui loader
        main_ui = QtCore.QFile(os.path.join(script_path, 'mvc_main.ui'))
        main_ui.open(QtCore.QFile.ReadOnly)
        self.main_ui_loader = QUiLoader()
        self.main_window = self.main_ui_loader.load(main_ui)
        # set connect login Ui
        self.login_window.login_btn.clicked.connect(self.user_login)
        self.login_window.input_id.returnPressed.connect(self.user_login)
        self.login_window.input_pw.returnPressed.connect(self.user_login)
        # set connect main Ui
        self.projects_listview.clicked.connect(self.project_selected)
        self.templates_listview.clicked.connect(self.template_selected)
        self.shots_listview.clicked.connect(self.shot_selected)
        self.main_window.reset_btn.clicked.connect(self.clear_list)
        self.main_window.render_btn.clicked.connect(self.render_execute)
        self.main_window.append_btn.clicked.connect(self.append_render_list)
        self.main_window.del_btn.clicked.connect(self.delete_render_list)
        self.main_window.logout_btn.clicked.connect(self.user_logout)
        # add listview to ui
        self.main_window.gridLayout_3.addWidget(self.projects_listview, 2, 0)
        self.main_window.gridLayout_3.addWidget(self.templates_listview, 2, 1)
        self.main_window.gridLayout_3.addWidget(self.shots_listview, 2, 2)
        self.main_window.gridLayout_3.addWidget(self.renderlists_listview, 2, 5)
        log_value = self.login_log.load_setting()
        if log_value['valid_host'] and log_value['valid_user']:
            self.login_log.host = log_value['host']
            self.login_log.user_id = log_value['user_id']
            self.login_log.user_pw = log_value['user_pw']
            self.pepper.login(self.login_log.host, self.login_log.user_id, self.login_log.user_pw)
            self.login_window.close()
            self.open_main_window()
        else:
            pass
        # app.exec_() : 프로그램을 대기상태,즉 무한루프상태로 만들어준다.
        self.app.exec_()

    def user_login(self):
        """mvc_login.ui를 디스플레이 해주는 메소드. 유저의 로그인 페이지 UI에서 Login 버튼 클릭, Enter 입력 시 실행된다. \n
        UI에서는 id, password를 입력받고, combobox를 통해 Houdini의 license 종류를 입력받는다. \n
        host는 http://192.168.3.116/api 로 고정되어 있다.
        입력받은 id, password 값을 pepper의 login 메소드를 통해 kitsu에 로그인한다.
        로그인 성공 시 입력받은 Houdini license 종류가 pepper의 self.software에 set 된다.
        이후 self.main_window가 바로 실행되어 pepper의 메인 UI가 디스플레이 된다.
        """
        self.login_log.host = "http://192.168.3.116/api"
        self.login_log.user_id = self.login_window.input_id.text()
        self.login_log.user_pw = self.login_window.input_pw.text()
        user_software = self.login_window.hipbox.currentText()[1:]

        if self.login_log.connect_gazu():
            self.pepper.software = user_software
            self.login_log.auto_login = True
            self.login_log.save_setting()
            self.login_window.close()
            self.open_main_window()

    def user_logout(self):
        if self.login_log.connect_gazu():
            self.login_log.log_out()
            self.main_window.close()
            self.login_window.show()

    def open_main_window(self):
        """mvc_main.ui를 디스플레이 해주는 메소드. 로그인 성공 시 실행된다. \n
        projects, templates, shots, render_lists의 네 가지 부분으로 나뉘어 있다. \n
        projects 에서는 로그인 된 유저가 assign 되어있는 project들을 projects_listview에 디스플레이 해준다.
        templates 에서는 선택된 project 안의 fx templates를 templates_listview에 디스플레이 해준다.
        shots 에서는 선택된 fx template가 casting 된 shots를 shots_listview에 디스플레이 해준다.
        renderlists 에서는 Houdini로 넘겨 precomp를 진행할 shot들을 renderlists_listview에 디스플레이 해준다. \n
        renderlists는 pepper.precomp_list에 담긴 shot 들의 name의 value 값만 보여주는 것이고,
        render 버튼 클릭 시 pepper.precomp_list 속 dict를 Houdini로 전달한다.
        """
        # get my project
        self.my_projects = self.pepper.get_my_projects()
        for my_project in self.my_projects:
            self.project_model.pepperlist.append(my_project)
        self.main_window.show()

    def project_selected(self, event):
        """projects_listview 의 project 를 클릭 시 실행 되는 메소드. \n
        클릭한 project 의 fx template 들을 pepper.project 에 set 한 뒤 self.all_assets 에 fx template 들을 받아 온다.
        그리고 가져온 fx template 들을 templates_listview 에 display 해준다.

        또, 기존과 다른 project 클릭 시 templates_listview 를 clear 한 뒤 클릭 된
        project 의 fx templates 들을 templates_listview 에 display 해준다.
        재 선택 시 Templates, Shots, Render files 의 selectionModel 들을 clear 해준다.

        Args:
            event: Listview click event
        """

        # event
        project_name = self.my_projects[event.row()]
        self.pepper.project = project_name
        self.all_assets = self.pepper.get_all_assets()
        print(f"project_name : {project_name} get_assets = {self.all_assets}")
        self.template_model.pepperlist.clear()
        self.shot_model.pepperlist.clear()

        # temp list asset append
        for asset in self.all_assets:
            self.template_model.pepperlist.append(asset)

        # set emit
        self.template_model.layoutChanged.emit()
        self.shot_model.layoutChanged.emit()
        self.templates_selection.clear()
        self.shots_selection.clear()
        self.renderlists_selection.clear()

    def template_selected(self, event):
        """templates_listview 의 template 를 클릭 시 실행 되는 메소드. \n
        클릭한 template 의 casting 된 shot 들을 pepper.asset 에 set 한 뒤 self.all_shots 에 받아 오고
        추가로 하단 Template info 에 created Artist,Time,Revision 정보를 보여 준다.
        그리고 template 의 casting 된 shot 들을 shots_listview 에 보여 준다.

        또, 기존과 다른 template 를 클릭 시 기존 shots_listview 의 shot_model 을 clear 한 뒤 클릭 된
        template 의 shot 들을 shots_listview 에 display 해준다.
        재 선택 시 Shots, Render files 의 selectionModel 들을 clear 해준다.

        Args:
            event: Listview click event
        """

        # event
        template_name = self.all_assets[event.row()]
        self.pepper.asset = template_name

        # set template info label
        name, time, rev = self.pepper.get_working_file_data('simulation', 'asset')
        self.main_window.template_info_label.setText(f"Artist : {name}, Created Time : {time}, Revision : {rev}")
        self.all_shots = self.pepper.get_casting_path_for_asset()

        self.shot_model.pepperlist.clear()

        for shot in self.all_shots:
            self.shot_model.pepperlist.append(shot['sequence_name'] + '_' + shot['shot_name'])

        # set emit, selected clear
        self.shot_model.layoutChanged.emit()
        self.shots_selection.clear()
        self.renderlists_selection.clear()

    def shot_selected(self, event):
        """Shots 를 선택 시 선택한 shot 의 정보(dict)를 self.all_shots = [] 에 담는 함수 이다.\n
        추가로 하단 Shot info 에 created Artist,Time,Revision 정보를 보여 준다.

        Args:
            event: Listview click event
        """
        shot_dict = self.all_shots[event.row()]

        self.pepper.sequence = shot_dict['sequence_name']
        self.pepper.shot = shot_dict['shot_name']

        name, time, rev = self.pepper.get_output_file_data('camera_cache', 'layout', 'shot')
        self.main_window.shot_info_label.setText(f"Artist : {name}, Created Time : {time}, Revision : {rev}")

        self.renderlists_selection.clear()

    def append_render_list(self):
        """

        Returns:

        """
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
        """

        Returns:

        """
        for idx in self.renderlists_selection.selectedRows():
            self.pepper.delete_precomp_dict(idx.data())
        self.render_model.pepperlist.clear()
        for render in self.pepper.precomp_list:
            self.render_model.pepperlist.append(render['name'])
        self.render_model.layoutChanged.emit()
        self.renderlists_selection.clear()

    def clear_list(self):
        """

        Returns:

        """
        self.pepper.precomp_list = []
        self.render_model.pepperlist.clear()
        self.render_model.layoutChanged.emit()

    def render_execute(self):
        houp = HouPepper()
        for precomp in self.pepper.precomp_list:
            houp.abc_path = precomp['layout_output_path']


def main():
    window = PepperWindow()


if __name__ == "__main__":
    main()