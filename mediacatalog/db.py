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

from mediacatalog.utils import nfo_to_dict, MAPPING, tv_nfo_to_dict
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


def scan_media(path, paths):
    records = []
    if not path:
        return records
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
        if nfo is not None:
            with open(nfo, "rt", encoding="utf8") as nfofile:
                content = nfofile.read()
        else:
            content = None
        record.update(nfo_to_dict(content))
        record["nfopath"] = nfo
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

def scan_tv_media(paths, path, new):
    if not path:
        return []
    records = []
    for folder in os.listdir(path):
        folderpath = os.path.join(path, folder)
        if folderpath not in paths:
            record = {}
            record["foldername"] = folder
            record["path"] = folderpath
            record["foldersize"] = get_folder_size(folderpath)
            record["images"] = find_image_files(folderpath)
            parts = folder.split()
            nfo = find_nfo(folderpath)
            try:
                record["foldertitle"] = parts[0]
                record["folderyear"] = parts[1].strip("()")
                record["folderimdb"] = parts[2].strip("()")
            except IndexError:
                pass
            if nfo is not None:
                with open(nfo, "rt", encoding="utf8") as nfofile:
                    content = nfofile.read()
            else:
                content = None
            record.update(tv_nfo_to_dict(content))
            record["nfopath"] = nfo
            record["seasons"] = {}
        else:
            record = paths[folderpath]
        scan_seasons(record, folderpath, new)
        records.append(record)
    return records

def scan_seasons(record, path, new):
    for item in os.listdir(path):
        fullpath = os.path.join(path, item)
        if os.path.isdir(fullpath) and item.lower().startswith("season"):
            record["seasons"].setdefault(item, [])
            episode_paths = [i["path"] for i in record["seasons"][item]]
            for epi in os.listdir(fullpath):
                epi_path = os.path.join(fullpath, epi)
                if epi_path in episode_paths:
                    continue
                parts = os.path.splitext(epi)[0].split("-")
                numbers = parts[1].strip()
                season, episode_num = numbers.lower().split("x")
                episode = {
                    "path": epi_path,
                    "season": int(season),
                    "title": parts[2].strip(),
                    "number": int(episode_num),
                    "userrating": 0.0,
                    "watched": "unwatched",
                    "playcount": 0,
                    "lastviewed": "",
                    "dateadded": datetime.datetime.today().strftime("%m-%d-%Y"),
                    "pin": False,
                }
                record["seasons"][item].append(episode)
                new.append(episode)

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
        for key in ["movies", "ufc", "documentaries"]:
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
                records += scan_media(val, paths)
            for record in records:
                path = record["path"]
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
                cursor.execute(
                    f"INSERT INTO {key} values(?, ?, ?)",
                    (path, foldername, jsondata),
                )
        self.conn.commit()
        self.refresh_tv()

    def refresh_tv(self):
        cursor = self.conn.cursor()
        values = self.setting("tv")
        cursor.execute(f"SELECT * FROM tv")
        current = cursor.fetchall()
        paths = {item[0]: json.loads(item[-1]) for item in current}
        for val in values:
            new = []
            records = scan_tv_media(paths, val, new)
            for record in records:
                jsondata = json.dumps(record)
                if record["path"] in paths:
                    cursor.execute(
                        f'UPDATE tv SET "json" = ? WHERE "foldername" = ?',
                        (jsondata, record["foldername"]),
                    )
                else:
                    cursor.execute(
                        f"INSERT INTO tv values(?, ?, ?)",
                        (record["path"], record["foldername"], jsondata),
                    )
            for episode in new:
                Diff.new_content[episode["path"]] = episode
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
