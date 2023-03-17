from PySide2 import QtWidgets


class PepperView(QtWidgets.QListView):
    """QtWidget의 QListView를 상속받 Viewer class로, project_listview, templates_listview, shots_listview에 사용된다.
    """
    def __init__(self, parent):
        super(PepperView, self).__init__(parent=None)
        pass


class PepperDnDView(QtWidgets.QListView):
    """QtWidget의 QListView를 상속받는 Viewer class로, drag & drop event를 accept해주는 메소드들을 가지고 있다.
    Drag & drop은 renderlists_listview에만 사용되며,
    Drag
    """
    def __init__(self, parent):
        super(PepperDnDView, self).__init__(parent=None)
        self.setDragEnabled(True)   
        self.setAcceptDrops(True)
        self.setDragDropMode(self.DragDrop)
        self.startIndex = None

    def dragEnterEvent(self, event):
        """Listview 안에서 하나의 row를 drag 했을 때 생기는 이벤트를 accept 해주는 메소드다.
        """
        self.startIndex = ''
        event.accept()

    def dropEvent(self, event):
        """Listview 안에서 drag된 row를 drop 했을 때 생기는 이벤트를 accept 해주는 메소드다. \n
        선택된 row의 index를 selections로 받고, drop된 row의 index는 destination_index로 받는다.
        기존 model.pepperlist의 data들은 updated_list에 저장해두고,
        destination_index에 맞는 위치에 selections의 data를 insert 한다.
        insert 이후에는 updated_list에서 기존 selections의 row를 pop을 통해 제거해준다. \n
        업데이트된 updated_list는 다시 model.pepperlist의 data로 들어간다.
        """
        selections = self.selectedIndexes()
        rev_selections = list(reversed(selections))
        QtWidgets.QListView.dropEvent(self, event)
        destination_index = self.indexAt(event.pos())
        dix_row = destination_index.row()
        model = destination_index.model()
        if model is None:
            return
        updated_list = model.pepperlist
        temp_list = []
        for idx in rev_selections:
            index_row = idx.row()
            if destination_index.isValid():
                temp_list.insert(0, updated_list[index_row])
                updated_list.pop(index_row)
        updated_list[dix_row:dix_row] = temp_list
        model.pepperlist = updated_list
        model.layoutChanged.emit()
