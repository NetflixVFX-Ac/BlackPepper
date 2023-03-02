import sys
import json
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import Qt, QFile
from PySide2.QtUiTools import QUiLoader

# Ui_MainWindow, QtBaseClass = loadUiType(qt_creator_file)
# Ui_MainWindow, QtBaseClass = QtCore.QFile(qt_creator_file)
# tick = QtGui.QImage('tick.png')


class TodoModel(QtCore.QAbstractListModel):
    def __init__(self, *args, todos=None, **kwargs):
        super(TodoModel, self).__init__(*args, **kwargs)
        self.todos = todos or []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            text = self.todos[index.row()]
            return text

        # if role == Qt.DecorationRole:
        #     text = self.todos[index.row()]
        #     if text:
        #         return text

    def rowCount(self, index):
        return len(self.todos)


class MainWindow:
    def __init__(self):
        # self.setupUi(self)
        self.model = TodoModel()
        qt_creator_file = "mainwindow.ui"
        loginUi = QtCore.QFile(qt_creator_file)
        loginUi.open(QtCore.QFile.ReadOnly)
        loader = QUiLoader()
        self.window = loader.load(loginUi)
        self.window.show()

        self.window.todoView.setModel(self.model)

        self.window.addButton.pressed.connect(self.add)
        self.window.deleteButton.pressed.connect(self.delete)
        self.window.completeButton.pressed.connect(self.complete)

    def add(self):
        """
        Add an item to our todo list, getting the text from the QLineEdit .todoEdit
        and then clearing it.
        """
        text = self.window.todoEdit.text()
        if text:  # Don't add empty strings.
            # Access the list via the model.
            self.model.todos.append(text)
            # Trigger refresh.
            self.model.layoutChanged.emit()
            #  Empty the input
            self.window.todoEdit.setText("")

    def delete(self):
        indexes = self.window.todoView.selectedIndexes()
        if indexes:
            # Indexes is a list of a single item in single-select mode.
            index = indexes[0]
            # Remove the item and refresh.
            del self.model.todos[index.row()]
            self.model.layoutChanged.emit()
            # Clear the selection (as it is no longer valid).
            self.todoView.clearSelection()
            self.save()

    def complete(self):
        indexes = self.window.todoView.selectedIndexes()
        if indexes:
            index = indexes[0]
            row = index.row()
            status, text = self.model.todos[row]
            self.model.todos[row] = (True, text)
            # .dataChanged takes top-left and bottom right, which are equal
            # for a single selection.
            self.model.dataChanged.emit(index, index)
            # Clear the selection (as it is no longer valid).
            self.todoView.clearSelection()
            self.save()



app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
app.exec_()


