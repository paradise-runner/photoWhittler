import sys

from PyQt5.QtWidgets import QApplication

from src.whittler import Whittler

if __name__ == '__main__':
    app = QApplication(sys.argv)
    screen_geometry = app.desktop().screenGeometry()
    width, height = screen_geometry.width(), screen_geometry.height()
    whittler = Whittler(width, height)
    whittler.show()
    sys.exit(app.exec_())
