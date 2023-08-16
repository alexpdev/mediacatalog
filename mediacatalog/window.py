import os

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from mediacatalog.db import SqlDatabase
from mediacatalog.style import style
from mediacatalog.utils import geticon, LOCAL
from mediacatalog.settings import SettingsWidget, setting, setSetting
from mediacatalog.mediapage import MediaPage, TvPage


class Window(QMainWindow):
    """Window object."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
        self.setObjectName("MainWindow")
        self.setWindowTitle("Fuzzy's Media Manager")
        self.setWindowIcon(geticon("popcorn"))
        self.central = QStackedWidget()
        self.db = SqlDatabase(LOCAL / "media.db")
        self.setWindowIcon(geticon("popcorn"))
        self.tabs = QTabWidget(parent=self)
        self.settings = SettingsWidget(self.db, self)
        self.settings.databaseReset.connect(self.onDbReset)
        self.movies = MediaPage("movies", self)
        self.tv = TvPage(self)
        self.ufc = MediaPage("ufc", self)
        self.tabs.addTab(self.movies, "Movies")
        self.documentaries = MediaPage("documentaries", self)
        self.tabs.addTab(self.tv, "TV")
        self.tabs.addTab(self.ufc, "UFC")
        self.tabs.addTab(self.documentaries, "Documentaries")
        self.central.addWidget(self.tabs)
        self.central.addWidget(self.settings)
        for tab in [self.movies, self.tv, self.ufc, self.documentaries]:
            tab.toSettings.connect(self.onToSettings)
        # self.menubar = self.menuBar()
        # self.filemenu = QMenu("File")
        # self.exitAction = QAction("Exit", self)
        # self.exitAction.triggered.connect(self.close)
        # self.settingsAction = QAction("Settings", self)
        # self.filemenu.addAction(self.settingsAction)
        # self.filemenu.addSeparator()
        # self.filemenu.addAction(self.exitAction)
        # self.settingsAction.triggered.connect(self.openSettings)
        self.settings.toHome.connect(self.onToHome)
        # self.menubar.addMenu(self.filemenu)
        self.setCentralWidget(self.central)
        self.settings.somethingChanged.connect(self.update_tables)
        self.resize(*self.db.setting("windowsize"))

    def onToHome(self):
        self.central.setCurrentWidget(self.tabs)

    def onToSettings(self):
        self.central.setCurrentWidget(self.settings)

    def onDbReset(self):
        del self.db
        self.db = SqlDatabase(LOCAL / "media.db")

    def update_tables(self):
        for page in [self.movies, self.tv, self.ufc, self.documentaries]:
            page.table.tableModel().getData()
            page.table.filter(None)
            page.table.selectRow(0)

    def setSetting(self, key, value):
        self.db.set_setting(key, value)

    def openSettings(self):
        self.central.setCurrentWidget(self.settings)

    def closeEvent(self, event):
        self.setSetting("windowsize", list(self.size().toTuple()))
        super().closeEvent(event)


def execute():
    app = QApplication([])
    app.setStyleSheet(style())
    try:
        window = Window()
    except Exception as e:
        print(e)
        temp = [[],[],[],[]]
        try:
            temp = [setting("tv"), setting("movies"), setting("ufc"), setting("documentaries")]
        except:
            pass
        os.remove(LOCAL / "media.db")
        window = Window()
        for key, value in zip(["tv", "movies", "ufc", "documentaries"],temp):
            setSetting(key, value)
    window.show()
    app.exec()
