import json
from typing import Any, Union
import PySide6.QtCore

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import humanfriendly

from mediacatalog.utils import geticon
from mediacatalog.db import Diff
from mediacatalog.settings import setting, setSetting, getData

class ListView(QTreeView):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setProperty("class", "Seasons")
        self._model = ListModel()
        self.setModel(self._model)

    def setSeasons(self, seasons):
        self._model.setSeasons(seasons)

    def row(self, index):
        return self._model._seasons[index]

    def current(self):
        row = self.selectionModel().currentIndex().row()
        return self.row(row)



class ListModel(QAbstractListModel):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._seasons = []
        self._header = ["Seasons"]

    def rowCount(self, index=None):
        return len(self._seasons)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Orientation.Horizontal:
            if role == Qt.ItemDataRole.DisplayRole:
                return self._header[section]
        return None

    def data(self, index, role):
        if index.isValid():
            if role == Qt.ItemDataRole.DisplayRole:
                return self._seasons[index.row()]
        return None

    def setSeasons(self, seasons):
        self.clear()
        self.insertRows(0, len(seasons), QModelIndex(), seasons)

    def clear(self):
        self.removeRows(0, self.rowCount(), QModelIndex())

    def insertRow(self, start, index=None):
        if index is None:
            index = QModelIndex()
        self.insertRows(start, 1, index)

    def removeRow(self, start, index=None):
        if index is None:
            index = QModelIndex()
        self.removeRows(start, 1, index)

    def insertRows(self, start, count, index, data=[]):
        self.beginInsertRows(QModelIndex(), start, start+count)
        for i, season in enumerate(data):
            self._seasons.insert(start+i, season)
        self.endInsertRows()

    def removeRows(self, start, count, index):
        self.beginRemoveRows(QModelIndex(), start, start+count)
        for i in list(range(start, start+count))[::-1]:
            del self._seasons[i]
        self.endRemoveRows()





