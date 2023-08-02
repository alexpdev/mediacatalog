from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

import os
import sys
from pathlib import Path
import json

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
    
    