from ffmpeg_process_bar import MainWindow
from PySide2 import QtWidgets
import os
import hou
import _alembic_hom_extensions as abc


seq_dir = '/mnt/project/hook/pepper/shots/sq01/0020/fx/output/movie_file/v001'
command = [
    'echo',
    'hi'
        ]
cmd = (' '.join(str(s) for s in command))
print(cmd)
print("seq_dir :", seq_dir)
if not os.path.isdir(seq_dir):
    os.makedirs(seq_dir)
app = QtWidgets.QApplication()
w = MainWindow(cmd, seq_dir)
w.show()
app.exec_()