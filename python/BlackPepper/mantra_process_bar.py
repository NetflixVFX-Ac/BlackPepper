import re
from PySide2 import QtWidgets, QtCore
import os
import glob
import shutil
import hou

class MantraMainWindow(QtWidgets.QMainWindow):

    def __init__(self, next_fx_path, output_path, abc_path, cam_node, total_frame):
        super().__init__()
        self.p = None
        self.total_frame = total_frame
        self.command = [
            'python',
            '/home/rapa/git/hook/python/BlackPepper/mantra_render.py',
            next_fx_path,
            output_path,
            abc_path,
            cam_node
        ]

        self.cmd = (' '.join(str(s) for s in self.command))

        self.btn = QtWidgets.QPushButton("MANTRA SEQUENCE RENDERING")
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
            self.p.start(self.cmd)

    def handle_stderr(self):
        data = self.p.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        progress = self.simple_percent_parser(stderr, self.total_frame)
        if progress:
            self.progress.setValue(progress)

        self.message(stderr)

    def handle_stdout(self):
        data = self.p.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        progress = self.simple_percent_parser(stdout, self.total_frame)
        if progress:
            self.progress.setValue(progress)

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
        self.close()

    def simple_percent_parser(self, output, total):
        progress_re = re.compile('_(\d+)\.jpg')
        m = progress_re.search(output)
        print("m :", m)
        if m:
            pc_complete = m.group(1)
            if pc_complete:
                pc = int(int(pc_complete) / total * 100)
                return pc
