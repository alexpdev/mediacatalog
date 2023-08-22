import random
import shutil
import subprocess
import webbrowser
from datetime import datetime

import humanfriendly
import cv2
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from mediacatalog import utils
from mediacatalog.settings import dropRow, setSetting, setting, updateField
from mediacatalog.table import ListView, TableView
from mediacatalog.utils import EPISODE, MAPPING, geticon


def reverse_mapping(field, mapping=MAPPING):
    for k, v in mapping.items():
        if field == v:
            return k
    return None


class DoubleClickLabel(QLabel):
    doubleClicked = Signal()

    def __init__(self):
        super().__init__()

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        self.doubleClicked.emit()
        return super().mouseDoubleClickEvent(event)


_tv_episode_mapping = list(utils.TV_MAPPING.items()) + list(utils.EPISODE.items())
_media_mapping = list(utils.MAPPING.items())


class MediaProfile(QWidget):
    fieldChanged = Signal(str, str)

    def __init__(self, table, mapping=_media_mapping, parent=None):
        super().__init__(parent=parent)
        self._mapping = mapping
        self._table = table
        self.images = None
        self.layout = QVBoxLayout(self)
        self.label = DoubleClickLabel()
        self.label.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding
        )
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.doubleClicked.connect(self.switchImage)
        self.label.setFixedHeight(int(self.height() * 0.45))
        self.layout.addWidget(self.label)
        self.scrollarea = QScrollArea()
        self.scrollarea.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scrollWidget = QWidget()
        self.scrollWidget.setProperty("class", "scrollBack")
        self.setContentsMargins(3, 3, 3, 3)
        self.layout.setSpacing(2)
        self.scrollarea.setWidget(self.scrollWidget)
        self.scrollarea.setWidgetResizable(True)
        self.scrolllayout = QVBoxLayout(self.scrollWidget)
        self.scrolllayout.setSpacing(2)
        self.layout.addWidget(self.scrollarea)
        self.fields = {}
        self.add_fields()

    def add_fields(self):
        fields = setting(f"{self._table}profilefields")
        for key, value in self._mapping:
            if key in ["plot", "comments"]:
                widget = FieldWidget(value, "text", self)
            else:
                widget = FieldWidget(value, "line", self)
            widget.fieldChanged.connect(self.onFieldChanged)
            widget.watchedEnabled.connect(self.onWatched)
            self.fields[key] = widget
            self.scrolllayout.addWidget(widget)
            if key not in fields:
                widget.setHidden(True)

    def section(self):
        return self._section

    def onWatched(self):
        self.fieldChanged.emit("Watched", "watched")
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
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def setCurrent(self, data):
        for k,v in self.fields.items():
            v.clear()
            v.setData(data)
        fields = setting(f"{self._table}profilefields")
        self.images = None
        if "image_cached" in data:
            self.images = data["image_cached"]
        elif "images" in data:
            self.images = data["images"]
        if self.images:
            self._current = self.images[0]
            self._currentPixmap = QPixmap(self.images[0])
            self.label.setPixmap(self._currentPixmap)
            self.label.setScaledContents(False)
            self.switchImage()
        for key, value in data.items():
            if key in self.fields:
                self.fields[key].setText(value)
        for k, v in self.fields.items():
            if k in fields:
                v.setHidden(False)
            else:
                v.setHidden(True)

    def resizeEvent(self, event):
        self.label.setFixedHeight(int(self.height() * 0.45))
        if self.images:
            self.scaleLabel()
        self.scrollWidget.setFixedWidth(self.scrollarea.viewport().width())
        super().resizeEvent(event)


class TvMediaProfile(MediaProfile):
    fieldChanged = Signal(str, str)

    def __init__(self, table="tv", mapping=_tv_episode_mapping, parent=None):
        super().__init__(table, mapping=mapping, parent=parent)


