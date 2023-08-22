import os
import sys
from datetime import datetime
from pathlib import Path

import parsel
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

PARENT = Path(__file__).parent.parent
ASSETS = PARENT / "assets"
if "MEI" in str(PARENT):
    LOCAL = Path(sys.executable).parent
else:
    LOCAL = PARENT


def getfile(text):
    path = ASSETS / text
    if os.path.exists(path):
        return str(path)
    return str(ASSETS / (text + ".png"))


def getimage(text):
    return QPixmap(getfile(text))


def geticon(text):
    return QIcon(getimage(text))


EPISODE = {
    "watched": "Watched",
    "episodetitle": "Episode Title",
    "episodenumber": "Episode Number",
    "episoderating": "Episode Rating",
    "playcount": "Play Count",
    "lastviewed": "Last Viewed",
    "dateadded": "Date Added",
    "resolution": "Resolution",
    "pin": "Pin",
}

TV_MAPPING = {
    "title": "Title",
    "plot": "Plot",
    "runtime": "Runtime",
    "userrating": "Rating",
    "tagline": "Tag Line",
    "mpaa": "Content Rating",
    "imdb": "IMDB",
    "genre": "Genre",
    "country": "Country",
    "premiered": "Premiered",
    "year": "Year",
    "trailer": "Trailer",
    "studio": "Studio",
    "status": "Status",
    "comments": "Comments",
    "nfopath": "NFO",
    "path": "Folder",
    "foldername": "Folder Name",
    "foldersize": "Folder Size",
}

MAPPING = {
    "watched": "Watched",
    "title": "Title",
    "plot": "Plot",
    "runtime": "Runtime",
    "userrating": "Rating",
    "tagline": "Tag Line",
    "mpaa": "Content Rating",
    "playcount": "Play Count",
    "imdb": "IMDB",
    "genre": "Genre",
    "country": "Country",
    "director": "Director",
    "premiered": "Premiered",
    "year": "Year",
    "trailer": "Trailer",
    "studio": "Studio",
    "dateadded": "Date Added",
    "status": "Status",
    "comments": "Comments",
    "quality": "Quality",
    "nfopath": "NFO",
    "path": "Folder",
    "foldername": "Folder Name",
    "foldersize": "Folder Size",
    "lastviewed": "Last Viewed",
    "pin": "Pin",
    "resolution": "Resolution"
}

STATUS = [
    "Active",
    "Deleted",
    "New",
]

RATING = ["0.0", "0.5", "1.0", "1.5", "2.0", "2.5", "3.0", "3.5", "4.0", "4.5", "5.0"]

GENRES = [
    "Action",
    "Adventure",
    "Animation",
    "Anime",
    "Apocalypse / Survival",
    "Biography",
    "Comedy",
    "Crime",
    "Dance",
    "Dark Comedy",
    "Documentary",
    "Drama",
    "Family",
    "Fantasy",
    "Foreign",
    "Found Footage",
    "Games",
    "Gore / Torture",
    "Hip-Hop",
    "History",
    "Horror",
    "Indie",
    "Money & Power",
    "Mystery",
    "Romance",
    "Sci-Fi",
    "Social Commentary",
    "Special Interest",
    "Suspense",
    "Thriller",
    "War",
    "Zombies",
    "Natalie",
    "(TV) Poker",
    "(TV) Competition",
    "(TV) Ended + All Eps",
    "(TV) Can be deleted",
    "",
]

QUALITY = [
    "[WQ] Worst Quality",
    "[LQ] Low Quality",
    "[SQ] Standard Quality",
    "[HQ] High Quality (~720P)",
    "[BQ] Best Quality (>= 1080p)",
    "[TB] Too Big for Quality",
    "[NU] Needs Upgrade",
    "[MSU] Missing Subs",
    "[HCS] Hard Coded Subs",
    "[BFF] Bad File Format",
    "[WL] Wrong Language",
    "[SYNC] Off Sync",
]


