import os

from PIL import Image
from PyQt5.QtCore import QPoint, QRect, Qt
from PyQt5.QtGui import QPainter, QPixmap

from src.constants import THUMBNAIL_SIZE
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
    destination_file_path = os.path.join(os.getcwd(), "_temp", f"{wf.file_name}.jpg")
    with Image.open(jpeg_file_path) as im:
        im.thumbnail(THUMBNAIL_SIZE)
        im.save(destination_file_path, "JPEG")
    return destination_file_path
