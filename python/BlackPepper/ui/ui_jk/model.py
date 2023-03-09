from PySide2 import QtCore
from PySide2.QtCore import Qt


class PepperModel(QtCore.QAbstractListModel):
    """

    """
    def __init__(self,  pepperlist=None):
        super(PepperModel, self).__init__()
        self.pepperlist = pepperlist or []


    def data(self, index, role):
        if role == Qt.DisplayRole:
            text = self.pepperlist[index.row()]
            return text

    def rowCount(self, index):
        return len(self.pepperlist)
