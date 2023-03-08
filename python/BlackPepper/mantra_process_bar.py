import re
from PySide2 import QtWidgets, QtCore
import os
import glob
import shutil
import hou

class MantraMainWindow(QtWidgets.QMainWindow):

    def __init__(self, hip_path, output_path, total_frame, cam_node, abc_range):
        super().__init__()
        self.hip_path = hip_path
        self.output_path = output_path
        self.total_frame = total_frame
        self.cam_node = cam_node
        self.abc_range = abc_range
        self.p = None
        self.btn = QtWidgets.QPushButton("Are you sure?")
        self.btn.pressed.connect(self.start_process)
        self.text = QtWidgets.QPlainTextEdit()
        self.text.setReadOnly(True)

        self.progress = QtWidgets.QProgressBar()
        self.progress.setRange(0, 100)

        l = QtWidgets.QVBoxLayout()
        l.addWidget(self.btn)
        l.addWidget(self.progress)
        l.addWidget(self.text)

        w = QtWidgets.QWidget()
        w.setLayout(l)

        self.setCentralWidget(w)

    def message(self, s):
        self.text.appendPlainText(s)

    def start_process(self):
        if self.p is None:  # No process running.
            self.p = QtCore.QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
            self.p.readyReadStandardOutput.connect(self.handle_stdout)
            self.p.readyReadStandardError.connect(self.handle_stderr)
            self.p.stateChanged.connect(self.handle_state)
            self.p.finished.connect(self.process_finished)  # Clean up once complete.
            self.p.start(self.set_mantra_for_render(self.hip_path, self.output_path))

    def set_mantra_for_render(self, hip_path, output_path):
        cam_setting = f'/obj/{self.cam_node}/'
        basename = os.path.basename(hip_path)
        home_path = os.path.expanduser('~')
        temp_path = os.path.join(home_path+'/temp', basename)
        if not os.path.isdir(home_path+'/temp'):
            os.makedirs(home_path+'/temp')
        shutil.copyfile(hip_path, temp_path)
        hou.hipFile.load(temp_path)
        root = hou.node('/out')
        if root is not None:
            n = root.createNode('ifd')
            n.parm('camera').set(cam_setting)
            n.parm('vm_picture').set(f'{output_path[:-8]}$F4.jpg')
            n.parm('trange').set(1)
            for i in n.parmTuple('f'):
                i.deleteAllKeyframes()
            n.parmTuple('f').set([self.abc_range[0] * hou.fps(), self.abc_range[1] * hou.fps(), 1])
            n.parm('vm_verbose').set(1)
            n.parm("execute").pressButton()
        output_dir = os.path.dirname(output_path) + '/*.jpg'
        error_dir = os.path.dirname(output_path) + '/*.jpg.mantra_checkpoint'
        file_list = glob.glob(output_dir)
        error_list = glob.glob(error_dir)
        if len(file_list) == self.abc_range[1] * hou.fps():
            if len(error_list) == 0:
                shutil.rmtree(home_path+'/temp')
            else:
                print("render error")
        else:
            print("missing sequence frame")
            # self.close()

    def handle_stderr(self):
        data = self.p.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        progress = self.simple_percent_parser(stderr, self.total_frame)
        if progress:
            self.progress.setValue(progress)

        self.message(stderr)

    def handle_stdout(self):
        data = self.p.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        self.message(stdout)

    def handle_state(self, state):
        states = {
            QtCore.QProcess.NotRunning: 'Not running',
            QtCore.QProcess.Starting: 'Starting',
            QtCore.QProcess.Running: 'Running',
        }
        state_name = states[state]
        self.message(f"State changed: {state_name}")

    def process_finished(self):
        self.message("Process finished.")
        self.p = None


    def simple_percent_parser(self, output, total):# 프로세스바에 시각화 해줄 수치를 만들어 내는 백분율계산기
        progress_re = re.compile("_(\d+).jpg")
        m = progress_re.search(output)
        print("m search :", m)
        if m:
            pc_complete = m.group(1)
            if pc_complete:
                pc = int(int(pc_complete) / total * 100)
                return pc


        # progress_re2 = re.compile("(\d+) frames successfully")
        # m2 = progress_re2.search(output)
        # if m2:
        #     pc_complete = m2.group(1)
        #     if pc_complete:
        #         print(pc_complete, total)
        #         pc = int(int(pc_complete) / total * 100)
        #         return pc #백분율을 통해 process bar에 보여질 값
