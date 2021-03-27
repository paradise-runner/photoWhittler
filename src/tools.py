import os
from typing import Dict
from PIL import Image
import shutil

from PyQt5.QtCore import QPoint, QRect, Qt
from PyQt5.QtGui import QPainter, QPixmap

from src.constants import TEMP_PATH, THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT
from src.whittle_file import WhittleFile


def join_pixmap(p1, p2, mode=QPainter.CompositionMode_SourceOver):
    s = p1.size()
    result = QPixmap(s)
    result.fill(Qt.transparent)
    painter =QPainter(result)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.drawPixmap(QPoint(), p1)
    painter.setCompositionMode(mode)
    painter.drawPixmap(QRect(0, 0, 24, 24), p2, p2.rect())
    painter.end()
    return result


def save_image_as_thumbnail(jpeg_file_path):
    wf = WhittleFile(jpeg_file_path)
    destination_file_path = os.path.join(TEMP_PATH, f"{wf.file_name}.jpg")
    im = Image.open(jpeg_file_path)
    im.thumbnail((THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT))
    im.save(destination_file_path, "JPEG")

    return destination_file_path


def get_next_key(_dict: Dict, key):
    current_index = list(_dict.keys()).index(key)
    next_key_index = current_index + 1
    try:
        return list(_dict.keys())[next_key_index]
    except IndexError:
        return None


def get_previous_key(dict: Dict, key):
    current_index = list(dict.keys()).index(key)
    previous_key_index = current_index - 1
    try:
        return list(dict.keys())[previous_key_index]
    except IndexError:
        return None


def thread_safe_file_copy(file_copy_tuple):
    current_location = file_copy_tuple[0]
    destination = file_copy_tuple[1]
    shutil.copy(current_location, destination)


def thread_safe_file_move(file_move_tuple):
    current_location = file_move_tuple[0]
    destination = file_move_tuple[1]
    shutil.move(current_location, destination)

