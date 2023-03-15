import os.path
import re

import gazu.task
from PySide2 import QtWidgets, QtCore
from BlackPepper.pepper import Houpub

class RenderMainWindow(QtWidgets.QMainWindow):
    """
    FFmpeg으로 Sequence file을 mov로 컨버팅하는 UI이다. 터미널에 명령하고 출력되는 정보를 Text Widget에 보여준다.
    정규표현을 활용하여 터미널에 출력되는 정보에서 컨버팅 중인 프레임을 파악하고 전체 프레임과 비교하여 Progress Widget으로
    진행사항을 유저에게 시각적으로 알려준다.
    """
    def __init__(self, cmd_list, total_frame_list):
        """Sequence file이 있는 경로와 mov파일이 저장될 경로, fps를 지정한다. 해당 인자들은 터미널에 명령내릴 command에 입력된다.


        Args:
            jpg_output_path (str): Sequence file path
            mov_output_path (str): output file path
        """
        super().__init__()
        self.pepper = Houpub()
        self.p = None
        self.is_interrupted = False
        self.mc = None
        self.fc = None
        self.check_fin = 0

########################################################


        self.cmd_list = cmd_list
        self.total_frame_list = total_frame_list


########################################################
        DEFAULT_STYLE = """
        QProgressBar{
            border: 2px solid grey;
            border-radius: 5px;
            text-align: center;
            font: 10pt\"Courier New\";
            color: rgb(225, 225, 225)
        }
        """

        self.mantra_check = re.compile('^python')
        self.ffmpeg_check = re.compile('^ffmpeg')
        self.ffmpeg_list = None
        self.progress = QtWidgets.QProgressBar()
        self.progress.setStyleSheet(DEFAULT_STYLE)
        self.progress.setRange(0, 100)

        self.text = QtWidgets.QPlainTextEdit()
        self.text.setReadOnly(True)
        self.btn_interrupt = QtWidgets.QPushButton("Interrupt")
        # self.btn_interrupt.clicked.connect(self.handle_interrupt)

        l = QtWidgets.QVBoxLayout()
        l.addWidget(self.progress)
        l.addWidget(self.text)
        l.addWidget(self.btn_interrupt)

        w = QtWidgets.QWidget()
        w.setStyleSheet(u"background-color: rgb(45, 45, 45);\n"
                        "selection-background-color: rgb(45, 180, 198);\n"
                        "font: 10pt\"Courier New\";\n"
                        "color: rgb(180, 180, 180);\n")
        w.setLayout(l)
        self.setWindowTitle('Black Pepper Progress')
        self.setCentralWidget(w)

        if len(self.cmd_list) == 0:
            return
        self.cmd = self.cmd_list.pop(0)
        self.total_frame = self.total_frame_list.pop(0)

        self.start_process(self.cmd)

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

        print("start!!!!!!!")
        print(cmd)
        print(self.total_frame)
        self.mc = self.mantra_check.search(cmd)
        self.fc = self.ffmpeg_check.search(cmd)


        if not self.p:
            self.p = QtCore.QProcess()

        self.p.waitForFinished()

        self.p.readyReadStandardOutput.connect(self.handle_stdout)
        self.p.readyReadStandardError.connect(self.handle_stderr)
        self.p.stateChanged.connect(self.handle_state)
        self.p.finished.connect(self.process_finished)  # Clean up once complete.
        # print('check check')
        self.p.start(cmd)

    def handle_stderr(self):
        """ QProcess Error정보를 받아온다. 바이트 신호를 번역하고 백분율 계산 함수를 실행시키고 컴퓨터가 보낸 정보를 Text에 출력한다.

        """
        data = self.p.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        if self.fc:
            progress = self.ffmpeg_simple_percent_parser(stderr, self.total_frame)
        if self.mc:
            progress = self.mantra_simple_percent_parser(stderr, self.total_frame)
        if progress:
            self.progress.setValue(progress)
        self.message(stderr)

    def handle_stdout(self):
        """ QProcess Output정보를 받아온다. 바이트 신호를 번역한 정보를 Text에 출력한다.

        """
        data = self.p.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        if self.fc:
            progress = self.ffmpeg_simple_percent_parser(stdout, self.total_frame)
        if self.mc:
            progress = self.mantra_simple_percent_parser(stdout, self.total_frame)
        if progress:
            self.progress.setValue(progress)

        self.message(stdout)

    def handle_state(self, state):
        """Qprocess state에 변동이 있을 경우, 해당 변화 정보를 출력한다.

        """
        states = {
            QtCore.QProcess.NotRunning: 'Not running',
            QtCore.QProcess.Starting: 'Starting',
            QtCore.QProcess.Running: 'Running',
        }
        state_name = states[state]
        self.message(f"State changed: {state_name}")

    def process_finished(self):
        """Qprocess finish가 날 경우, 바이트 신호를 번역한 정보를 Text에 출력한다.

        """
        print("fin")
        self.check_fin += 1
        print("check_fin :", self.check_fin)
        self.p.waitForFinished()
        if self.check_fin == 1:
            if self.fc:
                self.ffmpeg_list = self.cmd.split()
                path = self.ffmpeg_list[4][:-8]+'0001.jpg'
                path_basename = os.path.basename(path)
                path_re = re.compile('^(\w+)_(\w+)_(\d+)_')
                path_search = path_re.search(path_basename)
                project = path_search.group(1)
                sequence = path_search.group(2)
                shot = path_search.group(3)
                self.pepper.project = project.upper()
                self.pepper.sequence = sequence.upper()
                self.pepper.shot = shot
                self.pepper.entity = 'shot'
                self.pepper.publish_output_file('FX', 'jpg_sequence', 'jpg publish')
                self.pepper.publish_output_file('FX', 'movie_file', 'mov publish')
                thumbnail = self.pepper.publish_preview('FX', 'Ready To Start', 'test', path)
                gazu.task.set_main_preview(thumbnail)

        if len(self.cmd_list) > 0:
            self.cmd = self.cmd_list.pop(0)
            self.total_frame = self.total_frame_list.pop(0)
            self.check_fin = 0
            self.start_process(self.cmd)
        else:
            self.message("Process finished.")
            return


    def mantra_simple_percent_parser(self, output, total):
        """



        Args:
            output:
            total:

        Returns:

        """
        print("mantra total :", total)
        progress_re = re.compile('_(\d+)\.jpg')
        m = progress_re.search(output)
        if m:
            print("m :", m)
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
        print("ffmpeg total :", total)

        progress_re = re.compile("frame=   (\d+)")
        m = progress_re.search(output)
        if m:
            print("m search :", m)
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

    def closeEvent(self, event):
        if self.p is not None and self.p.state() == QtCore.QProcess.Running:
            self.p.terminate()
        super().closeEvent(event)
