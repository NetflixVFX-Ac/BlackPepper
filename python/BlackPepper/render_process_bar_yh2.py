import re
from PySide2 import QtWidgets, QtCore
import os
import glob
import hou
import _alembic_hom_extensions as abc


class RenderMainWindow(QtWidgets.QMainWindow):
    """
    Houdini Mantra를 활용하여 Template에 Alembic 카메라 값이 추가 된 Hip 파일을 Sequence file(.jpg)로 추출한다.
    터미널에서 mantra_render.py 를 실행하고, 터미널에 출력되는 정보를 Text Widget으로 보여준다.
    정규표현을 활용하여 터미널에 출력되는 정보에서 컨버팅 중인 프레임을 파악하고 전체 프레임과 비교하여 Progress Widget으로
    진행사항을 유저에게 시각적으로 알려준다.
    """

    def __init__(self, next_fx_path, jpg_output_path, mov_output_path, abc_path, cam_node):
        """



        Args:
            next_fx_path:
            jpg_output_path:
            abc_path:
            cam_node:
        """
        super().__init__()
        self.p = None
        self.p2 = None
        self.m = None
        self.total = None
        self.is_interrupted = False
        self.check = False
        self.pro_check = False
        self.filecnt = 0
        self.abc_range = abc.alembicTimeRange(abc_path)

        self.mantra_command = [
            'python',
            '/home/rapa/git/hook/python/BlackPepper/mantra_render.py',
            next_fx_path,
            jpg_output_path,
            abc_path,
            cam_node
        ]

        self.mantra_cmd = (' '.join(str(s) for s in self.mantra_command))

        self.output_dir = os.path.dirname(mov_output_path)
        self.seq_dir = os.path.dirname(jpg_output_path)
        print("seq_dir :", self.seq_dir)
        self.sequence_path = jpg_output_path[:-17] + jpg_output_path[-4:] + '_%04d.jpg'

        self.ffmpeg_command = [
            'ffmpeg',
            "-framerate", '24',  # 초당프레임
            "-i", self.sequence_path,  # 입력할 파일 이름
            "-q 0",  # 출력품질 정함(숫자가 높을 수록 품질이 떨어짐)
            "-threads 8",  # 속도향상을 위해 멀티쓰레드를 지정
            "-c:v", "libx264",  # 코덱
            "-pix_fmt", "yuv420p",  # 포맷양식
            "-y",  # 출력파일을 쓸 때 같은 이름의 파일이 있어도 확인없이 덮어씀
            "-loglevel", "debug",  # 인코딩 과정로그를 보여줌
            mov_output_path + '.mov'
        ]

        self.ffmpeg_cmd = (' '.join(str(s) for s in self.ffmpeg_command))

        # Create the "Interrupt" Button
        self.progress = QtWidgets.QProgressBar()
        self.progress.setRange(0, 100)
        self.text = QtWidgets.QPlainTextEdit()
        self.text.setReadOnly(True)
        self.btn_interrupt = QtWidgets.QPushButton("Interrupt")

        l = QtWidgets.QVBoxLayout()
        l.addWidget(self.btn_interrupt)
        l.addWidget(self.progress)
        l.addWidget(self.text)

        w = QtWidgets.QWidget()
        w.setStyleSheet(u"background-color: rgb(45, 45, 45);\n"
                        "selection-background-color: rgb(45, 180, 198);\n"
                        "font: 10pt\"Courier New\";\n"
                        "color: rgb(180, 180, 180);\n")
        w.setLayout(l)

        self.setCentralWidget(w)
        self.process_check()

    def message(self, s):
        """



        Args:
            s:

        Returns:

        """
        self.text.appendPlainText(s)

    def start_process(self, cmd):
        """



        Returns:

        """
        print('pro_check :', self.pro_check)
        if self.pro_check == False:  # No process running.
            print("cmd :", cmd)
            print("start process check :", self.check)
            self.message("Executing process")
            self.btn_interrupt.setText("Interrupt")
            self.p = QtCore.QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
            self.p.readyReadStandardOutput.connect(self.handle_stdout)
            self.p.readyReadStandardError.connect(self.handle_stderr)
            self.p.stateChanged.connect(self.handle_state)
            self.p.finished.connect(self.process_finished)  # Clean up once complete.
            self.p.start(cmd)
        else:
            self.message("FFmpeg Executing process")
            self.p2 = QtCore.QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
            self.p2.readyReadStandardOutput.connect(self.handle_stdout)
            self.p2.readyReadStandardError.connect(self.handle_stderr)
            self.p2.stateChanged.connect(self.handle_state)
            self.p2.finished.connect(self.process_finished)  # Clean up once complete.
            self.p2.start(cmd)

    def handle_stderr(self):
        """



        Returns:

        """
        print('handle pro_check :', self.pro_check)
        if self.pro_check == False:
            data = self.p.readAllStandardError()
        else:
            data = self.p2.readAllStandardError()
        print('stderr data :', data)
        stderr = bytes(data).decode("utf8")
        print("stderr self.check :", self.check)
        if self.check == False:
            progress = self.simple_percent_parser(stderr, 'mantra')
        elif self.check == None:
            progress = self.simple_percent_parser(stderr, 'ffmpeg')
        if progress:
            self.progress.setValue(progress)

        self.message(stderr)

    def handle_stdout(self):
        """



        Returns:

        """
        print('stdout pro_check :', self.pro_check)
        if self.pro_check == False:
            data = self.p.readAllStandardError()
        else:
            data = self.p2.readAllStandardError()
        print('stdout data :', data)
        stdout = bytes(data).decode("utf8")
        print("stdout self.check :", self.check)
        if self.check == False:
            progress = self.simple_percent_parser(stdout, 'mantra')
        elif self.check == True:
            progress = self.simple_percent_parser(stdout, 'ffmpeg')
        if progress:
            self.progress.setValue(progress)

        self.message(stdout)

    def handle_state(self, state):
        """



        Args:
            state:

        Returns:

        """
        states = {
            QtCore.QProcess.NotRunning: 'Not running',
            QtCore.QProcess.Starting: 'Starting',
            QtCore.QProcess.Running: 'Running',
        }
        state_name = states[state]
        self.message(f"State changed: {state_name}")
        if self.is_interrupted and state == QtCore.QProcess.NotRunning:
            self.process_check()

    def process_finished(self):
        """



        Returns:

        """
        self.message("Process finished.")
        if self.check == None:
            return
        # self.btn_interrupt.setText("Interrupt")
        self.p = None
        self.is_interrupted = False
        self.check = True
        self.pro_check = True
        self.process_check()

    def process_check(self):
        print("check :", self.check)
        if self.check == False:
            self.start_process(self.mantra_cmd)
        elif self.check == True:
            self.check = None
            self.start_process(self.ffmpeg_cmd)



    def simple_percent_parser(self, output, render_fmt):
        """



        Args:
            output:
            total:

        Returns:

        """
        if render_fmt == 'mantra':
            progress_re = re.compile('_(\d+)\.jpg')
            self.m = progress_re.search(output)
            self.total = int(self.abc_range[1]*hou.fps())
            print("mantra search :", self.m)
            print('mantra total:', self.total)
        elif render_fmt == 'ffmpeg':
            progress_re = re.compile("frame=   (\d+)")
            self.m = progress_re.search(output)
            self.total = self.tree(self.seq_dir)
            print("ffmpeg search :", self.m)
            print('ffmpeg total:', self.total)

        if self.m:
            pc_complete = self.m.group(1)
            if pc_complete:
                pc = int(int(pc_complete) / self.total * 100)
                return pc

    def tree(self, path):
        """ Sequence file이 있는 경로 내 파일의 갯수를 파악하여 Total frame을 계산한다.

        Args:
            path (str): Sequence file path

        Returns: filecnt

        """
        for x in sorted(glob.glob(path + "/*")):
            if os.path.isfile(x):
                self.filecnt += 1
            else:
                print("unknown:", x)
        return int(self.filecnt)
