import os
import shutil
import pickle
from typing import List
from concurrent.futures import ThreadPoolExecutor

from PyQt5.QtCore import QDir, Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import (
    QLabel,
    QWidget,
    QMenu,
    QAction,
    QFileDialog,
    QScrollArea,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
)

from src.general_window import GeneralWindow
from src.load_save_dialog import LoadSaveDialog
from src.tools import save_image_as_thumbnail, join_pixmap
from src.whittle_file import WhittleFile
from src.whittle_state import WhittleState
from src.constants import (
    JPG_EXTENSION,
    VALID_EXTENSIONS,
    BUTTON_STYLE,
    UPVOTED_FOLDER_NAME,
    RAW_EXTENSIONS,
    CHECKMARK_ICON_PATH,
    X_MARK_ICON_PATH,
    SAVE_STATE_PATH,
    RAW_UNEDITED_FOLDER_NAME,
    JPG_UNEDITED_FOLDER_NAME,
    TEMP_PATH,
)


class Whittler(GeneralWindow):

    def __init__(self):
        self.voting_dict = {}
        self.folder_path = None
        self.photo_picker_dict = {}
        self.whittled = False

        self.checkmark_icon = QIcon(CHECKMARK_ICON_PATH)
        self.x_mark_icon = QIcon(X_MARK_ICON_PATH)

        super().__init__()

        self.create_actions()
        self.create_menus()

        self.setWindowTitle("Photo Whittler")

        self.initUI()
        state = self.load_state()

        if state is not None:
            if state.whittled:
                return

        if state is not None and os.path.exists(str(state.folder_path)):
            self.load_save_dialog_box(state)

    def initUI(self):
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

    def create_actions(self):
        self.openFolderAct = QAction(
            "&Open Folder", self, shortcut="Ctrl+O", triggered=self.open_folder
        )
        self.organizeFolderAct = QAction(
            "&Organize Folder", self, shortcut="Ctrl+N", triggered=self.organize_folder
        )
        self.clearSateStateAct = QAction(
            "&Clear Save Sate", self, shortcut="Ctrl+E", triggered=self.clear_save_state
        )

    def create_menus(self):
        self.fileMenu = QMenu("&File", self)
        self.fileMenu.addAction(self.openFolderAct)
        self.fileMenu.addAction(self.organizeFolderAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.clearSateStateAct)

        self.menuBar().addMenu(self.fileMenu)

    def load_save_dialog_box(self, state):
        dialog = LoadSaveDialog()
        if dialog.exec_():
            self.folder_path = state.folder_path
            self.whittled = state.whittled
            self.open_folder(state.folder_path)
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

    def clear_save_state(self):
        if os.path.exists(SAVE_STATE_PATH):
            os.remove(SAVE_STATE_PATH)

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

    def organize_folder(self):
        def move_organized_files(organized_file_paths):
            current_location = organized_file_paths[0]
            destination = organized_file_paths[1]
            shutil.move(current_location, destination)

        organize_folder = QFileDialog.getExistingDirectory(self, "Open Folder", QDir.currentPath())
        if not os.path.exists(str(organize_folder)):
            return

        organize_dict = {}
        for file in os.listdir(organize_folder):
            wf = WhittleFile(os.path.join(organize_folder, file))
            if {wf.file_extension}.issubset(VALID_EXTENSIONS):
                if organize_dict.get(wf.file_name) is None:
                    organize_dict[wf.file_name] = {wf}
                else:
                    organize_dict[wf.file_name].add(wf)

        if not organize_dict:
            return None

        organize_dict = {
            file_name: wf_set for file_name, wf_set in organize_dict.items() if len(wf_set) == 2
        }
        if not organize_dict:
            return None

        file_extensions = []
        for file_name, wf_set in organize_dict.items():
            for wf in wf_set:
                file_extensions.append(wf.file_extension)

        file_extensions = set(file_extensions)
        if len(file_extensions) != 2:
            return None

        raw_unedited_folder_path = (os.path.join(organize_folder, RAW_UNEDITED_FOLDER_NAME))
        jpeg_unedited_folder_path = (os.path.join(organize_folder, JPG_UNEDITED_FOLDER_NAME))

        os.makedirs(raw_unedited_folder_path, exist_ok=True)
        os.makedirs(jpeg_unedited_folder_path, exist_ok=True)

        file_movement_list = []

        for file_name, wf_set in organize_dict.items():
            for wf in wf_set:
                if {wf.file_extension}.issubset(RAW_EXTENSIONS):
                    file_movement_list.append(
                        (
                            wf.file_path,
                            os.path.join(raw_unedited_folder_path, wf.file_name+wf.file_extension)
                        )
                    )
                else:
                    file_movement_list.append(
                        (
                            wf.file_path,
                            os.path.join(jpeg_unedited_folder_path, wf.file_name + wf.file_extension)
                        )
                    )

        with ThreadPoolExecutor() as tpe:
            tpe.map(move_organized_files, file_movement_list)

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
        if not os.path.exists(TEMP_PATH):
            os.makedirs(TEMP_PATH, exist_ok=True)

        thumbnails = [
            file for file in os.listdir(
                os.path.join(TEMP_PATH)
            ) if file.lower().endswith(JPG_EXTENSION)
        ]
        if thumbnails:
            for file in thumbnails:
                path = os.path.join(TEMP_PATH, file)
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