def nfo_to_dict(content):
    record = {}
    selector = parsel.Selector(content)
    record["title"] = selector.xpath("//title/text()").get()
    record["plot"] = selector.xpath("//plot/text()").get()
    record["runtime"] = selector.xpath("//runtime/text()").get()
    record["userrating"] = selector.xpath("//userrating/text()").get()
    record["tagline"] = selector.xpath("//tagline/text()").get()
    record["mpaa"] = selector.xpath("//mpaa/text()").get()
    record["playcount"] = selector.xpath("//playcount/text()").get()
    record["imdb"] = selector.xpath("//uniqueid[@type='imdb']/text()").get()
    record["genre"] = list(set(selector.xpath("//genre/text()").getall()))
    record["country"] = selector.xpath("//country/text()").get()
    record["director"] = selector.xpath("//director/text()").get()
    record["premiered"] = selector.xpath("//premiered/text()").get()
    record["year"] = selector.xpath("//year/text()").get()
    record["trailer"] = selector.xpath("//trailer/text()").get()
    record["studio"] = selector.xpath("//studio/text()").get()
    record["dateadded"] = selector.xpath("//dateadded/text()").get()
    record["status"] = selector.xpath("//status/text()").get()
    record["resolution"] = ""
    record["lastviewed"] = ""
    record["comments"] = ""
    record["quality"] = ""
    record["watched"] = "unwatched"
    record["pin"] = ""
    if record["runtime"] is None:
        record["runtime"] = 0
    if record["status"] is None:
        record["status"] = "Active"
    if record["userrating"] is None:
        record["userrating"] = 0.0
    if record["playcount"] is None:
        record["playcount"] = 0
    if record["dateadded"] is None:
        record["dateadded"] = datetime.today().strftime("%m-%d-%Y")
    if record["lastviewed"] == None:
        record["lastviewed"] = ""
    return record


def tv_nfo_to_dict(content):
    record = {}
    selector = parsel.Selector(content)
    record["title"] = selector.xpath("//title/text()").get()
    record["plot"] = selector.xpath("//plot/text()").get()
    record["runtime"] = selector.xpath("//runtime/text()").get()
    record["userrating"] = selector.xpath("//userrating/text()").get()
    record["tagline"] = selector.xpath("//tagline/text()").get()
    record["mpaa"] = selector.xpath("//mpaa/text()").get()
    record["imdb"] = selector.xpath("//uniqueid[@type='imdb']/text()").get()
    record["genre"] = list(set(selector.xpath("//genre/text()").getall()))
    record["country"] = selector.xpath("//country/text()").get()
    record["premiered"] = selector.xpath("//premiered/text()").get()
    record["year"] = selector.xpath("//year/text()").get()
    record["trailer"] = selector.xpath("//trailer/text()").get()
    record["studio"] = selector.xpath("//studio/text()").get()
    record["status"] = selector.xpath("//status/text()").get()
    record["comments"] = ""
    record["resolution"] = ""
    if record["runtime"] is None:
        record["runtime"] = 0
    if record["status"] is None:
        record["status"] = "Active"
    if record["userrating"] is None:
        record["userrating"] = 0.0
    return record