class ToolBar(QToolBar):
    somethingChanged = Signal()
    settingsPage = Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.settingsAction = QAction(geticon("settings"), "Settings", self)
        self.addAction(self.settingsAction)
        self.randomSortAction = QAction(geticon("vertical"), "Random Sort Table", self)
        self.addAction(self.randomSortAction)
        self.randomSortAction.setToolTip("Random Sort")
        left = QWidget()
        left.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        left.setFixedHeight(0)
        self.addWidget(left)
        self.filter_group = QGroupBox()
        self.filter_layout = QHBoxLayout(self.filter_group)
        self.filter_layout.setContentsMargins(2, 2, 2, 2)
        self.filter_layout.setSpacing(0)
        self.filter_group.setContentsMargins(0, 0, 0, 0)
        self.filter_toolbar = QToolBar()
        self.filter_layout.addWidget(self.filter_toolbar)
        title = QLabel("Title")
        self.filter_toolbar.addWidget(title)
        self.title_line = QLineEdit()
        self.title_line.setMaximumWidth(100)
        self.filter_toolbar.addWidget(self.title_line)
        self.filter_toolbar.addSeparator()
        self.quality = QToolButton()
        self.quality.setProperty("class", "filter")
        self.quality.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.quality.setText("Quality")
        self.filter_toolbar.addWidget(self.quality)
        self.filter_toolbar.addSeparator()
        self.genre = QToolButton()
        self.genre.setProperty("class", "filter")
        self.genre.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.genre.setText("Genre")
        self.filter_toolbar.addWidget(self.genre)
        self.filter_toolbar.addSeparator()
        self.status = QToolButton()
        self.status.setProperty("class", "filter")
        self.status.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.status.setText("Status")
        self.filter_toolbar.addWidget(self.status)
        self.filter_toolbar.addSeparator()
        self.watched = QToolButton()
        self.watched.setProperty("class", "filter")
        self.watched.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.watched.setText("Watched")
        self.filter_toolbar.addWidget(self.watched)
        self.filter_toolbar.addSeparator()
        self.rating = QToolButton()
        self.rating.setProperty("class", "filter")
        self.rating.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.rating.setText("Rating")
        self.filter_toolbar.addWidget(self.rating)
        self.filter_toolbar.addSeparator()
        folder_size = QLabel("Folder Size")
        self.filter_toolbar.addWidget(folder_size)
        self.folder_size_combo = QComboBox()
        self.folder_size_combo.setMaximumWidth(45)
        for i in [">", "<", "="]:
            self.folder_size_combo.addItem(i)
        self.filter_toolbar.addWidget(self.folder_size_combo)
        self.folder_size_value = QSpinBox()
        self.folder_size_value.setRange(0, 1000000000)
        self.filter_toolbar.addWidget(self.folder_size_value)
        self.reset = QAction("Reset")
        self.filter_toolbar.addAction(self.reset)
        self.reset.triggered.connect(self.on_reset)
        self.addWidget(self.filter_group)
        right = QWidget()
        right.setFixedHeight(0)
        right.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.addWidget(right)
        self.recent_list_action = QAction(geticon("list"), "Recently Watched", self)
        self.recent_list_action.setToolTip("Recently Watched")
        self.addAction(self.recent_list_action)
        self.delete_action = QAction(geticon("trash"), "Delete", self)
        self.addAction(self.delete_action)
        self.setupMenus()
        self.setupSignals()

    def on_reset(self):
        self.title_line.clear()
        for action in self.quality_action_group.actions():
            if action.isChecked():
                action.setChecked(False)
        for action in self.rating_action_group.actions():
            if action.isChecked():
                action.setChecked(False)
        for action in self.genre_action_group.actions():
            if action.isChecked():
                action.setChecked(False)
        for action in self.watched_action_group.actions():
            if action.isChecked():
                action.setChecked(False)
        for action in self.status_action_group.actions():
            if action.isChecked():
                action.setChecked(False)
        self.folder_size_value.setValue(0)
        self.onChange()

    def onChange(self, *args):
        self.somethingChanged.emit()

    def setupSignals(self):
        self.title_line.textChanged.connect(self.onChange)
        for action in self.quality_action_group.actions():
            action.toggled.connect(self.onChange)
        for action in self.genre_action_group.actions():
            action.toggled.connect(self.onChange)
        for action in self.watched_action_group.actions():
            action.toggled.connect(self.onChange)
        for action in self.rating_action_group.actions():
            action.toggled.connect(self.onChange)
        for action in self.status_action_group.actions():
            action.toggled.connect(self.onChange)
        self.folder_size_combo.currentTextChanged.connect(self.onChange)
        self.folder_size_value.valueChanged.connect(self.onChange)

    def gather_values(self):
        title = self.title_line.text()
        quality = [
            a.text() for a in self.quality_action_group.actions() if a.isChecked()
        ]
        rating = [a.text() for a in self.rating_action_group.actions() if a.isChecked()]
        genre = [a.text() for a in self.genre_action_group.actions() if a.isChecked()]
        watched = [
            a.text() for a in self.watched_action_group.actions() if a.isChecked()
        ]
        status = [a.text() for a in self.status_action_group.actions() if a.isChecked()]
        folder_operator = self.folder_size_combo.currentText()
        folder_size = self.folder_size_value.value()
        return {
            "title": title,
            "quality": quality,
            "rating": rating,
            "genre": genre,
            "watched": watched,
            "status": status,
            "folder_operator": folder_operator,
            "folder_size": folder_size,
        }

    def setupMenus(self):
        self.quality_menu = QMenu()
        self.quality_action_group = QActionGroup(self)
        self.quality_action_group.setExclusive(False)
        for quality in utils.QUALITY:
            action = QAction(quality, self)
            action.setCheckable(True)
            action.setChecked(False)
            self.quality_action_group.addAction(action)
            self.quality_menu.addAction(action)
        self.quality.setMenu(self.quality_menu)
        self.genre_menu = QMenu()
        self.genre_action_group = QActionGroup(self)
        self.genre_action_group.setExclusive(False)
        for genre in utils.GENRES:
            action = QAction(genre, self)
            action.setCheckable(True)
            action.setChecked(False)
            self.genre_action_group.addAction(action)
            self.genre_menu.addAction(action)
        self.genre.setMenu(self.genre_menu)
        self.rating_menu = QMenu()
        self.rating_action_group = QActionGroup(self)
        self.rating_action_group.setExclusive(False)
        for rating in [
            "0.0",
            "0.5",
            "1.0",
            "1.5",
            "2.0",
            "2.5",
            "3.0",
            "3.5",
            "4.0",
            "4.5",
            "5.0",
        ]:
            action = QAction(rating, self)
            action.setCheckable(True)
            action.setChecked(False)
            self.rating_action_group.addAction(action)
            self.rating_menu.addAction(action)
        self.rating.setMenu(self.rating_menu)
        self.watched_menu = QMenu()
        self.watched_action_group = QActionGroup(self)
        self.watched_action_group.setExclusive(False)
        for status in ["watched", "unwatched"]:
            action = QAction(status, self)
            action.setCheckable(True)
            action.setChecked(False)
            self.watched_action_group.addAction(action)
            self.watched_menu.addAction(action)
        self.watched.setMenu(self.watched_menu)
        self.status_menu = QMenu()
        self.status_action_group = QActionGroup(self)
        self.status_action_group.setExclusive(False)
        for status in utils.STATUS:
            action = QAction(status, self)
            action.setCheckable(True)
            action.setChecked(False)
            self.status_action_group.addAction(action)
            self.status_menu.addAction(action)
        self.status.setMenu(self.status_menu)


