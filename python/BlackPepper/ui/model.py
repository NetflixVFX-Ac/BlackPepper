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

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable


class PepperDnDModel(QtCore.QAbstractListModel):
    """

    """
    def __init__(self,  pepperlist=None):
        super(PepperDnDModel, self).__init__()
        self.pepperlist = pepperlist or []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            text = self.pepperlist[index.row()]
            return text

    def setData(self, start, index, role):
        print("AA", start, index)
        # item = self.pepperlist.pop(start)
        # self.pepperlist.insert(index, item)

    # def insertRow(self, row, count, index):
    #     self.beginInsertRows()
    #     self.endInsertRows()
    #
    # def removeRow(self, row, parent=None, *args, **kwargs):
    #     self.beginRemoveRows()
    #     self.endRemoveRows()

    def rowCount(self, index):
        return len(self.pepperlist)

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
