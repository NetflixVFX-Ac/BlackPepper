from PySide2 import QtCore
from PySide2.QtCore import Qt


class ShotModel(QtCore.QAbstractListModel):
    def __init__(self):
        super(ShotModel, self).__init__()
        self.shots = []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            text = self.shots[index.row()]
            return text

    def rowCount(self, index):
        return len(self.shots)
