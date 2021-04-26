import os
from typing import Dict
from PIL import Image
import shutil

from PyQt5.QtCore import QPoint, QRect, Qt
from PyQt5.QtGui import QPainter, QPixmap

from src.constants import TEMP_PATH
from src.whittle_file import WhittleFile


def join_pixmap(
        main_pixmap,
        icon_pixmap,
        screen_width: int,
        screen_height: int,
        mode=QPainter.CompositionMode_SourceOver
):
    s = main_pixmap.size()
    result = QPixmap(s)
    result.fill(Qt.transparent)
    painter =QPainter(result)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.drawPixmap(QPoint(), main_pixmap)
    painter.setCompositionMode(mode)
    vote_icon_width = get_width(screen_width, 24)
    vote_icon_height = get_height(screen_height, 24)
    painter.drawPixmap(
        QRect(0, 0, vote_icon_width, vote_icon_height),
        icon_pixmap, icon_pixmap.rect()
    )
    painter.end()
    return result


def save_image_as_thumbnail(thumbnail_save_info):
    jpeg_file_path, thumbnail_width, thumbnail_height = *thumbnail_save_info,

    wf = WhittleFile(jpeg_file_path)
    destination_file_path = os.path.join(TEMP_PATH, f"{wf.file_name}.jpg")
    im = Image.open(jpeg_file_path)
    im.thumbnail((thumbnail_width, thumbnail_height))
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


def get_width(screen_width: int, object_width: int):
    width_ratio = 1920 / object_width
    return screen_width / width_ratio


def get_height(screen_height: int, object_height: int):
    height_ratio = 1080 / object_height
    return screen_height / height_ratio
