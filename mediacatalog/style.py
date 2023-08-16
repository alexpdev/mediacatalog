import os
from urllib.request import pathname2url
from mediacatalog.utils import getfile, PARENT

_style = """
QWidget
{
    background-color: rgba(255, 255, 255, 255);
}
QFrame,
QStackedWidget
{
    background: none;
}
QMainWindow
{
    background: none;
}
QHeaderView
{
    background-color: rgba(215, 215, 215, 255);
}
QTableCornerButton::section,
QHeaderView::section
{
    border-top: none;
    border-left: none;
    border-right: 1px solid rgba(255, 255, 255, 255);
    border-bottom: 1px solid rgba(255, 255, 255, 255);
    background-color: rgba(215, 215, 215, 255);
}
QTableView::item,
QTableWidget::item,
QTreeView::item
{
    background-color: rgba(255, 255, 255, 255);
}
QLineEdit,
QSpinBox,
QDoubleSpinBox,
QProgressBar,
QComboBox
{
    background: qlineargradient(spread:pad,
        x1:0, y1:0,
        x2:0, y2:1,
        stop:0 rgba(235, 235, 235, 255),
        stop:0.617 rgba(216, 216, 216, 255),
        stop:1 rgba(205, 205, 205, 255)
    );
}
QLineEdit:hover,
QSpinBox:hover,
QDoubleSpinBox:hover,
QComboBox:hover
{
    background: qlineargradient(spread:pad,
        x1:0, y1:0,
        x2:0, y2:1,
        stop:0 rgba(229, 229, 229, 255),
        stop:0.617 rgba(210, 210, 210, 255),
        stop:1 rgba(199, 199, 199, 255)
    );
}
QComboBox,
QDockWidget::title,
QDoubleSpinBox,
QLineEdit,
QListWidget,
QProgressBar,
QSlider::groove:horizontal,
QSpinBox,
QTabBar::tab,
QTextEdit,
QWidget[qssClass="jobList"]
{
    border: 1px solid rgba(155, 155, 155, 255);
}
QToolBar,
QStatusBar
{
    color: rgba(25, 25, 25, 255);
    spacing: 15;
    padding: 3px;
    margin-top: 2px;
    margin-bottom: 2px;

}
QToolBar
{
    border-top: 1px solid rgba(255, 255, 255, 255);
    border-bottom: 1px solid rgba(205, 205, 205, 255);
    color: rgba(25, 25, 25, 255);
}
QToolButton
{
    background: transparent;
    border: 1px solid rgba(0, 0, 0, 0);
}
QToolButton:hover
{
    background-color: rgba(150,186,230, 128);
}
QToolButton:pressed
{
    background: qlineargradient(spread:pad,
        x1:0, y1:0,
        x2:0, y2:1,
        stop:0 rgba(70, 122, 201, 255),
        stop:0.381 rgba(100, 146, 212, 255),
        stop:1 rgba(150, 186, 230, 255)
    );
}
QToolButton:checked
{
    background: qlineargradient(spread:pad,
        x1:0, y1:0,
        x2:0, y2:1,
        stop:0 rgba(235, 235, 235, 255),
        stop:0.617 rgba(216, 216, 216, 255),
        stop:1 rgba(205, 205, 205, 255)
    );
    border: 1px inset rgba(165, 165, 165, 255);
}
QToolBar::separator
{
    margin-top: 2px;
    margin-bottom: 2px;
    background-color: rgba(205, 205, 205, 255);
    width: 2px;
}
QMenuBar
{
    background-color: rgba(255, 255, 255, 255);
}
QMenuBar::item
{
    spacing: 3px;
    padding: 6px 12px;
    background: transparent;
    color: rgba(25, 25, 25, 255);
}
QMenuBar::item:selected
{
    /* when selected using mouse or keyboard */
    background-color: rgba(90, 90, 90, 255);
    color: rgba(255, 168, 0, 255);
}
QMenuBar::item:pressed
{
    background-color: rgba(90, 90, 90, 255);
}
QMenu
{
    background-color: rgba(255, 255, 255, 255);
}
QMenu::item
{
    color: rgba(25, 25, 25, 255);
}
QMenu::item:selected
{
    background-color: rgba(90, 90, 90, 255);
    color: rgba(255, 168, 0, 255);
}
QMenu::separator
{
    height: 1px;
    background-color: rgba(205, 205, 205, 255);
}
QPushButton
{
    border: 1px outset rgba(215, 215, 215, 255);
    padding: 0px 6px;
    min-width: 2em;
    min-height: 1.5em;
    color: rgba(25, 25, 25, 255);
    background: qlineargradient(spread:pad,
        x1:0, y1:0,
        x2:0, y2:1,
        stop:0 rgba(195, 195, 195, 255),
        stop:0.617 rgba(170, 170, 170, 255),
        stop:1 rgba(155, 155, 155, 255)
    );
}
QPushButton:hover
{
    border: 1px outset rgba(170, 206, 250, 255);
    background: qlineargradient(spread:pad,
        x1:0, y1:0,
        x2:0, y2:1,
        stop:0 rgba(150, 186, 230, 255),
        stop:0.617 rgba(100, 146, 212, 255),
        stop:1 rgba(70, 122, 201, 255)
    );
}
QPushButton:pressed
{
    border: 1px solid rgba(170, 206, 250, 255);
    background: qlineargradient(spread:pad,
        x1:0, y1:0,
        x2:0, y2:1,
        stop:0 rgba(70, 122, 201, 255),
        stop:0.381 rgba(100, 146, 212, 255),
        stop:1 rgba(150, 186, 230, 255)
    );
}
QPushButton:flat
{
    border: none; /* no border for a flat push button */
    background: transparent;
}
QPushButton:default
{
    border: 1px outset rgba(165, 165, 165, 255);
}
QTabBar::tab
{
    color: rgba(25, 25, 25, 255);
    padding: 2px 12px 2px 12px;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
}
QTabBar::tab:selected
{
    background: qlineargradient(spread:pad,
        x1:0, y1:0,
        x2:0, y2:1,
        stop:0 rgba(235, 235, 235, 255),
        stop:1 rgba(255, 255, 255, 255)
    );
}
QTabBar::tab:!selected
{
    margin-top: 3px;
    color: rgb(135, 135, 135);
    background: qlineargradient(spread:pad,
        x1:0, y1:0,
        x2:0, y2:1,
        stop:0 rgba(215, 215, 215, 255),
        stop:1 rgba(235, 235, 235, 235)
    );
}
QTabBar::scroller
{
    width: 24px;
}
QTabBar QToolButton
{
    color: rgb(0, 0, 0);
}
QLabel
{
    padding: 0 3px;
    color: rgba(25, 25, 25, 255);
    background: none;
    font: normal;
}
QLineEdit
{
    color: rgba(25, 25, 25, 255);
}
QSpinBox,
QDoubleSpinBox
{
    color: rgba(25, 25, 25, 255);
}
QSpinBox::up-button,
QDoubleSpinBox::up-button
{
    image: url(%(up)s);
    border-width: 0px;
}
QSpinBox::down-button,
QDoubleSpinBox::down-button
{
    image: url(%(down)s);
    border-width: 0px;
}
QSpinBox::up-button:hover,
QDoubleSpinBox::up-button:hover,
QSpinBox::down-button:hover,
QDoubleSpinBox::down-button:hover
{
    background: qlineargradient(spread:pad,
        x1:0, y1:0,
        x2:0, y2:1,
        stop:0 rgba(195, 195, 195, 255),
        stop:0.617 rgba(170, 170, 170, 255),
        stop:1 rgba(155, 155, 155, 255)
    );
}
QSpinBox::up-button:pressed,
QDoubleSpinBox::up-button:pressed,
QSpinBox::down-button:pressed,
QDoubleSpinBox::down-button:pressed
{
    background: qlineargradient(spread:pad,
        x1:0, y1:0,
        x2:0, y2:1,
        stop:0 rgba(155, 155, 155, 255),
        stop:0.381 rgba(170, 170, 170, 255),
        stop:1 rgba(195, 195, 195, 255)
    );
}
QProgressBar
{
    text-align: center;
    vertical-align: center;
    color: rgba(25, 25, 25, 255);
    border-bottom-right-radius: 0px;
    border-top-right-radius:  0px;
    border-bottom-left-radius:  0px;
    border-top-left-radius:  0px;
    text-align: center;
}
QProgressBar::chunk
{
    background: qlineargradient(spread:pad,
        x1:0, y1:0,
        x2:0, y2:1,
        stop:0 rgba(150, 186, 230, 255),
        stop:0.617 rgba(100, 146, 212, 255),
        stop:1 rgba(70, 122, 201, 255)
    );
    color: rgba(25, 25, 25, 255);
    border-bottom-right-radius: 0px;
    border-top-right-radius: 0px;
    border-bottom-left-radius: 0px;
    border-top-left-radius: 0px;
}

QTreeView[class="Seasons"],
QTreeView QHeaderView {
    font-size: 12pt;
}

QListView,
QListWidget,
QTableView,
QTableWidget,
QTextEdit
{
    background-color: rgba(255, 255, 255, 255);
    color: rgba(25, 25, 25, 255);
}
QListView::item,
QListWidget::item
{
    background-color: rgba(235, 235, 235, 255);
    color: rgba(25, 25, 25, 255);
}
QListView::item:selected,
QListWidget::item:selected
{
    background-color: rgba(180, 180, 180, 255);
    color: rgba(25, 25, 25, 255);
    border-top: 1px solid 		rgba(215, 215, 215, 255);
    border-bottom: 1px solid 	rgba(135, 135, 135, 255);
    border-left: 1px solid 		rgba(205, 205, 205, 255);
    border-right: 1px solid		rgba(205, 205, 205, 255);
}
QTreeView,
QTreeWidget
{
    selection-background-color: transparent;
}
QTreeView::item:selected,
QTreeWidget::item:selected
{
    background-color: rgba(180, 180, 180, 255);
    color: rgba(25, 25, 25, 255);
}
QListView::item:alternate,
QTableWidget::item:alternate,
QListWidget::item:alternate
{
    background-color: rgba(245, 245, 245, 255);
    color: rgba(25, 25, 25, 255);
}
QListView::item:hover,
QListWidget::item:hover
{
    color: rgba(0, 0, 0, 255);
}
QListView::item:alternate:hover,
QListWidget::item:alternate:hover
{
    color: rgba(0, 0, 0, 255);
}
QTableView::item:selected,
QTableWidget::item:selected
{
    background-color: rgba(180, 180, 180, 255);
    color: rgba(25, 25, 25, 255);
}
QRadioButton,
QCheckBox
{
    color: rgba(25, 25, 25, 255);
}
QSlider
{
    background: none;
}
QSlider::groove:horizontal
{
    height: 5px; /* the groove expands to the size of the slider by default. by giving it a height, it has a fixed size */
    background: qlineargradient(spread:pad,
        x1:0, y1:0,
        x2:0, y2:1,
        stop:0 rgba(195, 195, 195, 255),
        stop:0.381 rgba(206, 206, 206, 255),
        stop:1 rgba(225, 225, 225, 255)
    );
    margin: 3px 0;
    border-radius: 3px;
}
QSlider::handle:horizontal
{
    background: qconicalgradient(cx:0.5, cy:0.5, angle:0,
        stop:0 			rgba(180, 180, 180, 255),
        stop:0.176136 rgba(120, 120, 120, 255),
        stop:0.5		rgba(180, 180, 180, 255),
        stop:0.664773 rgba(120, 120, 120, 255),
        stop:1			rgba(180, 180, 180, 255)
    );
    border: 0px solid rgb(142,142,142);
    width: 13px;
    margin: -4px 0; /* handle is placed by default on the contents rect of the groove. Expand outside the groove */
    border-radius: 6px;
}
QSlider::groove:vertical
{
    border: 1px solid rgba(105, 105, 105, 255);
    width: 6px; /* the groove expands to the size of the slider by default. by giving it a height, it has a fixed size */
    background: qlineargradient(spread:pad,
        x1:0, y1:0,
        x2:1, y2:0,
        stop:0 rgba(195, 195, 195, 255),
        stop:0.381 rgba(206, 206, 206, 255),
        stop:1 rgba(225, 225, 225, 255)
    );
    margin: 0 3px;
    border-radius: 3px;
}
QSlider::handle:vertical
{
    background: qconicalgradient(cx:0.5, cy:0.5, angle:0,
        stop:0 			rgba(180, 180, 180, 255),
        stop:0.176136	rgba(120, 120, 120, 255),
        stop:0.5		rgba(180, 180, 180, 255),
        stop:0.664773	rgba(120, 120, 120, 255),
        stop:1			rgba(180, 180, 180, 255)
    );
    border: 1px solid rgb(142,142,142);
    height: 12px;
    margin: 0 -4px; /* handle is placed by default on the contents rect of the groove. Expand outside the groove */
    border-radius: 6px;
}
QComboBox
{
    padding-right: 20px; /* make room for the arrows */
    color: rgba(25, 25, 25, 255);
}
QComboBox::drop-down
{
    border: none;
    image: url(%(down)s);
}
QComboBox:on
{
    background: qlineargradient(spread:pad,
        x1:0, y1:0,
        x2:0, y2:1,
        stop:0 rgba(229, 229, 229, 255),
        stop:0.617 rgba(210, 210, 210, 255),
        stop:1 rgba(199, 199, 199, 255)
    );
}
QComboBox::item
{
    background-color: rgba(255, 255, 255, 255);
}
QComboBox::item:selected
{
    background-color: rgb(90, 90, 90);
    color: rgb(255, 168, 0);
}
QComboBox QAbstractItemView
{
    selection-background-color: rgb(90, 90, 90);
    selection-color: rgb(255, 168, 0);
}
QStatusBar
{
    color: rgba(0, 88, 226, 255);
    font: normal;
}
QStatusBar::item
{
    spacing: 3px; /* spacing between menu bar items */
    padding: 6px 12px;
    border: 0;
    background: transparent;
    color: rgba(0, 88, 226, 255);
}
QScrollBar:down-arrow:vertical {
    image: url(%(cdown)s);
}
QScrollBar:up-arrow:vertical {
    image: url(%(cup)s);
}
QScrollBar:left-arrow:horizontal {
    image: url(%(left)s);
}

QScrollBar::right-arrow:horizontal {
    image: url(%(right)s);
}
QScrollBar:horizontal
{
    border: 0;
    background-color: rgba(215, 215, 215, 255);
    height: 15px;
    margin: 0 18px 0 18px;
}
QScrollBar::handle:horizontal
{
    background: qlineargradient(spread:pad,
        x1:0, y1:0,
        x2:0, y2:1,
        stop:0 rgba(150, 186, 230, 255),
        stop:0.617 rgba(100, 146, 212, 255),
        stop:1 rgba(70, 122, 201, 255)
    );
    min-width:20px;
}
QScrollBar::add-line:horizontal
{
    border: 0;
    background-color: rgba(215, 215, 215, 255);
    width: 15px;
    subcontrol-position: right;
    subcontrol-origin: margin;
}
QScrollBar::sub-line:horizontal
{
    border: 0;
    background-color: rgba(215, 215, 215, 255);
    width: 15px;
    subcontrol-position: left;
    subcontrol-origin: margin;
}
QScrollBar::sub-line:horizontal:hover, QScrollBar::add-line:horizontal::hover,
QScrollBar::sub-line:vertical:hover, QScrollBar::add-line:vertical:hover
{
    background: qlineargradient(spread:pad,
        x1:0, y1:0,
        x2:0, y2:1,
        stop:0 rgba(150, 186, 230, 255),
        stop:0.617 rgba(100, 146, 212, 255),
        stop:1 rgba(70, 122, 201, 255)
    );
}
QScrollBar::sub-line:horizontal::pressed, QScrollBar::add-line:horizontal::pressed,
QScrollBar::sub-line:vertical:pressed, QScrollBar::add-line:vertical:pressed
{
    background: qlineargradient(spread:pad,
        x1:0, y1:0,
        x2:0, y2:1,
        stop:0 rgba(70, 122, 201, 255),
        stop:0.381 rgba(100, 146, 212, 255),
        stop:1 rgba(150, 186, 230, 255)
    );
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical,
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal
{
    background: none;
}
QScrollBar:vertical
{
    border: 0;
    background-color: rgba(215, 215, 215, 255);
    width: 15px;
    margin: 18px 0 18px 0;
}
QScrollBar::handle:vertical
{
    background: qlineargradient(spread:pad,
        x1:0, y1:0,
        x2:1, y2:0,
        stop:0 rgba(150, 186, 230, 255),
        stop:0.617 rgba(100, 146, 212, 255),
        stop:1 rgba(70, 122, 201, 255)
    );
    min-height: 20px;
}
QScrollBar::add-line:vertical
{
    border: 0;
    background-color: rgba(215, 215, 215, 255);
    height: 15px;
    subcontrol-position: bottom;
    subcontrol-origin: margin;
}
QScrollBar::sub-line:vertical
{
    border: 0;
    background-color: rgba(215, 215, 215, 255);
    height: 15px;
    subcontrol-position: top;
    subcontrol-origin: margin;
}
QMainWindow::separator
{
    width: 3px;
}
QSplitter::handle
{
    border-radius: 0px;
    width: 2px;
    height: 5px;
    margin: 0px;
}
QWidget[class="scrollBack"] {
    /* background-image: url('./assets/wooden-texture.png') 0 0 0 0 stretch stretch; */
    background-color: #eee;
}
QLabel:disabled,
QCheckBox:disabled,
QLineEdit:disabled,
QComboBox:disabled,
QSpinBox:disabled,
QDoubleSpinBox:disabled,
QPushButton:disabled,
QMenu::item:disabled,
QMenuBar::item:disabled
{
    color: rgba(115, 115, 115, 255);
}
QScrollArea QWidget {
    background-color: #eee;
}
QScrollArea QLineEdit {

}
QLineEdit:disabled,
QComboBox:disabled,
QSpinBox:disabled,
QDoubleSpinBox:disabled
{
    border: 1px solid rgba(205, 205, 205, 255);
    background-color: rgba(235, 235, 235, 255);
}
QToolButton:disabled
{
    background-color: rgba(235, 235, 235, 255);
}
QWidget[class="fieldWidget"] {
    border: 1px solid #EEE;
}
QWidget[class="ratingWidget"],
QWidget[class="genreWidget"] {
    background-color: #EEE;
}
QLabel[class="field"] {
    background-color: qlineargradient(spread:pad,
        x1:0, y1:0,
        x2:0, y2:1,
        stop:0 rgba(70, 122, 201, 255),
        stop:0.381 rgba(100, 146, 212, 255),
        stop:1 rgba(150, 186, 230, 255)
    );
    border-radius: 3px;
    font-size: 8pt;
    font-weight: bold;
    border-bottom: 1px solid black;
    color: #000;
}
QPlainTextEdit[class="fieldtextedit"],
QLineEdit[class="fieldedit"] {
    background-color: #CCC;
    color: #000;
    border: 2px transparent solid;
    border-bottom: 2px solid black;
    font-size: 11pt;
    margin-top: 1px;
    margin-bottom: 1px;
}
QLabel[class="genre"] {
    background-color: #742;
    color: #FFF;
    padding: 2px;
    padding-top: 5px;
    padding-bottom: 5px;
    margin: 1px;
    font-size: 9pt;
    border: 1px outset #233;
}
QCommandLinkButton {
    font-size: 7pt;
}
Qmenu[class="ratingMenu"] {
    icon-size: 100px;
}
QToolButton { /* all types of tool button */
    border: 2px solid #8f8f91;
    /*margin-right: 4px;*/
    border-radius: 6px;
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #f6f7fa, stop: 1 #dadbde);
}

QToolButton[class="filter"] { /* only for MenuButtonPopup */
    padding-right: 20px; /* make way for the popup button */
}

QToolButton:pressed {
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #dadbde, stop: 1 #f6f7fa);
}


QToolButton::menu-button {
    border: 2px solid gray;
    border-top-right-radius: 6px;
    border-bottom-right-radius: 6px;
    /* 16px width + 4px for border = 20px allocated above */
}
QToolButton:open { /* when the button has its menu open */
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #dadbde, stop: 1 #f6f7fa);
}

QToolButton::menu-indicator {
    image: url(%(down)s);
    subcontrol-origin: padding;
    subcontrol-position: bottom right;
}

QToolButton::menu-indicator:pressed, QToolButton::menu-indicator:open {
    position: relative;
    top: 2px; left: 2px; /* shift the arrow by 2 px */
}
"""

def urlpath(path):
    val = os.path.relpath(path, PARENT)
    val = pathname2url(val)
    return val



def style():

    vals = {
        "up": urlpath(getfile("up")),
        "down": urlpath(getfile("down")),
        "left":  urlpath(getfile("caret-left")),
        "right":  urlpath(getfile("caret-right")),
        "cup":  urlpath(getfile("caret-up")),
        "cdown":  urlpath(getfile("caret-down")),
    }
    return _style % vals
