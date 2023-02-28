from PySide2 import QtCore
from PySide2.QtCore import Qt


class ProjectModel(QtCore.QAbstractListModel):
    def __init__(self):
        super(ProjectModel, self).__init__()
        self.projects = []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            text = self.projects[index.row()]
            return text

    def rowCount(self, index):
        return len(self.projects)