class TableModel(QAbstractTableModel):
    def __init__(self, table, mapping, fields=None, parent=None):
        super().__init__(parent=parent)
        self._table = table
        self._fields = fields if fields is not None else self._table
        self._mapping = mapping
        self._reverse = {v: k for k, v in mapping.items()}
        self._headers_labels = setting(self._fields + "columnfields")
        self._last_filters = None
        self._headers = [self._mapping[k] for k in self._headers_labels]
        self._master = []
        self._data = []
        if fields is None:
            self.getData()

    def headers(self):
        return self._headers

    def apply_filters(self, filters=None):
        if filters is None and self._last_filters is None:
            return
        if filters is None:
            filters = self._last_filters
        data = []
        for record in self._master:
            if filters["title"] and filters["title"].lower() not in record["title"].lower():
                continue
            if filters["quality"] and record["quality"] not in filters["quality"]:
                continue
            if filters["rating"] and record["userrating"] not in filters["rating"]:
                continue
            found = False
            if filters["genre"]:
                for genre in record["genre"]:
                    if genre in filters["genre"]:
                        found = True
                        break
            else:
                found = True
            if not found:
                continue
            if filters["watched"] and record["watched"] not in filters["watched"]:
                continue
            if filters["status"] and record["status"] not in filters["status"]:
                continue
            if filters["folder_operator"] and filters["folder_size"]:
                operator = filters["folder_operator"]
                size = filters["folder_size"]
                record_size = record["foldersize"]
                if operator == "=" and int(size) != int(record_size):
                    continue
                elif operator == ">" and int(size) < int(record_size):
                    continue
                elif operator == "<" and int(size) > int(record_size):
                    continue
            data.append(record)
        self.beginResetModel()
        self._data = data
        self.endResetModel()

    def toggleKey(self, key):
        if key in self._headers:
            index = self._headers.index(key)
            self.removeColumn(index, QModelIndex())
        else:
            index = list(self._reverse.keys()).index(key)
            self.insertColumn(index, key, QModelIndex())

    def clearRows(self):
        rows = self.rowCount(QModelIndex()) - 1
        while rows >= 0:
            self.removeRow(rows, QModelIndex())
            rows -= 1
        return

    def set_data(self, data):
        self.clearRows()
        for fullpath, record in data.items():
            record["path"] = fullpath
            self.insertRow(self.rowCount(QModelIndex), record, QModelIndex())

    def removeRow(self, row, parent=QModelIndex()):
        self.beginRemoveRows(parent, row, row)
        del self._data[row]
        self.endRemoveRows()

    def insertRow(self, row, value, parent=QModelIndex()):
        self.beginInsertRows(parent, row, row)
        self._data.insert(row, value)
        self._master.insert(row, value)
        self.endInsertRows()

    def getRow(self, index):
        return self._data[index.row()]

    def getData(self):
        self.clearRows()
        data = getData(self._table)
        for record in data:
            path, foldername, data = record
            data = json.loads(data)
            self.insertRow(self.rowCount(QModelIndex()), data, QModelIndex())
            self.apply_filters()

    def rowCount(self, _) -> int:
        return len(self._data)

    def columnCount(self, _):
        return len(self._headers)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Orientation.Horizontal:
            if role == Qt.ItemDataRole.DisplayRole:
                return self._mapping[self._headers_labels[section]]
            elif role == Qt.ItemDataRole.SizeHintRole and self._mapping[self._headers_labels[section]] in ["pin", "watched"]:
                return QSize(0, 10)
        return None

    def data(self, index, role):
        if index.isValid():
            row, col = index.row(), index.column()
            field = self._headers_labels[col]
            text = self._data[row][field]
            if field == "pin":
                if text:
                    if role == Qt.ItemDataRole.DecorationRole:
                        return QIcon(geticon("pin"))
                if role == Qt.ItemDataRole.DisplayRole:
                    return text
                elif role == Qt.ItemDataRole.SizeHintRole:
                    return QSize(0, 10)
            elif self._data[row]["path"] in Diff.missing_content:
                if role == Qt.ItemDataRole.ForegroundRole:
                    return QBrush(QColor("#400"))
            elif self._data[row]["path"] in Diff.new_content:
                if field in Diff.new_content[self._data[row]["path"]]:
                    if role == Qt.ItemDataRole.ForegroundRole:
                        return QBrush(QColor("#770"))
                    elif role == Qt.ItemDataRole.BackgroundRole:
                        return QBrush(QColor("#CCC"))
            elif field == "watched":
                if role == Qt.ItemDataRole.DecorationRole:
                    if text and text.lower() != "unwatched":
                        return

            elif field == "genre":
                if role == Qt.ItemDataRole.DisplayRole:
                    if isinstance(text, list):
                        return "  ".join(text)
            elif field == "foldersize":
                if role == Qt.ItemDataRole.DisplayRole:
                    return humanfriendly.format_size(text)
            if role == Qt.ItemDataRole.DisplayRole:
                return text
            if role == 100:
                try:
                    return float(text)
                except:
                    return text
        return None


    def removeColumn(self, column, parent=QModelIndex()):
        self.beginRemoveColumns(parent, column, column)
        del self._headers[column]
        del self._headers_labels[column]
        setSetting(self._fields + "columnfields", self._headers_labels)
        self.endRemoveColumns()

    def insertColumn(self, column, value, parent=QModelIndex()):
        self.beginInsertColumns(parent, column, column)
        self._headers_labels.insert(column, self._reverse[value])
        self._headers.insert(column, value)
        setSetting(self._fields + "columnfields", self._headers_labels)
        self.endInsertColumns()


