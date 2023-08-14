import os
import datetime
import pathlib
import sqlite3
import json
import shutil
from hashlib import md5

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from mediacatalog.utils import nfo_to_dict, MAPPING
from mediacatalog.settings import Settings, setting


class Diff:
    new_content = {}
    missing_content = []


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
        ".jpg",
        ".png",
        ".jpeg",
        ".tiff",
        ".gif",
    ]:
        paths.append(path)
        return paths
    elif os.path.isdir(path):
        for filename in os.listdir(path):
            fullpath = os.path.join(path, filename)
            paths += find_image_files(fullpath)
    return paths


def find_nfo(path):
    if not os.path.isdir(path):
        return None
    for item in os.listdir(path):
        if os.path.splitext(item)[-1].lower() == ".nfo":
            return os.path.join(path, item)
    return None


def scan_seasons(path):
    seasons = {}
    for name in os.listdir(os.path.realpath(path)):
        fullpath = os.path.join(path, name)
        if name.lower().startswith("season") and os.path.isdir(fullpath):
            seasons[fullpath] = {
                "name": name,
                "playcount": 0,
                "rating": 0,
                "episodes": {},
            }
            for episode in os.listdir(fullpath):
                episode_path = os.path.join(fullpath, episode)
                seasons[fullpath]["episodes"][episode_path] = {
                    "filename": episode,
                    "playcount": 0,
                    "rating": 0,
                    "title": os.path.splitext(episode)[0].split("- ")[-1],
                }
    return seasons


def scan_videos(path):
    video_files = []
    if not os.path.isdir(path):
        return None
    for name in os.listdir(path):
        if os.path.splitext(name)[-1].lower() in [
            ".avi",
            ".mkv",
            ".mp4",
            ".mov",
            ".wmv",
        ]:
            video_files.append(os.path.join(path, name))
    return video_files


def scan_media(path, category, paths, deep=False):
    records = []
    if not path:
        return records
    for item in os.listdir(path):
        record = {}
        fullpath = os.path.join(path, item)
        if fullpath in paths and not deep:
            continue
        record["foldername"] = item
        record["path"] = fullpath
        record["foldersize"] = get_folder_size(fullpath)
        record["images"] = find_image_files(fullpath)
        nfo = find_nfo(fullpath)
        if nfo is not None:
            with open(nfo, "rt", encoding="utf8") as nfofile:
                content = nfofile.read()
            record.update(nfo_to_dict(content))
            record["nfopath"] = nfo
        else:
            temp = {key: None for key in MAPPING.keys() if key not in record}
            record.update(temp)
        if category == "tv":
            record["seasons"] = scan_seasons(fullpath)
        else:
            if category == "movies":
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
        self.path = path
        self.missing_content = []
        self.imagedir = os.path.join(os.path.dirname(path), "imgs")
        self.setup_database(path)
        self.conn = sqlite3.connect(path)
        self.refresh_database()

    def settings(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM settings")
        settings_row = cursor.fetchall()
        settings_dict = json.loads(settings_row[0][1])
        return settings_dict

    def set_settings(self, settings):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE settings SET "value" = ? WHERE "key" = ?', (json.dumps(settings), "settings"))
        self.conn.commit()

    def setting(self, key):
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", ("settings",))
        val = cursor.fetchone()[0]
        d = json.loads(val)
        return d[key]

    def set_setting(self, key, value):
        settings = self.settings()
        settings[key] = value
        self.set_settings(settings)


    def refresh_database(self, deep=False):
        cursor = self.conn.cursor()
        for key in ["movies", "tv", "ufc", "documentaries"]:
            values = self.setting(key)
            records = []
            cursor.execute(f"SELECT * FROM {key}")
            current = cursor.fetchall()
            paths = []
            for row in current:
                path = row[0]
                if not os.path.exists(path):
                    self.missing_content.append(path)
                else:
                    paths.append(path)
            for val in values:
                records += scan_media(val, key, paths, deep=deep)
            for record in records:
                path = record["path"]
                if not deep:
                    Diff.new_content[path] = record
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
                if path in paths:
                    diff, record = self.compare_records(
                        record, json.loads(current[paths.index(path)][-1])
                    )
                    Diff.content[path] = diff
                    self.updateField(key, foldername, "json", json.dumps(record))
                else:
                    cursor.execute(
                        f"INSERT INTO {key} values(?, ?, ?)",
                        (path, foldername, jsondata),
                    )
        self.conn.commit()

    def setup_database(self, path):
        if os.path.exists(path):
            return
        if not os.path.exists(self.imagedir):
            os.mkdir(self.imagedir)
        con = sqlite3.connect(path)
        cursor = con.cursor()
        cursor.execute("CREATE TABLE movies(path, foldername, json)")
        cursor.execute("CREATE TABLE tv(path, foldername, json)")
        cursor.execute("CREATE TABLE ufc(path, foldername, json)")
        cursor.execute("CREATE TABLE documentaries(path, foldername, json)")
        cursor.execute("CREATE TABLE settings(key, value)")
        cursor.execute("INSERT INTO settings VALUES(?, ?)", ("settings", json.dumps(Settings.default)))
        con.commit()

    def updateField(self, table, foldername, key, value):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {table} WHERE foldername = ?", (foldername,))
        row = cursor.fetchone()
        jsondata = row[-1]
        record = json.loads(jsondata)
        record[key] = value
        jsondata = json.dumps(record)
        cursor.execute(
            f'UPDATE {table} SET "json" = ? WHERE "foldername" = ?',
            (jsondata, foldername),
        )
        self.conn.commit()

    def getData(self, table):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {table}")
        return cursor.fetchall()

    def compare_records(self, new_record, old_record):
        diff = {}
        for k, v in new_record.items():
            if k in ["userrating", "playcount", "dateadded", "lastviewed", "comments"]:
                continue
            if old_record[k] != v:
                if k != "seasons":
                    diff[k] = v
                    old_record[k] = v
                    continue
                for season in v:
                    if season not in old_record["seasons"]:
                        diff.setdefault("seasons", {})
                        diff["seasons"][season] = v
                        old_record["seasons"][season] = new_record["seasons"][season]
                    elif old_record["seasons"][season] != v:
                        diff["seasons"][season] = {"episodes": []}
                        for episode in season["episodes"]:
                            if episode not in old_record["seasons"][season]["episodes"]:
                                diff["season"][season]["episodes"].append(episode)
                                old_record["season"][season]["episodes"] = new_record[
                                    "season"
                                ][season]["episodes"]
        return diff, old_record
