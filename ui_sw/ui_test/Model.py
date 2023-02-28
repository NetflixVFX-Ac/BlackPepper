from PySide2 import QtCore
from PySide2.QtCore import Qt


class MainModel(QtCore.QAbstractListModel):
    def __init__(self, model=None):
        super(MainModel, self).__init__()
        self.model = model or []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            text = self.model[index.row()]
            return text

        # if role == Qt.DecorationRole:
        #     status, _ = self.todos[index.row()]
        #     if status:
        #         return tick

    def rowCount(self, index):
        return len(self.model)