from PySide2 import QtCore
from PySide2.QtCore import Qt


class TemplateModel(QtCore.QAbstractListModel):
    def __init__(self):
        super(TemplateModel, self).__init__()
        self.templates = []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            text = self.templates[index.row()]
            return text

    def rowCount(self, index):
        return len(self.templates)