class MediaPage(QWidget):
    toHome = Signal()
    toSettings = Signal()

    def __init__(self, table, parent=None):
        super().__init__(parent=parent)
        self._table = table
        self.layout = QVBoxLayout(self)
        self.splitter2 = QSplitter(Qt.Orientation.Vertical)
        self.layout.addWidget(self.splitter2)
        self.toolbar = ToolBar(self)
        self.layout.setSpacing(2)
        self.toolbar.somethingChanged.connect(self.filter_table)
        self.toolbar.delete_action.triggered.connect(self.on_delete)
        self.toolbar.settingsAction.triggered.connect(self.go_to_settings)
        self.toolbar.randomSortAction.triggered.connect(self.random_sort_table)
        self.splitter2.addWidget(self.toolbar)
        self.widget = QWidget()
        self.splitter2.addWidget(self.widget)
        layout1 = QVBoxLayout(self.widget)
        self.splitter = QSplitter()
        layout1.addWidget(self.splitter)
        self.table = TableView(table, MAPPING)
        self.table.setColumnMenu(utils.ColumnMenu)
        self.splitter.addWidget(self.table)
        self.table.selectionModel().currentRowChanged.connect(self.onRowChanged)
        slider_size = setting(f"{table}mediaslider")
        if slider_size:
            self.splitter.setSizes(slider_size)
        slider_size = setting(f"{table}toolbarslider")
        if slider_size:
            self.splitter2.setSizes(slider_size)
        self.splitter.splitterMoved.connect(self.updateSplitterSizes)
        self.splitter2.splitterMoved.connect(self.updateSplitterSizes)
        self.add_extras()
        hlayout = QHBoxLayout()
        self.count_label = QLabel("Count: ")
        self.layout.addLayout(hlayout)
        hlayout.addWidget(self.count_label)
        self.table.rowCountChanged.connect(self.set_count_label)
        self.set_count_label()

    def set_count_label(self):
        rows = self.table.tableModel().rowCount(None)
        self.count_label.setText(f"Count: {rows}")


    def on_delete(self):
        current = self.table.selectionModel().currentIndex()
        row = self.table.model().mapToSource(current)
        data = self.table.tableModel().getRow(row)
        text = data["foldername"]
        value = QMessageBox.question(
            self,
            f"Delete {text}",
            "Are you sure?",
            QMessageBox.StandardButton.Yes,
            QMessageBox.StandardButton.No,
        )
        if value == QMessageBox.StandardButton.Yes:
            shutil.rmtree(data["folderpath"])
            dropRow(self._table, data["path"])

    def filter_table(self):
        filters = self.toolbar.gather_values()
        self.table.filter(filters)

    def add_extras(self):
        self.addMediaProfile()

    def addMediaProfile(self):
        self.mediaProfile = MediaProfile(self._table, parent=self)
        self.mediaProfile.fieldChanged.connect(self.onFieldChanged)
        self.splitter.addWidget(self.mediaProfile)
        self.table.selectRow(0)

    def onFieldChanged(self, field, value):
        current = self.table.selectionModel().currentIndex()
        row = self.table.model().mapToSource(current)
        data = self.table.tableModel().getRow(row)
        foldername = data["foldername"]
        key = reverse_mapping(field)
        updateField(self._table, foldername, key, value)
        data[key] = value
        self.table.tableModel().dataChanged.emit(row, row)

    def updateSplitterSizes(self, *args):
        setSetting(f"{self._table}mediaslider", self.splitter.sizes())
        setSetting(f"{self._table}toolbarslider", self.splitter2.sizes())

    def onRowChanged(self, current, previous):
        row = self.table.model().mapToSource(current)
        row = self.table.tableModel().getRow(row)
        self.mediaProfile.setCurrent(row)

    def go_to_settings(self):
        self.toSettings.emit()

    def random_sort_table(self):
        self.table.model().setRandom()
        i = random.choice(range(self.table.model().columnCount()))
        self.table.model().sort(i,Qt.SortOrder.AscendingOrder)
        self.table.model().setRandom()


