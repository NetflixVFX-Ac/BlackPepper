import re
import os
import json
from PySide2 import QtWidgets, QtCore


class MantraMainWindow(QtWidgets.QMainWindow):
    """
    Houdini Mantra를 활용하여 Template에 Alembic 카메라 값이 추가 된 Hip 파일을 Sequence file(.jpg)로 추출한다.
    터미널에서 mantra_render.py 를 실행하고, 터미널에 출력되는 정보를 Text Widget으로 보여준다.
    정규표현을 활용하여 터미널에 출력되는 정보에서 컨버팅 중인 프레임을 파악하고 전체 프레임과 비교하여 Progress Widget으로
    진행사항을 유저에게 시각적으로 알려준다.
    """

    def __init__(self, next_fx_path, output_path, abc_path, cam_node, total_frame):
        """



        Args:
            next_fx_path:
            output_path:
            abc_path:
            cam_node:
            total_frame:
        """
        super().__init__()
        self.exc_dict = {}
        self.dir_path = ''
        self.user_path = ''

        self.render_dict = None
        self.process_box = None
        self.is_interrupted = False
        self.total_frame = total_frame
        self.command = [
            'python',
            '/home/rapa/git/hook/python/BlackPepper/mantra_render.py',
            next_fx_path,
            output_path,
            abc_path,
            cam_node
        ]
        self.cmd = (' '.join(str(command_string) for command_string in self.command))

        # Create the "Interrupt" Button
        self.progress = QtWidgets.QProgressBar()
        self.progress.setRange(0, 100)
        self.text = QtWidgets.QPlainTextEdit()
        self.text.setReadOnly(True)
        self.btn_interrupt = QtWidgets.QPushButton("Interrupt")
        self.btn_interrupt.clicked.connect(self.handle_interrupt)

        self.box_layout()

        self.start_process()

    def home_json_path(self):
        now_path = os.path.realpath(__file__)
        split_path = now_path.split('/')[:-2]
        self.dir_path = os.path.join('/'.join(split_path), '.config')
        self.user_path = os.path.join(self.dir_path, 'user.json')

    def save_frame_setting(self):
        self.exc_dict['frame'] = []
        self.exc_dict['frame'].append({

        })

    def box_layout(self):
        box = QtWidgets.QVBoxLayout()
        box.addWidget(self.btn_interrupt)
        box.addWidget(self.progress)
        box.addWidget(self.text)

        box_info = QtWidgets.QWidget()
        box_info.setStyleSheet(u"background-color: rgb(45, 45, 45);\n"
                               "selection-background-color: rgb(45, 180, 198);\n"
                               "font: 10pt\"Courier New\";\n"
                               "color: rgb(180, 180, 180);\n")
        box_info.setLayout(box)
        self.setCentralWidget(box_info)

    def message(self, to_user_message):
        """



        Args:
            to_user_message:

        Returns:

        """
        self.text.appendPlainText(to_user_message)

    def start_process(self):
        """



        Returns:

        """
        if self.process_box is None:  # No process running.
            self.message("Executing process")
            self.btn_interrupt.setText("Interrupt")
            self.process_box = QtCore.QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
            self.process_box.readyReadStandardOutput.connect(self.handle_stdout)
            self.process_box.readyReadStandardError.connect(self.handle_stderr)
            self.process_box.stateChanged.connect(self.handle_state)
            self.process_box.finished.connect(self.process_finished)  # Clean up once complete.
            self.process_box.start(self.cmd)

    def handle_stderr(self):
        """



        Returns:

        """
        data = self.process_box.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        progress = self.simple_percent_parser(stderr, self.total_frame)
        if progress:
            self.progress.setValue(progress)

        self.message(stderr)

    def handle_stdout(self):
        """



        Returns:

        """
        data = self.process_box.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        progress = self.simple_percent_parser(stdout, self.total_frame)
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

    def process_finished(self):
        """



        Returns:

        """
        self.message("Process finished.")
        self.btn_interrupt.setText("Restart")
        self.process_box = None

    def simple_percent_parser(self, output, total):
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

    def restart_process(self):
        self.progress.setValue(0)
        self.start_process()
        self.btn_interrupt.setText("Interrupt")

    def handle_interrupt(self):
        if self.process_box is not None:
            self.process_box.kill()
            self.btn_interrupt.setText("Restart")
            self.btn_interrupt.clicked.connect(self.restart_process)
        else:
            self.btn_interrupt.setText("Interrupt")
            self.start_process()