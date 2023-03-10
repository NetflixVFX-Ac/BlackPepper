import re
from PySide2 import QtWidgets, QtCore
import os
import glob


class RenderMainWindow(QtWidgets.QMainWindow):
    """
    Houdini Mantra를 활용하여 Template에 Alembic 카메라 값이 추가 된 Hip 파일을 Sequence file(.jpg)로 추출한다.
    터미널에서 mantra_render.py 를 실행하고, 터미널에 출력되는 정보를 Text Widget으로 보여준다.
    정규표현을 활용하여 터미널에 출력되는 정보에서 컨버팅 중인 프레임을 파악하고 전체 프레임과 비교하여 Progress Widget으로
    진행사항을 유저에게 시각적으로 알려준다.
    """

    def __init__(self, next_fx_path, jpg_output_path, mov_output_path, abc_path, cam_node, total_frame):
        """



        Args:
            next_fx_path:
            jpg_output_path:
            abc_path:
            cam_node:
            total_frame:
        """
        super().__init__()
        self.p = None
        self.is_interrupted = False
        self.check = False
        # self.is_interrupted = None
        self.total_frame = total_frame
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
        self.sequence_path = jpg_output_path[:-17] + jpg_output_path[-4:] + '_%04d.jpg'
        self.filecnt = 0
        self.ffmpeg_total_frame = self.tree(self.seq_dir)

        self.ffmpeg_command = [
            'ffmpeg',
            "-framerate", '24',  # 초당프레임
            "-i", self.sequence_path,  # 입력할 파일 이름
            "-q 0",  # 출력품질 정함(숫자가 높을 수록 품질이 떨어짐)
            "-threads 8",  # 속도향상을 위해 멀티쓰레드를 지정
            "-c:v", "prores_ks",  # 코덱
            "-pix_fmt", "yuv420p",  # 포맷양식
            "-y",  # 출력파일을 쓸 때 같은 이름의 파일이 있어도 확인없이 덮어씀
            "-loglevel", "debug",  # 인코딩 과정로그를 보여줌
            mov_output_path + '.mov'
        ]

        self.ff_cmd = (' '.join(str(s) for s in self.ffmpeg_command))

        # Create the "Interrupt" Button
        self.progress = QtWidgets.QProgressBar()
        self.progress.setRange(0, 100)
        self.text = QtWidgets.QPlainTextEdit()
        self.text.setReadOnly(True)
        # self.btn = QtWidgets.QPushButton("MANTRA SEQUENCE RENDERING")
        # self.btn.pressed.connect(self.start_process)
        self.btn_interrupt = QtWidgets.QPushButton("Interrupt")

        l = QtWidgets.QVBoxLayout()
        # l.addWidget(self.btn)
        # l.setStyleSheet("background-color:rgb(52, 52, 52);")
        l.addWidget(self.btn_interrupt)
        l.addWidget(self.progress)
        l.addWidget(self.text)

        w = QtWidgets.QWidget()
        w.setStyleSheet(u"background-color: rgb(45, 45, 45);\n"
                        "selection-background-color: rgb(45, 180, 198);\n"
                        "font: 10pt\"Courier New\";\n"
                        "color: rgb(180, 180, 180);\n")

        w.setLayout(l)

        # self.btn_interrupt = False

        self.setCentralWidget(w)
        self.start_process(self.mantra_cmd)
        self.handle_interrupt()

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
        if self.p is None:  # No process running.
            print("cmd :", cmd)
            self.message("Executing process")
            self.btn_interrupt.setText("Interrupt")
            self.p = QtCore.QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
            self.p.readyReadStandardOutput.connect(self.handle_stdout)
            self.p.readyReadStandardError.connect(self.handle_stderr)
            self.p.stateChanged.connect(self.handle_state)
            self.p.finished.connect(self.process_finished)  # Clean up once complete.
            self.p.start(cmd)

    def handle_stderr(self):
        """



        Returns:

        """
        data = self.p.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        print("stderr self.check :", self.check)
        if self.check:
            progress = self.mantra_simple_percent_parser(stderr, self.total_frame)
        else:
            progress = self.ffmpeg_simple_percent_parser(stderr, self.ffmpeg_total_frame)
        if progress:
            self.progress.setValue(progress)

        self.message(stderr)

    def handle_stdout(self):
        """



        Returns:

        """
        data = self.p.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        print("stdout self.check :", self.check)
        if self.check == False:
            progress = self.mantra_simple_percent_parser(stdout, self.total_frame)
        elif self.check == True:
            progress = self.ffmpeg_simple_percent_parser(stdout, self.ffmpeg_total_frame)
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
            self.start_process(self.mantra_cmd)

    def process_finished(self):
        """



        Returns:

        """
        self.message("Process finished.")
        # self.btn_interrupt.setText("Interrupt")
        self.p = None
        self.is_interrupted = False
        self.check = True
        self.start_process(self.ff_cmd)

    def mantra_simple_percent_parser(self, output, total):
        """



        Args:
            output:
            total:

        Returns:

        """
        progress_re = re.compile('_(\d+)\.jpg')
        m = progress_re.search(output)
        print("mantra search :", m)
        if m:
            pc_complete = m.group(1)
            if pc_complete:
                pc = int(int(pc_complete) / total * 100)
                return pc

    def ffmpeg_simple_percent_parser(self, output, total):
        """Progress bar에 넣을 정보를 백분율로 계산한다. \n
        컨버팅이 끝난 frame은 Text Widget에 표시되고, 정규표현식을 사용하여 Text Widget에서 해당 frame을 파악한다. \n
        tree 함수를 사용하여 구한 전체 frame을 분모로 설정하고 컨버팅이 끝난 frame을 분자로 설정하여 백분율을 계싼한다. \n
        Text Widget에 성공적으로 컨버팅이 끝난 정보가 출력될 때, 100 %를 출력해준다.

        Args:
            output (str): Text in Text Widget
            total (int): Total frame

        Returns: pc(progress percent)

        """
        progress_re = re.compile("frame=   (\d+)")
        m = progress_re.search(output)
        print("ffmpeg search :", m)
        if m:
            pc_complete = m.group(1)
            if pc_complete:
                pc = int(int(pc_complete) / total * 100)
                return pc

        progress_re2 = re.compile("(\d+) frames successfully")
        m2 = progress_re2.search(output)
        if m2:
            pc_complete = m2.group(1)
            if pc_complete:
                print(pc_complete, total)
                pc = int(int(pc_complete) / total * 100)
                return pc  # 백분율을 통해 process bar에 보여질 값

    def handle_interrupt(self):
        self.btn_interrupt.setCheckable(True)
        if self.btn_interrupt is True:
            self.btn_interrupt = QtWidgets.QPushButton("Restart")
            self.btn_interrupt.setCheckable(False)

        self.start_process(self.mantra_cmd)

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
