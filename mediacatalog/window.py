from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from mediacatalog.db import SqlDatabase
from mediacatalog.style import style
from mediacatalog.utils import geticon, LOCAL
from mediacatalog.settings import Settings
from mediacatalog.mediapage import MediaPage, TvPage


class Window(QMainWindow):
    """Window object."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
        self.setObjectName("MainWindow")
        self.setWindowTitle("Fuzzy's Media Manager")
        self.db = SqlDatabase(LOCAL / "media.db")
        self.setWindowIcon(geticon("popcorn"))
        self.central = QTabWidget(parent=self)
        self.settings = Settings(self.db, self)
        self.settings.databaseReset.connect(self.onDbReset)
        self.movies = MediaPage("movies", self)
        self.tv = TvPage("tv", self)
        self.ufc = MediaPage("ufc", self)
        self.central.addTab(self.movies, "Movies")
        self.documentaries = MediaPage("documentaries", self)
        self.central.addTab(self.tv, "TV")
        self.central.addTab(self.ufc, "UFC")
        self.central.addTab(self.documentaries, "Documentaries")
        self.central.addTab(self.settings, "Settings")
        self.setCentralWidget(self.central)
        self.settings.somethingChanged.connect(self.update_tables)
        self.resize(1500, 900)

    def onDbReset(self):
        del self.db
        self.db = SqlDatabase(LOCAL / "media.db")

    def update_tables(self):
        for page in [self.movies, self.tv, self.ufc, self.documentaries]:
            page.table.tableModel().refreshHeaders()
            page.table.tableModel().getData()
            page.table.selectRow(0)

    def setSetting(self, key, value):
        self.db.setSetting(key, value)


def execute():
    app = QApplication([])
    app.setStyleSheet(style())
    window = Window()
    window.show()
    app.exec()