class TvPage(QWidget):
    toHome = Signal()
    toSettings = Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.layout = QVBoxLayout(self)
        self.splitter2 = QSplitter(Qt.Orientation.Vertical)
        self.layout.addWidget(self.splitter2)
        self.toolbar = ToolBar(self)
        self.toolbar.somethingChanged.connect(self.filter_table)
        self.toolbar.settingsAction.triggered.connect(self.go_to_settings)
        self.splitter2.addWidget(self.toolbar)
        self.widget = QWidget()
        self.splitter2.addWidget(self.widget)
        layout1 = QVBoxLayout(self.widget)
        self.splitter = QSplitter()
        layout1.addWidget(self.splitter)
        self.table = TableView("tv", utils.TV_MAPPING)
        self.table.setColumnMenu(utils.TvColumnMenu)
        self.splitter.addWidget(self.table)
        self.table.selectionModel().currentRowChanged.connect(self.onRowChanged)
        slider_size = setting(f"tvmediaslider")
        if slider_size:
            self.splitter.setSizes(slider_size)
        slider_size = setting(f"tvtoolbarslider")
        if slider_size:
            self.splitter2.setSizes(slider_size)
        self.splitter.splitterMoved.connect(self.updateSplitterSizes)
        self.splitter2.splitterMoved.connect(self.updateSplitterSizes)
        self.seasons = ListView()
        self.episode_table = TableView("tv", EPISODE, fields="episode")
        self.episode_table.setColumnMenu(utils.EpisodeMenu)
        self.splitter.addWidget(self.seasons)
        self.splitter.addWidget(self.episode_table)
        self.seasons.selectionModel().currentChanged.connect(self.onSeasonSelected)
        self.episode_table.selectionModel().currentRowChanged.connect(
            self.onEpisodeSelected
        )
        self.addMediaProfile()

    def on_delete(self):
        current = self.table.selectionModel().currentIndex()
        row = self.table.model().mapToSource(current)
        data = self.table.tableModel().getRow(row)
        text = data["foldername"]
        value = QMessageBox.question(
            self,
            f"Delete {text}",
            "Are you sure?",
            QMessageBox.StandardButton.Yes,
            QMessageBox.StandardButton.No,
        )
        if value == QMessageBox.StandardButton.Yes:
            shutil.rmtree(data["folderpath"])
            dropRow(self._table, data["path"])

    def filter_table(self):
        filters = self.toolbar.gather_values()
        self.table.filter(filters)
        self.episode_table.filter(filters)

    def addMediaProfile(self):
        self.mediaProfile = TvMediaProfile("tv", parent=self)
        self.mediaProfile.fieldChanged.connect(self.onFieldChanged)
        self.splitter.addWidget(self.mediaProfile)
        self.table.selectRow(0)

    def onSeasonSelected(self, current, previous):
        row = self.table.selectionModel().selectedRows()[0]
        row = self.table.model().mapToSource(row)
        data = self.table.tableModel().getRow(row)
        season = data["seasons"][self.seasons.row(current.row())]
        season = {i["path"]: i for i in season}
        self.episode_table.tableModel().set_data(season)

    def onRowChanged(self, current, previous):
        row = self.table.tableModel().getRow(current)
        self.seasons.setSeasons(row["seasons"].keys())
        self.mediaProfile.setCurrent(row)

    def onEpisodeSelected(self, current, previous):
        row = self.episode_table.tableModel().getRow(current)
        self.mediaProfile.setCurrent(row)

    def updateSplitterSizes(self, *args):
        setSetting(f"tvmediaslider", self.splitter.sizes())
        setSetting(f"tvtoolbarslider", self.splitter2.sizes())

    def go_to_settings(self):
        self.toSettings.emit()

    def onFieldChanged(self, field, value):
        current = self.table.selectionModel().currentIndex()
        row = self.table.model().mapToSource(current)
        data = self.table.tableModel().getRow(row)
        foldername = data["foldername"]
        key = reverse_mapping(field, mapping=utils.TV_MAPPING)
        if not key:
            key = reverse_mapping(field, mapping=EPISODE)
            season_text = self.seasons.current()
            season_data = data["seasons"][season_text]
            episode = self.episode_table.selectionModel().currentIndex()
            episode_row = self.episode_table.model().mapToSource(episode)
            episode_data = self.episode_table.tableModel().getRow(episode_row)
            for record in season_data:
                if record["path"] == episode_data["path"]:
                    record[key] = value
                    episode_data[key] = value
                    break
            updateField("tv", foldername, "seasons", data["seasons"])
            self.table.tableModel().dataChanged.emit(row, row)
            self.episode_table.tableModel().dataChanged.emit(episode, episode)
        else:
            updateField("tv", foldername, key, value)
            data[key] = value
            self.table.tableModel().dataChanged.emit(row, row)


