import sys
import re
from PySide2 import QtWidgets, QtCore
import os
import glob

framerate = 24
input_pattern = "/home/rapa/dino/dino.%d.png"  # ffmpeg을 사용해 mov영상으로 만들 시퀀스 경로
output_file = "/home/rapa/Rnd_output_04.mp4"  # ffmpeg을 사용 후 mov영상으로 나온 결과가 저장될 경로
ffmpeg_path = "/mnt/pipeline/app/ffmpeg-5.1.1-i686-static/ffmpeg"  # ffmpeg모듈이 있는 경로(로컬내에 ffmpeg이 있다면 앞의 경로를 안써도 된다.)

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

cmd = (' '.join(str(s) for s in command))  # 'join()'메서드를 이용하여 문자열 리스트를 결합 command 리스트를 for문으로 읽어
# 모든 요소를 하나의 문자열로 연결, 문자열의 각 요소는 공백 문자(' ')으로 구분
print(cmd, "hihihi")  # ffmpeg을 실행하기 위한 명령문을 뽑아내줌


def tree(path):  # 백분율로 나누기 위한 분모를 구하는 함수(분모의 수는 디렉토리 안의 시퀀스 수와 같다.)
    global filecnt  # 전역함수로 filecnt는 코드내 어느 곳에서나 사용가능, 함수의 아웃풋 값이 담긴다.
    for x in sorted(glob.glob(path + "/*")):  # glob.glob은 제시한 확장자에 맞는 파일명을 리스트 형식으로 반환
        # -> path = /home/rapa/dino + /* 의 경로내의 모든 파일을 정리해서 차례대로 반환
        print('ssssss', x)  # sorted는 이터너블한 데이터를 정렬된 새로운 데이터로 만들어서 반환
        if os.path.isfile(x):  # os.path.isfile은 지정된 경로내에 파일이 있다면 True를 반환
            filecnt += 1  # 한줄 위의 코드가 참이라면 재귀함수지정 변수인 filecnt에 1을 더함 -> for문은 순차적으로 읽으니 x로 지정된 이름이 존재해 참일 때마다 +1이 축적됨
        else:
            print("unknown:", x)  # 만약 for문이 순차적으로 읽는 도중 경로내에 파일이 없다면 "unknown"을 프린트
    return int(filecnt)  # 리턴 값으로 시퀀스내의 시퀀스 수를 반환 -> 반환된 값은 백분율 식의 분모로 활용된다.


filecnt = 0  # tree함수를 사용해 시퀀스 수가 들어올 주머니
path_folder = os.path.dirname(input_pattern)  # tree함수를 사용해 시퀀스 수가 들어올 주머니
total_frame = tree(path_folder)  # 시퀀스가 들어있는 path가 인자값으로 들어온다면 'tree'함수를 실행
print(total_frame)


def simple_percent_parser(output, total):  # 프로세스바에 시각화 해줄 수치를 만들어 내는 백분율계산기
    progress_re = re.compile("frame= (\d+)")  # re.compile은 문자열을 컴파일(형태저장)하여
    # 패턴 객체를 반환(re.compile모듈안에 search(), match(), findall() 등과 같은 다양한 메소드를 지원)
    m = progress_re.search(output)  # 'output'안에 're.compile'로 저장한 문자열이 있다면 're.search'모듈을 사용해 're.compile'로 저장한 문자열을 반환
    print("ssssss", m)
    if m: # m == 존재하거나 True 일때
        pc_complete = m.group(1)  # re.search()로 검색된 패턴에서 첫 번째 괄호 안에 매칭된 문자열을 반환 ->("frame= (\d+)")의 (\d+)
        if pc_complete: # pc_complete == 존재하거나 True 일때
            print("xxxx", pc_complete)
            pc = int(int(pc_complete) / total * 100)  # pc_complete==실시간 frame값 / total==시퀀스 전체숫자값 * 100 ->퍼센테이지
            return pc  # gui인터페이스에 쓰여질 퍼센테이지 값

    progress_re2 = re.compile("(\d+) frames successfully")  # re.compile은 문자열을 컴파일(형태저장)
    m2 = progress_re2.search(
        output)  # 'output'안에 're.compile'로 저장한 문자열이 있다면 're.search'모듈을 사용해 're.compile'로 저장한 문자열을 반환
    if m2: # m2 == 존재하거나 True 일때
        pc_complete = m2.group(1)  # re.search()로 검색된 패턴에서 첫 번째 괄호 안에 매칭된 문자열을 반환 ->("frame= (\d+)")의 (\d+)
        if pc_complete:
            print(pc_complete, total)
            pc = int(int(pc_complete) / total * 100)  # pc_complete==실시간 frame값 / total==시퀀스 전체숫자값 * 100 ->퍼센테이지
            return pc  # 백분율을 통해 process bar에 보여질 값


