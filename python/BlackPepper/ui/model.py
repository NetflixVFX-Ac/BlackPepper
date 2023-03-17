from PySide2 import QtCore
from PySide2.QtCore import Qt


class PepperModel(QtCore.QAbstractListModel):
    """QAbstractListModel을 상속받는 model로, project_model, template_model, shot_model, render_list_model의 model로 사용된다.
    QAbstractListModel의 built-in 메소드들을 사용한다.
    """
    def __init__(self, pepperlist=None):
        super(PepperModel, self).__init__()
        self.pepperlist = pepperlist or []

    def data(self, index, role):
        """Model의 선택된 index에 맞는 data를 반환해주는 메소드.
        """
        if role == Qt.DisplayRole:
            text = self.pepperlist[index.row()]
            return text

    def rowCount(self, index):
        """Model의 총 row 개수를 반환해주는 메소드.
        """
        return len(self.pepperlist)

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable


class PepperDnDModel(QtCore.QAbstractListModel):
    """QAbstractListModel을 상속받는 model로, drag & drop event에 필요한 flag들을 가지고 있다. render_model에 사용된다. \n
    QAbstractListModel의 built-in 메소드들을 사용한다.

    """
    def __init__(self,  pepperlist=None):
        super(PepperDnDModel, self).__init__()
        self.pepperlist = pepperlist or []

    def data(self, index, role):
        """Model의 선택된 index에 맞는 data를 반환해주는 메소드. \n
        Renderlist에는 dict가 들어가기 때문에 dict가 선택되었을 때는 해당 dict의 'name'을 가져온다.
        """
        if role == Qt.DisplayRole:
            if isinstance(self.pepperlist[index.row()], str):
                text = self.pepperlist[index.row()]
            else:
                text = self.pepperlist[index.row()].get('name')
            return text

    def rowCount(self, index):
        """Model의 총 row 개수를 반환해주는 메소드.
        """
        if not self.pepperlist:
            return 0
        return len(self.pepperlist)

    def flags(self, index):
        """Drag & drop을 위해 ItemIsDragEnabled와 ItemIsDropEnabled를 설정했다.
        """
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
