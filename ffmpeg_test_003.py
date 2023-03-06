import sys
import re
from PySide2 import QtWidgets, QtCore
import os
import glob


framerate = 24
input_pattern = "/home/rapa/dino/dino.%d.png"#ffmpeg을 사용해 mov영상으로 만들 시퀀스 경로
output_file = "/home/rapa/Rnd_output_04.mp4"#ffmpeg을 사용 후 mov영상으로 나온 결과가 저장될 경로
ffmpeg_path = "/mnt/pipeline/app/ffmpeg-5.1.1-i686-static/ffmpeg" #ffmpeg모듈이 있는 경로(로컬내에 ffmpeg이 있다면 앞의 경로를 안써도 된다.)

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
    global filecnt #전역함수로 filecnt는 코드내 어느 곳에서나 사용가능, 함수의 아웃풋 값이 담긴다.
    for x in sorted(glob.glob(path + "/*")):#glob.glob은 제시한 확장자에 맞는 파일명을 리스트 형식으로 반환 -> path = /home/rapa/dino + /* 의 경로내의 모든 파일을 정리해서 차례대로 반환
        print('ssssss',x)                   #sorted는 이터너블한 데이터를 정렬된 새로운 데이터로 만들어서 반환
        if os.path.isfile(x):#os.path.isfile은 지정된 경로내에 파일이 있다면 True를 반환
            filecnt += 1 #한줄 위의 코드가 참이라면 재귀함수지정 변수인 filecnt에 1을 더함 -> for문은 순차적으로 읽으니 x로 지정된 이름이 존재해 참일 때마다 +1이 축적됨
        else:
            print("unknown:", x)#만약 for문이 순차적으로 읽는 도중 경로내에 파일이 없다면 "unknown"을 프린트
    return int(filecnt)#리턴 값으로 시퀀스내의 시퀀스 수를 반환 -> 반환된 값은 백분율 식의 분모로 활용된다.


filecnt = 0 #tree함수를 사용해 시퀀스 수가 들어올 주머니
path_folder = os.path.dirname(input_pattern) #tree함수를 사용해 시퀀스 수가 들어올 주머니
total_frame = tree(path_folder)
print(total_frame)


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
