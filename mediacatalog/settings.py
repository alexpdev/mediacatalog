from pathlib import Path

from mediacatalog.utils import geticon

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

class GroupBox(QGroupBox):

    somethingChanged = Signal(str, str)
    def __init__(self, title, parent=None):
        super().__init__(title, parent=parent)
        self._title = title
        self.layout = QVBoxLayout(self)
        self.list = QListWidget()
        self.add_button = QPushButton("Add")
        self.remove_button = QPushButton("Remove")
        hlayout = QHBoxLayout()
        hlayout.addWidget(self.add_button)
        hlayout.addWidget(self.remove_button)
        self.layout.addWidget(self.list)
        self.layout.addLayout(hlayout)
        self.add_button.clicked.connect(self.choose_folder)
        self.remove_button.clicked.connect(self.remove_folder)

    def choose_folder(self):
        dialog = DirectorySelectionDialog()
        dialog.selectionMade.connect(self.add_folder)
        dialog.exec()

    def onChange(self):
        items = [self.list.item(i) for i in range(self.list.count())]
        paths = [item.text() for item in items if item]
        self.somethingChanged.emit(self._title, ";".join(paths))

    def add_folder(self, path):
        self.list.addItem(path)
        self.onChange()

    def remove_folder(self):
        item = self.list.currentItem()
        index = self.list.indexFromItem(item)
        self.list.takeItem(index.row())
        self.onChange()




class Settings(QWidget):
    toHome = Signal()
    def __init__(self, db, parent=None):
        super().__init__(parent=parent)
        self.db = db
        self.layout = QVBoxLayout(self)
        grid = QGridLayout()
        self.toolbar = QToolBar()
        self.back_action = QAction(geticon("undo"), "Back", self)
        self.back_action.triggered.connect(self.toHome.emit)
        self.layout.addWidget(self.toolbar)
        self.toolbar.addAction(self.back_action)
        self.movies_box = GroupBox("Movies", self)
        self.tv_box = GroupBox("TV", self)
        self.ufc_box = GroupBox("UFC", self)
        self.documentaries_box = GroupBox("Documentaries", self)
        grid.addWidget(self.movies_box, 0, 0)
        grid.addWidget(self.tv_box, 0, 1)
        grid.addWidget(self.ufc_box, 1, 0)
        grid.addWidget(self.documentaries_box, 1, 1)
        self.layout.addLayout(grid)
        self.boxes = [self.movies_box, self.tv_box, self.ufc_box, self.documentaries_box]
        for box in self.boxes:
            box.somethingChanged.connect(self.update_settings)
        
    def update_settings(self, key, value):
        self.db.setSettings(key,value)
        self.db.refresh_contents()
        


class DirectorySelectionDialog(QDialog):
    selectionMade = Signal(str)

    def __init__(self, initial_path=None, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("Choose Directory...")
        self.setObjectName("SelectDir")
        self.setMinimumSize(200, 300)
        self.model = QFileSystemModel(parent=self)
        self.model.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot)
        root_index = self.model.setRootPath(self.model.myComputer())
        self.tree_view = QTreeView(parent=self)
        self.tree_view.setModel(self.model)
        self.tree_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setSortingEnabled(True)
        self.tree_view.sortByColumn(0, Qt.AscendingOrder)
        for i in range(1, self.model.columnCount()):
            self.tree_view.setColumnHidden(i, True)
        self.tree_view.scrollTo(root_index)
        self.tree_view.selectionModel().setCurrentIndex(
            root_index, QItemSelectionModel.Current | QItemSelectionModel.Select
        )
        self.tree_view.selectionModel().selectionChanged.connect(self.onCurrentChanged)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        self.ok_button = button_box.button(QDialogButtonBox.Ok)
        label = QLabel("Folder:")
        self.folder_name = QLineEdit(parent=self)
        self.folder_name.setDisabled(True)
        self.folder_name.setReadOnly(True)
        path_layout = QHBoxLayout()
        path_layout.addWidget(label)
        path_layout.addSpacing(10)
        path_layout.addWidget(self.folder_name)
        self.ok_button.clicked.connect(self.path_selected)
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tree_view)
        main_layout.addSpacing(10)
        main_layout.addLayout(path_layout)
        main_layout.addSpacing(10)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

    def path_selected(self):
        self.selectionMade.emit(str(self.directory()))
        self.close()

    def onCurrentChanged(self):
        file_info = self.model.fileInfo(self.tree_view.selectionModel().currentIndex())
        self.folder_name.setText(file_info.fileName())
        self.ok_button.setEnabled(file_info.isDir())
        self.ok_button.setDefault(file_info.isDir())
        self.tree_view.resizeColumnToContents(0)

    def directory(self):
        file_info = self.model.fileInfo(self.tree_view.selectionModel().currentIndex())
        return Path(file_info.absoluteFilePath())