import os
import sqlite3

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *


class SqlDatabase:
    def __init__(self, path):
        self.setup_database(path)
        self.conn = sqlite3.connect(path)

    def setSetting(self, key, value):
        curs = self.conn.cursor()
        curs.execute("UPDATE settings SET value = ? WHERE key = ?", (key, value))
        curs.close()
        self.conn.commit()

    def recurse_path(self, val, records):
        if os.path.isfile(val):
            
            
        
        
    
    
    def refresh_contents(self):
        cursor = self.conn.cursor()
        for key in ["Movies", "TV", "UFC", "Documentaries"]:
            cursor.execute("SELECT * FROM settings WHERE key = ?", (key,))
            value = cursor.fetchone()
            print(value)
            value = value[1]
            print(value)
            records = {}
            for val in value.split(";"):
                self.recurse_path(val, records)
                
                
                
            
        
        
    
    def setup_database(self, path):
        if os.path.exists(path):
            return
        con = sqlite3.connect(path)
        cursor = con.cursor()
        cursor.execute(
            "CREATE TABLE movies(FolderName, FolderPath, Title, Year, Rating, FolderSize, Watched, Genre, Quality, Status, Comments, Date Added, Plot)"
        )
        cursor.execute(
            "CREATE TABLE tv(FilePath, ShowTitle, Season, Episode, ShowRating, ShowGenre, ShowComments, SeasonComments, EpisodeComments, EpisodeWatched, EpisodeStatus, XShow, XSeason, ShowFolder, SeasonFolder, SeasonNo, FolderSize, NewEpisode)"
        )
        cursor.execute(
            "CREATE TABLE ufc(FolderName, FolderPath, Title, Year, Rating, FolderSize, Watched, Genre, Quality, Status, Comments, DateAdded, Plot)"
        )
        cursor.execute(
            "CREATE TABLE documentaries(FolderName, FolderPath, Title, Year, Rating, FolderSize, Watched, Genre, Quality, Status, Comments, DateAdded, Plot)"
        )
        cursor.execute("CREATE TABLE settings(key, value)")
        for i in ["Movies", "TV", "UFC", "Documentaries"]:
            cursor.execute("INSERT INTO settings VALUES(?, ?)", (i, ""))
        con.commit()


class Thread(QThread):
    def __init__(self):
        self._active = True
        self.queue = 