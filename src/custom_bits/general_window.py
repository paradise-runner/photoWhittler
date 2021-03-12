from PyQt5.QtWidgets import (
    QMainWindow,
)

from src.constants import BACKGROUND_COLOR, WINDOW_WIDTH, WINDOW_HEIGHT


class GeneralWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setStyleSheet(BACKGROUND_COLOR)

        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)

