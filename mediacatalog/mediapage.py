import json
import subprocess
import webbrowser

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *


from mediacatalog import utils
from mediacatalog.utils import MAPPING, SEASON, EPISODE
from mediacatalog.settings import setting, setSetting, updateField, getData


def reverse_mapping(field):
    for k, v in MAPPING.items():
        if field == v:
            return k


class MediaProfile(QWidget):
    fieldChanged = Signal(str, str)

    def __init__(self, table, parent=None):
        super().__init__(parent=parent)
        self._table = table
        self.images = None
        self.layout = QVBoxLayout(self)
        self.label = QLabel()
        self.label.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding
        )
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setScaledContents(True)
        self.button = QPushButton(self)
        self.button.clicked.connect(self.switchImage)
        self.label.setFixedHeight(int(self.height() * 0.25))
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
            widget.fieldChanged.connect(self.onFieldChanged)
            self.fields[key] = widget
            self.scrolllayout.addWidget(widget)

    def onFieldChanged(self, field, value):
        self.fieldChanged.emit(field, value)

    def switchImage(self):
        if self.images:
            index = self.images.index(self._current)
            if index + 1 < len(self.images):
                self._current = self.images[index + 1]
                self._currentPixmap = QPixmap(self._current)
            else:
                self._current = self.images[0]
                self._currentPixmap = QPixmap(self._current)
            # self.label.setPixmap(self._currentPixmap)
            self.scaleLabel()

    def scaleLabel(self):
        self.label.setPixmap(
            self._currentPixmap.scaled(
                self.label.width(),
                self.label.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
            )
        )

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
        self.label.setFixedHeight(int(self.height() * 0.25))
        if self.images:
            self.scaleLabel()
        self.scrollWidget.setFixedWidth(self.scrollarea.viewport().width())
        super().resizeEvent(event)

    def setCurrentSeason(self, data):
        print(data)
        pass

    def setCurrentEpisode(self, data):
        print(data)
        pass


class MediaPage(QWidget):
    toHome = Signal()

    def __init__(self, table, parent=None):
        super().__init__(parent=parent)
        self._table = table
        self.layout = QVBoxLayout(self)
        self.splitter = QSplitter()
        self.layout.addWidget(self.splitter)
        self.table = TableView(table, MAPPING)
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
        self.mediaProfile.fieldChanged.connect(self.onFieldChanged)
        self.splitter.addWidget(self.mediaProfile)
        self.table.selectRow(0)

    def onFieldChanged(self, field, value):
        current = self.table.selectionModel().selectedRows()[0]
        row = self.table.model().mapToSource(current)
        data = self.table.tableModel().getRow(row)
        foldername = data["foldername"]
        key = reverse_mapping(field)
        updateField(self._table, foldername, key, value)
        data[key] = value
        self.table.tableModel().dataChanged.emit(row, row)

    def updateSplitterSizes(self, *args):
        setSetting("splittersize", json.dumps(args))

    def onRowChanged(self, current, previous):
        row = self.table.model().mapToSource(current)
        row = self.table.tableModel().getRow(row)
        self.mediaProfile.setCurrent(row)


class TableView(QTableView):
    def __init__(self, table, mapping, fields=None, parent=None):
        super().__init__(parent=parent)
        self._table = table
        self._fields = fields if fields is not None else table
        self._model = SqlTableModel(self._table, mapping, fields=fields)
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
    def __init__(self, table, parent=None):
        super().__init__(table, parent=parent)
        self.season_table = TableView(table, SEASON, fields="season")
        self.season_table.setColumnMenu(utils.SeasonMenu)
        self.episode_table = TableView(table, EPISODE, fields="episode")
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
    def __init__(self, table, mapping, fields=None, parent=None):
        super().__init__(parent=parent)
        self._table = table
        self._fields = fields if fields is not None else self._table
        self._mapping = mapping
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
            idxs = [
                i
                for i in range(len(self._headers_labels))
                if self._headers_labels[i] not in headers_labels
            ]
            for idx in idxs:
                self.removeColumn(idx, QModelIndex())
        elif len(headers_labels) > len(self._headers_labels):
            idxs = [
                i
                for i in range(len(headers_labels))
                if headers_labels[i] not in self._headers_labels
            ]
            for idx in idxs:
                self.insertColumn(idx, headers_labels[idx], QModelIndex())

    def getData(self):
        self.clearRows()
        data = getData(self._table)
        for record in data:
            path, foldername, data = record
            data = json.loads(data)
            self.insertRow(self.rowCount(QModelIndex()), data, QModelIndex())

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


