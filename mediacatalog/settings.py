from pathlib import Path
import json
import os

from mediacatalog import utils
from mediacatalog.utils import MAPPING, EPISODE, GENRES, QUALITY, geticon

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

class Settings:
    default = {
        'movies': [],
        "tv": [],
        "ufc": [],
        "documentaries":[],
        "documentariesprofilefields": list(MAPPING.keys()),
        "moviesprofilefields": list(MAPPING.keys()),
        "tvprofilefields": list(MAPPING.keys()),
        "ufcprofilefields": list(MAPPING.keys()),
        "documentariescolumnfields": list(MAPPING.keys()),
        "moviescolumnfields": list(MAPPING.keys()),
        "tvcolumnfields": list(utils.TV_MAPPING.keys()),
        "ufccolumnfields": list(MAPPING.keys()),
        "episodecolumnfields": list(EPISODE.keys()),
        "genres": GENRES,
        "quality": QUALITY,
        "windowsize": (1300, 700),
        "documentariestoolbarslider": [],
        "tvtoolbarslider": [],
        "moviestoolbarslider": [],
        "ufctoolbarslider": [],
        "documentariesmediaslider":[],
        "moviesmediaslider":[],
        "ufcmediaslider": [],
        "tvmediaslider":[]
    }
    current = None
    db = None


def setting(key):
    return Settings.current[key]

def setSetting(key, value):
    Settings.current[key] = value
    Settings.db.set_settings(Settings.current)

def updateField(table, foldername, key, value):
    Settings.db.updateField(table, foldername, key, value)

def getData(table):
    return Settings.db.getData(table)


class GroupBox(QGroupBox):
    somethingChanged = Signal()

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
        self.refresh_list()

    def refresh_list(self):
        contents = setting(self._title.lower())
        for path in contents:
            self.list.addItem(path)

    def choose_folder(self):
        result = QFileDialog.getExistingDirectory(self, "Choose Root Directory")
        if result:
            result = Path(result).resolve()
            self.add_folder(str(result))


    def onChange(self):
        items = [self.list.item(i) for i in range(self.list.count())]
        paths = [item.text() for item in items if item and item.text()]
        key = self._title.lower()
        setSetting(key, paths)
        self.somethingChanged.emit()

    def add_folder(self, path):
        self.list.addItem(path)
        self.onChange()

    def remove_folder(self):
        item = self.list.currentItem()
        index = self.list.indexFromItem(item)
        self.list.takeItem(index.row())
        self.onChange()


class TagBox(QGroupBox):
    somethingChanged = Signal(str, str)

    def __init__(self, title, field, parent=None):
        super().__init__(title, parent=parent)
        self._title = title
        self._field = field
        self.layout = QVBoxLayout(self)
        self.list = QListWidget()
        self.add_button = QPushButton("Add")
        self.remove_button = QPushButton("Remove")
        hlayout = QHBoxLayout()
        hlayout.addWidget(self.add_button)
        hlayout.addWidget(self.remove_button)
        self.layout.addWidget(self.list)
        self.layout.addLayout(hlayout)
        self.add_button.clicked.connect(self.add_field)
        self.remove_button.clicked.connect(self.remove_field)
        self.refresh_list()

    def refresh_list(self):
        options = setting(self._field)
        for option in options:
            self.list.addItem(option)

    def onChange(self):
        items = [self.list.item(i) for i in range(self.list.count())]
        paths = [item.text() for item in items if item and item.text()]
        self.somethingChanged.emit(self._field.lower(), paths)

    def add_field(self):
        text = QInputDialog.getText(self, f"Enter {self._field}", f"{self._field}")
        if text:
            path = text.replace("/", "\\")
            self.list.addItem(path)
            self.onChange()

    def remove_field(self):
        item = self.list.currentItem()
        index = self.list.indexFromItem(item)
        self.list.takeItem(index.row())
        self.onChange()


class FieldBox(QGroupBox):
    somethingChanged = Signal(str, str)

    def __init__(self, title, field, parent=None):
        super().__init__(title, parent=parent)
        self._title = title
        self._field = field
        self.layout = QVBoxLayout(self)
        self.list = QListWidget()
        self.layout.addWidget(self.list)
        self.list.itemChanged.connect(self.onChange)
        self.refresh_list()

    def refresh_list(self):
        options = setting(self._field)
        for key, value in MAPPING.items():
            item = QListWidgetItem()
            item.setText(value)
            if key in options:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)
            self.list.addItem(item)

    def onChange(self):
        items = [self.list.item(i) for i in range(self.list.count())]
        paths = [
            item.text()
            for item in items
            if item and item.text() and item.checkState() == Qt.CheckState.Checked
        ]
        fields = []
        for key, value in MAPPING.items():
            if value in paths:
                fields.append(key)
        self.somethingChanged.emit(self._field.lower(), fields)


