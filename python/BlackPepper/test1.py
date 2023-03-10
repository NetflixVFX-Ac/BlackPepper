from PySide2 import QtWidgets, QtCore


class ASDFASDFASDF(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.text = QtWidgets.QPlainTextEdit()
        print("CCCC")

def main():
    app = QtWidgets.QApplication()
    m = ASDFASDFASDF()
    m.show()
    app.exec_()

if __name__ == "__main__":
    main()

