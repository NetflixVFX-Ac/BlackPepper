import re
from PySide2 import QtWidgets, QtCore
import os
import glob
import hou
import _alembic_hom_extensions as abc


class RenderMainWindow(QtWidgets.QMainWindow):
    """
    FFmpeg으로 Sequence file을 mov로 컨버팅하는 UI이다. 터미널에 명령하고 출력되는 정보를 Text Widget에 보여준다.
    정규표현을 활용하여 터미널에 출력되는 정보에서 컨버팅 중인 프레임을 파악하고 전체 프레임과 비교하여 Progress Widget으로
    진행사항을 유저에게 시각적으로 알려준다.
    """
    def __init__(self, next_fx_path , jpg_output_path, mov_output_path, abc_path, cam_node):
        """Sequence file이 있는 경로와 mov파일이 저장될 경로, fps를 지정한다. 해당 인자들은 터미널에 명령내릴 command에 입력된다.


        Args:
            jpg_output_path (str): Sequence file path
            mov_output_path (str): output file path
        """
        super().__init__()
        self.p = None
        self.p2 = None
        self.is_interrupted = False
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
        print("mantra cmd :", self.mantra_cmd)
        self.mantra_total_frame = self.abc_range[1]*hou.fps()
        print("mantra total frame :", self.mantra_total_frame)

###########################################################################################

        self.output_dir = None
        self.seq_dir = None
        self.sequence_path = jpg_output_path[:-17] + jpg_output_path[-4:] + '_%04d.jpg'
        self.filecnt = 0

############################################################################################

        self.output_dir = os.path.dirname(mov_output_path)
        self.seq_dir = os.path.dirname(jpg_output_path)
        print("seq_dir :", self.seq_dir)
        self.sequence_path = jpg_output_path[:-17] + jpg_output_path[-4:] + '_%04d.jpg'
        self.filecnt = 0
        self.ffmpeg_total_frame = self.ffmpeg_tree(self.seq_dir)
        print("ffmpeg_total_frame :", self.total_frame)

        self.ffmpeg_command = [
            "ffmpeg",
            "-framerate 24",  # 초당프레임
            "-i", self.sequence_path,  # 입력할 파일 이름
            "-q 0",  # 출력품질 정함(숫자가 높을 수록 품질이 떨어짐)
            "-threads 8",  # 속도향상을 위해 멀티쓰레드를 지정
            "-c:v", "prores_ks",  # 코덱
            "-pix_fmt", "yuv420p",  # 포맷양식
            "-y",  # 출력파일을 쓸 때 같은 이름의 파일이 있어도 확인없이 덮어씀
            "-loglevel", "debug",  # 인코딩 과정로그를 보여줌
            mov_output_path + '.mov'
        ]
        self.ffmpeg_cmd = (' '.join(str(s) for s in self.ffmpeg_command))
        print("ffmpeg cmd : ", self.ffmpeg_cmd)

        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir)

############################################################################################

        self.progress = QtWidgets.QProgressBar()
        self.progress.setRange(0, 100)

        self.text = QtWidgets.QPlainTextEdit()
        self.text.setReadOnly(True)
        self.btn_interrupt = QtWidgets.QPushButton("Interrupt")
        self.btn_interrupt.clicked.connect(self.handle_interrupt)

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
        self.start_process(self.mantra_cmd)

    def message(self, s):
        """  Text Widget에 메시지를 출력한다

        Args:
            s(str): text
        """
        self.text.appendPlainText(s)

    def start_process(self, cmd):
        """ Qprocess를 활용하여 터미널에 명령을 내려주고 터미널 신호에 따라 출력하는 내용을 달리한다. \n
        진행 중, 오류, 변동, 마무리 단계마다 Text Widget에 상태를 Handling 한다.

        """
        self.p = QtCore.QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
        self.p.readyReadStandardOutput.connect(self.mantra_handle_stdout)
        self.p.readyReadStandardError.connect(self.mantra_handle_stderr)
        self.p.stateChanged.connect(self.mantra_handle_state)
        self.p.finished.connect(self.mantra_process_finished)  # Clean up once complete.
        self.p.start(cmd)

    def mantra_handle_stderr(self):
        """ QProcess Error정보를 받아온다. 바이트 신호를 번역하고 백분율 계산 함수를 실행시키고 컴퓨터가 보낸 정보를 Text에 출력한다.

        """
        data = self.p.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        progress = self.mantra_simple_percent_parser(stderr, self.mantra_total_frame)
        if progress:
            self.progress.setValue(progress)
        self.message(stderr)

    def mantra_handle_stdout(self):
        """ QProcess Output정보를 받아온다. 바이트 신호를 번역한 정보를 Text에 출력한다.

        """
        data = self.p.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        self.message(stdout)

    def mantra_handle_state(self, state):
        """Qprocess state에 변동이 있을 경우, 해당 변화 정보를 출력한다.

        """
        states = {
            QtCore.QProcess.NotRunning: 'Not running',
            QtCore.QProcess.Starting: 'Starting',
            QtCore.QProcess.Running: 'Running',
        }
        state_name = states[state]
        self.message(f"State changed: {state_name}")

    def mantra_process_finished(self):
        """Qprocess finish가 날 경우, 바이트 신호를 번역한 정보를 Text에 출력한다.

        """
        self.message("Process finished.")
        self.p = None
        self.close()

    def ffmpeg_tree(self, path):
        """ Sequence file이 있는 경로 내 파일의 갯수를 파악하여 Total frame을 계산한다.

        Args:
            path (str): Sequence file path

        Returns: filecnt

        """
        for x in sorted(glob.glob(path + "/*")):
            print("tree x :", x)
            if os.path.isfile(x):
                self.filecnt += 1
            else:
                print("unknown:", x)
        return int(self.filecnt)

    def mantra_simple_percent_parser(self, output, total):
        """



        Args:
            output:
            total:

        Returns:

        """
        progress_re = re.compile('_(\d+)\.jpg')
        m = progress_re.search(output)
        print("m :", m)
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
        print("m search :", m)
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
