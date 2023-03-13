import sys
import os
import glob
import json
import webbrowser
from BlackPepper.process.mantra_process_bar_w import MantraMainWindow
from PySide2 import QtCore, QtWidgets
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QMainWindow
from PySide2.QtWidgets import QAction, QApplication
from BlackPepper.ui.model import PepperModel, PepperDnDModel
from BlackPepper.ui.view import PepperView, PepperDnDView
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QAction, QApplication, QMenu
from BlackPepper.ui.model import PepperModel
from BlackPepper.ui.view import PepperView
from BlackPepper.pepper import Houpub
from BlackPepper.process.houpepper import HouPepper
from BlackPepper.ui.auto_login import Auto_log
import hou
from datetime import datetime


class PepperWindow(QMainWindow):
    def __init__(self):
        """이 모듈은 pepper를 통해 얻어 온 kitsu 상의 template asset과 casting 된 shot들의 정보들을 UI를 통해 보여준다.
        UI 모듈은 controller, model, view로 분리되어 있고, mvc_login, mvc_main의 .ui 파일이 UI 데이터를 가지고 있다. \n
        메인 UI의 4개 model은 PepperModel에서 가져오며, ListView는 PepperView에서 가져온다.
        여러 개의 shot들을 한번에 선택해 조정할 수 있도록 shots와 rendelistes의 view는 ExtendedSelection으로 설정했다. \n
        PepperWindow 실행 시 self.login_ui가 우선 실행된다.
        """
        super().__init__()
        self.pepper = Houpub()
        self.login_log = Auto_log()
        self.projects_selection = None
        self.templates_selection = None
        self.shots_selection = None
        self.renderlists_selection = None
        self.temp_rev = None
        self.cam_rev = None
        self.mantra_window = None
        self.main_menu = None
        self.main_menu_bar = None

        self.my_projects = []
        self.all_assets = []
        self.all_shots = []
        self.render_list_data = []
        self.filename = []
        # model instance
        self.project_model = PepperModel()
        self.template_model = PepperModel()
        self.shot_model = PepperModel()
        self.render_model = PepperDnDModel()
        # listview instance
        self.projects_listview = PepperView(self)
        self.templates_listview = PepperView(self)
        self.shots_listview = PepperView(self)
        self.renderlists_listview = PepperDnDView(self)
        self.shots_listview.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.renderlists_listview.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        # setModel
        self.projects_listview.setModel(self.project_model)
        self.projects_listview.setStyleSheet("background-color:rgb(52, 52, 52);")
        self.projects_listview.setSpacing(2)
        self.templates_listview.setModel(self.template_model)
        self.templates_listview.setStyleSheet("background-color:rgb(52, 52, 52);")
        self.templates_listview.setSpacing(2)
        self.shots_listview.setModel(self.shot_model)
        self.shots_listview.setStyleSheet("background-color:rgb(52, 52, 52);")
        self.shots_listview.setSpacing(2)
        self.renderlists_listview.setModel(self.render_model)
        self.renderlists_listview.setStyleSheet("background-color:rgb(52, 52, 52);")
        self.renderlists_listview.setSpacing(2)

        self.projects_selection = self.projects_listview.selectionModel()
        self.templates_selection = self.templates_listview.selectionModel()
        self.shots_selection = self.shots_listview.selectionModel()
        self.renderlists_selection = self.renderlists_listview.selectionModel()

        # get script_path
        # __file__ (전역변수) : 현재 열려있는 파일의 위치와 이름을 가지고 있는 문자열 변수
        # path.realpath(파일이름) : 현재 파일의  표준 경로+이름 을 반환
        script_path = os.path.dirname(os.path.realpath(__file__))
        # login Ui loader
        login_ui = QtCore.QFile(os.path.join(script_path, 'mvc_login_3.ui'))
        login_ui.open(QtCore.QFile.ReadOnly)
        self.login_ui_loader = QUiLoader()
        self.login_window = self.login_ui_loader.load(login_ui)
        self.login_window.setWindowTitle('Black Pepper Login')
        self.login_window.move(1000, 300)
        self.login_window.show()
        # main Ui loader
        main_ui = QtCore.QFile(os.path.join(script_path, 'mvc_main_3.ui'))
        main_ui.open(QtCore.QFile.ReadOnly)
        self.main_ui_loader = QUiLoader()
        self.main_window = self.main_ui_loader.load(main_ui)
        self.main_window.setWindowTitle('Black Pepper')
        self.main_window.move(700, 250)
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
        self.main_window.temp_rev_cbox.currentTextChanged.connect(self.renew_template_info)
        # add listview to ui
        self.main_window.gridLayout_3.addWidget(self.projects_listview, 2, 0)
        self.main_window.gridLayout_3.addWidget(self.templates_listview, 2, 1)
        self.main_window.gridLayout_3.addWidget(self.shots_listview, 2, 2)
        self.main_window.gridLayout_3.addWidget(self.renderlists_listview, 2, 5)
        # set statusbar to window
        self.login_window.statusBar().showMessage('kitsu 로그인 하세요!  houdini 확장자 선택하세요!')
        self.main_window.statusBar().showMessage('project 를 선택하세요 !')
        # set main menubar
        self.set_login_menubar()

        # self.set_main_menubar()

        # set auto login
        self.set_auto_login()
        self.set_main_menubar()


    def set_auto_login(self):
        log_path = self.login_log.user_path
        self.login_log.host = "http://192.168.3.116/api"
        log_id = self.login_window.input_id.text()
        log_pw = self.login_window.input_pw.text()
        log_sfw = self.login_window.hipbox.currentText()[1:]
        log_value = self.login_log.load_setting()
        log_dict = self.login_log.user_dict
        if os.path.exists(log_path) and(not log_dict['auto'] or log_id != log_value['user_id']
                                        or log_pw != log_value['user_pw'] or log_sfw != log_value['user_ext']):
            self.login_log.user_id = log_id
            self.login_log.user_pw = log_pw
            self.login_log.user_ext = log_sfw
            self.login_log.valid_host = True
            self.login_log.valid_user = True
            self.login_log.auto_login = True
            self.login_log.save_setting()
            return
        if log_value['valid_host'] and log_value['valid_user']:
            self.login_log.host = log_value['host']
            self.login_log.user_id = log_value['user_id']
            self.login_log.user_pw = log_value['user_pw']
            self.login_log.user_ext = log_value['user_ext']
            self.pepper.login(self.login_log.host, self.login_log.user_id, self.login_log.user_pw)
            self.pepper.software = self.login_log.user_ext
            self.login_window.close()
            self.open_main_window()
        else:
            pass

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
        self.login_log.user_ext = self.login_window.hipbox.currentText()[1:]

        if self.login_log.connect_login():
            self.pepper.software = self.login_log.user_ext
            self.login_log.auto_login = True
            self.login_log.save_setting()
            self.login_window.close()
            self.open_main_window()

    def user_logout(self):
        if self.login_log.connect_login():
            self.login_log.log_out()

            self.pepper.precomp_list.clear()
            self.render_list_data.clear()

            self.render_model.layoutChanged.emit()
            self.template_model.layoutChanged.emit()
            self.shot_model.layoutChanged.emit()

            self.render_model.pepperlist.clear()
            self.template_model.pepperlist.clear()
            self.shot_model.pepperlist.clear()

            self.projects_selection.clear()
            self.renderlists_selection.clear()
            self.templates_selection.clear()
            self.shots_selection.clear()

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
        """projects_listview 의 project 를 클릭 시 실행 되는 함수이다.

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
        self.main_window.statusBar().showMessage('temp 를 선택하세요 !')

    def template_selected(self, event):
        """templates_listview 의 template 를 클릭 시 실행 되는 메소드. \n
        클릭한 template 의 casting 된 shot 들을 pepper.asset 에 set 한 뒤 self.all_shots 에 받아 오고
        추가로 하단 Template info 에 created Artist,Time,Revision 정보를 보여 준다.
        그리고 template 의 casting 된 shot 들을 shots_listview 에 보여 준다.

        또, 기존과 다른 template 를 클릭 시 기존 shots_listview 의 shot_model 을 clear 한 뒤 클릭 된
        template 의 shot 들을 shots_listview 에 display 해준다.
        재 선택 시 Shots, Render files 의 selectionModel(선택된 모델) 들을 clear 해준다.

        Args:
            event: Listview click event
        """

        # event
        template_name = self.all_assets[event.row()]
        self.pepper.asset = template_name
        self.pepper.entity = 'asset'
        rev_list = self.pepper.get_every_revision_for_working_file('fx_template')
        self.renew_template_cbox(rev_list)

        self.renew_template_info()
        # set template info label
        # name, time, rev = self.pepper.get_working_file_data('simulation', 'asset')
        # self.main_window.template_info_label.setText(f"Artist : {name}, Created Time : {time}, Revision : {rev}")
        self.all_shots = self.pepper.get_casting_path_for_asset()

        self.shot_model.pepperlist.clear()

        for shot in self.all_shots:
            self.shot_model.pepperlist.append(shot['sequence_name'] + '_' + shot['shot_name'])

        # set emit, selected clear
        self.shot_model.layoutChanged.emit()
        self.shots_selection.clear()
        self.renderlists_selection.clear()
        self.main_window.statusBar().showMessage('shots 를 선택하세요 ! 다중선택가능 ! ')

    def renew_template_info(self):
        revision = self.main_window.temp_rev_cbox.currentText()
        name, time, rev = self.pepper.get_working_file_data('simulation', revision, 'asset')
        time = 'Date ' + time[:10] + ' Time ' + time[11:]
        self.main_window.template_info_label.setText(f"{name}, {time}, Revision : ")

    def shot_selected(self, event):
        """Shots 를 선택 시 선택한 shot 의 정보(dict)를 self.all_shots = [] 에 담는 함수 이다.\n
        추가로 하단 Shot info 에 created Artist,Time,Revision 정보를 보여 준다.

        Args:
            event: Listview click event
        """
        shot_dict = self.all_shots[event.row()]

        self.pepper.sequence = shot_dict['sequence_name']
        self.pepper.shot = shot_dict['shot_name']
        self.pepper.entity = 'shot'
        rev_list = self.pepper.get_every_revision_for_output_file('camera_cache', 'layout')
        self.renew_shot_cbox(rev_list)
        self.renew_shot_info()
        self.renderlists_selection.clear()

    def renew_shot_info(self):
        revision = self.main_window.shot_rev_cbox.currentText()
        name, time, rev = self.pepper.get_output_file_data('camera_cache', 'layout', revision, 'shot')
        time = 'Date ' + time[:10] + ' Time ' + time[11:]
        self.main_window.shot_info_label.setText(f"{name}, {time}, Revision : ")

    def renew_template_cbox(self, rev_list):
        self.main_window.temp_rev_cbox.clear()
        for rev in rev_list:
            self.main_window.temp_rev_cbox.addItem(f'{rev}')

    def renew_shot_cbox(self, rev_list):
        self.main_window.shot_rev_cbox.clear()
        for rev in rev_list:
            self.main_window.shot_rev_cbox.addItem(f'{rev}')

    def append_render_list(self):
        """main window 의 append_btn 에 연결 되어 클릭시 사용 되는 함수 이다.

            선택된 shot 들의 shot_dict 를  pepper의 make_precomp_dict 를 사용하여 shot 별로 houdini에서 필요한
        path들을 딕셔너리로 만들고 self.precomp_list에 넣어주고 render_moderl.pepperlist clear 정리해준다.
        그리고 pepper 의 precomp_list를 render_moderl.pepperlist 에 append 한다.
        추가로 Shots, Render files 의 selectionModel(선택된 모델) 들을 clear 해준다.
        """
        selections = self.shots_selection.selectedRows()
        if len(selections) == 0:
            return
        temp_rev = int(self.main_window.temp_rev_cbox.currentText())
        shot_rev = self.main_window.shot_rev_cbox.currentText()
        if shot_rev == '':
            shot_rev = None
        else:
            shot_rev = int(shot_rev)
        if len(selections) == 1:
            shot_dict = self.all_shots[selections[0].row()]
            self.pepper.make_precomp_dict(shot_dict, temp_revision=temp_rev, cam_revision=shot_rev)
            self.renew_render_list()
            self.shots_selection.clear()
            return
        for idx in selections:
            shot_dict = self.all_shots[idx.row()]
            self.pepper.make_precomp_dict(shot_dict, temp_revision=temp_rev)
            self.shots_selection.clear()
        self.renew_render_list()

    def renew_render_list(self):
        self.render_model.pepperlist.clear()
        for render in self.pepper.precomp_list:
            self.render_model.pepperlist.append(render['name'])
        self.render_model.layoutChanged.emit()
        self.renderlists_selection.clear()

    def delete_render_list(self):
        """main window 의 del_btn 에 연결 되어 클릭시 사용 되는 함수 이다.

            renderlists_selection(선택된 render files) 들을 pepper의 delete_precomp_dict를 사용하여 precomp_list에서 remove한다.
        path들을 딕셔너리로 만들고 self.precomp_list에 넣어주고 render_moderl.pepperlist clear 정리해준다.
        그리고 pepper 의 precomp_list를 render_moderl.pepperlist 에 append 한다.
        추가로 Shots, Render files 의 selectionModel(선택된 모델) 들을 clear 해준다.
        """
        for idx in self.renderlists_selection.selectedRows():
            self.pepper.delete_precomp_dict(idx.data())
        self.renew_render_list()

    def clear_list(self):
        """main window 의 reset_btn에 연결 되어 render files list를 reset하는 함수이다.
        render files list( pepper.precomp_list)를 [] 빈 리스트로 만들고, render_moderl.pepperlist 를 clear 한다.
        """
        self.pepper.precomp_list = []
        self.render_model.pepperlist.clear()
        self.render_model.layoutChanged.emit()

    def set_login_menubar(self):
        """로그인 창의 메뉴바를 셋팅하는 함수이다.

            메뉴바에 'Menu'를 만들고 'Menu'안에 'Exit'를 만들었고 'Ctrl+Q' 단축키 또는 'Exit' 클릭시 창의 X 와 같은 기능으로
         어플리케이션이 종료 된다.
        """
        login_menu_bar = self.login_window.menuBar()
        login_menu = login_menu_bar.addMenu('Menu')
        exit_action = QAction('Exit', self.login_window)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(QApplication.instance().quit)
        login_menu.addAction(exit_action)

    def set_main_menubar(self):
        """메인 창의 메뉴바를 셋팅하는 함수이다.

            함수에는 메뉴바에 preset 을 셋팅하는 함수를 포함 하고있다.
        'Menu' 와 'Help' 메뉴바를 만들고 'Menu' 에는 먼저 set_main_window_preset() 함수의 'Recent Presets' 와
        'Logout','Exit' 들을 추가하고 단축키와 클릭시 컨넥트 되어있는 함수가 발생한다.
        'Help' 에는 Black Pepper 에 필요한 kitsu, SideFX등 같은 관련 사이트들 을 열고 단축키도 추가 되어있다.
        """
        self.main_menu_bar = self.main_window.menuBar()
        self.main_menu_bar.setNativeMenuBar(False)
        # set Menu
        self.main_menu = self.main_menu_bar.addMenu('Menu')
        # set main window preset
        self.set_mainwindow_preset()
        # 구분자 추가
        self.main_menu.addSeparator()
        # addMenu 'Exit'
        exit_action = QAction('Exit', self.main_window)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(QApplication.instance().quit)
        self.main_menu.addAction(exit_action)
        # addMenu Help
        main_helpmenu = self.main_menu_bar.addMenu('Help')
        # set kitsu
        kisu_action = QAction('Kitsu', self.main_window)
        kisu_action.setShortcut('F1')
        kisu_action.setStatusTip('Kitsu site open')
        kisu_action.triggered.connect(lambda: webbrowser.open('http://192.168.3.116/'))
        main_helpmenu.addAction(kisu_action)
        # set sidefx
        sidefx_action = QAction('Side Fx', self.main_window)
        sidefx_action.setShortcut('F2')
        sidefx_action.setStatusTip('Side Fx site open')
        sidefx_action.triggered.connect(lambda: webbrowser.open('https://www.sidefx.com/'))
        main_helpmenu.addAction(sidefx_action)
        # set scanline vfx
        scanline_action = QAction('Scanline VFX', self.main_window)
        scanline_action.setShortcut('F3')
        scanline_action.setStatusTip('Scanline VFX site open')
        scanline_action.triggered.connect(lambda: webbrowser.open('https://www.scanlinevfx.com/'))
        main_helpmenu.addAction(scanline_action)
        # addMenu 'User'
        self.main_user = self.main_menu_bar.addMenu('User')
        host_info = QAction(f'host : {self.login_log.host}', self.main_window)
        self.main_user.addAction(host_info)
        id_info = QAction(f'id : {self.login_log.user_id}', self.main_window)
        self.main_user.addAction(id_info)
        self.main_user.addSeparator()
        # set 'Logout'
        logout_action = QAction('Logout', self.main_window)
        logout_action.setShortcut('Ctrl+L')
        logout_action.setStatusTip('Logout application')
        logout_action.triggered.connect(self.user_logout)
        self.main_user.addAction(logout_action)

    def set_mainwindow_preset(self):
        """메인창의 메뉴바에 Recent precet 메뉴를 만들어주 함수이다.

            메뉴바 'Menu' 에 'Recent Presets는'메뉴에 path 에 있는 최신 5개의 json 파일들을 내림차순으로 보여준다.
        """
        recent_menu = QMenu('Recent Presets', self.main_window)

        directory_path = '/home/rapa/git/hook/python/BlackPepper/ui'
        json_files = sorted(glob.glob(os.path.join(directory_path, '*.json')), key=os.path.getmtime, reverse=True)[:5]

        for file_path in json_files:
            file_action = QAction(os.path.basename(file_path), self)
            file_action.triggered.connect(lambda _, path=file_path: self.handle_file(path))
            recent_menu.addAction(file_action)
        self.main_menu.addMenu(recent_menu)

    def handle_file(self, file_path):  #수정예정
        """

        Args:
            file_path:

        Returns:

        """
        # TODO: 파일 내용 처리하기
        # self.load_preset_set()
        pass

    def save_preset_json(self):  #  json파일이 게속만들어짐. json파일 하나로 수정 예정
        """Render 버튼을 누르면 main ui 의 preset 정보들이 json 으로 저장되는 함수이다.

            로그인한 사용자의 id와 파일 생성 시간으로 json파일을 저장하고 중복되는 파일 이름은 최대 5개의 json파일이 저장되고
            파일 이름 중복시 v1~v5로 만들어지고 v1으로 덮어씌워진다.
        """
        now = datetime.now()
        base_filename = f'{self.pepper.identif}_{now.date()}_time_{now.hour}:{now.minute}'

        # base_filename = 'render_check_list'
        ext = '.json'
        i = 1
        while i <= 5:
            self.filename = f"{base_filename}_v{i}{ext}"
            if not os.path.isfile(self.filename):
                break
            i += 1
        if i > 5:
            i = 1
        self.filename = f"{base_filename}_v{i}{ext}"

        self.render_model.pepperlist.clear()
        for render in self.pepper.precomp_list:
            self.render_list_data.append(render['name'])
        with open(self.filename, "w") as f:
            json.dump(self.render_list_data, f, ensure_ascii=False)

    def load_preset_set(self):  # 함수수정예정
        """preset이 저장되어있는 json파일을 load하는 함수이다.

            render 클릭시 저장된 precomp list 정보들을 담고 있는 json파일을 load 하고  main window preset 셋팅하고
        메뉴바의 Recent preset 에  connect 되어 클릭시 실행되는 함수이다.
        """
        with open(self.render_list_path, "r") as f:
            self.render_list_data = json.load(f)
            print(self.render_list_data)

    def precomp_list_len(self):  # 함수수정예정
        """추가된 precom list 의 갯수를 반환하는 함수이다.

            pre render 할 list들의 갯수를 계산 하는 함수이다.
        """
        # total = len(self.render_list_data)
        self.render_model.pepperlist.clear()
        for render in self.pepper.precomp_list:
            self.render_model.pepperlist.append(render['name'])
        self.render_model.layoutChanged.emit()
        self.shots_selection.clear()
        self.renderlists_selection.clear()

    def render_execute(self):
        houp = HouPepper()
        for precomp in self.pepper.precomp_list:
            temp_working_path, layout_output_path, fx_working_path, jpg_output_path, video_output_path \
                = self.path_seperator(precomp)
            houp.set_fx_working_for_shot(temp_working_path, layout_output_path,
                                         f'{fx_working_path}.{self.pepper.software.get("file_extension")}')
        for precomp in self.pepper.precomp_list:
            temp_working_path, layout_output_path, fx_working_path, jpg_output_path, video_output_path \
                = self.path_seperator(precomp)
            self.mantra_window = MantraMainWindow(f'{fx_working_path}.{self.pepper.software.get("file_extension")}',
                                                  jpg_output_path, layout_output_path, houp.cam_node,
                                                  houp.abc_range[1] * hou.fps())
            self.mantra_window.resize(800, 600)
            self.mantra_window.move(1000, 250)
            self.mantra_window.show()
            # f = FFmpegMainWindow(fx_next_output, mov_next_output, hou.fps())
            # f.resize(800, 600)
            # f.move(1000, 250)
            # f.show()

        # pepper.precomp_list 의 갯수가 0 이면 return !
        if len(self.pepper.precomp_list) == 0:
            return

        self.save_preset_json()

        self.pepper.precomp_list.clear()
        self.render_list_data.clear()

        self.render_model.layoutChanged.emit()
        self.template_model.layoutChanged.emit()
        self.shot_model.layoutChanged.emit()

        self.render_model.pepperlist.clear()
        self.template_model.pepperlist.clear()
        self.shot_model.pepperlist.clear()

        self.projects_selection.clear()
        self.renderlists_selection.clear()
        self.templates_selection.clear()
        self.shots_selection.clear()

    @staticmethod
    def path_seperator(precomp):
        temp_working_path = precomp['temp_working_path']
        layout_output_path = precomp['layout_output_path']
        fx_working_path = precomp['fx_working_path']
        jpg_output_path = precomp['jpg_output_path']
        video_output_path = precomp['video_output_path']
        return temp_working_path, layout_output_path, fx_working_path, jpg_output_path, video_output_path


def main():
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QtWidgets.QApplication(sys.argv)
    window = PepperWindow()
    app.exec_()


if __name__ == "__main__":
    main()
