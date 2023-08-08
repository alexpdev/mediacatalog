import json
import subprocess
from datetime import datetime
import webbrowser

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *


from mediacatalog import utils
from mediacatalog.utils import MAPPING, SEASON, EPISODE
from mediacatalog.table import TableView
from mediacatalog.settings import setting, setSetting, updateField


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
        self.scrollWidget.setProperty("class", "scrollBack")
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
            widget.watchedEnabled.connect(self.onWatched)
            self.fields[key] = widget
            self.scrolllayout.addWidget(widget)

    def onWatched(self):
        self.fieldChanged.emit("Watched", "true")
        self.fieldChanged.emit("Play Count", "1")
        self.fieldChanged.emit("Last Viewed", datetime.today().strftime("%m-%d-%Y"))

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
            self.scaleLabel()

    def scaleLabel(self):
        self.label.setPixmap(
            self._currentPixmap.scaled(
                self.label.width(),
                self.label.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
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
        pass

    def setCurrentEpisode(self, data):
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




class Watched(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._parent = parent
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
        halfpixmap = QPixmap(utils.getimage("halfstar")).scaledToHeight(30)
        count = float(text)
        while count > .5:
            label = QLabel()
            label.setPixmap(pixmap)
            self._labels.append(label)
            self._widget_layout.addWidget(label)
            count -= 1
        if count == .5:
            label = QLabel()
            label.setPixmap(halfpixmap)
            self._labels.append(label)
            self._widget_layout.addWidget(label)
            count -= .5
        self._widget_layout.addStretch(1)
        self._layout.addWidget(self._widget)


class PlainTextEdit(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._parent = parent
        self.setReadOnly(True)
        self.setMaximumHeight(65)
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
        if self._text.lower() in ["pin"]:
            value = QMessageBox.question(self, self._text, "Add to Pinned Items?", QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.No)
            if value == QMessageBox.StandardButton.Yes:
                self.fieldChanged.emit("true")
            else:
                self.fieldChange.emit("false")
        elif self._text.lower() in [ "season", "episode",  "nfo", "path", "folder name", "folder size"]:
            pass
        elif self._text.lower() in ["imdb", "title", "plot", "tag line","country", "director", "year", "trailer", "studio", "status", "content\nrating", "comments"]:
            msgbox = QInputDialog.getText(
                self,
                "Edit " + self._text,
                self._text,
                QLineEdit.EchoMode.Normal,
                self._parent._value,
            )
            if msgbox and msgbox[0]:
                self.fieldChanged.emit(msgbox[0])
        elif self._text.lower() in ["premiered",  "last\nviewed", "date\nadded"]:
            msgbox = DateDialog(self._text, self._parent.line.text())
            msgbox.chosen.connect(self.setFieldChange)
            msgbox.exec()
        elif self._text.lower() in ["runtime", "play\ncount"]:
            msgbox = QInputDialog.getInt(self, "Edit " + self._text, self._text, int(self._parent.line.text()))
            if msgbox and msgbox[0]:
                self.fieldChanged.emit(msgbox[0])
        elif self._text.lower() in ["quality"]:
            lst = utils.QUALITY.values()
            msgbox = QInputDialog.getItem(self, "Edit " + self._text, self._text, lst, 0, False)
            if msgbox and msgbox[0]:
                for k,v in utils.QUALITY.items():
                    if msgbox[0] == v:
                        self.fieldChanged.emit(k)
                        break
        elif self._text.lower() == "rating":
            menu = QMenu()
            action_05 = QAction(".5", self)
            menu.addAction(action_05)
            action_05.triggered.connect(lambda: self.fieldChanged.emit(str(.5)))
            action_1 = QAction("1", self)
            menu.addAction(action_1)
            action_1.triggered.connect(lambda: self.fieldChanged.emit(str(1)))
            action_105 = QAction("1.5", self)
            menu.addAction(action_105)
            action_105.triggered.connect(lambda: self.fieldChanged.emit(str(1.5)))
            action_2 = QAction("2", self)
            menu.addAction(action_2)
            action_2.triggered.connect(lambda: self.fieldChanged.emit(str(2)))
            action_205 = QAction("2.5", self)
            menu.addAction(action_205)
            action_205.triggered.connect(lambda: self.fieldChanged.emit(str(2.5)))
            action_3 = QAction("3", self)
            menu.addAction(action_3)
            action_3.triggered.connect(lambda: self.fieldChanged.emit(str(3)))
            action_305 = QAction("3.5", self)
            menu.addAction(action_305)
            action_305.triggered.connect(lambda: self.fieldChanged.emit(str(3.5)))
            action_4 = QAction("4", self)
            menu.addAction(action_4)
            action_4.triggered.connect(lambda: self.fieldChanged.emit(str(4)))
            action_405 = QAction("4.5", self)
            menu.addAction(action_405)
            action_405.triggered.connect(lambda: self.fieldChanged.emit(str(4.5)))
            action_5 = QAction("5", self)
            menu.addAction(action_5)
            action_5.triggered.connect(lambda: self.fieldChanged.emit(str(5)))
            menu.exec(QCursor.pos())

        return super().mouseDoubleClickEvent(event)

    def setFieldChange(self, value):
        print(value, type(value))
        self.fieldChanged.emit(value)

class DateDialog(QDialog):
    chosen = Signal(str)

    def __init__(self, field, current, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("Edit " +  field)
        self.vboxlayout = QVBoxLayout(self)
        self.dateedit = QDateEdit()
        self.label = QLabel(field)
        self.formlayout = QFormLayout()
        self.formlayout.addRow(field, self.dateedit)
        self.button = QPushButton("Ok", self)
        self.vboxlayout.addLayout(self.formlayout)
        self.vboxlayout.addWidget(self.button)
        self.button.clicked.connect(self.submit)

    def submit(self):
        date = self.dateedit.date().toPython()
        output = date.strftime("%m-%d-%Y")
        self.chosen.emit(output)
        self.done(1)


class FieldWidget(QWidget):
    fieldChanged = Signal(str, str)
    watchedEnabled = Signal()

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
            self.line.checkbox.clicked.connect(self.watchedToggled)
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

    def watchedToggled(self):
        if self.line.checkbox.isChecked():
            self.watchedEnabled.emit()

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
        if isinstance(self.line, LineEdit):
            self.line.setCursorPosition(0)
