from PySide2 import QtCore
from PySide2.QtCore import Qt


class MainModel(QtCore.QAbstractListModel):
    def __init__(self, *args, model=None, **kwargs):
        super(MainModel, self).__init__(*args, **kwargs)
        self.model = model or []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            text = self.model[index.row()]
            return text

    def rowCount(self, index):
        return len(self.model)


class TempModel(QtCore.QAbstractListModel):
    def __init__(self, *args, todos=None, **kwargs):
        super(TempModel, self).__init__(*args, **kwargs)
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