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
        # self.setDropIndicatorShown(True)

    # def get_selected_data(self):
    #     if not self.model():
    #         return
    #     return self.model().selectedIndexes()[-1]

    def dragEnterEvent(self, event):
        # super(PepperView, self).dragEnterEvent(event)
        # print("drag", event)
        self.startIndex = ''
        # event.
        event.accept()

    # def dragMoveEvent(self, event):
    #     super(PepperDnDView, self).dragMoveEvent(event)
        # if event object is object:
        #     do not accept event
        # print(event)
        # event.accept()

    # def dropEvent(self, event):
        # super(PepperDnDView, self).dropEvent(event)
        # print("drop", event)
        # model = self.model().setData(self.startIndex)
        # event.accept()

    def dropEvent(self, event):
        # print(event.dropAction())
        super(PepperDnDView, self).dropEvent(event)
        # print("drop", event)

        # from_index = self.currentIndex()
        # destination_index = self.indexAt(event.pos())
        # if destination_index.isValid():
        #     QtWidgets.QListView.dropEvent(self, event)
        #     model = destination_index.model()
        #     updated_list = model.pepperlist
        #     updated_list.insert(destination_index.row(), updated_list.pop(from_index.row()))
        #     model.updated_list = updated_list

        selections = self.selectedIndexes()
        # print('selections : ', selections)
        destination_index = self.indexAt(event.pos())
        # print('to index : ', destination_index)
        # print(selections)
        rev_selections = list(reversed(selections))
        dix_row = destination_index.row()

        QtWidgets.QListView.dropEvent(self, event)
        model = destination_index.model()
        updated_list = model.pepperlist
        temp_list = []
        for idx in rev_selections:
            # print(idx)
            # print(idx.data())
            index_row = idx.row()
            if destination_index.isValid():

                # print(index_row, dix_row)

                # print('mod : ', model)

                # print('pepperlist : ', model.pepperlist)
                # print(updated_list[index_row], "AA")
                temp_list.insert(0, updated_list[index_row])
                updated_list.pop(index_row)

                # updated_list.insert(dix_row, updated_list.pop(index_row))
                # print('d_idx_row : ', destination_index.row())
                # print('idx_row : ', idx.row())
        updated_list[dix_row:dix_row] = temp_list
        model.pepperlist = updated_list
        model.layoutChanged.emit()
        # if dix_row < 0:
        # dix_row += 1
        # print('updated_list : ', model.pepperlist)

# def main():
#     testlist = [0, 1, 2, 3, 4, 5]
#     fulllen = len(testlist)
#     deletelist = [0, 2, 4, 5]
#     deletelen = len(deletelist)
#     point = 3
#     the_point = point - (fulllen - deletelen) + 1
#     if the_point < 0:
#         the_point = 0
#     print(the_point)
#     for i in deletelist:
#         testlist.remove(i)
#     for i in deletelist:
#         testlist.insert(the_point, i)
#         the_point += 1
#     print(testlist)
#
#
# if __name__ == "__main__":
#     main()
