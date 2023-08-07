import os
import sys
from datetime import datetime
from pathlib import Path

import parsel

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *


PARENT = Path(__file__).parent.parent
ASSETS = PARENT / "assets"
if "MEI" in str(PARENT):
    LOCAL = Path(sys.executable).parent
else:
    LOCAL = PARENT


def getimage(text):
    path = ASSETS / text
    if os.path.exists(path):
        pix = QPixmap(str(path))
    else:
        pix = QPixmap(str(path) + ".png")
    return pix


def geticon(text):
    return QIcon(getimage(text))


SEASON = {"playcount": "Play Count", "name": "Name", "rating": "Rating"}

EPISODE = {
    "filename": "File Name",
    "playcount": "Play Count",
    "title": "Title",
    "rating": "Rating",
}

MAPPING = {
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
    "season": "Season",
    "episode": "Episode",
    "dateadded": "Date Added",
    "status": "Status",
    "comments": "Comments",
    "quality": "Quality",
    "nfopath": "NFO",
    "path": "Folder",
    "foldername": "Folder Name",
    "foldersize": "Folder Size",
    "lastviewed": "Last Viewed",
    "watched": "Watched",
}

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
    "Blank",
]

QUALITY = {
    "WQ": "Worst Quality",
    "LQ": "Low Quality",
    "SQ": "Standard Quality",
    "HQ": "High Quality (~720P)",
    "BQ": "Best Quality (>= 1080p)",
    "TB": "Too Big for Quality",
    "NU": "Needs Upgrade",
    "MSU": "Missing Subs",
    "HCS": "Hard Coded Subs",
    "BFF": "Bad File Format",
    "WL": "Wrong Language",
    "SYNC": "Off Sync",
    "": "Blank",
}


def nfo_to_dict(content):
    selector = parsel.Selector(content)
    record = {}
    record["title"] = selector.xpath("//title/text()").get()
    record["plot"] = selector.xpath("//plot/text()").get()
    record["runtime"] = selector.xpath("//runtime/text()").get()
    record["userrating"] = selector.xpath("//userrating/text()").get()
    record["tagline"] = selector.xpath("//tagline/text()").get()
    record["movie"] = selector.xpath("//movie").get() is not None
    record["tv"] = selector.xpath("//tvshow").get() is not None
    record["mpaa"] = selector.xpath("//mpaa/text()").get()
    record["playcount"] = selector.xpath("//playcount/text()").get()
    record["imdb"] = selector.xpath("//uniqueid[@type='imdb']/text()").get()
    record["genre"] = ";".join(selector.xpath("//genre/text()").getall())
    record["country"] = selector.xpath("//country/text()").get()
    record["director"] = selector.xpath("//director/text()").get()
    record["premiered"] = selector.xpath("//premiered/text()").get()
    record["year"] = selector.xpath("//year/text()").get()
    record["trailer"] = selector.xpath("//trailer/text()").get()
    record["studio"] = selector.xpath("//studio/text()").get()
    record["vcodec"] = selector.xpath("//video/codec/text()").get()
    record["acodec"] = selector.xpath("//audio/codec/text()").get()
    record["height"] = selector.xpath("//video/height/text()").get()
    record["width"] = selector.xpath("//vide/width/text()").get()
    record["season"] = selector.xpath("//season/text()").get()
    record["episode"] = selector.xpath("//episode/text()").get()
    record["dateadded"] = selector.xpath("//dateadded/text()").get()
    record["tag"] = ";".join(selector.xpath("//tag/text()").getall())
    record["status"] = selector.xpath("//status/text()").get()
    record["lastviewed"] = ""
    record["comments"] = ""
    record["quality"] = ""
    record["watched"] = False
    record["actors"] = []
    if record["userrating"] is None:
        record["userrating"] = 0
    if record["playcount"] is None:
        record["playcount"] = 0
    if record["dateadded"] is None:
        record["dateadded"] = datetime.today().strftime("%m-%d-%Y")
    if record["lastviewed"] == None:
        record["lastviewed"] = "-"
    for actor in selector.xpath("//actor"):
        name = actor.xpath("./name/text()").get()
        role = actor.xpath("./role/text()").get()
        record["actors"].append([name, role])
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


class SeasonMenu(QMenu):
    menuItemToggled = Signal(str)
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.playcount_action = QAction("Play Count")
        self.playcount_action.setCheckable(True)
        self.addAction(self.playcount_action)
        self.playcount_action.toggled.connect(lambda : self.columnToggled("Play Count"))
        self.name_action = QAction("Name")
        self.name_action.setCheckable(True)
        self.addAction(self.name_action)
        self.name_action.toggled.connect(lambda : self.columnToggled("Name"))
        self.rating_action = QAction("Rating")
        self.rating_action.setCheckable(True)
        self.addAction(self.rating_action)
        self.rating_action.toggled.connect(lambda : self.columnToggled("Rating"))
        self._reverse = {val:key for key,val in SEASON.items()}

    def columnToggled(self, text):
        key = self._reverse[text]
        self.menuItemToggled.emit(key)

    def setCheckedItems(self, lst):
        for action in self.actions():
            key = self._reverse[action.text()]
            if key in lst:
                action.setChecked(True)