class SettingsWidget(QWidget):
    toHome = Signal()
    somethingChanged = Signal()
    databaseReset = Signal()

    def __init__(self, db, parent=None):
        super().__init__(parent=parent)
        self.setDatabase(db)
        self.layout = QVBoxLayout(self)
        self.toolbar = QToolBar()
        self.backAction = QAction(geticon("back"), "<-", self)
        self.toolbar.addAction(self.backAction)
        self.layout.addWidget(self.toolbar)
        self.backAction.triggered.connect(self.toHome.emit)
        self.deep_reset_checkbox = QCheckBox("Deep Refresh Mode")
        self.reset_database_button = QPushButton("Reset Database")
        self.refresh_database_button = QPushButton("Refresh Database")
        self.movies_box = GroupBox("Movies", self)
        self.tv_box = GroupBox("TV", self)
        self.ufc_box = GroupBox("UFC", self)
        self.documentaries_box = GroupBox("Documentaries", self)
        self.tablefields = QListWidget()
        self.profilefields = QListWidget()
        self.genres = TagBox("Genre Tags", "genres", self)
        self.quality = TagBox("Quality Tags", "quality", self)
        self.moviesprofile = FieldBox("Movies Profile", "moviesprofilefields", self)
        self.tvprofile = FieldBox("TV Profile", "tvprofilefields", self)
        self.ufcprofile = FieldBox("UFC Profile", "ufcprofilefields", self)
        self.documentariesprofile = FieldBox(
            "Documentaries Profile", "documentariesprofilefields", self
        )
        self.reset_database_button.clicked.connect(self.onResetDatabase)
        self.refresh_database_button.clicked.connect(self.onRefreshDatabase)
        hlayout1 = QHBoxLayout()
        vlayout0 = QVBoxLayout()
        vlayout2 = QVBoxLayout()
        vlayout4 = QVBoxLayout()
        vlayout0.addWidget(self.movies_box)
        vlayout0.addWidget(self.tv_box)
        vlayout0.addWidget(self.ufc_box)
        vlayout0.addWidget(self.documentaries_box)
        hlayout1.addLayout(vlayout0)
        self.layout.addLayout(hlayout1)
        vlayout4.addWidget(self.reset_database_button)
        vlayout4.addWidget(self.refresh_database_button)
        vlayout4.addWidget(self.deep_reset_checkbox)
        vlayout4.addWidget(self.genres)
        vlayout4.addWidget(self.quality)
        vlayout2.addWidget(self.moviesprofile)
        vlayout2.addWidget(self.tvprofile)
        vlayout2.addWidget(self.ufcprofile)
        vlayout2.addWidget(self.documentariesprofile)
        hlayout1.addLayout(vlayout2)
        hlayout1.addLayout(vlayout4)
        self.boxes = [
            self.movies_box,
            self.tv_box,
            self.ufc_box,
            self.documentaries_box,
            self.genres,
            self.quality,
            self.tvprofile,
            self.moviesprofile,
            self.ufcprofile,
            self.documentariesprofile,
        ]
        for box in self.boxes:
            box.somethingChanged.connect(self.update_settings)

    def setDatabase(self, db):
        Settings.db = db
        Settings.current = db.settings()

    def onResetDatabase(self):
        os.remove(Settings.db.path)
        self.databaseReset.emit()

    def onRefreshDatabase(self):
        if self.deep_reset_checkbox.isChecked():
            Settings.db.refresh_database(deep=True)
        else:
            Settings.db.refresh_database()
        self.somethingChanged.emit()

    def update_settings(self, *args):
        if len(args) == 2:
            key, value = args
            setSetting(key, value)
        Settings.db.refresh_database()
        self.somethingChanged.emit()


class DirectorySelectionDialog(QDialog):
    selectionMade = Signal(str)

    def __init__(self, initial_path=None, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("Choose Directory...")
        self.setObjectName("SelectDir")
        self.setMinimumSize(200, 300)
        self.model = QFileSystemModel(parent=self)
        self.model.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot | QDir.Hidden)
        root_index = self.model.setRootPath("////")
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

    def sizeHint(self):
        return QSize(300, 300)

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
