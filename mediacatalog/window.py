from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from mediacatalog.db import SqlDatabase
from mediacatalog.style import style
from mediacatalog.utils import geticon, LOCAL
from mediacatalog.settings import Settings



class MediaProfile(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.layout = QVBoxLayout(self)
        self.image = QLabel()
        self.layout.addWidget(self.image)
        title_label = QLabel("Title: ")
        year_label = QLabel("Year: ")
        rating_label = QLabel("Rating: ")
        genre_label = QLabel("Genre: ")
        quality_label = QLabel("Quality: ")
        watched_label = QLabel("Watched: ")
        plot_label = QLabel("Plot: ")
        comments_label = QLabel("Comments: ")
        self.title_line = QPlainTextEdit()
        self.year_line = QLineEdit()
        self.rating_line = QLineEdit()
        self.genre_line = QLineEdit()
        self.quality_line = QLineEdit()
        self.watched_line = QLineEdit()
        self.plot_line = QPlainTextEdit()
        self.comment_line = QPlainTextEdit()
        hlayout1 = QHBoxLayout()
        hlayout2 = QHBoxLayout()
        hlayout3 = QHBoxLayout()
        hlayout4 = QHBoxLayout()
        hlayout5 = QHBoxLayout()
        hlayout6 = QHBoxLayout()
        hlayout7 = QHBoxLayout()
        hlayout8 = QHBoxLayout()
        hlayout1.addWidget(title_label)
        hlayout1.addWidget(self.title_line)
        hlayout2.addWidget(year_label)
        hlayout2.addWidget(self.year_line)
        hlayout3.addWidget(rating_label)
        hlayout3.addWidget(self.rating_line)
        hlayout4.addWidget(genre_label)
        hlayout4.addWidget(self.genre_line)
        hlayout5.addWidget(quality_label)
        hlayout5.addWidget(self.quality_line)
        hlayout6.addWidget(watched_label)
        hlayout6.addWidget(self.watched_line)
        hlayout7.addWidget(plot_label)
        hlayout7.addWidget(self.plot_line)
        hlayout8.addWidget(comments_label)
        hlayout8.addWidget(self.comment_line)
        self.layout.addLayout(hlayout1)
        self.layout.addLayout(hlayout2)
        self.layout.addLayout(hlayout3)
        self.layout.addLayout(hlayout4)
        self.layout.addLayout(hlayout5)
        self.layout.addLayout(hlayout6)
        self.layout.addLayout(hlayout7)
        self.layout.addLayout(hlayout8)


class MediaPage(QWidget):
    toHome = Signal()
    
    def __init__(self, db, parent=None):
        super().__init__(parent=parent)
        self.db = db
        self.layout = QVBoxLayout(self)
        self.toolbar = QToolBar()
        self.back_action = QAction(geticon("undo"), "Back", self)
        self.back_action.triggered.connect(self.toHome.emit)
        self.toolbar.addAction(self.back_action)
        self.layout.addWidget(self.toolbar)
        self.splitter = QSplitter()
        self.layout.addWidget(self.splitter)
        self.table = QTableView()
        self.mediaProfile = MediaProfile(self)
        self.splitter.addWidget(self.table)
        self.splitter.addWidget(self.mediaProfile)



class MainPage(QWidget):
    
    toHome = Signal()
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.layout = QGridLayout(self)
        self.movies_button = QPushButton("Movies")
        self.tv_button = QPushButton("TV Shows")
        self.ufc_button = QPushButton("UFC")
        self.documentaries_button = QPushButton("Documentaries")
        self.settings_button = QPushButton("Settings")
        self.layout.addWidget(self.movies_button, 0, 0)
        self.layout.addWidget(self.tv_button, 0, 1)
        self.layout.addWidget(self.ufc_button, 1, 0)
        self.layout.addWidget(self.documentaries_button, 1, 1)
        self.layout.addWidget(self.settings_button, 2, 1)


class Window(QMainWindow):
    """Window object."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
        self.setObjectName('MainWindow')
        self.setWindowTitle("Media Catalog")
        self.db = SqlDatabase(LOCAL / "media.db")
        self.setWindowIcon(geticon("popcorn"))
        self.central = QStackedWidget(parent=self)
        self.mainpage = MainPage()
        self.movies = MediaPage(self.db, self)
        self.tv = MediaPage(self.db, self)
        self.ufc = MediaPage(self.db, self)
        self.documentaries = MediaPage(self.db, self)
        self.settings = Settings(self.db, self)
        for widget in [self.mainpage, self.movies, self.tv, self.ufc, self.documentaries, self.settings]:
            self.central.addWidget(widget)
            widget.toHome.connect(self.open_main)
        self.setCentralWidget(self.central)
        self.mainpage.movies_button.clicked.connect(self.open_movies)
        self.mainpage.tv_button.clicked.connect(self.open_tv)
        self.mainpage.ufc_button.clicked.connect(self.open_ufc)
        self.mainpage.documentaries_button.clicked.connect(self.open_documentaries)
        self.mainpage.settings_button.clicked.connect(self.open_settings)
        self.settings.setSetting.connect(self.setSetting)
        self.resize(1000, 800)
        
    def setSetting(self, key, value):
        self.db.setSetting(key, value)
    
    def open_main(self):
        self.central.setCurrentWidget(self.mainpage)
    
    def open_movies(self):
        self.central.setCurrentWidget(self.movies)
    
    def open_settings(self):
        self.central.setCurrentWidget(self.settings)
    
    def open_tv(self):
        self.central.setCurrentWidget(self.tv)
    
    def open_documentaries(self):
        self.central.setCurrentWidget(self.documentaries)
    
    def open_ufc(self):
        self.central.setCurrentWidget(self.ufc)
        




def execute():
    app = QApplication([])
    app.setStyleSheet(style)
    window = Window()
    window.show()
    app.exec()