class TableView(QTableView):
    def __init__(self, table, mapping, fields=None, parent=None):
        super().__init__(parent=parent)
        self._table = table
        self._fields = fields if fields is not None else table
        self._model = TableModel(self._table, mapping, fields=fields)
        self._proxy_model = QSortFilterProxyModel()
        self._proxy_model.setSortRole(100)
        self.setModel(self._proxy_model)
        self._proxy_model.setSourceModel(self._model)
        self._proxy_model.setDynamicSortFilter(True)
        headers = self._model.headers()
        if "Pin" in headers:
            self._pin_delegate = PinDelegate(self)
            self.setItemDelegateForColumn(headers.index("Pin"), self._pin_delegate)
        if "Watched" in headers:
            self._watched_delegate = WatchedDelegate(self)
            self.setItemDelegateForColumn(headers.index("Watched"), self._watched_delegate)
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

    def setColumnMenu(self, menu):
        self.columnMenu = menu()
        self.columnMenu.setCheckedItems(self.tableModel().headers())
        self.columnMenu.menuItemToggled.connect(self.toggleColumnHeader)

    def toggleColumnHeader(self, key):
        self.tableModel().toggleKey(key)

    def selectVisibleColumns(self, point):
        self.columnMenu.popup(self.mapToGlobal(point))

    def tableModel(self):
        return self._model

    def filter(self, filters):
        self.tableModel().apply_filters(filters)


class CheckBoxDelegate(QStyledItemDelegate):

    createEditor = lambda self, _, __, ___: None

    def paint(self, painter, option, index):
        checked = bool(index.model().data(index, Qt.DisplayRole))
        check_box_style_option = QStyleOptionButton()

        if (index.flags() & Qt.ItemIsEditable) > 0:
            check_box_style_option.state |= QStyle.State_Enabled
        else:
            check_box_style_option.state |= QStyle.State_ReadOnly

        if checked:
            check_box_style_option.state |= QStyle.State_On
        else:
            check_box_style_option.state |= QStyle.State_Off

        check_box_style_option.rect = self.getCheckBoxRect(option)
        if not index.model().hasFlag(index, Qt.ItemFlag.ItemIsEditable):
            check_box_style_option.state |= QStyle.State_ReadOnly
        QApplication.style().drawControl(QStyle.CE_CheckBox, check_box_style_option, painter)


    def editorEvent(self, event, model, option, index):
        if not (index.flags() & Qt.ItemIsEditable) > 0:
            return False
        if event.type() == QEvent.MouseButtonRelease or event.type() == QEvent.MouseButtonDblClick:
            if event.button() != Qt.LeftButton or not self.getCheckBoxRect(option).contains(event.pos()):
                return False
            if event.type() == QEvent.MouseButtonDblClick:
                return True
        elif event.type() == QEvent.KeyPress:
            if event.key() != Qt.Key_Space and event.key() != Qt.Key_Select:
                return False
        else:
            return False
        self.setModelData(None, model, index)
        return True

    def setModelData (self, editor, model, index):
        newValue = not bool(index.model().data(index, Qt.DisplayRole))
        model.setData(index, newValue, Qt.EditRole)


    def getCheckBoxRect(self, option):
        check_box_style_option = QStyleOptionButton()
        check_box_rect = QApplication.style().subElementRect(QStyle.SE_CheckBoxIndicator, check_box_style_option, None)
        check_box_point = QPoint (option.rect.x() +
                             option.rect.width() / 2 -
                             check_box_rect.width() / 2,
                             option.rect.y() +
                             option.rect.height() / 2 -
                             check_box_rect.height() / 2)
        return QRect(check_box_point, check_box_rect.size())


class PinDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)


    def paint(self, painter, option, index):
        value = self.parent().model().data(index, Qt.ItemDataRole.DisplayRole)
        if value:
            icon = geticon("pin")
            icon.paint(painter, option.rect, Qt.AlignCenter)

class WatchedDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)


    def paint(self, painter, option, index):
        value = self.parent().model().data(index, Qt.ItemDataRole.DisplayRole)
        if value != "unwatched":
            icon = geticon("check")
            icon.paint(painter, option.rect, Qt.AlignCenter)
