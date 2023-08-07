import json
import subprocess
import webbrowser

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *


from mediacatalog import utils
from mediacatalog.utils import MAPPING, SEASON, EPISODE
from mediacatalog.settings import setting, setSetting


class MediaProfile(QWidget):
    def __init__(self, table, parent=None):
        super().__init__(parent=parent)
        self._table = table
        self.images = None
        self.layout = QVBoxLayout(self)
        self.label = QLabel()
        self.label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setScaledContents(True)
        self.button = QPushButton(self)
        self.button.clicked.connect(self.switchImage)
        self.label.setFixedHeight(int(self.height() * .25))
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.button)
        self.scrollarea = QScrollArea()
        self.scrollarea.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scrollWidget = QWidget()
        self.setContentsMargins(5, 5, 5, 5)
        self.scrollarea.setWidget(self.scrollWidget)
        self.scrollarea.setWidgetResizable(True)
        self.scrolllayout = QVBoxLayout(self.scrollWidget)
        self.button = QPushButton()
        self.layout.addWidget(self.scrollarea)
        self.fields = {}
        for key, value in MAPPING.items():
            if key in ["plot", "comments"]:
                widget = FieldWidget(value, "text", self)
            else:
                widget = FieldWidget(value, "line", self)
            self.fields[key] = widget
            self.scrolllayout.addWidget(widget)

    def switchImage(self):
        if self.images:
            index = self.images.index(self._current)
            if index + 1 < len(self.images):
                self._current = self.images[index+1]
                self._currentPixmap = QPixmap(self._current)
            else:
                self._current   =  self.images[0]
                self._currentPixmap = QPixmap(self._current)
            # self.label.setPixmap(self._currentPixmap)
            self.scaleLabel()

    def scaleLabel(self):
        self.label.setPixmap(self._currentPixmap.scaled(self.label.width(), self.label.height(), Qt.AspectRatioMode.KeepAspectRatio))

    def setCurrent(self, data):
        fields = json.loads(setting(self._table + "profilefields"))
        self.images = data["images"]
        if self.images:
            self._current = self.images[0]
            self._currentPixmap = QPixmap(self.images[0])
            self.label.setPixmap(self._currentPixmap)
        for key, value in data.items():
            if key in self.fields:
                self.fields[key].setText(value)
                if key not in fields:
                    self.fields[key].hide()
                else:
                    self.fields[key].show()

    def resizeEvent(self, event):
        self.label.setFixedHeight(int(self.height() * .25))
        if self.images:
            self.scaleLabel()
        super().resizeEvent(event)

    def setCurrentSeason(self, data):
        print(data)
        pass

    def setCurrentEpisode(self, data):
        print(data)
        pass



class MediaPage(QWidget):
    toHome = Signal()

    def __init__(self, db, table, parent=None):
        super().__init__(parent=parent)
        self.db = db
        self._table = table
        self.layout = QVBoxLayout(self)
        self.splitter = QSplitter()
        self.layout.addWidget(self.splitter)
        self.table = TableView(db, table, MAPPING)
        self.table.setColumnMenu(utils.ColumnMenu)
        self.splitter.addWidget(self.table)
        self.table.selectionModel().currentRowChanged.connect(self.onRowChanged)
        self.splitter.splitterMoved.connect(self.updateSplitterSizes)
        self.splitter.setSizes(json.loads(setting("splittersize")))
        self.add_extras()

    def add_extras(self):
        self.addMediaProfile()

    def addMediaProfile(self):
        self.mediaProfile = MediaProfile(self._table, self)
        self.splitter.addWidget(self.mediaProfile)
        self.table.selectRow(0)

    def updateSplitterSizes(self, *args):
        setSetting("splittersize", json.dumps(args))

    def onRowChanged(self, current, previous):
        row = self.table.model().mapToSource(current)
        row = self.table.tableModel().getRow(row)
        self.mediaProfile.setCurrent(row)


