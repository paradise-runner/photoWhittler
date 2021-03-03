import sys
import os
import shutil
import pickle
from typing import List
from concurrent.futures import ThreadPoolExecutor

from PIL import Image
from PyQt5.QtCore import QDir, Qt, QSize, QPoint, QRect
from PyQt5.QtGui import QPixmap, QIcon, QPainter
from PyQt5.QtWidgets import (
    QLabel,
    QWidget,
    QMainWindow,
    QMenu,
    QAction,
    QFileDialog,
    QScrollArea,
    QHBoxLayout,
    QVBoxLayout,
    QApplication,
    QPushButton,
)

from load_save_dialog import LoadSaveDialog, WhittleState
from constants import (
    JPG_EXTENSION,
    WhittleFile,
    VALID_EXTENSIONS,
    BACKGROUND_COLOR,
    BUTTON_STYLE,
    UPVOTED_FOLDER_NAME,
    RAW_EXTENSIONS,
    CHECKMARK_ICON_PATH,
    X_MARK_ICON_PATH,
    THUMBNAIL_SIZE,
    SAVE_STATE_PATH,
)


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


class Whittler(QMainWindow):

    def __init__(self):
        self.voting_dict = {}
        self.folder_path = None
        self.photo_picker_dict = {}
        self.whittled = False

        self.checkmark_icon = QIcon(CHECKMARK_ICON_PATH)
        self.x_mark_icon = QIcon(X_MARK_ICON_PATH)

        super().__init__()

        self.setStyleSheet(BACKGROUND_COLOR)

        self.windowLayout = QVBoxLayout()
        self.workingLayout = QHBoxLayout()

        self.photoLayout = QVBoxLayout()
        self.actionsLayout = QVBoxLayout()

        self.selectedImage = QLabel()

        self.photoLayout.addStretch()
        self.photoLayout.addWidget(self.selectedImage)
        self.photoLayout.addStretch()

        self.upvote_button = QPushButton("Upvote", self)
        self.upvote_button.setStyleSheet(BUTTON_STYLE)
        self.downvote_button = QPushButton("Downvote", self)
        self.downvote_button.setStyleSheet(BUTTON_STYLE)
        self.whittle_button = QPushButton("Whittle", self)
        self.whittle_button.setStyleSheet(BUTTON_STYLE)
        self.whittle_button.clicked.connect(self.whittle)

        self.actionsLayout.addWidget(self.upvote_button, alignment=Qt.AlignLeft)
        self.actionsLayout.addWidget(self.downvote_button, alignment=Qt.AlignLeft)
        self.actionsLayout.addWidget(self.whittle_button, alignment=Qt.AlignLeft)

        self.workingLayout.addLayout(self.photoLayout, 4)
        self.workingLayout.addLayout(self.actionsLayout, 1)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFixedHeight(130)
        widget_content = QWidget()
        self.scroll_area.setWidget(widget_content)
        self.photoPickerLayout = QHBoxLayout(widget_content)

        self.windowLayout.addLayout(self.workingLayout, 2)
        self.windowLayout.addWidget(self.scroll_area)

        widget = QWidget()
        widget.setLayout(self.windowLayout)
        self.setCentralWidget(widget)

        self.create_actions()
        self.create_menus()

        self.setWindowTitle("Whittler")
        self.resize(1000, 600)
        state = self.load_state()

        if state.whittled:
            return

        if state is not None and os.path.exists(str(state.folder_path)):
            self.load_save_dialog_box(state)

    def load_save_dialog_box(self, state):
        dialog = LoadSaveDialog()
        if dialog.exec_():
            self.folder_path = state.folder_path
            self.whittled = state.whittled
            self.open_folder()
            self.voting_dict = state.voting_dict
            for file_name, wf_set in self.voting_dict.items():
                wf = next(iter(wf_set))
                if wf.edit_file is not None:
                    if wf.edit_file:
                        self._upvote_main_photo(wf.file_path)
                    else:
                        self._downvote_main_photo(wf.file_path)
        else:
            return

    def whittle(self):
        def copy_files_to_upvoted_folder(upvote_file_path):
            current_location = upvote_file_path[0]
            destination = upvote_file_path[1]
            shutil.copy(current_location, destination)

        if not self.voting_dict:
            return

        upvote_file_paths = []

        os.makedirs(os.path.join(self.folder_path, UPVOTED_FOLDER_NAME), exist_ok=True)

        for file_name, wf_set in self.voting_dict.items():
            raw_w_file = next(wf for wf in wf_set if {wf.file_extension}.issubset(RAW_EXTENSIONS))

            if not raw_w_file.edit_file:
                continue

            upvoted_file_path = os.path.join(
                self.folder_path,
                UPVOTED_FOLDER_NAME,
                f"{raw_w_file.file_name}{raw_w_file.file_extension}"
            )

            upvote_file_paths.append((raw_w_file.file_path, upvoted_file_path))

        with ThreadPoolExecutor() as tpe:
            tpe.map(copy_files_to_upvoted_folder, upvote_file_paths)

        self.whittled = True

    def open_folder(self, folder_path=None):
        self.voting_dict = {}
        self.photo_picker_dict = {}
        if not os.path.exists(str(folder_path)):
            folder_path = None
        if folder_path is None:
            self.folder_path = QFileDialog.getExistingDirectory(self, "Open Folder", QDir.currentPath())
        else:
            self.folder_path = folder_path
        for root, dir, files in os.walk(self.folder_path):
            for file in files:
                wf = WhittleFile(os.path.join(root, file))
                if {wf.file_extension}.issubset(VALID_EXTENSIONS):
                    if self.voting_dict.get(wf.file_name) is None:
                        self.voting_dict[wf.file_name] = {wf}
                    else:
                        self.voting_dict[wf.file_name].add(wf)
        if not self.voting_dict:
            return

        # filter out file_names that don't have a JPG whittle file as we want to load those into
        # memory
        self.voting_dict = {
            file_name: wf_set for file_name, wf_set in self.voting_dict.items() if
            any([wf.file_extension == JPG_EXTENSION for wf in wf_set])
        }
        if not self.voting_dict:
            return

        # before we create new thumbnails, delete any that exit in cwd
        self.clean_up_temp()

        file_names = list(self.voting_dict.keys())
        jpg_photo_file_paths = []
        for file_name in file_names:
            wf = next(
                wf for wf in self.voting_dict[file_name] if wf.file_extension == JPG_EXTENSION
            )
            jpg_photo_file_paths.append(wf.file_path)

        with ThreadPoolExecutor() as tpe:
            results = tpe.map(save_image_as_thumbnail, jpg_photo_file_paths)
        photo_file_paths = list(results)
        photo_file_paths.sort()

        self.clear_programmatically_populated_layouts()
        self.populate_photo_picker(photo_file_paths)

        full_res = self.get_full_res_photo_path(photo_file_paths[0])
        self.set_main_photo(full_res)

    def get_full_res_photo_path(self, photo_file_path):
        file_name = WhittleFile(photo_file_path).file_name
        return next(
            wf.file_path for wf in self.voting_dict[file_name] if wf.file_extension == JPG_EXTENSION
        )

    def set_main_photo(self, file_path):
        if not os.path.exists(str(file_path)):
            return
        pixmap = QPixmap(file_path)
        pixmap = pixmap.scaled(600, 600, Qt.KeepAspectRatio)
        self.selectedImage.setPixmap(pixmap)

        try:
            self.upvote_button.clicked.disconnect()
        except Exception:
            pass
        try:
            self.downvote_button.clicked.disconnect()
        except Exception:
            pass

        self.upvote_button.clicked.connect(
            lambda checked, _file_path=file_path: self._upvote_main_photo(_file_path)
        )
        self.downvote_button.clicked.connect(
            lambda checked, _file_path=file_path: self._downvote_main_photo(_file_path)
        )

    def populate_photo_picker(self, photo_file_paths: List):
        def _get_icon(photo_file_path):
            return QIcon(photo_file_path)

        if not photo_file_paths:
            return

        with ThreadPoolExecutor(max_workers=20) as tpe:
            results = tpe.map(_get_icon, photo_file_paths)

        icons = list(results)
        for photo_file_path, icon in zip(photo_file_paths, icons):
            photo_button = QPushButton()
            photo_button.setStyleSheet(BUTTON_STYLE)
            photo_button.setIcon(icon)
            photo_button.setIconSize(QSize(100, 100))
            photo_button.setFixedSize(130, 100)
            full_res_file_path = self.get_full_res_photo_path(photo_file_path)
            photo_button.clicked.connect(
                lambda checked, _path=full_res_file_path: self.set_main_photo(_path))
            self.photoPickerLayout.addWidget(photo_button)
            self.photo_picker_dict.update(
                {WhittleFile(photo_file_path).file_name: (photo_button, photo_file_path)}
            )

    def create_actions(self):
        self.openFolderAct = QAction(
            "&Open Folder", self, shortcut="Ctrl+O", triggered=self.open_folder
        )
        self.exitAct = QAction("&Exit", self, shortcut="Ctrl+Q", triggered=self.close)

    def create_menus(self):
        self.fileMenu = QMenu("&File", self)
        self.fileMenu.addAction(self.openFolderAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.menuBar().addMenu(self.fileMenu)

    def clear_programmatically_populated_layouts(self):
        while self.photoPickerLayout.count():
            child = self.photoPickerLayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.selectedImage.setPixmap(QPixmap())

    def _upvote_main_photo(self, file_path):
        wf_name = WhittleFile(file_path).file_name
        wf_set = self.voting_dict.get(wf_name)

        if wf_set is None:
            return

        for wf in wf_set:
            wf.edit_file = True
        upvoted_photo_button = self.photo_picker_dict[wf_name][0]
        thumbnail_file_path = self.photo_picker_dict[wf_name][1]
        self._update_button_with_vote(
            upvoted_photo_button,
            thumbnail_file_path,
            CHECKMARK_ICON_PATH,
        )
        self.voting_dict[wf_name] = wf_set

    def _downvote_main_photo(self, file_path):
        wf_name = WhittleFile(file_path).file_name
        wf_set = self.voting_dict.get(wf_name)

        if wf_set is None:
            return

        for wf in wf_set:
            wf.edit_file = False

        downvoted_photo_button = self.photo_picker_dict[wf_name][0]
        thumbnail_file_path = self.photo_picker_dict[wf_name][1]
        self._update_button_with_vote(
            downvoted_photo_button,
            thumbnail_file_path,
            X_MARK_ICON_PATH,
        )

    @staticmethod
    def clean_up_temp():
        thumbnails = [
            file for file in os.listdir(
                os.path.join(os.getcwd(), "_temp")
            ) if file.lower().endswith(JPG_EXTENSION)
        ]
        if thumbnails:
            for file in thumbnails:
                path = os.path.join(os.getcwd(), "_temp", file)
                os.remove(path)

    @staticmethod
    def _update_button_with_vote(button, thumbnail_path, icon_path):
        temp_icon = QIcon()
        main_image_pixmap = QPixmap(thumbnail_path)
        icon_image_pixmap = QPixmap(icon_path)
        result = join_pixmap(main_image_pixmap, icon_image_pixmap)
        temp_icon.addPixmap(result)
        button.setIcon(temp_icon)
        button.setIconSize(QSize(100, 100))

    def save_state(self):
        if os.path.exists(SAVE_STATE_PATH):
            os.remove(SAVE_STATE_PATH)
        with open(SAVE_STATE_PATH, "wb") as file:
            pickle.dump(
                WhittleState(self.folder_path, self.voting_dict, self.whittled),
                file,
                pickle.HIGHEST_PROTOCOL
            )

    @staticmethod
    def load_state():
        if os.path.exists(SAVE_STATE_PATH):
            with open(SAVE_STATE_PATH, "rb") as file:
                return pickle.load(file)
        return None

    def closeEvent(self, event):
        self.clean_up_temp()
        self.save_state()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    whittler = Whittler()
    whittler.show()
    sys.exit(app.exec_())
