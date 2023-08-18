import os

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from mediacatalog.db import SqlDatabase
from mediacatalog.mediapage import MediaPage, TvPage
from mediacatalog.settings import (RecentDialog, SettingsWidget,
                                   connectionClose, setSetting, setting)
from mediacatalog.style import style
from mediacatalog.utils import LOCAL, geticon


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
            tab.toolbar.recent_list_action.triggered.connect(self.show_recent)
        self.settings.toHome.connect(self.onToHome)
        self.setCentralWidget(self.central)
        self.settings.somethingChanged.connect(self.update_tables)
        self.resize(*self.db.setting("windowsize"))

    def show_recent(self):
        recentdialog = RecentDialog()
        recentdialog.exec()

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
        temp = [[], [], [], []]
        try:
            temp = [
                setting("tv"),
                setting("movies"),
                setting("ufc"),
                setting("documentaries"),
            ]
        except:
            pass

        connectionClose()
        os.remove(LOCAL / "media.db")
        window = Window()
        for key, value in zip(["tv", "movies", "ufc", "documentaries"], temp):
            setSetting(key, value)
    window.show()
    app.exec()