class MainWindow(QtWidgets.QMainWindow):  # Qt라이브러리를 사용하는 클래스, MainWindow 클래스는
    # QtWidgets.QMainWindow 클래스를 상속하여 작성
    def __init__(self):
        super().__init__()  # mainwindow의 클래스를 모두 가져오겠다. 이 클래스의 역할이 Qmainwindow역할을 하게 만드는 코드.
        # MainWindow 클래스가 QtWidgets.QMainWindow 클래스에서 상속한 모든 기능을 사용
        # QMainWindow를 상속받은 MainWindow클래스는 QMainWindow(부모)의 자식이다. 하지만 super()함수를
        # 사용하여 자식이 부모의 지위를 가지게 한다. == (올바른 부모 클래스의 메서드를 호출할 수 있다.)

        self.p = None

        self.btn = QtWidgets.QPushButton("Execute")  # QtWidgets모듈에서 버튼을 만들어주는 함수를 불러오고 이름을 "execute"적는다.
        self.btn.pressed.connect(self.start_process)  # 위에서 만든 버튼이 눌렀을 때 작동할 함수를 pressed.connect모듈로 연결한다.
        self.text = QtWidgets.QPlainTextEdit()  # 텍스트를 위젯의 두께에 맞게 만들어준다. -> ffmpeg의 인코딩 로그정보가 나오는 부분
        self.text.setReadOnly(True)  # setReadOnly() 메서드를 사용하여 text속성을 읽기 전용으로 설정 -> 프로그램 사용자가
        # 위젯 텍스트를 수정하지 못하게 하기 위함이다. -> ffmpeg의 인코딩 로그정보가 나오는 부분

        self.progress = QtWidgets.QProgressBar()  # 작업 진행 상황을 시각적으로 나타내는 위젯
        self.progress.setRange(0, 100)  # setRange() 메서드를 사용하여 '프로그레스바'의 최소값과 최대값을 지정
        # -버튼 위젯 생성 부분-

        l = QtWidgets.QVBoxLayout()  # 위젯이 수직으로 배치되는 레이아웃 클래스입니다.
        # 이 레이아웃은 부모 위젯의 크기에 따라 자식 위젯을 자동으로 수직으로 배치해줍니다.
        # -레이아웃 생성 부분-
        l.addWidget(self.btn)  # ffmpeg을 실행할 ui상의 버튼 위젯
        l.addWidget(self.progress)  # 작업 진행 상황을 시각적으로 나타내는 위젯
        l.addWidget(self.text)  # ffmpeg의 인코딩 로그정보를 보여주는 위젯
        # -버튼 위젯을 레이아웃에 추가하는 부분-

        w = QtWidgets.QWidget()  # 부모 위젯을 생성 -> GUI상 레이아웃과 레이아웃에 추가될 위젯이 보여질 창
        w.setLayout(l)  # 부모 위젯에 QVBoxLayout 설정 -> l == gui상에 올라갈 위젯 묶음

        self.setCentralWidget(w)  # QMainWindow를 위젯을 중앙에 위치하는 설정하는 역할

    def message(self, s):  # 위젯 로그창에 메세지를 써주는 함수
        self.text.appendPlainText(s)

    def start_process(self):
        if self.p is None:  # 조건이 참일 경우 코드 실행함
            self.message("Executing process")  # gui에서 'execute'버튼을 누를 시"Executing process"가 TextWidget에 뜸
            self.p = QtCore.QProcess()  # start(), write(), readAll(), kill()과 같은 메소드를 제공하며 이러한 메소드를 사용하여 프로세스의 동작을 관리
            self.p.readyReadStandardOutput.connect(self.handle_stdout)
            self.p.readyReadStandardError.connect(self.handle_stderr)
            self.p.stateChanged.connect(self.handle_state)  # 프로세스의 상태가 변경될 때마다 상태를 알려줌
            self.p.finished.connect(self.process_finished)  # 실행이 완료될 때 호출될 함수를 연결, 함수 또는 람다 함수를 매개 변수로 받음
            self.p.start(cmd)  # p.start(cmd)는 QtCore.QProcess 클래스의 메소드, 외부 스크립트를 실행 -> cmd == ffmpeg 실행문

    def handle_stderr(self):
        data = self.p.readAllStandardError()  # QtCore.QProcess()처리 정보를 받아옴
        stderr = bytes(data).decode("utf8")  # 컴퓨터가 보내주는 바이트 신호(이진법 신호)를 사람이 읽을 수 있는 말로 변역하는 코드
        progress = simple_percent_parser(stderr,
                                         total_frame)  # simple_percent_parser -> 프로세스바에 시각화 해줄 수치를 만들어 내는 백분율계산기
        if progress:
            self.progress.setValue(progress)  # self.progress = QtWidgets.QProgressBar()
            # 작업 진행 상황을 시각적으로 나타내는 위젯에 setValue로 연결해 계산기에서 보낸 수치값을 송출

        self.message(stderr)  # edit창에 컴퓨터가 보낸 로그 정보를 적어줌

    def handle_stdout(self):
        data = self.p.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")  # 컴퓨터가 보내주는 바이트 신호(이진법 신호)를 사람이 읽을 수 있는 말로 변역하는 코드
        self.message(stdout)  # edit창에 컴퓨터가 보낸 로그 정보를 적어줌

    def handle_state(self, state):
        states = {
            QtCore.QProcess.NotRunning: 'Not running',
            QtCore.QProcess.Starting: 'Starting',
            QtCore.QProcess.Running: 'Running',
        }
        state_name = states[state] # 딕셔너리를 사용하여 QProcess.ProcessState 값에 대응하는 문자열 값을 가져옴
        self.message(f"State changed: {state_name}")  # 위젯 로그창에 메세지를 써주는 함수

    def process_finished(self):  # 위젯 로그창에 메세지를 써주는 함수를 사용해 "Process finished."를 인코딩 마지막에 써줌
        self.message("Process finished.")  # 위젯 로그창에 메세지를 써주는 함수
        self.p = None


def main():
    app = QtWidgets.QApplication(sys.argv)  # GUI창을 불러오는 함수 -> 창을 가져옴
    w = MainWindow()  # QtWidgets.QMainWindow를 상속받은 클래스(mainwindow)를 가져옴 -> 도면
    w.show()  # 부모 위젯 표시 -> w == QtWidgets.QWidget() -> 도면을 창에 붙임
    app.exec_()  # 이벤트 루프를 시작하고, 이벤트 루프가 종료될 때까지 대기
    # 이벤트 루프는 Qt 어플리케이션에서 발생하는 이벤트(사용자 입력, 타이머, 시그널 등)를 처리 -> 기다리라고 얘기하는 함수 종료하지말라 컴퓨터한테


if __name__ == '__main__':
    main()
