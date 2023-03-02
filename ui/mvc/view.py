from PySide2 import QtWidgets


class PepperView(QtWidgets.QListView):
    def __init__(self, parent):
        super(PepperView, self).__init__(parent=None)

    def get_selected_project(self):
        if not self.model():
            return
        return self.model().selectedIndexes()[-1]