class TableView(QTableView):
    def __init__(self, db, table, mapping, fields=None, parent=None):
        super().__init__(parent=parent)
        self._table = table
        self._fields = fields if fields is not None else table
        self._model = SqlTableModel(db, self._table, mapping, fields=fields)
        self._proxy_model = QSortFilterProxyModel()
        self.setModel(self._proxy_model)
        self._proxy_model.setSourceModel(self._model)
        self._proxy_model.setDynamicSortFilter(True)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.horizontalHeader().setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.horizontalHeader().customContextMenuRequested.connect(
            self.selectVisibleColumns
        )
        self.setSortingEnabled(True)
        self.columnMenu = None
        self.labels = json.loads(setting(self._fields + "columnfields"))

    def setColumnMenu(self, menu):
        self.columnMenu = menu()
        self.columnMenu.setCheckedItems(self.labels)

    def toggleColumnHeader(self, key):
        if key in self.labels:
            self.labels.remove(key)
        else:
            self.labels.append(key)
        setSetting(self._fields + "columnfields", json.dumps(self.labels))
        self._model.refreshHeaders()

    def selectVisibleColumns(self, point):
        self.columnMenu.menuItemToggled.connect(self.toggleColumnHeader)
        self.columnMenu.popup(self.mapToGlobal(point))

    def tableModel(self):
        return self._model


class TvPage(MediaPage):
    def __init__(self, db, table, parent=None):
        super().__init__(db, table, parent=parent)
        self.season_table = TableView(db, table, SEASON, fields="season")
        self.season_table.setColumnMenu(utils.SeasonMenu)
        self.episode_table = TableView(db, table, EPISODE, fields="episode")
        self.episode_table.setColumnMenu(utils.EpisodeMenu)
        self.splitter.addWidget(self.season_table)
        self.splitter.addWidget(self.episode_table)
        self.season_table.selectionModel().currentRowChanged.connect(
            self.onSeasonSelected
        )
        self.episode_table.selectionModel().currentRowChanged.connect(
            self.onEpisodeSelected
        )
        self.addMediaProfile()

    def add_extras(self):
        pass

    def onSeasonSelected(self, current, previous):
        row = self.season_table.tableModel().getRow(current)
        self.mediaProfile.setCurrentSeason(row)
        self.episode_table.tableModel().set_data(row["episodes"])

    def onRowChanged(self, current, previous):
        row = self.table.tableModel().getRow(current)
        self.mediaProfile.setCurrent(row)
        self.season_table.tableModel().set_data(row["seasons"])

    def onEpisodeSelected(self, current, previous):
        row = self.episode_table.tableModel().getRow(current)
        self.mediaProfile.setCurrentEpisode(row)


class SqlTableModel(QAbstractTableModel):
    def __init__(self, db, table, mapping, fields=None, parent=None):
        super().__init__(parent=parent)
        self._table = table
        self._fields = fields if fields is not None else self._table
        self._mapping = mapping
        self._db = db
        self._reverse = {v: k for k, v in mapping.items()}
        self._headers_labels = None
        self._headers = None
        self._data = []
        self.refreshHeaders()
        if fields is None:
            self.getData()

    def clearRows(self):
        rows = self.rowCount(QModelIndex()) - 1
        while rows >= 0:
            self.removeRow(rows, QModelIndex())
            rows -= 1
        return

    def set_data(self, data):
        self.clearRows()
        for fullpath, record in data.items():
            record["Path"] = fullpath
            self.insertRow(self.rowCount(QModelIndex), record, QModelIndex())

    def removeRow(self, row, parent=QModelIndex()):
        self.beginRemoveRows(parent, row, row)
        del self._data[row]
        self.endRemoveRows()

    def insertRow(self, row, value, parent=QModelIndex()):
        self.beginInsertRows(parent, row, row)
        self._data.insert(row, value)
        self.endInsertRows()

    def getRow(self, index):
        return self._data[index.row()]

    def refreshHeaders(self):
        headers_labels = json.loads(setting(self._fields + "columnfields"))
        if self._headers_labels is None:
            self._headers_labels = headers_labels
            self._headers = [self._mapping[i] for i in self._headers_labels]
        elif len(headers_labels) < len(self._headers_labels):
            idxs = [i for i in range(len(self._headers_labels)) if self._headers_labels[i] not in headers_labels]
            for idx in idxs:
                self.removeColumn(idx, QModelIndex())
        elif len(headers_labels) > len(self._headers_labels):
            idxs = [i for i in range(len(headers_labels)) if headers_labels[i] not in self._headers_labels]
            for idx in idxs:
                self.insertColumn(idx, headers_labels[idx], QModelIndex())

    def getData(self):
        self._data = []
        data = self._db.getData(self._table)
        for record in data:
            path, foldername, data = record
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

    def removeColumn(self, column, parent=QModelIndex()):
        self.beginRemoveColumns(parent, column, column)
        del self._headers[column]
        del self._headers_labels[column]
        self.endRemoveColumns()

    def insertColumn(self, column, value, parent=QModelIndex()):
        self.beginRemoveColumns(parent, column, column)
        self._headers_labels.insert(column, value)
        self._headers.insert(column, self._mapping[value])
        self.endRemoveColumns()


class LineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._parent = parent
        self.setReadOnly(True)
        self.setProperty("class", "fieldedit")

    def minimumSizeHint(self):
        return self.sizeHint()

    def sizeHint(self):
        size = super().sizeHint()
        return QSize(size.width(), self._parent.height())


class RatingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._parent = parent
        self.layout = QHBoxLayout(self)
        self.labels = []

    def setText(self, text):
        current = len(self.labels)
        if int(text) < current:
            for _ in range(current - int(text)):
                self.labels[0].deleteLater()
                del self.labels[0]
        elif int(text) > current:
            for _ in range(int(text) - current):
                label = QLabel()
                pix = QPixmap(utils.getimage("star")).scaledToHeight(self._parent.height())
                label.setPixmap(pix)
                self.labels.append(label)
                self.layout.addWidget(label)


class PlainTextEdit(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._parent = parent
        self.setReadOnly(True)
        self.setProperty("class", "fieldtextedit")

    def text(self):
        return self.toPlainText()

    def setText(self, text):
        self.setPlainText(text)

class GenreWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setProperty("class", "genreWidget")
        self.hlayout = QHBoxLayout(self)
        self.setContentsMargins(0,0,0,0)
        self.hlayout.setContentsMargins(0,0,0,0)
        self.hlayout.setSpacing(0)
        self.labels = []

    def setText(self, text):
        total_labels = len(self.labels) - 1
        while total_labels >= 0:
            label = self.labels[total_labels]
            label.deleteLater()
            self.labels.remove(label)
            total_labels -= 1
        for item in text.split(";"):
            label = QLabel(item)
            label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
            label.setProperty("class", "genre")
            self.hlayout.addWidget(label)
            self.labels.append(label)

class FieldLabel(QLabel):
    fieldChanged = Signal(str)
    def __init__(self, text, parent=None):
        super().__init__(text, parent=parent)
        self._text = text
        self._parent = parent



    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        msgbox = QInputDialog.getText(self, "Edit " + self._text, self._text, QLineEdit.EchoMode.Normal, self._parent._value)
        print(msgbox)
        if msgbox and msgbox[0]:
            self.fieldChanged.emit(msgbox[0])
        return super().mouseDoubleClickEvent(event)



class FieldWidget(QWidget):
    def __init__(self, field, widget="line", parent=None):
        super().__init__(parent=parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self._line = widget
        self._field = field
        self.setProperty("class", "fieldWidget")
        if len(field.split()) > 1:
            field = "\n".join(field.split())
        self.label = FieldLabel(field, self)
        self.label.setProperty("class", "field")
        self.label.setFixedWidth(68)
        print(field)
        self.label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.layout = QFormLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        if self._field == "Rating":
            self.line = RatingWidget(self)
        elif self._field in ["Genre", "Content Rating"]:
            self.line = GenreWidget(self)
        elif self._field in ["NFO Path", "Trailer", "Folder Path"]:
            self.line = QCommandLinkButton(self)
            self.line.clicked.connect(self.open_path)
        elif widget == "line":
            self.line = LineEdit(self)
        elif widget == "text":
            self.line = PlainTextEdit(self)
        self._value = None
        self.layout.addRow(self.label, self.line)
        self.label.fieldChanged.connect(self.setText)

    def open_path(self):
        if self._field == "Trailer":
            webbrowser.open_new_tab(self.line.text())
        else:
            subprocess.run(f"explorer.exe {self.line.text()}")

    def setText(self, text):
        self._value = text
        self.line.setText(str(text))
