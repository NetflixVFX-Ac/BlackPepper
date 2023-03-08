import re
from PySide2 import QtWidgets, QtCore
import os
import glob


class FFmpegMainWindow(QtWidgets.QMainWindow):
    """



    """
    def __init__(self, seq_path, output_path, framerate):
        """



        Args:
            seq_path:
            output_path:
            framerate:
        """
        super().__init__()
        self.p = None
        self.output_dir = os.path.dirname(output_path)
        self.seq_dir = os.path.dirname(seq_path)
        self.sequence_path = seq_path[:-8] + '%04d.jpg'

        self.filecnt = 0
        self.total_frame = self.tree(self.seq_dir)
        print(self.total_frame)

        self.command = [
            'ffmpeg',
            "-framerate", str(framerate),  # 초당프레임
            "-i", self.sequence_path,  # 입력할 파일 이름
            "-q 0",  # 출력품질 정함(숫자가 높을 수록 품질이 떨어짐)
            "-threads 8",  # 속도향상을 위해 멀티쓰레드를 지정
            "-c:v", "libx264",  # 코덱
            "-pix_fmt", "yuv420p",  # 포맷양식
            "-y",  # 출력파일을 쓸 때 같은 이름의 파일이 있어도 확인없이 덮어씀
            "-loglevel", "debug",  # 인코딩 과정로그를 보여줌
            output_path
        ]
        self.cmd = (' '.join(str(s) for s in self.command))
        print("cmd : ", self.cmd)

        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir)

        self.text = QtWidgets.QPlainTextEdit()
        self.text.setReadOnly(True)

        self.progress = QtWidgets.QProgressBar()
        self.progress.setRange(0, 100)

        l = QtWidgets.QVBoxLayout()
        l.addWidget(self.progress)
        l.addWidget(self.text)

        w = QtWidgets.QWidget()
        w.setLayout(l)

        self.setCentralWidget(w)
        self.start_process()

    def message(self, s):
        """



        Args:
            s:

        Returns:

        """
        self.text.appendPlainText(s)

    def start_process(self):
        """



        Returns:

        """
        self.p = QtCore.QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
        self.p.readyReadStandardOutput.connect(self.handle_stdout)
        self.p.readyReadStandardError.connect(self.handle_stderr)
        self.p.stateChanged.connect(self.handle_state)
        self.p.finished.connect(self.process_finished)  # Clean up once complete.
        self.p.start(self.cmd)

    def handle_stderr(self):
        """



        Returns:

        """
        data = self.p.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        progress = self.simple_percent_parser(stderr, self.total_frame)
        if progress:
            self.progress.setValue(progress)
        self.message(stderr)

    def handle_stdout(self):
        """



        Returns:

        """
        data = self.p.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
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

    def process_finished(self):
        """



        Returns:

        """
        self.message("Process finished.")
        self.p = None
        self.close()

    def tree(self, path):  # 백분율로 나누기 위한 분모를 구하는 함수(분모의 수는 디렉토리 안의 시퀀스 수와 같다.)
        """




        Args:
            path:

        Returns:

        """
        for x in sorted(glob.glob(path + "/*")):
            print("tree x :", x)
            if os.path.isfile(x):
                self.filecnt += 1
            else:
                print("unknown:", x)
        return int(self.filecnt)

    def simple_percent_parser(self, output, total):# 프로세스바에 시각화 해줄 수치를 만들어 내는 백분율계산기
        """




        Args:
            output:
            total:

        Returns:

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
                return pc #백분율을 통해 process bar에 보여질 값
