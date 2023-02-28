import sys
import re
from PySide2 import QtWidgets, QtCore

cmd = '/mnt/pipeline/app/ffmpeg-5.1.1-i686-static/ffmpeg -framerate 24 -i /mnt/project/test/dino/dino.%d.png -c:v libx264 -pix_fmt yuv420p -y -loglevel debug /home/rapa/aaa.mp4'


def simple_percent_parser(output, total):

    progress_re = re.compile("frame= (\d+)")

    m = progress_re.search(output)
    if m:
        pc_complete = m.group(1)
        if pc_complete:
            pc = int(int(pc_complete) / total * 100)
            return pc


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.p = None

        self.btn = QtWidgets.QPushButton("Execute")
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
        if self.p is None:
            self.message("Executing process")
            self.p = QtCore.QProcess()
            self.p.readyReadStandardOutput.connect(self.handle_stdout)
            self.p.readyReadStandardError.connect(self.handle_stderr)
            self.p.stateChanged.connect(self.handle_state)
            self.p.finished.connect(self.process_finished)
            self.p.start(cmd)

    def handle_stderr(self):
        data = self.p.readAllStandardError()
        stderr = bytes(data).decode("utf8")

        progress = simple_percent_parser(stderr, 127)
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