class Watched(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setProperty("class", "Watched")
        self.layout = QVBoxLayout(self)
        self.checkbox = QCheckBox()
        self.checkbox.setFixedWidth(15)
        self.layout.addWidget(self.checkbox)

    def setText(self, value):
        if value in ["True", "true", True, 1, "1"]:
            self.checkbox.setChecked(True)
        else:
            self.checkbox.setChecked(False)

    def minimumSizeHint(self):
        return self.checkbox.size()


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
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setProperty("class", "ratingWidget")
        self._parent = parent
        self.setFixedHeight(30)
        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._widget = QWidget()
        self._widget_layout = None
        self._layout.addWidget(self._widget)
        self._labels = []

    def clearWidget(self):
        for item in range(self._layout.count()):
            if item and item.widget():
                item.widget().deleteLater()
        if self._widget_layout is not None:
            for i in range(self._widget_layout.count()):
                item = self._widget_layout.takeAt(i)
                if item and item.widget():
                    item.widget().deleteLater()
        self._widget.deleteLater()
        self._labels = []

    def setText(self, text):
        self.clearWidget()
        self._widget = QWidget()
        self._widget_layout = QHBoxLayout(self._widget)
        self._widget_layout.setContentsMargins(0, 0, 0, 0)
        self._widget_layout.setSpacing(0)
        pixmap = QPixmap(utils.getimage("star")).scaledToHeight(30)
        for _ in range(int(text)):
            label = QLabel()
            label.setPixmap(pixmap)
            self._labels.append(label)
            self._widget_layout.addWidget(label)
        self._widget_layout.addStretch(1)
        self._layout.addWidget(self._widget)


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
        self.setFixedHeight(35)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setProperty("class", "genreWidget")
        self.setContentsMargins(0, 0, 0, 0)
        self._layout = QHBoxLayout(self)
        self._labels = []
        self._widget_layout = None
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

    def clear_layout(self):
        for layout in [self._layout, self._widget_layout]:
            if layout is None:
                continue
            for i in range(self._layout.count()):
                item = self._layout.takeAt(i)
                if item and item.widget():
                    item.widget().deleteLater()
        self._labels = []

    def setText(self, text):
        self.clear_layout()
        self._widget = QWidget()
        self._widget_layout = QHBoxLayout(self._widget)
        self._widget_layout.setContentsMargins(0, 0, 0, 0)
        self._widget_layout.setSpacing(0)
        for item in text.split(";"):
            label = QLabel(item)
            label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
            label.setProperty("class", "genre")
            self._widget_layout.addWidget(label)
            self._labels.append(label)
        self._widget_layout.addStretch(1)
        self._layout.addWidget(self._widget)


class FieldLabel(QLabel):
    fieldChanged = Signal(str)

    def __init__(self, text, parent=None):
        super().__init__(text, parent=parent)
        self._text = text
        self._parent = parent

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        msgbox = QInputDialog.getText(
            self,
            "Edit " + self._text,
            self._text,
            QLineEdit.EchoMode.Normal,
            self._parent._value,
        )
        if msgbox and msgbox[0]:
            self.fieldChanged.emit(msgbox[0])
        return super().mouseDoubleClickEvent(event)


class FieldWidget(QWidget):
    fieldChanged = Signal(str, str)

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
        self.label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.layout = QFormLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        if self._field == "Rating":
            self.line = RatingWidget(self)
        elif self._field == "Watched":
            self.line = Watched(self)
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
        self.label.fieldChanged.connect(self.onFieldChanged)

    def onFieldChanged(self, text):
        self.setText(text)
        self.fieldChanged.emit(self._field, text)

    def open_path(self):
        if self._field == "Trailer":
            webbrowser.open_new_tab(self.line.text())
        else:
            subprocess.run(f"explorer.exe {self.line.text()}")

    def setText(self, text):
        self._value = text
        self.line.setText(str(text))
