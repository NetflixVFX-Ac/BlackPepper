import sys
import os
import glob
import json
import webbrowser
from PySide2 import QtCore, QtWidgets
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QMainWindow
from BlackPepper.ui.model import PepperModel
from BlackPepper.ui.view import PepperView
from BlackPepper.pepper import Houpub
from BlackPepper.houpepper import HouPepper

from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QAction, QApplication

from datetime import datetime


class PepperWindow(QMainWindow):
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
        self.projects_selection = None
        self.templates_selection = None
        self.shots_selection = None
        self.renderlists_selection = None
        self.my_projects = []
        self.all_assets = []
        self.all_shots = []
        self.render_list_data = []
        self.filename = []
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
        login_ui = QtCore.QFile(os.path.join(script_path, 'ui_backup/mvc_login_2.ui'))
        login_ui.open(QtCore.QFile.ReadOnly)
        self.login_ui_loader = QUiLoader()
        self.login_window = self.login_ui_loader.load(login_ui)
        self.login_window.setWindowTitle('Black Pepper v0.0.1')
        self.login_window.move(1000, 300)
        self.login_window.show()
        # main Ui loader
        main_ui = QtCore.QFile(os.path.join(script_path, 'ui_backup/mvc_main_3_sw.ui'))
        main_ui.open(QtCore.QFile.ReadOnly)
        self.main_ui_loader = QUiLoader()
        self.main_window = self.main_ui_loader.load(main_ui)
        self.main_window.move(700, 250)
        self.main_window.setWindowTitle('Black Pepper v0.0.1')

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
        # add listview to ui
        self.main_window.gridLayout_3.addWidget(self.projects_listview, 2, 0)
        self.main_window.gridLayout_3.addWidget(self.templates_listview, 2, 1)
        self.main_window.gridLayout_3.addWidget(self.shots_listview, 2, 2)
        self.main_window.gridLayout_3.addWidget(self.renderlists_listview, 2, 5)

        # set statusbar to window
        self.login_window.statusBar().showMessage('kitsu 로그인 하세요!  houdini 확장자 선택하세요!')
        self.main_window.statusBar().showMessage('project 를 선택하세요 !')

        # set main menubar
        self.main_menu_bar = self.main_window.menuBar()
        self.main_menu_bar.setNativeMenuBar(False)
        self.main_filemenu = self.main_menu_bar.addMenu('Menu')
        self.save_precomp_list_json()
        exitAction = QAction('Exit')
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QApplication.instance().quit)
        self.main_filemenu.addAction(exitAction)


        # login_menu_bar = self.login_window.menuBar()
        # login_menu_bar.setNativeMenuBar(False)
        # login_filemenu = login_menu_bar.addMenu('login test')
        #
        # # main menubar
        # main_menu_bar = self.main_window.menuBar()
        # main_menu_bar.setNativeMenuBar(False)
        # # set File menubar
        # main_filemenu = main_menu_bar.addMenu('File')
        # exitAction = QAction('Exit')
        # exitAction.setShortcut('Ctrl+Q')
        # exitAction.setStatusTip('Exit application')
        # exitAction.triggered.connect(QApplication.instance().quit)
        # main_filemenu.addAction(exitAction)
        # # set Help menubar
        # main_helpmenu = main_menu_bar.addMenu('Help')
        #
        # # set Preset menubar
        # main_presetmenu = main_menu_bar.addMenu('Preset')

        # directory_path = '/home/rapa/git/hook/python/BlackPepper/ui/ui_sw'
        # json_files = sorted(glob.glob(os.path.join(directory_path, '*.json')), key=os.path.getmtime, reverse=True)[:5]
        # for file_path in json_files:
        #     action = QAction(os.path.basename(file_path), self)
        #     action.triggered.connect(lambda _, path=file_path: self.handle_file(path))
        #     filemenu.addAction(action)

        main_helpmenu = self.main_menu_bar.addMenu('Help')
        # menubar help 버튼에 링크 추가하기
        # self.exitAction.triggered.connect(lambda: webbrowser.open('http://192.168.3.116/'))
        kisuAction = QAction('Kitsu')
        kisuAction.setShortcut('F1')
        kisuAction.setStatusTip('Kitsu site open')
        kisuAction.triggered.connect(lambda: webbrowser.open('http://192.168.3.116/'))
        main_helpmenu.addAction(kisuAction)
        # self.main_window.actionGazu.triggered.connect(lambda: webbrowser.open('https://gazu.cg-wire.com/index.html'))
        # self.main_window.actionSidefx.triggered.connect(lambda: webbrowser.open('https://www.sidefx.com/'))

        # file_menu = menu_bar.addMenu('File')
        # self.main_window.menubar().
        # self.main_window.recentRenderlist1.triggered.connect(lambda checked, filename=self.filename: self.open_recent_file(self.filename))
        # recent_file_menu = QMenu("Menu1")
        # recent_files = self.pepper.precomp_list
        # print(recent_files)
        # for file_name in recent_files:
        #     action = QAction(file_name, recent_file_menu)
        #     action.triggered.connect(lambda checked, file_name=file_name: self.open_recent_file(file_name))
        #     recent_file_menu.addAction(action)
        # menu_bar = self.menuBar()
        # menu_bar.addMenu(recent_file_menu)
        # self.createActions()
        # self.createMenus()
        # app.exec_() : 프로그램을 대기상태,즉 무한루프상태로 만들어준다.
        self.app.exec_()

    def save_precomp_list_json(self):
        """

        Returns:

        """
        directory_path = '/BlackPepper/ui/ui_sw'
        json_files = sorted(glob.glob(os.path.join(directory_path, '*.json')), key=os.path.getmtime, reverse=True)[:5]

        for file_path in json_files:
            file_path = QAction(os.path.basename(file_path))
            file_path.triggered.connect(lambda _, path=file_path: self.handle_file(path))
            self.main_filemenu.addAction(file_path)

        self.main_filemenu.addSeparator() # QMenu에 구분선 추가

    def ui_menubar(self):
        # add login menubar
        login_menu_bar = self.login_window.QMenuBar(self)
        login_menu_bar.setNativeMenuBar(False)
        login_menu = login_menu_bar.addMenu('login test')

        # add main menubar
        main_menu_bar = self.main_window.QMenuBar(self)
        main_menu_bar.setNativeMenuBar(False)

        add_menu = main_menu_bar.addMenu('Menu')
        exit_action = QAction('Exit')
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(QApplication.instance().quit)
        add_menu.addAction(exit_action)

        # set Help menubar
        # main_help = main_menu_bar.addMenu('Help')
        # kitsu_action = QAction('Kitsu host site')
        # kitsu_action.setShortcut('F1')
        # kitsu_action.setStatusTip('Kitsu houst site oepn')
        # main_help.triggered.connect(lambda: webbrowser.open('http://192.168.3.116/'))
        #
        # # set Preset menubar
        # main_preset = main_menu_bar.addMenu('Preset')

    def handle_file(self, file_path):
        # TODO: 파일 내용 처리하기

        pass

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
        self.login_window.close()
        self.open_main_window()

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
        self.main_window.statusBar().showMessage('temp 를 선택하세요 !')

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

    # menu bar
    def createActions(self):
        self.newAct = QAction("&New", self, shortcut=QKeySequence.New,
                statusTip="Create a new file", triggered=self.newFile)

        self.openAct = QAction("&Open...", self, shortcut=QKeySequence.Open,
                statusTip="Open an existing file", triggered=self.open)

        self.saveAct = QAction("&Save", self, shortcut=QKeySequence.Save,
                statusTip="Save the document to disk", triggered=self.save)

        self.saveAsAct = QAction("Save &As...", self,
                shortcut=QKeySequence.SaveAs,
                statusTip="Save the document under a new name",
                triggered=self.saveAs)

        # for i in range(MainWindow.MaxRecentFiles):
        #     self.recentFileActs.append(
        #             QAction(self, visible=False,
        #                     triggered=self.openRecentFile))

        # self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q",
        #         statusTip="Exit the application",
        #         triggered=QApplication.instance().closeAllWindows)

        self.aboutAct = QAction("&About", self,
                statusTip="Show the application's About box",
                triggered=self.about)

        # self.aboutQtAct = QAction("About &Qt", self,
        #         statusTip="Show the Qt library's About box",
        #         triggered=QApplication.instance().aboutQt)

    def createMenus(self):
        self.fileMenu = self.main_window.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.newAct)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addAction(self.saveAsAct)
        self.separatorAct = self.fileMenu.addSeparator()
        # for i in range(MainWindow.MaxRecentFiles):
        #     self.fileMenu.addAction(self.recentFileActs[i])
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)
        self.updateRecentFileActions()

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

    def menubar_clear(self):

        pass

    def menubar_open_preset(self, file_name):
        # 파일을 열거나 처리하는 코드
        pass

    def save_preset_json(self):
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

    def chat_gpt_2(self):
        filename = 'render_check_list.json'

        if not os.path.isfile(filename):
            # 파일이 존재하지 않는 경우
            self.render_model.pepperlist.clear()
            for render in self.pepper.precomp_list:
                self.render_list_data.append(render['name'])
            with open(filename, "w") as f:
                json.dump(self.render_list_data, f, ensure_ascii=False)
        else:
            # 파일이 존재하는 경우
            base_filename, ext = os.path.splitext(filename)
            i = 1
            while i <= 5 and os.path.isfile(f"{base_filename}_v{i}{ext}"):
                i += 1
            if i <= 5:
                filename = f"{base_filename}_v{i}{ext}"
            else:
                filename = f"{base_filename}_v1{ext}"
            self.render_model.pepperlist.clear()
            for render in self.pepper.precomp_list:
                self.render_list_data.append(render['name'])
            with open(filename, "w") as f:
                json.dump(self.render_list_data, f, ensure_ascii=False)

    def chat_gpt(self):
        filename = 'render_check_list.json'

        if not os.path.isfile(filename):
            self.render_model.pepperlist.clear()
            for render in self.pepper.precomp_list:
                self.render_list_data.append(render['name'])
            with open(filename, "w") as f:
                json.dump(self.render_list_data, f, ensure_ascii=False)
        else:
            base_filename, ext = os.path.splitext(filename)
            i = 1
            while i <= 5 and os.path.isfile(filename):
                filename = f"{base_filename}_v{i}{ext}"
                i += 1
            if i > 5:
                filename = f"{base_filename}_v1{ext}"
            self.render_model.pepperlist.clear()
            for render in self.pepper.precomp_list:
                self.render_list_data.append(render['name'])
            with open(filename, "w") as f:
                json.dump(self.render_list_data, f, ensure_ascii=False)

    def precomp_list_save_tt(self):
        # render_list_path = '/home/rapa/git/hook/python/BlackPepper/ui/ui_sw/render_check_list.json'
        render_list_path = 'render_check_list.json'

        index = 0
        while os.path.exists(render_list_path):
            render_list_path = re.sub(r'_\d+(?=[.]\w+$)', r'', render_list_path)
            render_list_path = re.sub(r'(?=[.]\w+$)', rf'_{index}', render_list_path)
            index += 1

        # if os.path.isfile(render_list_path):
        #     self.render_list_data.clear()
        # render_list = self.pepper.precomp_list()

        self.render_model.pepperlist.clear()
        for render in self.pepper.precomp_list:
            self.render_list_data.append(render['name'])
        with open(render_list_path, "w") as f:
            json.dump(self.render_list_data, f, ensure_ascii=False)

    def load_preset_set(self):
        with open(self.render_list_path, "r") as f:
            self.render_list_data = json.load(f)
            print(self.render_list_data)

    def precomp_list_len(self):
        total = len(self.render_list_data)

        self.render_model.pepperlist.clear()
        for render in self.pepper.precomp_list:
            self.render_model.pepperlist.append(render['name'])
        self.render_model.layoutChanged.emit()
        self.shots_selection.clear()
        self.renderlists_selection.clear()

    def render_execute(self):
        # houp = HouPepper()
        # for precomp in self.pepper.precomp_list:
        #     temp_working_path, layout_output_path, fx_working_path, video_output_path = self.path_seperator(precomp)
        #     print(temp_working_path, layout_output_path, fx_working_path)
        #     houp.set_fx_working_for_shot(temp_working_path, layout_output_path,
        #                                  f'{fx_working_path}.{self.pepper.software.get("file_extension")}')
        # for precomp in self.pepper.precomp_list:
        #     temp_working_path, layout_output_path, fx_working_path, video_output_path = self.path_seperator(precomp)
        #     houp.set_mantra_for_render(f'{fx_working_path}.{self.pepper.software.get("file_extension")}',
        #                                video_output_path)
        if len(self.pepper.precomp_list) == 0:
            return

        # self.precomp_list_save()

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
        video_output_path = precomp['video_output_path']
        return temp_working_path, layout_output_path, fx_working_path, video_output_path


def main():
    window = PepperWindow()


if __name__ == "__main__":
    main()
