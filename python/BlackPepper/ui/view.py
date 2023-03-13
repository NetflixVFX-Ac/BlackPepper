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
        print("drag", event)
        self.startIndex = ''
        # event.
        event.accept()

    # def dragMoveEvent(self, event):
    #     super(PepperView, self).dragMoveEvent(event)
    #     event.accept()

    def dropEvent(self, event):
        # super(PepperDnDView, self).dropEvent(event)
        print(event.source)
        print("drop", event)
        # model = self.model().setData(self.startIndex, index)
        event.accept()


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
