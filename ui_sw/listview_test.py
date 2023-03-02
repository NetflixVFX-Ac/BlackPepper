import sys
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *


import Model

class test(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()


    def setup_ui(self):

        test = ['a', 'b', 'pepper']
        listview = QListView(self)
        model = QStandardItemModel()
        for f in test:
            model.appendRow(QStandardItem(f))
        listview.setModel(model)
        listview.move(50,50)
        listview.resize(500,300)

        self.resize(600,400)
        self.show()


if __name__ =='__main__':
    app = QApplication(sys.argv)
    tt = test()

    sys.exit(app.exec_())
