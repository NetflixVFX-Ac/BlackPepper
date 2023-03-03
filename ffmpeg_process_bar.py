import sys
import re
from PySide2 import QtWidgets, QtCore
import os
import glob


framerate = 24
input_pattern = "/home/rapa/dino/dino.%d.png"
output_file = "/home/rapa/Rnd_output_04.mp4"
ffmpeg_path = "/mnt/pipeline/app/ffmpeg-5.1.1-i686-static/ffmpeg"

command = [
    ffmpeg_path,
    "-framerate", str(framerate),  # 초당프레임
    "-i", input_pattern,  # 입력할 파일 이름
    "-q 0",  # 출력품질 정함(숫자가 높을 수록 품질이 떨어짐)
    "-threads 8",  # 속도향상을 위해 멀티쓰레드를 지정
    "-c:v", "libx264",  # 코덱
    "-pix_fmt", "yuv420p",  # 포맷양식
    "-y",  # 출력파일을 쓸 때 같은 이름의 파일이 있어도 확인없이 덮어씀
    "-loglevel", "debug",  # 인코딩 과정로그를 보여줌
    output_file
]

cmd = (' '.join(str(s) for s in command))
print(cmd)# ffmpeg을 실행하기 위한 명령문을 뽑아내줌

def tree(path):# 백분율로 나누기 위한 분모를 구하는 함수(분모의 수는 디렉토리 안의 시퀀스 수와 같다.)
    global filecnt
    for x in sorted(glob.glob(path + "/*")):
        if os.path.isfile(x):
            filecnt += 1
        else:
            print("unknown:", x)
    return int(filecnt)


filecnt = 0
path_folder = os.path.dirname(input_pattern)
total_frame = tree(path_folder)


def simple_percent_parser(output, total):# 프로세스바에 시각화 해줄 수치를 만들어 내는 백분율계산기
    progress_re = re.compile("frame= (\d+)")
    m = progress_re.search(output)
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


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.p = None

        self.btn = QtWidgets.QPushButton("Execute")#GUI인터페이스를 만들어주는 부분
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
            self.message("Executing process")
            self.p = QtCore.QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
            self.p.readyReadStandardOutput.connect(self.handle_stdout)
            self.p.readyReadStandardError.connect(self.handle_stderr)
            self.p.stateChanged.connect(self.handle_state)
            self.p.finished.connect(self.process_finished)  # Clean up once complete.
            self.p.start(cmd)

    def handle_stderr(self):
        data = self.p.readAllStandardError()
        stderr = bytes(data).decode("utf8")

        progress = simple_percent_parser(stderr, total_frame)
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


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec_()


if __name__ == '__main__':
    main()
