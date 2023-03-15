import sys
import os
import json
import webbrowser
from BlackPepper.process.mantra_process_bar_w import MantraMainWindow
from PySide2 import QtCore, QtWidgets
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QMainWindow, QAction, QApplication, QMenu
from BlackPepper.ui.model import PepperModel, PepperDnDModel
from BlackPepper.ui.view import PepperView, PepperDnDView
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
        self.recent_menu = None
        self.saved_menu = None
        self.projects_selection = None
        self.templates_selection = None
        self.shots_selection = None
        self.renderlists_selection = None
        self.temp_rev = None
        self.cam_rev = None
        self.mantra_window = None
        self.main_filemenu = None
        self.main_user = None
        self.main_menu_bar = None
        self.render_process = None

        self.my_projects = []
        self.all_assets = []
        self.all_shots = []
        self.render_list_data = []
        self.saved_list_data = []
        self.filename = []

        self.preset_json_path = 'render_check_list.json'

        # model instance
        self.project_model = PepperModel()
        self.template_model = PepperModel()
        self.shot_model = PepperModel()
        self.render_model = PepperDnDModel()
        self.render_list_model = PepperModel()
        # listview instance
        self.projects_listview = PepperView(self)
        self.templates_listview = PepperView(self)
        self.shots_listview = PepperView(self)
        self.renderlists_listview = PepperDnDView(self)
        self.shots_listview.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
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
        self.main_window.setWindowTitle('BlackPepper 0.1')
        self.main_window.move(700, 250)
        # check Ui loader
        check_ui = QtCore.QFile(os.path.join(script_path, 'mvc_YN_3.ui'))
        check_ui.open(QtCore.QFile.ReadOnly)
        self.check_ui_loader = QUiLoader()
        self.check_window = self.login_ui_loader.load(check_ui)
        self.check_window.setWindowTitle('Render Check List')
        self.check_window.move(1000, 300)
        self.check_window.checklist.setModel(self.render_list_model)
        # Render check list button
        self.check_window.close_btn.clicked.connect(self.close_fullpath)
        self.check_window.render_btn.clicked.connect(self.render_execute)
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
        self.main_window.save_btn.clicked.connect(self.save_user_renderlists)
        self.main_window.path_btn.clicked.connect(self.render_file_check)
        self.main_window.template_rev_cbox.currentTextChanged.connect(self.renew_template_info)

        # add listview to ui
        self.main_window.gridLayout_3.addWidget(self.projects_listview, 2, 0)
        self.main_window.gridLayout_3.addWidget(self.templates_listview, 2, 1)
        self.main_window.gridLayout_3.addWidget(self.shots_listview, 2, 2)
        self.main_window.gridLayout_3.addWidget(self.renderlists_listview, 2, 5)
        # set statusbar to window
        self.login_window.statusBar().showMessage('kitsu 로그인 하세요!  houdini 확장자 선택하세요!')
        self.main_window.statusBar().showMessage('project 를 선택하세요 !')
        # set main menubar
        self.create_login_menubar()

        # set auto login
        self.set_auto_login()
        self.create_main_menubar()

    def set_auto_login(self):
        """
        사용자가 로그인을 할 때 로그인 창에 id, password를 적고 houdini 확장자를 선택한다. \n
        그 때 .config에 저장된 json파일의 'auto'에 host 연결정보, id연결정보,id, password, host, houdini 확장자를 기록한다. \n
        만약 기존에 json파일이 없으면 창에서 id, password를 저장하고 만약 정보가 있으면 id, password, houdini 확장자를 받아와서
        로그인 버튼을 누른다.
        """
        # get login window to initial login information
        log_path = self.login_log.user_path
        self.login_log.host = "http://192.168.3.116/api"
        log_id = self.login_window.input_id.text()
        log_pw = self.login_window.input_pw.text()
        log_sfw = self.login_window.hipbox.currentText()[1:]
        log_value = self.login_log.load_setting()
        log_dict = self.login_log.user_dict

        # get to json key 'auto' check
        if os.path.exists(log_path) and not log_dict['auto']:
            for auto_loop in log_dict['auto']:
                if log_id != auto_loop['user_id'] or log_pw != auto_loop['user_pw'] or log_sfw != auto_loop['user_ext']:
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

        # set initial login information
        self.login_log.host = "http://192.168.3.116/api"
        self.login_log.user_id = self.login_window.input_id.text()
        self.login_log.user_pw = self.login_window.input_pw.text()
        self.login_log.user_ext = self.login_window.hipbox.currentText()[1:]

        # if connect login, get login information and close login window, open main window
        if self.login_log.connect_login():
            self.pepper.software = self.login_log.user_ext
            self.login_log.auto_login = True
            self.login_log.save_setting()
            self.login_window.close()
            self.open_main_window()

    def user_logout(self):
        """
        로그인 된 사용자가 로그아웃 버튼을 누르면 모든 창이 clear가 된다. \n
        그 후 id, password, host, houdini 확장자, host 연결상태, id 연결상태를 모두 초기화하고 로그인 창이 새로 뜬다.
        """

        # if connect login, log out, all window clear and close main window, open login window
        if self.login_log.connect_login():
            self.login_log.log_out()

            # render data list clear
            self.render_list_data.clear()

            # render, template, shot, project list clear
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

            # main window close and login window show
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
        self.main_window.template_info_label.setText("")
        self.main_window.shot_info_label.setText("")
        self.main_window.template_rev_cbox.clear()
        self.main_window.shot_rev_cbox.clear()

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
        self.all_assets = []
        for asset in self.pepper.get_all_assets():
            if self.pepper.check_asset_type(asset, 'fx_template') is not None:
                self.all_assets.append(asset)
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

    def renew_template_info(self):
        revision = self.main_window.template_rev_cbox.currentText()
        name, time, rev = self.pepper.get_working_file_data('simulation', revision, 'asset')
        date = time[:10]
        clock = time[11:]
        self.main_window.template_info_label.setText(f"{name}\n{date}\n{clock}")

    def renew_shot_info(self):
        revision = self.main_window.shot_rev_cbox.currentText()
        name, time, rev = self.pepper.get_output_file_data('camera_cache', 'layout', revision, 'shot')
        date = time[:10]
        clock = time[11:]
        self.main_window.shot_info_label.setText(f"{name}\n{date}\n{clock}")

    def renew_template_cbox(self, rev_list):
        self.main_window.template_rev_cbox.clear()
        for rev in rev_list:
            self.main_window.template_rev_cbox.addItem(f'{rev}')

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
        temp_rev = int(self.main_window.template_rev_cbox.currentText())
        shot_rev = self.main_window.shot_rev_cbox.currentText()
        if shot_rev == '':
            shot_rev = None
        else:
            shot_rev = int(shot_rev)
        if len(selections) == 1:
            shot_dict = self.all_shots[selections[0].row()]
            precomp = self.pepper.make_precomp_dict(shot_dict, temp_revision=temp_rev, cam_revision=shot_rev)
            self.check_and_append_render_list(precomp)
            self.renew_render_list()
            return
        for idx in selections:
            shot_dict = self.all_shots[idx.row()]
            precomp = self.pepper.make_precomp_dict(shot_dict, temp_revision=temp_rev)
            self.check_and_append_render_list(precomp)
        self.renew_render_list()

    def check_and_append_render_list(self, path_dict):
        if path_dict in self.render_model.pepperlist:
            return
        self.render_model.pepperlist.append(path_dict)
        return

    def renew_render_list(self):
        self.shots_selection.clear()
        self.render_model.layoutChanged.emit()
        self.renderlists_selection.clear()

    def delete_render_list(self):
        """main window 의 del_btn 에 연결 되어 클릭시 사용 되는 함수 이다.

            renderlists_selection(선택된 render files) 들을 pepper의 delete_precomp_dict를 사용하여 precomp_list에서 remove한다.
        path들을 딕셔너리로 만들고 self.precomp_list에 넣어주고 render_moderl.pepperlist clear 정리해준다.
        그리고 pepper 의 precomp_list를 render_moderl.pepperlist 에 append 한다.
        추가로 Shots, Render files 의 selectionModel(선택된 모델) 들을 clear 해준다.
        """
        if not self.renderlists_selection.selectedRows():
            return
        idx = self.renderlists_selection.selectedRows()[0]
        for precomp in self.render_model.pepperlist:
            if precomp['name'] == idx.data():
                self.render_model.pepperlist.remove(precomp)
        self.render_model.pepperlist.clear()
        self.renew_render_list()

    def clear_list(self):
        """main window 의 reset_btn에 연결 되어 render files list를 reset하는 함수이다.
        render files list( pepper.precomp_list)를 [] 빈 리스트로 만들고, render_moderl.pepperlist 를 clear 한다.
        """
        self.pepper.precomp_list = []
        self.render_model.pepperlist.clear()
        self.render_model.layoutChanged.emit()

    def create_login_menubar(self):
        """로그인 창에 메뉴바를 만들고 셋팅하는 함수이다.

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

    def create_main_menubar(self):
        """메인 윈도우에 메뉴바를 만들고 셋팅하 함수이다.

            함수에는 메뉴바에 preset 을 셋팅하는 함수를 포함 하고있다.
        'Menu' 와 'Help' 메뉴바를 만들고 'Menu' 에는 먼저 set_main_window_preset() 함수의 'Recent Presets' 와
        'Logout','Exit' 들을 추가하고 단축키와 클릭시 컨넥트 되어있는 함수가 발생한다.
        'Help' 에는 Black Pepper 에 필요한 kitsu, SideFX등 같은 관련 사이트들 을 열고 단축키도 추가 되어있다.
        """
        self.main_menu_bar = self.main_window.menuBar()
        self.main_menu_bar.setNativeMenuBar(False)
        # create 'File' menu
        self.main_filemenu = self.main_menu_bar.addMenu('&File')
        # 동적으로 메뉴를 채워주는 부분
        self.main_filemenu.aboutToShow.connect(self.set_main_menubar)
        # create Help menu
        main_helpmenu = self.main_menu_bar.addMenu('&Help')
        # 'File' menu add 'Open Recent preset' & 'Exit'
        self.set_main_menubar()
        # set kitsu
        kisu_action = QAction('Kitsu', self.main_window)
        kisu_action.setShortcut('F1')
        kisu_action.setStatusTip('Kitsu site open')
        kisu_action.triggered.connect(lambda: webbrowser.open('http://192.168.3.116/'))
        main_helpmenu.addAction(kisu_action)
        # set sidefx
        sidefx_action = QAction('SideFX', self.main_window)
        sidefx_action.setShortcut('F2')
        sidefx_action.setStatusTip('SideFX site open')
        sidefx_action.triggered.connect(lambda: webbrowser.open('https://www.sidefx.com/'))
        main_helpmenu.addAction(sidefx_action)
        # help add scanline vfx
        scanline_action = QAction('Scanline VFX', self.main_window)
        scanline_action.setShortcut('F3')
        scanline_action.setStatusTip('Scanline VFX site open')
        scanline_action.triggered.connect(lambda: webbrowser.open('https://www.scanlinevfx.com/'))
        main_helpmenu.addAction(scanline_action)
        # create menu 'User'
        self.main_user = self.main_menu_bar.addMenu('&User')
        host_info = QAction(f'host : {self.login_log.host}', self.main_window)
        self.main_user.addAction(host_info)
        id_info = QAction(f'id : {self.login_log.user_id}', self.main_window)
        self.main_user.addAction(id_info)
        self.main_user.addSeparator()
        # 'User' add 'Logout'
        logout_action = QAction('&Logout', self.main_window)
        logout_action.setShortcut('Ctrl+L')
        logout_action.setStatusTip('Logout application')
        logout_action.triggered.connect(self.user_logout)
        self.main_user.addAction(logout_action)

    def set_main_menubar(self):
        """메인창의 file 메뉴 'Open Recent Presets' 의 sub 메뉴들을 만들어주는 함수이다.

            메뉴바 'Menu' 에 'Recent Presets는'메뉴에 path json file 을 불러오고 최신 5개의 json render_model.pepperlist
            5번 인덱스가 제일 최신 json dict 정보이다.
        """
        self.main_filemenu.clear()
        self.create_json()

        self.recent_menu = QMenu('Open recent renderlists', self.main_window)
        self.saved_menu = QMenu('Open saved renderlists', self.main_window)

        with open(self.preset_json_path, 'r') as f:
            self.render_list_data = json.load(f)

        for json_files in self.render_list_data['recent']:
            for file_path in json_files:
                file_action = self.append_renderlist_to_menubar(file_path)
                self.recent_menu.addAction(file_action)

        for json_files in self.render_list_data['saved']:
            for file_path in json_files:
                file_action = self.append_renderlist_to_menubar(file_path)
                self.saved_menu.addAction(file_action)

        self.main_filemenu.addMenu(self.recent_menu)
        self.main_filemenu.addMenu(self.saved_menu)

        # add 'Exit'
        exit_action = QAction('&Exit', self.main_window)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(QApplication.instance().quit)
        self.main_filemenu.addAction(exit_action)

    def append_renderlist_to_menubar(self, render_list):
        file_action = QAction(render_list, self)
        file_action.triggered.connect(lambda: self.handle_file(file_action.text()))
        return file_action

    def handle_file(self, text):
        """메인창의 file 메뉴 'Open Recent Presets' 의 원하는 Preset 을 선택시 실행되는 함수이다.

            json 을 load 하고 정보들을 main window 에 set 한다.
        """
        if text.startswith("saved"):
            list_type = 'saved'
        elif text.startswith("recent"):
            list_type = 'recent'
        else:
            return
        render_lists = self.render_list_data.get(list_type)
        for render_list in render_lists:
            the_list = render_list.get(text)
            if the_list is not None:
                self.render_model.pepperlist = the_list
        self.renew_render_list()

    def save_recent_renderlists(self):
        """save preset json path 의 json 을 불러오고 recent key 값에 정보를 저장하는 함수이다.

            path 에 json 파일이 없으면 json 을 만들어주는 함수를 사용하여 json 을 만들어주고 json을 load 하여 'recent' key에
            render_moderl.pepperlist(렌다할 render files들) dict 들을 날짜,시간별로 리스트로 json을 저장한다.
        """
        if len(self.render_model.pepperlist) == 0:
            return
        self.create_json()
        self.open_json()
        recent_data = self.render_list_data.get('recent', [])
        now = datetime.now()
        # 최대 인덱스 5까지 새로운 value가 추가되도록 수정
        if len(recent_data) >= 5:
            recent_data.pop(0)  # 가장 오래된 데이터 삭제
        recent_data.append({
            f'recent_{now.date()}_time_{now.hour}:{now.minute}:{now.second}': self.render_model.pepperlist
        })
        # 'recent' key 값의 value로 저장
        self.render_list_data['recent'] = recent_data
        self.save_json(self.render_list_data)

    def save_user_renderlists(self):
        """save preset json path 의 json 을 불러오고 recent key 값에 정보를 저장하는 함수이다.

            path 에 json 파일이 없으면 json 을 만들어주는 함수를 사용하여 json 을 만들어주고 json을 load 하여 'recent' key에
            render_moderl.pepperlist(렌다할 render files들) dict 들을 날짜,시간별로 리스트로 json을 저장한다.
        """
        if len(self.render_model.pepperlist) == 0:
            return
        self.create_json()
        self.open_json()
        saved_data = self.render_list_data.get('saved', [])
        now = datetime.now()
        # 최대 인덱스 5까지 새로운 value가 추가되도록 수정
        if len(saved_data) >= 10:
            saved_data.pop(0)  # 가장 오래된 데이터 삭제
        saved_data.append({
            f'saved_{now.date()}_time_{now.hour}:{now.minute}:{now.second}': self.render_model.pepperlist
        })
        # 'recent' key 값의 value로 저장
        self.render_list_data['saved'] = saved_data
        self.save_json(self.render_list_data)

    def open_json(self):
        with open(self.preset_json_path, 'r') as f:
            self.render_list_data = json.load(f)

    def save_json(self, data):
        with open(self.preset_json_path, "w") as f:
            json.dump(data, f, ensure_ascii=False)

    def create_json(self):
        """preset이 저장되어있는 json파일이 없으면 json 파일을 만들어주는 함수이다.
        """
        if not os.path.exists(self.preset_json_path):
            self.render_list_data = {
                "recent": [],
                "saved": []
            }
            data_to_save = self.render_list_data

            with open(self.preset_json_path, "w") as f:
                json.dump(data_to_save, f, ensure_ascii=False)

    def render_file_check(self):
        self.render_list_model.pepperlist.clear()
        for render_file in self.render_model.pepperlist:
            self.render_list_model.pepperlist.append(f"\n{render_file['name']} : \n "
                                                     f"{render_file['temp_working_path']}\n "
                                                     f"{render_file['layout_output_path']}\n "
                                                     f"{render_file['fx_working_path']}\n "
                                                     f"{render_file['jpg_output_path']}\n "
                                                     f"{render_file['video_output_path']}\n")
        self.render_list_model.layoutChanged.emit()
        self.check_window.show()

    def close_fullpath(self):
        self.check_window.close()

    def render_execute(self):
        houp = HouPepper()
        if not self.render_model.pepperlist:
            return
        self.save_recent_renderlists()
        for precomp in self.render_model.pepperlist:
            temp_working_path, layout_output_path, fx_working_path, jpg_output_path, video_output_path \
                = self.path_seperator(precomp)
            houp.set_fx_working_for_shot(temp_working_path, layout_output_path,
                                         f'{fx_working_path}.{self.pepper.software.get("file_extension")}')
            cmd_list, total_frame_list = houp.make_cmd(precomp)

        # for precomp in self.render_model.pepperlist:
        #     temp_working_path, layout_output_path, fx_working_path, jpg_output_path, video_output_path \
        #         = self.path_seperator(precomp)
        #     houp.set_fx_working_for_shot(temp_working_path, layout_output_path,
        #                                  f'{fx_working_path}.{self.pepper.software.get("file_extension")}')
        # for precomp in self.render_model.pepperlist:
        #     temp_working_path, layout_output_path, fx_working_path, jpg_output_path, video_output_path \
        #         = self.path_seperator(precomp)
        #     self.mantra_window = MantraMainWindow(f'{fx_working_path}.{self.pepper.software.get("file_extension")}',
        #                                           jpg_output_path, layout_output_path, houp.cam_node,
        #                                           houp.abc_range[1] * hou.fps())
        #     self.mantra_window.resize(800, 600)
        #     self.mantra_window.move(1000, 250)
        #     self.mantra_window.show()
        # f = FFmpegMainWindow(fx_next_output, mov_next_output, hou.fps())
        # f.resize(800, 600)
        # f.move(1000, 250)
        # f.show()

        # print('cmd_list :', cmd_list)
        # print('total_frame_list :', total_frame_list)
        # self.render_process = RenderMainWindow(cmd_list, total_frame_list)
        # self.render_process.resize(800, 600)
        # self.render_process.move(1000, 250)
        # self.render_process.show()

        # self.pepper.precomp_list.clear()
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
