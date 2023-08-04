import os
import sys
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
    


MAPPING = {
    "title": "Title",
    "plot": "Plot",
    "runtime": "Runtime",
    "userrating": "Rating",
    "tagline": "Tag\nLine",
    "movie": "Movie",
    "tv": "TV",
    "mpaa": "Content\nRating",
    "playcount": "Play\nCount",
    "imdb": "IMDB",
    "genre": "Genre",
    "country": "Country",
    "director": "Director",
    "premiered": "Premiered",
    "year": "Year",
    "trailer": "Trailer",
    "studio": "Studio",
    "vcodec": "Video\nCodec",
    "acodec": "Audio\nCodec",
    "height": "Height",
    "width": "Width",
    "season": "Season",
    "episode": "Episode",
    "dateadded": "Date\nAdded",
    "tag": "Tag",
    "status": "Status",
    "comments": "Comments",
    "quality": "Quality",
    "actors": "Actors",
    "nfopath": "NFO\nPath",
    "folderpath": "Folder\nPath",
    "foldername": "Folder\nName",
    "foldersize": "Folder\nSize",
    "images": "Image\nPaths",
    "lastviewed": "Last\nViewed",
    "watched": "Watched"
}

GENRES = ["Action","Adventure","Animation","Anime","Apocalypse / Survival","Biography","Comedy","Crime","Dance","Dark Comedy","Documentary","Drama","Family","Fantasy","Foreign","Found Footage","Games","Gore / Torture","Hip-Hop","History","Horror","Indie","Money & Power","Mystery","Romance","Sci-Fi","Social Commentary","Special Interest","Suspense","Thriller","War","Zombies","Natalie","(TV) Poker","(TV) Competition","(TV) Ended + All Eps","(TV) Can be deleted","Blank"]

QUALITY = {
    "WQ" : "Worst Quality",
    "LQ" : "Low Quality",
    "SQ" : "Standard Quality",
    "HQ" : "High Quality (~720P)",
    "BQ" : "Best Quality (>= 1080p)",
    "TB" : "Too Big for Quality",
    "NU" : "Needs Upgrade",
    "MSU" : "Missing Subs",
    "HCS" : "Hard Coded Subs",
    "BFF" : "Bad File Format",
    "WL" : "Wrong Language",
    "SYNC" : "Off Sync",
    "": "Blank"
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
        size += QSize(2 * self.contentsMargins().top(), 2 * self.contentsMargins().top())
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
