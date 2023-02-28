from PySide2 import QtCore
from PySide2.QtCore import Qt


class RenderModel(QtCore.QAbstractListModel):
    def __init__(self):
        super(RenderModel, self).__init__()
        self.renders = []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            text = self.renders[index.row()]
            return text

    def rowCount(self, index):
        return len(self.renders)
