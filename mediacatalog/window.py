import json
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *


from mediacatalog.db import SqlDatabase
from mediacatalog.style import style
from mediacatalog.utils import geticon, LOCAL, MAPPING, FlowLayout
from mediacatalog.settings import Settings, setting


class LineEdit(QLineEdit):
    
    def sizeHint(self):
        return self.minimumSizeHint()
    
    def minimumSizeHint(self):
        font = self.font()
        text = self.text()
        width = QFontMetrics(font).horizontalAdvance(text)
        height = QFontMetrics(font).height()
        return QSize(max(width, 20), max(height, 40))

class FieldWidget(QWidget):
    def __init__(self, field, widget="line", parent=None):
        super().__init__(parent=parent)
        self._line = widget
        self._field = field
        self.label = QLabel(field)
        self.label.setFixedWidth(50)
        self.layout = QFormLayout(self)
        if widget == "line":
            self.line = QLineEdit()
        elif widget == "text":
            self.line = QPlainTextEdit()
            self.line.setFixedWidth(300)
        self.layout.addRow(self.label, self.line)
    
    def setText(self, text):
        if self._line == "line":
            self.line.setText(str(text))
        elif self._line == "text":
            self.line.setPlainText(str(text))




class MediaProfile(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.layout = QVBoxLayout(self)
        self.scrollarea = QScrollArea()
        self.scrollWidget = QWidget()
        self.scrollarea.setWidget(self.scrollWidget)
        self.scrollarea.setWidgetResizable(True)
        self.scrolllayout = FlowLayout(self.scrollWidget)
        self.button = QPushButton()
        self.imagestack = QStackedWidget()        
        self.labels = {}
        self.layout.addWidget(self.imagestack)
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.scrollarea)
        self._margins = 5
        self.fields = {}
        self.button.clicked.connect(self.next_image)
        for key,value in MAPPING.items():
            if key in ["plot", "comments"]:
                widget = FieldWidget(value, "text", self)
            else:
                widget = FieldWidget(value, "line", self)
            self.fields[key] = widget
            self.scrolllayout.addWidget(widget)
    
    def next_image(self):
        images = list(self.labels.values())
        i = images.index(self.imagestack.currentWidget())
        if i < len(images) - 1:
            self.imagestack.setCurrentWidget(images[i+1])
        else:
            self.imagestack.setCurrentWidget(images[0])
    
    def setCurrent(self, data):
        for label in self.labels.values():
            label.deleteLater()
        fields = setting("profilefields").split(";")
        self.labels = {}
        for image in data["images"]:
            label = QLabel()
            pixmap = QPixmap(image).scaled(QSize(int(self.width() * .8), int(self.height()*.3)), Qt.AspectRatioMode.KeepAspectRatio)
            label.setPixmap(pixmap)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.imagestack.addWidget(label)
            self.imagestack.setCurrentWidget(label)
            self.labels[image] = label
        for key,value in data.items():
            self.fields[key].setText(value)
            if key not in fields:
                self.fields[key].hide()
            else:
                self.fields[key].show()
    
    def resizeEvent(self, event):
        for key, value in self.labels.items():
            pixmap = QPixmap(key).scaled(QSize(int(event.size().width() *.8), int(event.size().height() * .3)), Qt.AspectRatioMode.KeepAspectRatio)
            value.setPixmap(pixmap)
        return super().resizeEvent(event)

