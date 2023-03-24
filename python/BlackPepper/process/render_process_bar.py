import gazu
import os.path
import re
from PySide2 import QtWidgets, QtCore
from BlackPepper.pepper import Houpub
from PySide2.QtCore import QTimer, QCoreApplication


class RenderMainWindow(QtWidgets.QMainWindow):
    """
    Houdini Mantra를 활용하여 sequence file로 render하고 FFmpeg으로 Sequence file을 mov로 컨버팅하는 UI이다. \n
    터미널에 명령하고 출력되는 정보를 Text Widget에 보여준다. 정규표현을 활용하여 터미널에 출력되는 정보에서 컨버팅 중인 프레임을 파악하고 \n
    전체 프레임과 비교하여 Progress Widget으로 진행사항을 유저에게 시각적으로 알려준다.
    """

    def __init__(self, cmd_list, total_frame_list):
        """

        Args:
            cmd_list:
            total_frame_list:
        """
        super().__init__()
        self.pepper = Houpub()
        self.process = None
        self.is_interrupted = False
        self.mantra_search = None
        self.ffmpeg_search = None
        self.check_fin = 0
        self.cmd_list = cmd_list
        self.total_frame_list = total_frame_list


        progress_default_style = """
        QProgressBar{
            border: 2px solid grey;
            border-radius: 5px;
            text-align: center;
            font: 10pt\"Courier New\";
            color: rgb(225, 225, 225)
        }
        
        QProgressBar::chunk {
            background-color: qlineargradient(spread:pad, x1:0, y1:0.511364, 
            x2:1, y2:0.523, stop:0 rgba(153, 255, 153, 255), stop:1 rgba(000, 102, 000, 255));
        }
        """

        self.progress_completed_style = """
        QProgressBar{
            border: 2px solid grey;
            border-radius: 5px;
            text-align: center;
            font: 10pt\"Courier New\";
            color: rgb(225, 225, 225)
        }
        
        QProgressBar::chunk {
            background-color: qlineargradient(spread:pad, x1:0, y1:0.511364, 
            x2:1, y2:0.523, stop:0 rgba(153, 204, 255, 255), stop:1 rgba(000, 051, 153, 255));
        }        
        """

        background_default_style = """
        QWidget{
            background-color: rgb(45, 45, 45);
            selection-background-color: rgb(45, 180, 198);
            font: 10pt\"Courier New\";
            color: rgb(180, 180, 180)
        }
        """

        self.mantra_check = re.compile('^python')
        self.ffmpeg_check = re.compile('^ffmpeg')
        self.ffmpeg_list = None
        self.progress = QtWidgets.QProgressBar()
        self.progress.setStyleSheet(progress_default_style)

        self.progress.setRange(0, 100)

        self.text = QtWidgets.QPlainTextEdit()
        self.text.setReadOnly(True)
        self.btn_interrupt = QtWidgets.QPushButton("Exit")
        self.btn_interrupt.clicked.connect(self.handle_interrupt)

        box_layout = QtWidgets.QVBoxLayout()
        box_layout.addWidget(self.progress)
        box_layout.addWidget(self.text)
        box_layout.addWidget(self.btn_interrupt)

        main_widget = QtWidgets.QWidget()
        main_widget.setStyleSheet(background_default_style)
        main_widget.setLayout(box_layout)
        self.setWindowTitle('Black Pepper Process')
        self.setCentralWidget(main_widget)

        if len(self.cmd_list) == 0:
            return
        self.cmd = self.cmd_list.pop(0)
        self.total_frame = self.total_frame_list.pop(0)
        self.start_process()

    def message(self, text):
        """Text Widget에 메시지를 출력해준다.

        Args:
            text(str): text
        """
        self.text.appendPlainText(text)

    def start_process(self):
        """Qprocess를 활용하여 터미널에 명령을 내려주고 터미널 신호에 따라 출력하는 내용을 달리한다. \n
        진행 중, 오류, 변동, 마무리 단계마다 Text Widget에 상태를 Handling 한다.
        """
        self.mantra_search = self.mantra_check.search(self.cmd)
        self.ffmpeg_search = self.ffmpeg_check.search(self.cmd)

        if not self.process:
            self.process = QtCore.QProcess()

        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.stateChanged.connect(self.handle_state)
        self.process.finished.connect(self.process_finished)
        self.process.start(self.cmd)

    def handle_stderr(self):
        """QProcess Error정보를 받아온다. 바이트 신호를 번역하고 백분율 계산 함수를 실행시키고 컴퓨터가 보낸 정보를 Text에 출력한다.
        """
        if not self.process:
            return
        data = self.process.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        if self.ffmpeg_search:
            progress = self.ffmpeg_simple_percent_parser(stderr, self.total_frame)
        if self.mantra_search:
            progress = self.mantra_simple_percent_parser(stderr, self.total_frame)
        if progress:
            self.progress.setValue(progress)
        self.message(stderr)

    def handle_stdout(self):
        """QProcess Output정보를 받아온다. 바이트 신호를 번역한 정보를 Text에 출력한다.
        """
        if not self.process:
            return
        data = self.process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        if self.ffmpeg_search:
            progress = self.ffmpeg_simple_percent_parser(stdout, self.total_frame)
        if self.mantra_search:
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
        self.message(f'finished : {self.cmd}, {self.is_interrupted}')

        self.process.waitForFinished()

        if self.is_interrupted:
            return

        self.check_fin += 1
        if self.check_fin == 1:
            if self.ffmpeg_search:
                self.ffmpeg_list = self.cmd.split()
                path = self.ffmpeg_list[4][:-8] + '0001.jpg'
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
                self.pepper.publish_working_file('FX')
                self.pepper.publish_output_file('FX', 'jpg_sequence', 'jpg publish')
                self.pepper.publish_output_file('FX', 'movie_file', 'mov publish')
                self.pepper.publish_output_file('FX', 'EXR', 'exr publish')
                thumbnail = self.pepper.publish_preview('FX', 'Ready To Start', 'test', path)
                gazu.task.set_main_preview(thumbnail)

        if len(self.cmd_list) > 0:
            self.cmd = self.cmd_list.pop(0)
            self.total_frame = self.total_frame_list.pop(0)
            self.check_fin = 0
            self.start_process()
        else:
            self.cmd = None
            self.message("Process finished.")
            self.progress.setStyleSheet(self.progress_completed_style)
            return

    @staticmethod
    def mantra_simple_percent_parser(output, total):
        """Houdini Mantra가 실행될 때, Progress bar에 넣을 값을 구하는 메소드, 백분율로 계산한다. \n
        컨버팅이 끝난 frame은 Text Widget에 표시되고, 정규표현식을 사용하여 Text Widget에서 해당 frame을 파악한다. \n
        Alembic file Camera에서 가져온 frame range Out count를 분모로 하고 정규표현으로 찾은 현재 frame을 분자로 하여 계산한다.\n

        Args:
            output (str): Text in Text Widget
            total (int): Total frame

        Returns:
            pc(progress percent)
        """
        progress_re = re.compile('_(\d+)\.jpg')
        frame_search = progress_re.search(output)
        if frame_search:
            frame_group = frame_search.group(1)
            if frame_group:
                percentage = int(int(frame_group) / total * 100)
                return percentage

    def handle_interrupt(self):
        """interrupt button 클릭 시, 실행되는 메소드다. 진행 중인 Process를 중단시키고 Restart button으로 변경한다. \n
        변경 된 button을 다시 클릭할 경우, Process를 처음부터 다시 실행한다.
        """

        if not self.is_interrupted:
            self.is_interrupted = True
            if self.process is not None and self.process.state() == QtCore.QProcess.Running:
                self.process.kill()
                self.process = None
                QCoreApplication.processEvents()
                QTimer.singleShot(0, self.close)

    @staticmethod
    def ffmpeg_simple_percent_parser(output, total):
        """FFmpeg이 실행될 때, Progress bar에 넣을 값을 구하는 메소드, 백분율로 계산한다. \n
        컨버팅이 끝난 frame은 Text Widget에 표시되고, 정규표현식을 사용하여 Text Widget에서 해당 frame을 파악한다. \n
        Alembic file Camera에서 가져온 frame range Out count를 분모로 하고 정규표현으로 찾은 현재 frame을 분자로 하여 계산한다.\n
        Text Widget에 성공적으로 컨버팅이 끝난 정보가 출력될 때, 100 %를 출력해준다.

        Args:
            output (str): Text in Text Widget
            total (int): Total frame

        Returns:
            pc(progress percent)
        """
        progress_re = re.compile("frame=   (\d+)")
        frame_search = progress_re.search(output)
        if frame_search:
            frame_group = frame_search.group(1)
            if frame_group:
                percentage = int(int(frame_group) / total * 100)
                return percentage

        progress_re2 = re.compile("(\d+) frames successfully")
        fin_search = progress_re2.search(output)
        if fin_search:
            frame_group = fin_search.group(1)
            if frame_group:
                percentage = int(int(frame_group) / total * 100)
                return percentage  # 백분율을 통해 process bar에 보여질 값

    def closeEvent(self, event):
        """Process UI를 종료시키는 Event가 발생할 경우, 진행 중인 QProcess를 중단시킨다.
        """
        if self.process is not None and self.process.state() == QtCore.QProcess.Running:
            self.process.terminate()
        super().closeEvent(event)