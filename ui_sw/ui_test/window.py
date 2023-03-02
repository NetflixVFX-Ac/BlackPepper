"""

login.ui를 불러와서 사용자가 Login 버튼을 누르면 login.ui 창을 닫고 main.ui 창을 연다.

Qt디자이너 에서 설정한 ui 를 가져와서 listview와 Model.py를 컨트롤한다.

"""

import sys
from PySide2 import QtCore, QtWidgets
# from PySide2.QtWidgets import QWidget
# from PySide2.QtCore import Qt, QFile
from PySide2.QtUiTools import QUiLoader

from pepper import Houpub
from Model import MainModel


# 영빈님 sub class
class ProjectView(QtWidgets.QListView):
    def __init__(self, parent):
        super(ProjectView, self).__init__(parent=None)

    def get_selected_project(self):
        if not self.model():
            return
        return self.model().selectedIndexes()[-1]


class MainWindow:

    def __init__(self):
        super().__init__()

        self.get_shots = None
        self.get_casting_shots = None
        self.get_assets = None
        self.get_projects = None

        self.host = None
        self.email = None
        self.pw = None
        self.pepper = Houpub()

        # model loader
        self.model_proj = MainModel()
        self.model_temp = MainModel()
        self.model_shot = MainModel()
        self.model_render = MainModel()

        # login Ui loader
        login_ui_file = "/home/rapa/git/hook/ui_sw/ui_test/login.ui"
        login_ui = QtCore.QFile(login_ui_file)
        login_ui.open(QtCore.QFile.ReadOnly)
        loader = QUiLoader()
        self.window_login = loader.load(login_ui)
        self.window_login.show()

        # main Ui loader
        main_ui_file = "/home/rapa/git/hook/ui_sw/ui_test/main.ui"
        main_ui = QtCore.QFile(main_ui_file)
        main_ui.open(QtCore.QFile.ReadOnly)
        loader = QUiLoader()
        self.window_main = loader.load(main_ui)
        self.window_main.show()

        # set connect Ui
        self.window_login.login_btn.clicked.connect(self.set_login)

        self.window_main.lv_proj.clicked.connect(self.choice_project)
        self.window_main.lv_temp.clicked.connect(self.choice_temp)
        self.window_main.lv_shot.clicked.connect(self.choice_shot)

        self.window_main.add_btn.clicked.connect(self.add_render_file)
        # self.window_main.del_btn.clicked.connect(self.del_render_file)

    def set_login(self):
        email = self.window_login.input_id.text()
        pw = self.window_login.input_pw.text()
        software_ext = self.window_login.hipbox.currentText()[1:]
        self.login_data(email, pw, sel_software=software_ext)

    def login_data(self, email, pw, sel_software):
        self.host = "http://192.168.3.116/api"
        self.email = email
        self.pw = pw

        self.pepper.login(self.host, email, pw)
        self.pepper.software = sel_software
        print(f"login id : {email} , software : {sel_software}")
        self.window_login.close()
        self.open_main()

    def open_main(self):
        # setModel
        self.window_main.lv_proj.setModel(self.model_proj)
        self.get_projects = self.pepper.get_my_projects()
        print(f"get_projects = {self.get_projects}")
        # project list append
        for get_project in self.get_projects:
            self.model_proj.model.append(get_project)

        # self.window_main.show()

    def choice_project(self, event):
        """
        project 선택시 이벤트 발생
        Args:
            event:

        Returns:

        """
        # setModel
        self.window_main.lv_temp.setModel(self.model_temp)
        # event
        project_name = self.get_projects[event.row()]
        self.pepper.project = project_name
        self.get_assets = self.pepper.get_all_assets()
        print(f"project_name : {project_name} get_assets = {self.get_assets}")
        self.model_temp.model.clear()

        # temp list asset append
        for get_asset in self.get_assets:
            self.model_temp.model.append(get_asset)

        # reset 시그널! emit !
        self.model_temp.layoutChanged.emit()


    def choice_temp(self, event):
        # setModel
        self.window_main.lv_shot.setModel(self.model_shot)
        # event
        template_name = self.get_assets[event.row()]
        self.pepper.asset = template_name
        self.get_casting_shots = self.pepper.get_casting_path_for_asset()

        self.model_shot.model.clear()

        for get_casting_shot in self.get_casting_shots:
            self.model_shot.model.append(get_casting_shot["sequence_name"]+"_"+get_casting_shot["shot_name"])
        print(f"{template_name}_casting_shots = {get_casting_shot['sequence_name']+'_'+get_casting_shot['shot_name']}")
        self.model_shot.layoutChanged.emit()


    def choice_shot(self, event):
        """
        샷 리스트를 선택하면 정보를 가져온다 . 이정보를 add_btn 에서 사용한다.
        Args:
            event:

        Returns:

        """
        precomp = None
        # setModel
        self.window_main.lv_render.setModel(self.model_render)


        # event
        shot_name = self.get_casting_shots[event.row()]
        print(shot_name)
        # self.pick_precomp = shot_name
        self.pepper.make_precomp_dict(shot_name)
        self.model_render.model.clear()

        # for precomp in self.pepper.precomp_list:
        #         self.model_render.model.append(precomp["name"])
        # self.model_render.layoutChanged.emit()

    def choice_render(self, event):

        self.window_main.lv_render.setModel(self.model_render)

        pass

    def add_render_file(self, event):
        """
        add_btn 을 설정하는 함수이다.
        lv_shot (listview)  pepper.get_casting_path_for_asset 된 seq_name , shot_name 을 click 하고
        add_btn 을 clicked 하면 lv_render(liseview) 에 추가 한다.
        render files listview 에 있는 render 할 파일목록들을
        """
        self.window_main.lv_render.setModel(self.model_render)
        shot_name = self.get_casting_shots[event.row()]
        # text = self.window.todoEdit.text()
        self.pepper.make_precomp_dict(shot_name)
        self.model_render.model.clear()

        for precomp in self.pepper.precomp_list:
                self.model_render.model.append(precomp["name"])
        self.model_render.layoutChanged.emit()
        if text:  # Don't add empty strings.
            # Access the list via the model.
            self.model_render.model.append(text)
            # Trigger refresh.
            self.model_render.layoutChanged.emit()
            #  Empty the input
            self.window_main.lv_render.setText("")

    def del_render_file(self):
        pass

    def reset_render_file(self):
        pass


QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
app.exec_()
