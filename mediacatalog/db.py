import os
import sqlite3
import json
import shutil
from hashlib import md5

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from mediacatalog.utils import nfo_to_dict, QUALITY, GENRES, MAPPING

def get_folder_size(path):
    total = 0
    if os.path.isfile(path):
        return os.path.getsize(path)
    elif os.path.isdir(path):
        for filename in os.listdir(path):
            fullpath = os.path.join(path, filename)
            total += get_folder_size(fullpath)
    return total

def find_image_files(path):
    paths = []
    if os.path.isfile(path) and os.path.splitext(path)[-1].lower() in [
        ".jpg", ".png", ".jpeg", ".tiff", ".gif"
    ]:
        paths.append(path)
        return paths
    elif os.path.isdir(path):
        for filename in os.listdir(path):
            fullpath = os.path.join(path, filename)
            paths += find_image_files(fullpath)
    return paths

def find_nfo(path):
    for item in os.listdir(path):
        if os.path.splitext(item)[-1].lower() == ".nfo":
            return os.path.join(path, item)
    return None

def scan_seasons(path):
    seasons = {}
    for name in os.listdir(path):
        if name.lower().startswith("season"):
            seasons[name] = []
            fullpath = os.path.join(path, name)
            for episode in os.listdir(fullpath):
                episode_path = os.path.join(fullpath, episode)
                seasons[name].append(episode_path)
    return seasons

def scan_videos(path):
    video_files = []
    for name in os.listdir(path):
        if os.path.splitext(name)[-1].lower() in [
            ".avi", ".mkv", ".mp4", ".mov", ".wmv"
        ]:
            video_files.append(os.path.join(path, name))
    return video_files

def scan_media(path, category, paths):
    records = []
    for item in os.listdir(path):
        record = {}
        fullpath = os.path.join(path, item)
        if fullpath in paths:
            continue
        record["foldername"] = item
        record["path"] = fullpath
        record["foldersize"] = get_folder_size(fullpath)
        record["images"] = find_image_files(fullpath)
        nfo = find_nfo(fullpath)
        with open(nfo, "rt", encoding="utf8") as nfofile:
            content = nfofile.read()
        record.update(nfo_to_dict(content))
        if category=="tv":
            record["seasons"] = scan_seasons(fullpath)
        else: 
            if category=="movies":
                parts = item.split()
                try:
                    record["foldertitle"] = parts[0]
                    record["folderyear"] = parts[1].strip("()")
                    record["folderimdb"] = parts[2].strip("()")
                except IndexError:
                    pass
            record["videofiles"] = scan_videos(fullpath)
        records.append(record)
    return records

class SqlDatabase:

    def __init__(self, path):
        self.imagedir = os.path.join(os.path.dirname(path), "imgs")
        self.setup_database(path)
        self.conn = sqlite3.connect(path)
        self.refresh_database()

    def setSetting(self, key, value):
        print(key, value)
        curs = self.conn.cursor()
        curs.execute(f'UPDATE settings SET "value" = "{value}" WHERE "key" = "{key}"')
        self.conn.commit()
        curs.close()

    def refresh_database(self, deep=False):
        cursor = self.conn.cursor()
        for key in ["movies", "tv", "ufc", "documentaries"]:
            cursor.execute("SELECT * FROM settings WHERE key = ?", (key,))
            value = cursor.fetchone()
            if not value:
                continue
            value = value[1]
            records = []
            cursor.execute(f"SELECT * FROM {key}")
            current = cursor.fetchall()
            paths = [i[0] for i in current]
            for val in value.split(";"):
                records += scan_media(val, key, paths)
            for record in records:
                path = record["path"]
                foldername = record["foldername"]
                record["image_cached"] = []
                for img in record["images"]:
                    ext = os.path.splitext(img)[-1]
                    with open(img, "rb") as imgfile:
                        name = md5(imgfile.read()).hexdigest()
                    loc = os.path.join(self.imagedir, name + ext)
                    shutil.copy(img, loc) 
                    record["image_cached"].append(loc)
                jsondata = json.dumps(record)
                cursor.execute(f"INSERT INTO {key} values(?, ?, ?)", (path, foldername, jsondata))
        self.conn.commit()

    def setting(self, key):
        cur = self.conn.cursor()
        cur.execute(f"SELECT * FROM settings WHERE key = ?", (key,))
        result = cur.fetchall()[0][1]
        return result

    def setup_database(self, path):
        if os.path.exists(path):
            return
        if not os.path.exists(self.imagedir):
            os.mkdir(self.imagedir)
        con = sqlite3.connect(path)
        cursor = con.cursor()
        cursor.execute(
            "CREATE TABLE movies(path, foldername, json)"
        )
        cursor.execute(
            "CREATE TABLE tv(path, foldername, json)"
        )
        cursor.execute(
            "CREATE TABLE ufc(path, foldername, json)"
        )
        cursor.execute(
            "CREATE TABLE documentaries(path, foldername, json)"
        )
        cursor.execute("CREATE TABLE settings(key, value)")
        for i in ["movies", "tv", "ufc", "documentaries"]:
            cursor.execute("INSERT INTO settings VALUES(?, ?)", (i, ""))
        cursor.execute("INSERT INTO settings VALUES(?, ?)", ("genres", ";".join(GENRES)))
        cursor.execute("INSERT INTO settings VALUES(?, ?)", ("quality", ";".join(list(QUALITY.keys()))))
        cursor.execute("INSERT INTO settings VALUES(?, ?)", ("tablefields", ";".join(list(MAPPING.keys()))))
        cursor.execute("INSERT INTO settings VALUES(?, ?)", ("profilefields", ";".join(list(MAPPING.keys()))))
        con.commit()

    def update_field(self, table, foldername, key, value):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {table} WHERE foldername = ?", (foldername,))
        row = cursor.fetchone()
        jsondata = row[-1]
        record = json.loads(jsondata)
        record[key] = value
        jsondata = json.dumps(record)
        cursor.execute(f"UPDATE {table} SET \"json\" = \"{jsondata}\" WHERE \"foldername\" = \"{foldername}\"")
        self.conn.commit()

    def getData(self, table):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {table}")
        return cursor.fetchall()