from PySide2 import QtWidgets


class PepperView(QtWidgets.QListView):
    def __init__(self, parent):
        super(PepperView, self).__init__(parent=None)

    def get_selected_data(self):
        if not self.model():
            return
        return self.model().selectedIndexes()[-1]


class PepperDnDView(QtWidgets.QListView):
    def __init__(self, parent):
        super(PepperDnDView, self).__init__(parent=None)
        self.setDragEnabled(True)   
        self.setAcceptDrops(True)
        self.setDragDropMode(self.DragDrop)
        self.startIndex = None

    def dragEnterEvent(self, event):
        self.startIndex = ''
        event.accept()

    # def dragMoveEvent(self, event):
    #     super(PepperDnDView, self).dragMoveEvent(event)
    #     if event object is object:
    #         do not accept event
    #     print(event)
    #     event.accept()

    def dropEvent(self, event):
        selections = self.selectedIndexes()
        rev_selections = list(reversed(selections))
        QtWidgets.QListView.dropEvent(self, event)
        destination_index = self.indexAt(event.pos())
        dix_row = destination_index.row()
        model = destination_index.model()
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
