from PyQt5.QtWidgets import (
    QMainWindow,
)

from src.constants import BACKGROUND_COLOR, WINDOW_WIDTH, WINDOW_HEIGHT
from src.tools import get_width, get_height


class GeneralWindow(QMainWindow):

    def __init__(self, screen_width, screen_height):
        super().__init__()

        self.setStyleSheet(BACKGROUND_COLOR)

        self.resize(
            get_width(screen_width, WINDOW_WIDTH),
            get_height(screen_height, WINDOW_HEIGHT)
        )
        self.setFixedSize(self.size())
