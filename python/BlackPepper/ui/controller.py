import sys
import os
import json
import webbrowser
from BlackPepper.process.render_process_bar import RenderMainWindow
# from BlackPepper.process.mantra_process_bar_w import MantraMainWindow
from PySide2 import QtCore, QtWidgets
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QMainWindow, QAction, QApplication, QMenu
from BlackPepper.ui.model import PepperModel, PepperDnDModel
from BlackPepper.ui.view import PepperView, PepperDnDView
from BlackPepper.pepper import Houpub
from BlackPepper.process.houpepper import HouPepper
from BlackPepper.ui.auto_login import Auto_log
from BlackPepper.log.moduler_log import Logger
import hou
from datetime import datetime


class PepperWindow(QMainWindow):
    """이 모듈은 pepper를 통해 얻어 온 kitsu 상의 template asset과 casting 된 shot들의 정보들을 UI를 통해 보여준다. \n
    UI 모듈들은 controller, model, view로 분리되어 있고, mvc_login, mvc_main의 .ui 파일이 UI 데이터를 가지고 있다.
    main UI의 Model은 PepperModel에서 가져오며, View는 PepperView에서 가져온다.
    여러 개의 shot들을 한번에 선택해 조정할 수 있도록 shot의 listview selectionModel은 ExtendedSelection으로 설정되어있다.
    클래스 선언시 login UI를 디스플레이 하고, 로그인 정보를 저장해둬 최초 로그인 이후로는 이전 로그인 정보를 통해 자동 로그인이 가능하다.
    로그인한 유저에게 assign된 project를 모두 불러오며, project 선택시 task status가 Done인 FX template들을 모두 불러온다.
    template 선택 시 해당 template에 casting된 shots들을 모두 불러온다. template의 listview 하단에서 해당 template의
    정보를 알 수 있으며, template의 revision도 선택할 수 있다. shot들은 shot의 listview로 들어가며, 개별 shot 선택시
    shot의 listview 하단에서 해당 shot의 정보를 알 수 있으며, revision도 선택할 수 있다. 다중 선택시 최신 revision이 선택된다.
    선택된 shot들을 오른쪽 화살표 버튼을 통해 Render files에 추가할 수 있다.
    Render list 상단에는 전체 경로를 보여주는 full path 버튼, 현재 Render list를 저장해주는 save 버튼,
    그리고 현재 Render list를 초기화 해주는 버튼이 있다.
    상단 메뉴바에서는 미리 저장해두거나 최근에 렌더했던 shot들을 다시 가져올 수 있고, Kitsu와 SideFX로 바로 연결되는 탭이 있다.
    Render 버튼을 통해 렌더 큐를 Houdini에 넘길 수 있다. 렌더 도중에는 Progress UI를 디스플레이한다.
    """
    def __init__(self):
        super().__init__(parent=None)
        self.pepper = Houpub()
        self.login_log = Auto_log()
        self.projects_selection = None
        self.templates_selection = None
        self.shots_selection = None
        self.renderlists_selection = None
        self.temp_rev = None
        self.cam_rev = None
        self.mantra_window = None
        self.main_filemenu = None
        self.render_process = None
        self.my_projects = []
        self.all_assets = []
        self.all_shots = []
        self.render_list_data = {}
        self.saved_list_data = []
        self.filename = []
        self.preset_json_path = ''
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
        # set model
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
        # listview selection model
        self.projects_selection = self.projects_listview.selectionModel()
        self.templates_selection = self.templates_listview.selectionModel()
        self.shots_selection = self.shots_listview.selectionModel()
        self.renderlists_selection = self.renderlists_listview.selectionModel()
        # get script_path
        script_path = os.path.dirname(os.path.realpath(__file__))  # path.realpath : 현재 파일의 경로+이름 을 반환
        # login UI loader
        login_ui = QtCore.QFile(os.path.join(script_path, 'mvc_login_3.ui'))
        login_ui.open(QtCore.QFile.ReadOnly)
        self.login_ui_loader = QUiLoader()
        self.login_window = self.login_ui_loader.load(login_ui)
        self.login_window.setWindowTitle('Black Pepper v0.01')
        self.login_window.move(1000, 300)
        self.login_window.show()
        # main UI loader
        main_ui = QtCore.QFile(os.path.join(script_path, 'mvc_main_3.ui'))
        main_ui.open(QtCore.QFile.ReadOnly)
        self.main_ui_loader = QUiLoader()
        self.main_window = self.main_ui_loader.load(main_ui)
        self.main_window.setWindowTitle('Black Pepper v0.0.1')
        self.main_window.move(700, 250)
        # check UI loader
        check_ui = QtCore.QFile(os.path.join(script_path, 'mvc_YN_3.ui'))
        check_ui.open(QtCore.QFile.ReadOnly)
        self.check_ui_loader = QUiLoader()
        self.check_window = self.login_ui_loader.load(check_ui)
        self.check_window.setWindowTitle('Render Check List')
        self.check_window.move(1000, 300)
        self.check_window.checklist.setModel(self.render_list_model)
        # login UI clicked event
        self.login_window.login_btn.clicked.connect(self.user_login)
        self.login_window.input_id.returnPressed.connect(self.user_login)
        self.login_window.input_pw.returnPressed.connect(self.user_login)
        # main UI clicked event
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
        # main UI clicked event
        self.check_window.close_btn.clicked.connect(self.close_fullpath)
        self.check_window.render_btn.clicked.connect(self.render_execute)
        # listview to UI
        self.main_window.gridLayout_3.addWidget(self.projects_listview, 2, 0)
        self.main_window.gridLayout_3.addWidget(self.templates_listview, 2, 1)
        self.main_window.gridLayout_3.addWidget(self.shots_listview, 2, 2)
        self.main_window.gridLayout_3.addWidget(self.renderlists_listview, 2, 5)
        # status bar message
        self.login_window.statusBar().showMessage('Select licence version of houdini to log-in')
        self.main_window.statusBar().showMessage('Select project to find templates')
        self.main_window.path_btn.setStatusTip('Show full path of render files')
        self.main_window.save_btn.setStatusTip("Save render files list as preset")
        self.main_window.reset_btn.setStatusTip('Clear render files list')
        # set main menubar
        self.create_login_menubar()
        # set auto login
        self.set_auto_login()

    def set_auto_login(self):
        """auto login을 설정하는 메소드. \n
        사용자가 로그인을 할 때 로그인 창에 id, password를 적고 houdini 확장자를 선택한다.
        .config에 저장된 json파일의 'auto'에 host 연결정보, id연결정보, id, password, host, houdini 확장자를 기록한다. \n
        만약 기존에 json파일이 없으면 창에서 id, password를 저장하고 만약 정보가 있으면 id, password, houdini 확장자를 받아와서
        로그인 버튼을 누른다.
        """
        # initialize information from login UI
        log_path = self.login_log.user_path
        self.login_log.host = "http://192.168.3.116/api"
        log_id = self.login_window.input_id.text()
        log_pw = self.login_window.input_pw.text()
        log_sfw = self.login_window.hipbox.currentText()[1:]
        log_value = self.login_log.load_setting()
        log_dict = self.login_log.user_dict
        # check json file to get auto login information
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
        """main UI에서 사용자를 로그아웃 시키는 메소드. \n
        listview, user info, houdini 확장자, host 연결상태, id 연결상태를 모두 초기화하고 로그인 창이 새로 뜬다.
        """
        if self.login_log.connect_login():
            self.login_log.log_out()
            # clear lists, models, and data
            self.render_list_data.clear()
            self.render_model.pepperlist.clear()
            self.template_model.pepperlist.clear()
            self.shot_model.pepperlist.clear()
            self.projects_selection.clear()
            self.renderlists_selection.clear()
            self.templates_selection.clear()
            self.shots_selection.clear()
            self.render_model.layoutChanged.emit()
            self.template_model.layoutChanged.emit()
            self.shot_model.layoutChanged.emit()
            # Close main UI and show login UI
            self.main_window.close()
            self.login_window.show()

    def open_main_window(self):
        """로그인 성공 시 main UI를 디스플레이 해주는 메소드. \n
        projects, templates, shots, render_lists의 네 가지 listview 나뉘어 있으며
        projects 에서는 로그인 된 유저가 assign 되어있는 project들을 projects_listview에 디스플레이 해준다.
        templates 에서는 선택된 project 안의 fx templates를 templates_listview에 디스플레이 해준다.
        shots 에서는 선택된 fx template가 casting 된로 shots를 shots_listview에 디스플레이 해준다.
        renderlists 에서는 Houdini로 넘겨 precomp를 진행할 shot들을 renderlists_listview에 디스플레이 해준다. \n
        renderlists는 self.render_model.pepperlist에 담긴 shot들의 name의 value 값만 보여주는 것이고,
        render 버튼 클릭 시 self.render_model.pepperlist 를 Houdini로 전달한다.
        """
        self.create_main_menubar()
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
        """projects_listview 의 project 를 클릭 시 실행 되는 메소드.\n
        선택한 project의 fx template 들을 pepper.project 에 set 한 뒤 self.all_assets 에 fx template들을 받아 온다.
        그리고 가져온 fx template 들을 templates_listview 에 디스플레이 해준다.
        다른 project 클릭 시 templates_listview 를 clear 한 뒤 이 메소드를 다시 실행하게 된다.

        Args:
            event: Listview click event
        """
        project_name = self.my_projects[event.row()]
        self.pepper.project = project_name
        self.all_assets = []
        # append templates to template listview
        for asset in self.pepper.get_all_assets():
            if self.pepper.check_asset_type(asset, 'fx_template') is None:
                continue
            self.pepper.asset = asset
            self.pepper.entity = 'asset'
            if self.pepper.check_task_status('Done', 'simulation') is True:
                self.all_assets.append(asset)
        self.template_model.pepperlist.clear()
        self.shot_model.pepperlist.clear()
        for asset in self.all_assets:
            self.template_model.pepperlist.append(asset)
        # renew listview
        self.template_model.layoutChanged.emit()
        self.shot_model.layoutChanged.emit()
        self.templates_selection.clear()
        self.shots_selection.clear()
        self.renderlists_selection.clear()
        self.main_window.statusBar().showMessage('Select template')

    def template_selected(self, event):
        """templates_listview의 template 클릭 시 실행 되는 메소드. \n
        클릭한 template이 casting된 shot들의 dict를 가져온다. dict에서 sequence_name, shot_name을 가져와 shot의 이름을 만들어
        shot listview에 디스플레이 해준다. \n
        선택된 template의 정보를 template listview 하단에 디스플레이 해준다. comboBox를 통해 template의 revision을 선택할 수 있다.

        Args:
            event: Listview click event
        """
        template_name = self.all_assets[event.row()]
        self.pepper.asset = template_name
        self.pepper.entity = 'asset'
        # reset comboBox, get template info
        rev_list = self.pepper.get_every_revision_for_working_file('fx_template')
        self.renew_template_cbox(rev_list)
        self.renew_template_info()
        # append shot names to shot listview
        self.all_shots = self.pepper.get_casting_path_for_asset()
        self.shot_model.pepperlist.clear()
        for shot in self.all_shots:
            self.pepper.sequence = shot['sequence_name']
            self.pepper.shot = shot['shot_name']
            self.pepper.entity = 'shot'
            if self.pepper.check_task_status('Done', 'layout_camera') is True:
                self.shot_model.pepperlist.append(shot['sequence_name'] + '_' + shot['shot_name'])
        # renew listview
        self.shot_model.layoutChanged.emit()
        self.shots_selection.clear()
        self.renderlists_selection.clear()
        self.main_window.statusBar().showMessage('shots 를 선택하세요 ! 다중선택가능 ! ')

    def shot_selected(self, event):
        """shots_listview의 하나의 shot을 클릭시 실행되는 메소드. \n
        선택된 shot 정보를 shot listview 하단에 디스플레이 해준다. comboBox를 통해 shot의 revision을 선택할 수 있다.
        다중 선택시 실행되지 않고, 하나의 shot을 선택했을 때만 실행된다.

        Args:
            event: Listview click event
        """
        shot_dict = self.all_shots[event.row()]
        self.pepper.sequence = shot_dict['sequence_name']
        self.pepper.shot = shot_dict['shot_name']
        self.pepper.entity = 'shot'
        rev_list = self.pepper.get_every_revision_for_output_file('camera_cache', 'layout_camera')
        self.renew_shot_cbox(rev_list)
        self.renew_shot_info()
        self.renderlists_selection.clear()

    def renew_template_info(self):
        """template_info_label에 template info를 디스플레이 해주는 메소드. \n
        선택된 template의 simulation working file에서 작업자의 이름, 수정 시각, revision을 가져온다.
        """
        revision = self.main_window.template_rev_cbox.currentText()
        name, time, rev = self.pepper.get_working_file_data('simulation', revision, 'asset')
        date = time[:10]
        clock = time[11:]
        self.main_window.template_info_label.setText(f"{name}\n{date}\n{clock}")

    def renew_shot_info(self):
        """shot_info_label에 shot info를 디스플레이 해주는 메소드. \n
        선택된 shot의 camera_cache output file에서 작업자의 이름, 수정 시각, revision을 가져온다.
        """
        revision = self.main_window.shot_rev_cbox.currentText()
        name, time, rev = self.pepper.get_output_file_data('camera_cache', 'layout_camera', revision, 'shot')
        date = time[:10]
        clock = time[11:]
        self.main_window.shot_info_label.setText(f"{name}\n{date}\n{clock}")

    def renew_template_cbox(self, rev_list):
        """template_rev_cbox에 선택된 template의 모든 revision을 추가해주는 메소드. \n
        comboBox의 정보대로 렌더할 shot의 template revision이 결정된다.
        """
        self.main_window.template_rev_cbox.clear()
        for rev in rev_list:
            self.main_window.template_rev_cbox.addItem(f'{rev}')

    def renew_shot_cbox(self, rev_list):
        """shot_rev_cbox에 선택된 shot의 모든 revision을 추가해주는 메소드. \n
        comboBox의 정보대로 렌더할 shot의 camera_cache revision이 결정된다.
        """
        self.main_window.shot_rev_cbox.clear()
        for rev in rev_list:
            self.main_window.shot_rev_cbox.addItem(f'{rev}')

    def append_render_list(self):
        """main UI의 append_btn에 연결되어 클릭시 실행되는 메소드. \n
        선택된 shot들을 pepper.make_precomp_dict를 사용해 BlackPepper의 렌더에서 필요한 path들을 dict로 만든다.
        완성된 dict는 self.render_model.pepperlist에 append된다.
        """
        self.main_window.statusBar().showMessage('Order of render files can be changed by drag & drop')
        selections = self.shots_selection.selectedRows()
        # Return if row isn't selected
        if len(selections) == 0:
            return
        # Get revisions from comboBox
        temp_rev = int(self.main_window.template_rev_cbox.currentText())
        shot_rev = self.main_window.shot_rev_cbox.currentText()
        if shot_rev == '':
            shot_rev = None
        else:
            shot_rev = int(shot_rev)
        # Shot revision is used when only one row is selected
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
        """Render list에 중복된 dict가 들어가지 않게 체크해주고, 중복되지 않는다면 dict를 Render list에 추가해주는 메소드. \n
        Shot name이 같아도 revision이 다르다면 Render list에 들어갈 수 있다.
        """
        if path_dict in self.render_model.pepperlist:
            return
        self.render_model.pepperlist.append(path_dict)
        return

    def renew_render_list(self):
        """Render list의 listview를 최신화 해주는 메소드. \n
        """
        self.shots_selection.clear()
        self.render_model.layoutChanged.emit()
        self.renderlists_selection.clear()

    def delete_render_list(self):
        """main UI의 del_btn에 연결되어 클릭시 사용되는 메소드.\n
        Render list의 선택된 shot을 self.render_model.pepperlist에서 제거한다.
        """
        if not self.renderlists_selection.selectedRows():
            return
        idx = self.renderlists_selection.selectedRows()[0]
        for precomp in self.render_model.pepperlist:
            if precomp['name'] == idx.data():
                self.render_model.pepperlist.remove(precomp)
        self.renew_render_list()

    def clear_list(self):
        """main UI의 reset_btn에 연결되어 클릭시 Render list를 초기화하는 메소드. \n
        self.render_model.pepperlist도 같이 초기화되며, 초기 상태로 돌아가기 때문에 조심해야 한다.
        """
        self.pepper.precomp_list = []
        self.render_model.pepperlist.clear()
        self.render_model.layoutChanged.emit()

    def create_login_menubar(self):
        """login UI에 메뉴바를 생성하는 메소드. \n
        Menu 탭 내부에 Exit 버튼이 있으며, Ctrl+Q 입력시 Exit 버튼을 누른 것과 같이 UI와 BlackPepper가 종료된다.
        """
        login_menu_bar = self.login_window.menuBar()
        login_menu = login_menu_bar.addMenu('Menu')
        exit_action = QAction('Exit', self.login_window)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(QApplication.instance().quit)
        login_menu.addAction(exit_action)

    def create_main_menubar(self):
        """main UI에 메뉴바를 생성하는 메소드. \n
        상단 메뉴바에 Menu, Help, User 탭이 생성된다. Menu 탭에는 Recent renderlist, Saved renderlist가 생성된다.
        Recent renderlist에는 최근에 렌더한 shot들의 정보가 저장되어있고, Saved renderlist에는 저장한 shot들의 정보가 저장되어있다. \n
        Help 탭에는 Kistu, SideFX, 그리고 각 VFX studio들의 웹페이지의 하이퍼링크가 생성된다. \n
        User 탭에는 Host의 주소와 User ID가 디스플레이 되고, Logout 버튼이 있다.
        각 탭에는 단축키가 있어서 빠르게 접근할 수 있다.
        """
        # Getting json file path
        self.home_json_path()
        # Creating File menu
        main_menu_bar = self.main_window.menuBar()
        main_menu_bar.setNativeMenuBar(False)
        main_menu_bar.clear()
        self.main_filemenu = main_menu_bar.addMenu('&File')
        # Updating File menu when opening menubar
        self.main_filemenu.aboutToShow.connect(self.set_main_menubar)
        # Creating Help menu
        main_helpmenu = main_menu_bar.addMenu('&Help')
        # 'File' menu add 'Open Recent preset' & 'Exit'
        self.set_main_menubar()
        # Set Kitsu website link
        kisu_action = QAction('Kitsu', self.main_window)
        kisu_action.setShortcut('F1')
        kisu_action.setStatusTip('Open Kitsu website')
        kisu_action.triggered.connect(lambda: webbrowser.open('http://192.168.3.116/'))
        main_helpmenu.addAction(kisu_action)
        # Set SideFX website link
        sidefx_action = QAction('SideFX', self.main_window)
        sidefx_action.setShortcut('F2')
        sidefx_action.setStatusTip('Open SideFX website')
        sidefx_action.triggered.connect(lambda: webbrowser.open('https://www.sidefx.com/'))
        main_helpmenu.addAction(sidefx_action)
        main_helpmenu.addSeparator()
        # Set Scanline VFX website link
        scanline_action = QAction('Scanline VFX', self.main_window)
        scanline_action.setShortcut('F5')
        scanline_action.setStatusTip('Open Scanline VFX website')
        scanline_action.triggered.connect(lambda: webbrowser.open('https://www.scanlinevfx.com/'))
        main_helpmenu.addAction(scanline_action)
        # Set VA Studio website link
        va_action = QAction('VA Studio', self.main_window)
        va_action.setShortcut('F6')
        va_action.setStatusTip('Open VA studio website')
        va_action.triggered.connect(lambda: webbrowser.open('https://www.vastudio.co.kr/'))
        main_helpmenu.addAction(va_action)
        # Set Westworld website link
        west_action = QAction('Westworld', self.main_window)
        west_action.setShortcut('F7')
        west_action.setStatusTip('Open Westworld website')
        west_action.triggered.connect(lambda: webbrowser.open('https://www.westworld.co.kr/'))
        main_helpmenu.addAction(west_action)
        # Creating User menu
        main_user = main_menu_bar.addMenu('&User')
        host_info = QAction(f'Host : {self.login_log.host}', self.main_window)
        main_user.addAction(host_info)
        id_info = QAction(f'User ID : {self.login_log.user_id}', self.main_window)
        main_user.addAction(id_info)
        main_user.addSeparator()
        # Creating logout in User menu
        logout_action = QAction('&Logout', self.main_window)
        logout_action.setShortcut('Ctrl+L')
        logout_action.setStatusTip('Logout application')
        logout_action.triggered.connect(self.user_logout)
        main_user.addAction(logout_action)

    def set_main_menubar(self):
        """main UI의 menubar 중 File menu의 submenu들을 생성해주는 메소드. \n
        Recent renderlist에는 최근에 렌더한 shot들의 정보가 저장되어있고, Saved renderlist에는 저장한 shot들의 정보가 저장되어있다.
        각 최대 5개의 list를 저장할 수 있고, 이미 5개가 있는 상태에서 list가 새로 저장될 시 가장 오래된 list를 삭제한다.
        """
        # Renew filemenu
        self.main_filemenu.clear()
        self.create_json()
        # Make submenus
        recent_menu = QMenu('Recent renderlists', self.main_window)
        saved_menu = QMenu('Saved renderlists', self.main_window)
        with open(self.preset_json_path, 'r') as f:
            self.render_list_data = json.load(f)
        # Get recent renderlists from json file
        for renderlists in self.render_list_data['recent']:
            for renderlist in renderlists:
                file_action = self.append_renderlist_to_menubar(renderlist)
                recent_menu.addAction(file_action)
        # Get saved renderlists from json file
        for renderlists in self.render_list_data['saved']:
            for renderlist in renderlists:
                file_action = self.append_renderlist_to_menubar(renderlist)
                saved_menu.addAction(file_action)
        # Add submenus to file menu
        self.main_filemenu.addMenu(recent_menu)
        self.main_filemenu.addMenu(saved_menu)
        self.main_filemenu.addSeparator()
        # Add exit
        exit_action = QAction('&Exit', self.main_window)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(QApplication.instance().quit)
        self.main_filemenu.addAction(exit_action)

    def append_renderlist_to_menubar(self, render_list):
        file_action = QAction(render_list, self)
        file_action.triggered.connect(lambda: self.get_renderlist(file_action.text()))
        return file_action

    def get_renderlist(self, text):
        """저장된 Renderlist를 self.render_model.pepperlist에 다시 가져와주는 메소드. \n
        File의 submenu 안의 renderlist를 클릭시 실행된다. 해당 renderlist의 이름으로 json file 안의 딕셔너리에서 value값을 찾아온다.
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
        """Render 버튼 클릭시 json file의 recent 키에 self.render_model.pepperlist 안의 shot 정보들을 저장하는 메소드. \n
        Render files가 비어있다면 실행되지 않는다.
        json file이 없을 시 생성해주고, recent 안에 key는 현재 시각, value는 shot 정보들로 저장이 된다.
        """
        if len(self.render_model.pepperlist) == 0:
            return
        self.create_json()
        self.open_json()
        recent_data = self.render_list_data.get('recent', [])
        now = datetime.now()
        # Max index of recent data is 5
        if len(recent_data) >= 5:
            recent_data.pop(4)
        recent_data.insert(0, {
            f'recent_{now.date()}_time_{now.hour}:{now.minute}:{now.second}': self.render_model.pepperlist
        })
        # 'recent': [self.render_model.pepperlist]
        self.render_list_data['recent'] = recent_data
        self.save_json(self.render_list_data)

    def save_user_renderlists(self):
        """Save 버튼 클릭시 json file의 saved 키에 self.render_model.pepperlist 안의 shot 정보들을 저장하는 메소드. \n
        Render files가 비어있다면 실행되지 않는다.
        json file이 없을 시 생성해주고, saved 안에 key는 현재 시각, value는 shot 정보들로 저장이 된다.
        """
        if len(self.render_model.pepperlist) == 0:
            return
        self.create_json()
        self.open_json()
        saved_data = self.render_list_data.get('saved', [])
        now = datetime.now()
        # Max index of recent data is 5
        if len(saved_data) >= 5:
            saved_data.pop(4)
        saved_data.insert(0, {
            f'saved_{now.date()}_time_{now.hour}:{now.minute}:{now.second}': self.render_model.pepperlist
        })
        # 'saved': [self.render_model.pepperlist]
        self.render_list_data['saved'] = saved_data
        self.save_json(self.render_list_data)

    def home_json_path(self):
        """json file의 로컬 위치를 찾아주는 메소드. \n
        controller 모듈의 실행 위치를 기준으로 .config/user.json 안에 json file이 있기 때문에
        os.path.realpath(__file__)을 통해 절대 경로를 가져오고 구해진 절대 경로를 통해 상대경로로 json file을 찾는다.
        """
        now_path = os.path.realpath(__file__)
        split_path = now_path.split('/')[:-2]
        dir_path = os.path.join('/'.join(split_path), '.config')
        self.preset_json_path = os.path.join(dir_path, 'user.json')

    def open_json(self):
        """json file을 open해 self.render_list_data에 넣어주는 메소드.
        """
        with open(self.preset_json_path, 'r') as f:
            self.render_list_data = json.load(f)

    def save_json(self, data):
        """json file이 업데이트 되어야 할 때 data를 json file에 업데이트 해주는 메소드.
        """
        with open(self.preset_json_path, "w") as f:
            json.dump(data, f, ensure_ascii=False)

    def create_json(self):
        """json file이 없다면 생성해주고, 안에 필요한 dict가 없을 시 생성해주는 메소드.
        """
        self.home_json_path()
        with open(self.preset_json_path, 'r') as json_file:
            self.render_list_data = json.load(json_file)
            if 'recent' not in self.render_list_data:
                self.render_list_data['recent'] = []
            if 'saved' not in self.render_list_data:
                self.render_list_data['saved'] = []
            data_to_save = self.render_list_data
            with open(self.preset_json_path, "w") as f:
                json.dump(data_to_save, f, ensure_ascii=False)

    def render_file_check(self):
        """check UI의 render_list_model에 render list안의 shot들이 houdini에 넘겨 줄 모든 path들을 디스플레이 해주는 메소드. \n
        main UI의 listview에서는 볼 수 없었던 fx template의 working file path, camera_cache의 output file path,
        shot의 FX working file과 output file이 저장될 path, 그리고 template와 camera_cache의 revision을 볼 수 있다.
        """
        self.render_list_model.pepperlist.clear()
        for render_file in self.render_model.pepperlist:
            temp_rev = render_file['temp_working_path'].split('.')[0][-3:]
            cam_rev = render_file['layout_output_path'].split('.')[0][-3:]
            self.render_list_model.pepperlist.append(f"\n{render_file['name']}\n "
                                                     f"Template revision : {temp_rev}\n "
                                                     f"Layout camera revision : {cam_rev}\n " 
                                                     f"{render_file['temp_working_path']}\n "
                                                     f"{render_file['layout_output_path']}\n "
                                                     f"{render_file['fx_working_path']}\n "
                                                     f"{render_file['jpg_output_path']}\n "
                                                     f"{render_file['video_output_path']}\n")
        self.render_list_model.layoutChanged.emit()
        self.check_window.show()

    def close_fullpath(self):
        """check_window를 닫아주는 메소드. Exit 버튼 클릭시 실행된다.
        """
        self.check_window.close()

    def render_execute(self):
        """render list에 있는 shot의 path를 읽어와 template에 Alembic file의 camera값이 들어간 fx working file을 만든다. \n
        precomp의 dictionary value로 만든 command list와 total frame list를 활용하여 Render Progress UI를 실행한다. \n
        Render Progress UI에서는 Houdini Mantra sequence file render, FFmpeg jpg to mov converting 순으로 진행된다. \n
        render 버튼 클릭시 실행되며, 이전까지 선택한 설정들을 초기화 해준다.
        """
        houp = HouPepper()
        save_log = Logger()

        self.home_json_path()
        log_dict = {}
        with open(self.preset_json_path, 'r') as f:
            log_dict = json.load(f)
        for ident in log_dict['auto']:
            save_log.set_logger(ident['user_id'])

        if not self.render_model.pepperlist:
            return
        self.save_recent_renderlists()
        for precomp in self.render_model.pepperlist:
            temp_working_path, layout_output_path, fx_working_path, jpg_output_path, video_output_path \
                = self.pepper.path_seperator(precomp)
            houp.set_fx_working_for_shot(temp_working_path, layout_output_path,
                                         f'{fx_working_path}.{self.pepper.software.get("file_extension")}')
            cmd_list, total_frame_list = houp.make_cmd(precomp)

        self.render_process = RenderMainWindow(cmd_list, total_frame_list)
        self.render_process.resize(800, 600)
        self.render_process.move(1000, 250)
        self.render_process.show()

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


def main():
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QtWidgets.QApplication(sys.argv)
    window = PepperWindow()
    app.exec_()


if __name__ == "__main__":
    main()