class Watched(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._parent = parent
        self.setProperty("class", "Watched")
        self.layout = QVBoxLayout(self)
        self.checkbox = QCheckBox()
        self.checkbox.setFixedWidth(15)
        self.layout.addWidget(self.checkbox)

    def clear(self):
        self.setText(False)

    def setText(self, value):
        if value in ["True", "true", True, 1, "1", "watched"]:
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
        for i in range(self._layout.count()):
            item = self._layout.takeAt(i)
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
        if text is None:
            text = 0
        if text == "None":
            text = 0
        count = float(text)
        while count > 0.5:
            label = QLabel()
            label.setPixmap(pixmap)
            self._labels.append(label)
            self._widget_layout.addWidget(label)
            count -= 1
        if count == 0.5:
            label = QLabel()
            label.setPixmap(halfpixmap)
            self._labels.append(label)
            self._widget_layout.addWidget(label)
            count -= 0.5
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

    def clear(self):
        return self.clear_layout()

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
        if isinstance(text, str):
            text = [text]
        for item in text:
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
            value = QMessageBox.question(
                self,
                self._text,
                "Add to Pinned Items?",
                QMessageBox.StandardButton.Yes,
                QMessageBox.StandardButton.No,
            )
            if value == QMessageBox.StandardButton.Yes:
                self.fieldChanged.emit("true")
            else:
                self.fieldChange.emit("false")
        elif self._text.lower() in [
            "nfo",
            "path",
            "folder name",
            "folder size",
            "episode\nnumber",
        ]:
            pass
        elif self._text.lower() in [
            "imdb",
            "title",
            "plot",
            "tag line",
            "country",
            "director",
            "year",
            "trailer",
            "studio",
            "status",
            "content\nrating",
            "comments",
            "episode\ntitle",
        ]:
            msgbox = QInputDialog.getText(
                self,
                "Edit " + self._text,
                self._text,
                QLineEdit.EchoMode.Normal,
                self._parent._value,
            )
            if msgbox and msgbox[0]:
                self.fieldChanged.emit(msgbox[0])
        elif self._text.lower() in ["premiered", "last\nviewed", "date\nadded"]:
            if self._parent.line.text():
                vals = list(map(int, self._parent.line.text().split("-")))
                date = QDate(vals[-1], vals[0], vals[1])
                msgbox = DateDialog(
                    self._text,
                    date,
                )
            else:
                msgbox = DateDialog(self._text, QDate().currentDate())
            msgbox.chosen.connect(self.setFieldChange)
            msgbox.exec()
        elif self._text.lower() == "resolution":
            result = QFileDialog.getOpenFileName(self, "Choose video file...", self._parent._data["path"], "Video File (*.mp4, *.mkv)")
            if result and result[0]:
                vid = cv2.VideoCapture(result[0])
                height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
                width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
                self._parent.setText(f"{height}x{width}")
                self.fieldChanged.emit(f"{height}x{width}")
        elif self._text.lower() in ["runtime", "play\ncount"]:
            value = self._parent.line.text()
            if not value:
                value = "0"
            msgbox = QInputDialog.getInt(
                self, "Edit " + self._text, self._text, int(value)
            )
            if msgbox and msgbox[0]:
                self.fieldChanged.emit(str(msgbox[0]))
        elif self._text.lower() in ["quality"]:
            lst = utils.QUALITY
            msgbox = QInputDialog.getItem(
                self, "Edit " + self._text, self._text, lst, 0, False
            )
            if msgbox and msgbox[0]:
                self.fieldChanged.emit(msgbox[0])
        elif self._text.lower() == "genre":
            self.open_genre_dialog(self._parent.value())
        elif self._text.lower() in ["rating", "episode\nrating"]:
            menu = QMenu()
            action_00 = QAction("0.0", self)
            menu.addAction(action_00)
            action_00.triggered.connect(lambda: self.fieldChanged.emit(str(0.0)))
            action_05 = QAction("0.5", self)
            menu.addAction(action_05)
            action_05.triggered.connect(lambda: self.fieldChanged.emit(str(0.5)))
            action_1 = QAction("1.0", self)
            menu.addAction(action_1)
            action_1.triggered.connect(lambda: self.fieldChanged.emit(str(1.0)))
            action_105 = QAction("1.5", self)
            menu.addAction(action_105)
            action_105.triggered.connect(lambda: self.fieldChanged.emit(str(1.5)))
            action_2 = QAction("2.0", self)
            menu.addAction(action_2)
            action_2.triggered.connect(lambda: self.fieldChanged.emit(str(2.0)))
            action_205 = QAction("2.5", self)
            menu.addAction(action_205)
            action_205.triggered.connect(lambda: self.fieldChanged.emit(str(2.5)))
            action_3 = QAction("3.0", self)
            menu.addAction(action_3)
            action_3.triggered.connect(lambda: self.fieldChanged.emit(str(3.0)))
            action_305 = QAction("3.5", self)
            menu.addAction(action_305)
            action_305.triggered.connect(lambda: self.fieldChanged.emit(str(3.5)))
            action_4 = QAction("4.0", self)
            menu.addAction(action_4)
            action_4.triggered.connect(lambda: self.fieldChanged.emit(str(4.0)))
            action_405 = QAction("4.5", self)
            menu.addAction(action_405)
            action_405.triggered.connect(lambda: self.fieldChanged.emit(str(4.5)))
            action_5 = QAction("5.0", self)
            menu.addAction(action_5)
            action_5.triggered.connect(lambda: self.fieldChanged.emit(str(5.0)))
            menu.exec(QCursor.pos())
        return super().mouseDoubleClickEvent(event)

    def setFieldChange(self, value):
        self.fieldChanged.emit(value)

    def open_genre_dialog(self, value):
        self.dialog = GenreDialog(value, self)
        self.dialog.genreSelected.connect(self.onGenreSelected)
        self.dialog.exec()

    def onGenreSelected(self, lst):
        self._parent.setText(lst)

    def minimumSizeHint(self):
        width = super().minimumSizeHint().width()
        height = self._parent.line.height()
        return QSize(width, height)


class GenreDialog(QDialog):
    genreSelected = Signal(list)

    def __init__(self, value, parent=None):
        super().__init__(parent=parent)
        self._value = value
        genres = setting("genres")
        layout = QVBoxLayout(self)
        self.listwidget = QListWidget()
        layout.addWidget(self.listwidget)
        self.okaybutton = QPushButton("Okay")
        self.cancelbutton = QPushButton("Cancel")
        hlayout = QHBoxLayout()
        hlayout.addWidget(self.okaybutton)
        hlayout.addWidget(self.cancelbutton)
        layout.addLayout(hlayout)
        self.okaybutton.clicked.connect(self.onOkay)
        self.cancelbutton.clicked.connect(self.onCancel)
        for genre in genres:
            checkbox = QCheckBox(genre)
            item = QListWidgetItem()
            self.listwidget.addItem(item)
            self.listwidget.setItemWidget(item, checkbox)
            if self._value:
                if genre in self._value:
                    checkbox.setChecked(True)

    def onOkay(self):
        genres = []
        for i in range(self.listwidget.count()):
            item = self.listwidget.item(i)
            widget = self.listwidget.itemWidget(item)
            if widget.isChecked():
                genres.append(widget.text())
        self.genreSelected.emit(genres)
        self.close()

    def onCancel(self):
        self.close()


class DateDialog(QDialog):
    chosen = Signal(str)

    def __init__(self, field, current, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("Edit " + field)
        self.vboxlayout = QVBoxLayout(self)
        self.dateedit = QDateEdit(current)
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


class CommandLinkButton(QCommandLinkButton):

    def __init__(self, description, parent=None):
        super().__init__(parent=parent)
        self._description = description

    def setText(self, text):
        self.setDescription(text)
        super().setText(self._description)

    def clear(self):
        self.setText("")
        self.setDescription("")

class GenreLineEdit(QLineEdit):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setReadOnly(True)
        self.setProperty("class", "GenreLine")
        self.setMaximumHeight(55)

    def setText(self, txt):
        if isinstance(txt, list):
            txt = "; ".join(txt)
        super().setText(txt)

class PinLabel(QLabel):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setMaximumHeight(55)


class FieldWidget(QWidget):
    fieldChanged = Signal(str, str)
    watchedEnabled = Signal()

    def __init__(self, field, widget="line", parent=None):
        super().__init__(parent=parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self._line = widget
        self._data = None
        self._field = field
        self.setProperty("class", "fieldWidget")
        if len(field.split()) > 1:
            field = "\n".join(field.split())
        self.label = FieldLabel(field, self)
        self.label.setProperty("class", "field")
        self.label.setFixedWidth(68)
        self.setMinimumWidth(200)
        self.label.setAlignment(
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter
        )
        self.layout = QFormLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        if self._field in ["Rating", "Episode Rating"]:
            self.line = RatingWidget(self)
        elif self._field == "Watched":
            self.line = Watched(self)
            self.line.checkbox.clicked.connect(self.watchedToggled)
        elif self._field in ["Content Rating","Genre"]:
            self.line = GenreWidget(self)
        elif self._field in ["NFO", "Trailer", "Folder"]:
            if self._field == "Trailer":
                self.line = CommandLinkButton("Open In Browser", self)
            elif self._field == "NFO":
                self.line = CommandLinkButton("Open In Notepad", self)
            else:
                self.line = CommandLinkButton("Open In Explorer", self)
            self.line.clicked.connect(self.open_path)
        elif self._field == "Pin":
            self.line = PinLabel()
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
            webbrowser.open_new_tab(self.line.description())
        else:
            subprocess.run(f"explorer.exe {self.line.description()}")

    def setData(self, data):
        self._data = data

    def setText(self, text):
        self._value = text
        if self._field == "Title" and not text:
            title = self._data["foldername"].split(" (")[0]
            self.fieldChanged.emit("Title", title)
            text = title
        if self._field == "Year" and not text:
            year = self._data["foldername"].split(" (")[1]
            self.fieldChanged.emit("Year", year)
            text = year
        if self._field == "Folder Size":
            text = humanfriendly.format_size(int(text))
        elif isinstance(text, int):
            text = str(text)
        self.line.setText(text)
        if isinstance(self.line, LineEdit):
            self.line.setCursorPosition(0)
        if self._field == "Pin":
            if text == "true":
                self.line.setPixmap(utils.getimage("pin"))
            else:
                self.line.setPixmap(QPixmap())

    def clear(self):
        if self._field == "Pin":
            self.line.setPixmap(QPixmap())
        elif self._field == "Rating":
            self.line.clearWidget()
        else:
            self.line.clear()


    def value(self):
        return self._value
