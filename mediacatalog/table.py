import json

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from mediacatalog.utils import geticon
from mediacatalog.db import Diff
from mediacatalog.settings import setting, setSetting, getData

class TableModel(QAbstractTableModel):
    def __init__(self, table, mapping, fields=None, parent=None):
        super().__init__(parent=parent)
        self._table = table
        self._fields = fields if fields is not None else self._table
        self._mapping = mapping
        self._reverse = {v: k for k, v in mapping.items()}
        self._headers_labels = None
        self._last_filters = None
        self._headers = None
        self._master = []
        self._data = []
        self.refreshHeaders()
        if fields is None:
            self.getData()

    def apply_filters(self, filters=None):
        if filters is None and self._last_filters is None:
            return
        if filters is None:
            filters = self._last_filters
        data = []
        for record in self._master:
            print(record)
            print(filters["title"])
            if filters["title"] and filters["title"].lower() not in record["title"].lower():

                continue
            if filters["quality"] and record["quality"] not in filters["quality"]:
                continue
            if filters["rating"] and record["rating"] not in filters["rating"]:
                continue
            found = False
            if filters["genre"]:
                for genre in record["genre"]:
                    if genre in filters["genre"]:
                        found = True
                        break
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



    def clearRows(self):
        rows = self.rowCount(QModelIndex()) - 1
        while rows >= 0:
            self.removeRow(rows, QModelIndex())
            rows -= 1
        return

    def set_data(self, data):
        self.clearRows()
        for fullpath, record in data.items():
            record["Path"] = fullpath
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

    def refreshHeaders(self):
        headers_labels = json.loads(setting(self._fields + "columnfields"))
        if self._headers_labels is None:
            self._headers_labels = headers_labels
            self._headers = [self._mapping[i] for i in self._headers_labels]
        elif len(headers_labels) < len(self._headers_labels):
            idxs = [
                i
                for i in range(len(self._headers_labels))
                if self._headers_labels[i] not in headers_labels
            ]
            for idx in idxs:
                self.removeColumn(idx, QModelIndex())
        elif len(headers_labels) > len(self._headers_labels):
            idxs = [
                i
                for i in range(len(headers_labels))
                if headers_labels[i] not in self._headers_labels
            ]
            for idx in idxs:
                self.insertColumn(idx, headers_labels[idx], QModelIndex())

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
                return self._headers[section]
        return None

    def data(self, index, role):
        if index.isValid():
            row, col = index.row(), index.column()
            label = self._headers[col]
            field = self._reverse[label]
            text = self._data[row][field]
            if field == "pin":
                if text:
                    if role == Qt.ItemDataRole.DecorationRole:
                        return QIcon(geticon("pin"))
                elif role == Qt.ItemDataRole.DisplayRole:
                    return None
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
                if role == Qt.ItemDataRole.CheckStateRole:
                    if text:
                        return Qt.CheckState.Checked
                    else:
                        return Qt.CheckState.Unchecked
                elif role == Qt.ItemDataRole.DisplayRole:
                    return None
            if role == Qt.ItemDataRole.DisplayRole:
                return text
        return None

    def removeColumn(self, column, parent=QModelIndex()):
        self.beginRemoveColumns(parent, column, column)
        del self._headers[column]
        del self._headers_labels[column]
        self.endRemoveColumns()

    def insertColumn(self, column, value, parent=QModelIndex()):
        self.beginRemoveColumns(parent, column, column)
        self._headers_labels.insert(column, value)
        self._headers.insert(column, self._mapping[value])
        self.endRemoveColumns()


class TableView(QTableView):
    def __init__(self, table, mapping, fields=None, parent=None):
        super().__init__(parent=parent)
        self._table = table
        self._fields = fields if fields is not None else table
        self._model = TableModel(self._table, mapping, fields=fields)
        self._proxy_model = QSortFilterProxyModel()
        self.setModel(self._proxy_model)
        self._proxy_model.setSourceModel(self._model)
        self._proxy_model.setDynamicSortFilter(True)
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
        self.labels = json.loads(setting(self._fields + "columnfields"))

    def setColumnMenu(self, menu):
        self.columnMenu = menu()
        self.columnMenu.setCheckedItems(self.labels)

    def toggleColumnHeader(self, key):
        if key in self.labels:
            self.labels.remove(key)
        else:
            self.labels.append(key)
        setSetting(self._fields + "columnfields", json.dumps(self.labels))
        self._model.refreshHeaders()

    def selectVisibleColumns(self, point):
        self.columnMenu.menuItemToggled.connect(self.toggleColumnHeader)
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