class EpisodeMenu(QMenu):
    menuItemToggled = Signal(str)
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.filename_action = QAction("File Name")
        self.filename_action.setCheckable(True)
        self.addAction(self.filename_action)
        self.filename_action.toggled.connect(lambda : self.columnToggled("File Name"))
        self.playcount_action = QAction("Play Count")
        self.playcount_action.setCheckable(True)
        self.addAction(self.playcount_action)
        self.playcount_action.toggled.connect(lambda : self.columnToggled("Play Count"))
        self.title_action = QAction("Title")
        self.title_action.setCheckable(True)
        self.addAction(self.title_action)
        self.title_action.toggled.connect(lambda : self.columnToggled("Title"))
        self.rating_action = QAction("Rating")
        self.rating_action.setCheckable(True)
        self.addAction(self.rating_action)
        self.rating_action.toggled.connect(lambda : self.columnToggled("Rating"))
        self._reverse = {val:key for key,val in EPISODE.items()}

    def columnToggled(self, text):
        key = self._reverse[text]
        self.menuItemToggled.emit(key)

    def setCheckedItems(self, lst):
        for action in self.actions():
            key = self._reverse[action.text()]
            if key in lst:
                action.setChecked(True)

class ColumnMenu(QMenu):
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
        # self.movie_action = QAction("Movie")
        # self.addAction(self.movie_action)
        # self.movie_action.setCheckable(True)
        # self.movie_action.toggled.connect(lambda: self.columnToggled("Movie"))
        # self.tv_action = QAction("TV")
        # self.addAction(self.tv_action)
        # self.tv_action.setCheckable(True)
        # self.tv_action.toggled.connect(lambda: self.columnToggled("TV"))
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
        # self.vcodec_action = QAction("Video Codec")
        # self.addAction(self.vcodec_action)
        # self.vcodec_action.setCheckable(True)
        # self.vcodec_action.toggled.connect(lambda: self.columnToggled("Video Codec"))
        # self.acodec_action = QAction("Audio Codec")
        # self.addAction(self.acodec_action)
        # self.acodec_action.setCheckable(True)
        # self.acodec_action.toggled.connect(lambda: self.columnToggled("Audio Codec"))
        # self.height_action = QAction("Height")
        # self.addAction(self.height_action)
        # self.height_action.setCheckable(True)
        # self.height_action.toggled.connect(lambda: self.columnToggled("Height"))
        # self.width_action = QAction("Width")
        # self.addAction(self.width_action)
        # self.width_action.setCheckable(True)
        # self.width_action.toggled.connect(lambda: self.columnToggled("Width"))
        self.season_action = QAction("Season")
        self.addAction(self.season_action)
        self.season_action.setCheckable(True)
        self.season_action.toggled.connect(lambda: self.columnToggled("Season"))
        self.episode_action = QAction("Episode")
        self.addAction(self.episode_action)
        self.episode_action.setCheckable(True)
        self.episode_action.toggled.connect(lambda: self.columnToggled("Episode"))
        self.dateadded_action = QAction("Date Added")
        self.addAction(self.dateadded_action)
        self.dateadded_action.setCheckable(True)
        self.dateadded_action.toggled.connect(lambda: self.columnToggled("Date Added"))
        # self.tag_action = QAction("Tag")
        # self.addAction(self.tag_action)
        # self.tag_action.setCheckable(True)
        # self.tag_action.toggled.connect(lambda: self.columnToggled("Tag"))
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
        # self.actors_action = QAction("Actors")
        # self.addAction(self.actors_action)
        # self.actors_action.setCheckable(True)
        # self.actors_action.toggled.connect(lambda: self.columnToggled("Actors"))
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
        self.foldername_action.toggled.connect(lambda: self.columnToggled("Folder Name"))
        self.foldersize_action = QAction("Folder Size")
        self.addAction(self.foldersize_action)
        self.foldersize_action.setCheckable(True)
        self.foldersize_action.toggled.connect(lambda: self.columnToggled("Folder Size"))
        # self.images_action = QAction("Image Paths")
        # self.addAction(self.images_action)
        # self.images_action.setCheckable(True)
        # self.images_action.toggled.connect(lambda: self.columnToggled("Image Paths"))
        self.lastviewed_action = QAction("Last Viewed")
        self.addAction(self.lastviewed_action)
        self.lastviewed_action.setCheckable(True)
        self.lastviewed_action.toggled.connect(lambda: self.columnToggled("Last Viewed"))
        self.watched_action = QAction("Watched")
        self.addAction(self.watched_action)
        self.watched_action.setCheckable(True)
        self.watched_action.toggled.connect(lambda: self.columnToggled("Watched"))
        self._reverse = {val:key for key,val in MAPPING.items()}

    def columnToggled(self, text):
        key = self._reverse[text]
        self.menuItemToggled.emit(key)

    def setCheckedItems(self, lst):
        for action in self.actions():
            key = self._reverse[action.text()]
            if key in lst:
                action.setChecked(True)
