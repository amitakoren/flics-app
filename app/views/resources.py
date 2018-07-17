import os

from PyQt5.QtGui import QIcon

RESOURCES_DIR = os.path.abspath('./resources')

# Icons
ICONS_DIR = os.path.join(RESOURCES_DIR, 'icons')
ICON_DICT = {
    'window': os.path.join(ICONS_DIR, 'window.png'),
    'new_file': os.path.join(ICONS_DIR, 'new_file.png'),
    'save': os.path.join(ICONS_DIR, 'save.png'),
    'restart': os.path.join(ICONS_DIR, 'restart.png'),
    'exit': os.path.join(ICONS_DIR, 'exit.png'),
    'undo': os.path.join(ICONS_DIR, 'undo.png'),
    'readme': os.path.join(ICONS_DIR, 'readme.png')
}


def get_icon(key: str):
    return QIcon(ICON_DICT[key])