class FlowLayout(QLayout):
    def __init__(self, parent=None):
        super().__init__(parent)
        if parent is not None:
            self.setContentsMargins(QMargins(0, 0, 0, 0))
        self._item_list = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self._item_list.append(item)

    def count(self):
        return len(self._item_list)

    def itemAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self._do_layout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._item_list:
            size = size.expandedTo(item.minimumSize())
        size += QSize(
            2 * self.contentsMargins().top(), 2 * self.contentsMargins().top()
        )
        return size

    def _do_layout(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self.spacing()
        for item in self._item_list:
            style = item.widget().style()
            layout_spacing_x = style.layoutSpacing(
                QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Horizontal
            )
            layout_spacing_y = style.layoutSpacing(
                QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Vertical
            )
            space_x = spacing + layout_spacing_x
            space_y = spacing + layout_spacing_y
            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0
            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            x = next_x
            line_height = max(line_height, item.sizeHint().height())
        return y + line_height - rect.y()


class EpisodeMenu(QMenu):
    menuItemToggled = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.title_action = QAction("Episode Title")
        self.title_action.setCheckable(True)
        self.addAction(self.title_action)
        self.title_action.toggled.connect(lambda: self.columnToggled("Episode Title"))
        self.number_action = QAction("Episode Number")
        self.number_action.setCheckable(True)
        self.addAction(self.number_action)
        self.number_action.toggled.connect(lambda: self.columnToggled("Episode Number"))
        self.rating_action = QAction("Episode Rating")
        self.rating_action.setCheckable(True)
        self.addAction(self.rating_action)
        self.rating_action.toggled.connect(lambda: self.columnToggled("Episode Rating"))
        self.playcount_action = QAction("Play Count")
        self.playcount_action.setCheckable(True)
        self.addAction(self.playcount_action)
        self.playcount_action.toggled.connect(lambda: self.columnToggled("Play Count"))
        self.lastviewed_action = QAction("Last Viewed")
        self.addAction(self.lastviewed_action)
        self.lastviewed_action.setCheckable(True)
        self.lastviewed_action.toggled.connect(
            lambda: self.columnToggled("Last Viewed")
        )
        self.watched_action = QAction("Watched")
        self.addAction(self.watched_action)
        self.watched_action.setCheckable(True)
        self.watched_action.toggled.connect(lambda: self.columnToggled("Watched"))
        self.dateadded_action = QAction("Date Added")
        self.addAction(self.dateadded_action)
        self.dateadded_action.setCheckable(True)
        self.dateadded_action.toggled.connect(lambda: self.columnToggled("Date Added"))
        self.resolution_action = QAction("Resolution")
        self.addAction(self.resolution_action)
        self.resolution_action.setCheckable(True)
        self.resolution_action.toggled.connect(lambda: self.columnToggled("Resolution"))
        self.pin_action = QAction("Pin")
        self.addAction(self.pin_action)
        self.pin_action.setCheckable(True)
        self.pin_action.toggled.connect(lambda: self.columnToggled("Pin"))
        self._reverse = {val: key for key, val in EPISODE.items()}

    def columnToggled(self, text):
        # key = self._reverse[text]
        self.menuItemToggled.emit(text)

    def setCheckedItems(self, lst):
        for action in self.actions():
            key = self._reverse[action.text()]
            if key in lst:
                action.setChecked(True)


class ColumnMenu(QMenu):
    menuItemToggled = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.watched_action = QAction("Watched")
        self.addAction(self.watched_action)
        self.watched_action.setCheckable(True)
        self.watched_action.toggled.connect(lambda: self.columnToggled("Watched"))
        self.title_action = QAction("Title")
        self.addAction(self.title_action)
        self.title_action.setCheckable(True)
        self.title_action.toggled.connect(lambda: self.columnToggled("Title"))
        self.plot_action = QAction("Plot")
        self.addAction(self.plot_action)
        self.plot_action.setCheckable(True)
        self.plot_action.toggled.connect(lambda: self.columnToggled("Plot"))
        self.runtime_action = QAction("Runtime")
        self.addAction(self.runtime_action)
        self.runtime_action.setCheckable(True)
        self.runtime_action.toggled.connect(lambda: self.columnToggled("Runtime"))
        self.userrating_action = QAction("Rating")
        self.addAction(self.userrating_action)
        self.userrating_action.setCheckable(True)
        self.userrating_action.toggled.connect(lambda: self.columnToggled("Rating"))
        self.tagline_action = QAction("Tag Line")
        self.addAction(self.tagline_action)
        self.tagline_action.setCheckable(True)
        self.tagline_action.toggled.connect(lambda: self.columnToggled("Tag Line"))
        self.mpaa_action = QAction("Content Rating")
        self.addAction(self.mpaa_action)
        self.mpaa_action.setCheckable(True)
        self.mpaa_action.toggled.connect(lambda: self.columnToggled("Content Rating"))
        self.playcount_action = QAction("Play Count")
        self.addAction(self.playcount_action)
        self.playcount_action.setCheckable(True)
        self.playcount_action.toggled.connect(lambda: self.columnToggled("Play Count"))
        self.imdb_action = QAction("IMDB")
        self.addAction(self.imdb_action)
        self.imdb_action.setCheckable(True)
        self.imdb_action.toggled.connect(lambda: self.columnToggled("IMDB"))
        self.genre_action = QAction("Genre")
        self.addAction(self.genre_action)
        self.genre_action.setCheckable(True)
        self.genre_action.toggled.connect(lambda: self.columnToggled("Genre"))
        self.country_action = QAction("Country")
        self.addAction(self.country_action)
        self.country_action.setCheckable(True)
        self.country_action.toggled.connect(lambda: self.columnToggled("Country"))
        self.director_action = QAction("Director")
        self.addAction(self.director_action)
        self.director_action.setCheckable(True)
        self.director_action.toggled.connect(lambda: self.columnToggled("Director"))
        self.premiered_action = QAction("Premiered")
        self.addAction(self.premiered_action)
        self.premiered_action.setCheckable(True)
        self.premiered_action.toggled.connect(lambda: self.columnToggled("Premiered"))
        self.year_action = QAction("Year")
        self.addAction(self.year_action)
        self.year_action.setCheckable(True)
        self.year_action.toggled.connect(lambda: self.columnToggled("Year"))
        self.trailer_action = QAction("Trailer")
        self.addAction(self.trailer_action)
        self.trailer_action.setCheckable(True)
        self.trailer_action.toggled.connect(lambda: self.columnToggled("Trailer"))
        self.studio_action = QAction("Studio")
        self.addAction(self.studio_action)
        self.studio_action.setCheckable(True)
        self.studio_action.toggled.connect(lambda: self.columnToggled("Studio"))
        self.dateadded_action = QAction("Date Added")
        self.addAction(self.dateadded_action)
        self.dateadded_action.setCheckable(True)
        self.dateadded_action.toggled.connect(lambda: self.columnToggled("Date Added"))
        self.status_action = QAction("Status")
        self.addAction(self.status_action)
        self.status_action.setCheckable(True)
        self.status_action.toggled.connect(lambda: self.columnToggled("Status"))
        self.comments_action = QAction("Comments")
        self.addAction(self.comments_action)
        self.comments_action.setCheckable(True)
        self.comments_action.toggled.connect(lambda: self.columnToggled("Comments"))
        self.quality_action = QAction("Quality")
        self.addAction(self.quality_action)
        self.quality_action.setCheckable(True)
        self.quality_action.toggled.connect(lambda: self.columnToggled("Quality"))
        self.nfopath_action = QAction("NFO")
        self.addAction(self.nfopath_action)
        self.nfopath_action.setCheckable(True)
        self.nfopath_action.toggled.connect(lambda: self.columnToggled("NFO"))
        self.path_action = QAction("Folder")
        self.addAction(self.path_action)
        self.path_action.setCheckable(True)
        self.path_action.toggled.connect(lambda: self.columnToggled("Folder"))
        self.foldername_action = QAction("Folder Name")
        self.addAction(self.foldername_action)
        self.foldername_action.setCheckable(True)
        self.foldername_action.toggled.connect(
            lambda: self.columnToggled("Folder Name")
        )
        self.foldersize_action = QAction("Folder Size")
        self.addAction(self.foldersize_action)
        self.foldersize_action.setCheckable(True)
        self.foldersize_action.toggled.connect(
            lambda: self.columnToggled("Folder Size")
        )
        self.lastviewed_action = QAction("Last Viewed")
        self.addAction(self.lastviewed_action)
        self.lastviewed_action.setCheckable(True)
        self.lastviewed_action.toggled.connect(
            lambda: self.columnToggled("Last Viewed")
        )
        self.resolution_action = QAction("Resolution")
        self.addAction(self.resolution_action)
        self.resolution_action.setCheckable(True)
        self.resolution_action.toggled.connect(lambda: self.columnToggled("Resolution"))
        self.pin_action = QAction("Pin")
        self.addAction(self.pin_action)
        self.pin_action.setCheckable(True)
        self.pin_action.toggled.connect(lambda: self.columnToggled("Pin"))
        self._reverse = {val: key for key, val in MAPPING.items()}

    def columnToggled(self, text):
        self.menuItemToggled.emit(text)

    def setCheckedItems(self, lst):
        for action in self.actions():
            if action.text() in lst:
                action.setChecked(True)


class TvColumnMenu(QMenu):
    menuItemToggled = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.title_action = QAction("Title")
        self.addAction(self.title_action)
        self.title_action.setCheckable(True)
        self.title_action.toggled.connect(lambda: self.columnToggled("Title"))
        self.plot_action = QAction("Plot")
        self.addAction(self.plot_action)
        self.plot_action.setCheckable(True)
        self.plot_action.toggled.connect(lambda: self.columnToggled("Plot"))
        self.runtime_action = QAction("Runtime")
        self.addAction(self.runtime_action)
        self.runtime_action.setCheckable(True)
        self.runtime_action.toggled.connect(lambda: self.columnToggled("Runtime"))
        self.userrating_action = QAction("Rating")
        self.addAction(self.userrating_action)
        self.userrating_action.setCheckable(True)
        self.userrating_action.toggled.connect(lambda: self.columnToggled("Rating"))
        self.tagline_action = QAction("Tag Line")
        self.addAction(self.tagline_action)
        self.tagline_action.setCheckable(True)
        self.tagline_action.toggled.connect(lambda: self.columnToggled("Tag Line"))
        self.mpaa_action = QAction("Content Rating")
        self.addAction(self.mpaa_action)
        self.mpaa_action.setCheckable(True)
        self.mpaa_action.toggled.connect(lambda: self.columnToggled("Content Rating"))
        self.imdb_action = QAction("IMDB")
        self.addAction(self.imdb_action)
        self.imdb_action.setCheckable(True)
        self.imdb_action.toggled.connect(lambda: self.columnToggled("IMDB"))
        self.genre_action = QAction("Genre")
        self.addAction(self.genre_action)
        self.genre_action.setCheckable(True)
        self.genre_action.toggled.connect(lambda: self.columnToggled("Genre"))
        self.country_action = QAction("Country")
        self.addAction(self.country_action)
        self.country_action.setCheckable(True)
        self.country_action.toggled.connect(lambda: self.columnToggled("Country"))
        self.premiered_action = QAction("Premiered")
        self.addAction(self.premiered_action)
        self.premiered_action.setCheckable(True)
        self.premiered_action.toggled.connect(lambda: self.columnToggled("Premiered"))
        self.year_action = QAction("Year")
        self.addAction(self.year_action)
        self.year_action.setCheckable(True)
        self.year_action.toggled.connect(lambda: self.columnToggled("Year"))
        self.trailer_action = QAction("Trailer")
        self.addAction(self.trailer_action)
        self.trailer_action.setCheckable(True)
        self.trailer_action.toggled.connect(lambda: self.columnToggled("Trailer"))
        self.studio_action = QAction("Studio")
        self.addAction(self.studio_action)
        self.studio_action.setCheckable(True)
        self.studio_action.toggled.connect(lambda: self.columnToggled("Studio"))
        self.status_action = QAction("Status")
        self.addAction(self.status_action)
        self.status_action.setCheckable(True)
        self.status_action.toggled.connect(lambda: self.columnToggled("Status"))
        self.comments_action = QAction("Comments")
        self.addAction(self.comments_action)
        self.comments_action.setCheckable(True)
        self.comments_action.toggled.connect(lambda: self.columnToggled("Comments"))
        self.nfopath_action = QAction("NFO")
        self.addAction(self.nfopath_action)
        self.nfopath_action.setCheckable(True)
        self.nfopath_action.toggled.connect(lambda: self.columnToggled("NFO"))
        self.path_action = QAction("Folder")
        self.addAction(self.path_action)
        self.path_action.setCheckable(True)
        self.path_action.toggled.connect(lambda: self.columnToggled("Folder"))
        self.foldername_action = QAction("Folder Name")
        self.addAction(self.foldername_action)
        self.foldername_action.setCheckable(True)
        self.foldername_action.toggled.connect(
            lambda: self.columnToggled("Folder Name")
        )
        self.foldersize_action = QAction("Folder Size")
        self.addAction(self.foldersize_action)
        self.foldersize_action.setCheckable(True)
        self.foldersize_action.toggled.connect(
            lambda: self.columnToggled("Folder Size")
        )
        self._reverse = {val: key for key, val in TV_MAPPING.items()}

    def columnToggled(self, text):
        self.menuItemToggled.emit(text)

    def setCheckedItems(self, lst):
        for action in self.actions():
            if action.text() in lst:
                action.setChecked(True)