class SqlTableModel(QAbstractTableModel):
    
    def __init__(self, db, table, parent=None):
        super().__init__(parent=parent)
        self._table = table
        self._db = db
        self._reverse = {v:k for k,v in MAPPING.items()}
        self._headers_labels = self._db.setting("tablefields").split(";")
        self._headers = [MAPPING[i] for i in self._headers_labels]
        self._data = []
        self.getData()
        
    def getRow(self, index):
        return self._data[index.row()]

    def refreshHeaders(self):
        self._headers_labels = self._db.setting("tablefields").split(";")
        self._headers = [MAPPING[i] for i in self._headers_labels]

    def getData(self):
        self._data = []
        data = self._db.getData(self._table)
        for record in data:
            title, path, data = record
            data = json.loads(data)
            self._data.append(data)
        
    def rowCount(self, _) -> int:
        return len(self._data)

    def columnCount(self, _):
        return len(self._headers)
    
    def headerData(self, section, orientation, role):
        if orientation == Qt.Orientation.Horizontal:
            if role == Qt.ItemDataRole.DisplayRole:
                return self._headers[section]
        return None
    
    def data(self, index, role):
        if index.isValid():
            if role == Qt.ItemDataRole.DisplayRole:
                row, col = index.row(), index.column()
                label = self._headers[col]
                field = self._reverse[label]
                text = self._data[row][field]
                return text
        return None


class MediaPage(QWidget):
    toHome = Signal()
    
    def __init__(self, db, table, parent=None):
        super().__init__(parent=parent)
        self.db = db
        self._table = table
        self.layout = QVBoxLayout(self)
        self.toolbar = QToolBar()
        self.back_action = QAction(geticon("undo"), "Back", self)
        self.back_action.triggered.connect(self.toHome.emit)
        self.toolbar.addAction(self.back_action)
        self.layout.addWidget(self.toolbar)
        self.splitter = QSplitter()
        self.layout.addWidget(self.splitter)
        self.table = QTableView()
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.model = SqlTableModel(self.db, self._table, self)
        self.table.setModel(self.model)
        self.mediaProfile = MediaProfile(self)
        self.splitter.addWidget(self.table)
        self.splitter.addWidget(self.mediaProfile)
        self.table.selectionModel().currentRowChanged.connect(self.onRowChanged)
        self.table.selectRow(0)
    
    def onRowChanged(self, current, previous):
        row = self.model.getRow(current)
        self.mediaProfile.setCurrent(row)
    
        
        



class MainPage(QWidget):
    
    toHome = Signal()
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.layout = QGridLayout(self)
        self.movies_button = QPushButton("Movies", self)
        self.tv_button = QPushButton("TV Shows", self)
        self.ufc_button = QPushButton("UFC", self)
        self.documentaries_button = QPushButton("Documentaries", self)
        self.settings_button = QPushButton("Settings")
        for button in [self.movies_button, self.tv_button, self.ufc_button, self.documentaries_button, self.settings_button]:
            font = QFont()
            font.setPointSize(25)
            button.setFont(font)
            button.setMaximumWidth(300)
            button.setMinimumHeight(100)
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
        self.settings = Settings(self.db, self)
        self.mainpage = MainPage()
        self.movies = MediaPage(self.db, "movies", self)
        self.tv = MediaPage(self.db, "tv", self)
        self.ufc = MediaPage(self.db, "ufc", self)
        self.documentaries = MediaPage(self.db, "documentaries", self)
        for widget in [self.mainpage, self.movies, self.tv, self.ufc, self.documentaries, self.settings]:
            self.central.addWidget(widget)
            widget.toHome.connect(self.open_main)
        self.setCentralWidget(self.central)
        self.mainpage.movies_button.clicked.connect(self.open_movies)
        self.mainpage.tv_button.clicked.connect(self.open_tv)
        self.mainpage.ufc_button.clicked.connect(self.open_ufc)
        self.mainpage.documentaries_button.clicked.connect(self.open_documentaries)
        self.mainpage.settings_button.clicked.connect(self.open_settings)
        self.settings.somethingChanged.connect(self.update_tables)
        self.resize(1500, 900)
    
    def update_tables(self):
        for page in [self.movies, self.tv, self.ufc, self.documentaries]:
            page.model.getData()
            page.model.refreshHeaders()
            page.table.selectRow(0)
        
        
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
    app.setStyleSheet(style())
    window = Window()
    window.show()
    app.exec()