import os
import shutil
import pickle
from typing import List
from concurrent.futures import ThreadPoolExecutor

from PyQt5.QtCore import QDir, Qt, QSize, QEvent
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
    QInputDialog
)

from src.custom_bits.general_window import GeneralWindow
from src.tools import (
    save_image_as_thumbnail,
    join_pixmap,
    get_previous_key,
    get_next_key,
    get_width,
    get_height,
)
from src.whittle_file import WhittleFile
from src.whittle_state import WhittleState
from src.custom_bits.dialogs import (
    LoadSaveDialog,
    ErrorDialog,
    ActionCompleteDialog,
)
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
    PHOTO_PICKER_HEIGHT,
    MAIN_PHOTO_HEIGHT_AND_WIDTH,
    THUMBNAIL_WIDTH,
    THUMBNAIL_HEIGHT,
    PICKER_BUTTON_WIDTH,
    PICKER_BUTTON_HEIGHT,
    PICKER_BUTTON_STYLE,
    SELECTED_PICKER_BUTTON_STYLE,
    LIGHT_TEXT_COLOR,
    WHITTLE_BUTTON_STYLE,
    UPVOTE_BUTTON_STYLE,
    DOWNVOTE_BUTTON_STYLE,
)


class Whittler(GeneralWindow):

    def __init__(self, screen_width, screen_height):
        self.voting_dict = {}
        self.folder_path = None
        self.photo_picker_dict = {}
        self.whittled = False
        self.main_photo_file_path = None
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.checkmark_icon = QIcon(CHECKMARK_ICON_PATH)
        self.x_mark_icon = QIcon(X_MARK_ICON_PATH)

        super().__init__(screen_width, screen_height)

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

    def _get_width(self, object_width):
        return get_width(self.screen_width, object_width)

    def _get_height(self, object_height):
        return get_height(self.screen_height, object_height)

    def eventFilter(self, source, event):
        # Over-ride the scrolling of the key presses to move between main photos along the photo
        # picker
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Right:
                self._set_next_photo_as_main()
            elif event.key() == Qt.Key_Left:
                self._set_previous_photo_as_main()
            elif event.key() == Qt.Key_Up:
                self._upvote_main_photo()
            elif event.key() == Qt.Key_Down:
                self._downvote_main_photo()
            return True
        return super(Whittler, self).eventFilter(source, event)

    def initUI(self):
        self.windowLayout = QVBoxLayout()

        self.workingLayout = QHBoxLayout()

        self.photoLayout = QVBoxLayout()
        self.actionsLayout = QVBoxLayout()
        self.missionControlLayout = QHBoxLayout()
        self.buttonLayout = QHBoxLayout()

        self.selectedImage = QLabel()

        self.photoLayout.addWidget(self.selectedImage)

        self.upvote_button = QPushButton("Upvote", self)
        self.upvote_button.setStyleSheet(UPVOTE_BUTTON_STYLE)
        self.downvote_button = QPushButton("Downvote", self)
        self.downvote_button.setStyleSheet(DOWNVOTE_BUTTON_STYLE)

        self.statsLabel = QLabel(self)
        self.statsLabel.setStyleSheet(LIGHT_TEXT_COLOR)
        self.whittle_button = QPushButton("Whittle", self)
        self.whittle_button.setStyleSheet(WHITTLE_BUTTON_STYLE)
        self.whittle_button.clicked.connect(self.whittle)

        self.actionsLayout.addLayout(self.missionControlLayout)
        self.actionsLayout.addLayout(self.buttonLayout)
        self.actionsLayout.setContentsMargins(10, 0, 10, 0)

        self.missionControlLayout.addWidget(self.statsLabel, alignment=Qt.AlignLeft)
        self.missionControlLayout.addWidget(self.whittle_button, alignment=Qt.AlignRight)

        self.buttonLayout.addWidget(self.upvote_button, alignment=Qt.AlignLeft)
        self.buttonLayout.addWidget(self.downvote_button, alignment=Qt.AlignRight)

        # self.workingLayout.
        self.workingLayout.addLayout(self.photoLayout, 2)
        self.workingLayout.addLayout(self.actionsLayout, 1)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.installEventFilter(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFixedHeight(self._get_height(PHOTO_PICKER_HEIGHT))
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        widget_content = QWidget()
        self.scroll_area.setWidget(widget_content)
        self.photoPickerLayout = QHBoxLayout(widget_content)
        self.photoPickerLayout.setSpacing(5)

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
        self.archivePhotosAct = QAction(
            "&Organize Folder", self, shortcut="Ctrl+M", triggered=self.archive_photos
        )

    def create_menus(self):
        self.fileMenu = QMenu("&File", self)
        self.fileMenu.addAction(self.openFolderAct)
        self.fileMenu.addAction(self.archivePhotosAct)
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
            self._set_stats()
            for file_name, wf_set in self.voting_dict.items():
                wf = next(iter(wf_set))
                voted_photo_button = self.photo_picker_dict[wf.file_name][0]
                thumbnail_file_path = self.photo_picker_dict[wf.file_name][1]
                if wf.edit_file is not None:
                    if wf.edit_file:
                        icon_path = CHECKMARK_ICON_PATH
                    else:
                        icon_path = X_MARK_ICON_PATH
                    self._update_button_with_vote(
                        voted_photo_button,
                        thumbnail_file_path,
                        icon_path,
                    )
            return

    def whittle(self):
        if not self.voting_dict:
            ErrorDialog(
                error="Unable to Whittle files",
                error_reason="No photos imported to Whittler to take action on.",
            ).exec_()
            return

        upvote_file_paths = []

        os.makedirs(os.path.join(self.folder_path, UPVOTED_FOLDER_NAME), exist_ok=True)

        for file_name, wf_set in self.voting_dict.items():
            raw_w_file = next((wf for wf in wf_set if {wf.file_extension}.issubset(RAW_EXTENSIONS)), None)

            if raw_w_file is None:
                continue

            if not raw_w_file.edit_file:
                continue

            upvoted_file_path = os.path.join(
                self.folder_path,
                UPVOTED_FOLDER_NAME,
                f"{raw_w_file.file_name}{raw_w_file.file_extension}"
            )

            upvote_file_paths.append((raw_w_file.file_path, upvoted_file_path))

        if not upvote_file_paths:
            ErrorDialog(
                error="Unable to Whittle files",
                error_reason="No photos upvoted.  Please upvote photos to allow Whittling.",
            ).exec_()
            return

        with ThreadPoolExecutor() as tpe:
            tpe.map(thread_safe_file_copy, upvote_file_paths)

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

        if self.folder_path == "":
            return

        for root, dir, files in os.walk(self.folder_path):
            for file in files:
                wf = WhittleFile(os.path.join(root, file))
                if {wf.file_extension}.issubset(VALID_EXTENSIONS):
                    if self.voting_dict.get(wf.file_name) is None:
                        self.voting_dict[wf.file_name] = {wf}
                    else:
                        self.voting_dict[wf.file_name].add(wf)
        if not self.voting_dict:
            ErrorDialog(
                error="Unable to open folder",
                error_reason="Unable to locate any valid photo files at folder path.  "
                             "Please select a new folder to begin Whittling.",
                extra_info=f'Folder path: "{self.folder_path}".'
            ).exec_()
            return

        # filter out file_names that don't have a JPG whittle file as we want to load those into
        # memory
        self.voting_dict = {
            file_name: wf_set for file_name, wf_set in self.voting_dict.items() if
            any([wf.file_extension == JPG_EXTENSION for wf in wf_set])
        }
        if not self.voting_dict:
            ErrorDialog(
                error="Unable to open folder",
                error_reason="Unable to locate any valid JPG files at folder path.  "
                             "Please select a new folder to begin Whittling.",
                extra_info=f'Folder path: "{self.folder_path}".'
            ).exec_()
            return

        # before we create new thumbnails, delete any that exit in cwd
        self._clean_up_temp()

        file_names = list(self.voting_dict.keys())
        thumbnail_save_info = []
        for file_name in file_names:
            wf = next(
                wf for wf in self.voting_dict[file_name] if wf.file_extension == JPG_EXTENSION
            )
            thumbnail_save_info.append(
                [wf.file_path, self._get_width(THUMBNAIL_WIDTH), self._get_height(THUMBNAIL_HEIGHT)]
            )

        with ThreadPoolExecutor() as tpe:
            results = tpe.map(save_image_as_thumbnail, thumbnail_save_info)
        photo_file_paths = list(results)
        photo_file_paths.sort()

        self._clear_programmatically_populated_layouts()
        self._populate_photo_picker(photo_file_paths)

        full_res = self._get_full_res_photo_path(photo_file_paths[0])
        self._set_main_photo(full_res)
        self._set_stats()

    def organize_folder(self, folder_path=None):

        if folder_path is None:
            organize_folder = QFileDialog.getExistingDirectory(self, "Open Folder", QDir.currentPath())
            if organize_folder == "":
                return
        else:
            organize_folder = folder_path

        organize_dict = {}
        for file in os.listdir(organize_folder):
            wf = WhittleFile(os.path.join(organize_folder, file))
            if {wf.file_extension}.issubset(VALID_EXTENSIONS):
                if organize_dict.get(wf.file_name) is None:
                    organize_dict[wf.file_name] = {wf}
                else:
                    organize_dict[wf.file_name].add(wf)

        if not organize_dict:
            ErrorDialog(
                error="Unable to organize folder",
                error_reason="Unable to locate any photo files with valid file extension types.",
                extra_info=f'Supported extension types: "{*VALID_EXTENSIONS,}".'
            ).exec_()
            return

        organize_dict = {
            file_name: wf_set for file_name, wf_set in organize_dict.items() if len(wf_set) == 2
        }
        if not organize_dict:
            ErrorDialog(
                error="Unable to organize folder",
                error_reason="Folder to organize did not contain any files where there were 2 file "
                             "types per unique photo.",
            ).exec_()
            return

        file_extensions = []
        for file_name, wf_set in organize_dict.items():
            for wf in wf_set:
                file_extensions.append(wf.file_extension)

        file_extensions = set(file_extensions)
        if len(file_extensions) != 2:
            ErrorDialog(
                error="Unable to organize folder",
                error_reason="Folder to organize contained more than two file extensions.",
                extra_info=f'File Extensions: "{*file_extensions,}"'
            ).exec_()
            return

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
            tpe.map(thread_safe_file_move, file_movement_list)

        ActionCompleteDialog(
            action="Folder Organization",
            action_message=f'Finished organizing "{os.path.basename(organize_folder)}" folder.'
        ).exec_()

    def archive_photos(self):
        unarchived_location = QFileDialog.getExistingDirectory(
            self, "Select Unarchived Photo Location", QDir.currentPath()
        )
        if unarchived_location == "":
            return

        # maybe make this part of a config that can be set?
        archive_location = QFileDialog.getExistingDirectory(
            self, "Select Archive Location", QDir.currentPath()
        )

        ok, archive_name = QInputDialog.getText(self, "Archive Name", "Enter Name")
        if ok and archive_name:
            pass
        elif not ok:
            return
        elif not archive_name:
            ErrorDialog(
                error="Unable to create archive folder",
                error_reason="No name was passed in for archive.",
            ).exec_()
            return

        archive_path = os.path.join(archive_location, archive_name)
        os.mkdir(archive_path, exist_ok=True)

        file_paths_to_archive = []
        for root, dir, files in os.walk(unarchived_location):
            for file in files:
                wf = WhittleFile(os.path.join(root, file))
                if {wf.file_extension}.issubset(VALID_EXTENSIONS):
                    files_to_archive.append(
                        (
                            wf.file_path,
                            os.path.join(archive_path, wf.file_name + wf.file_extension)
                        )
                    )

        with ThreadPoolExecutor() as tpe:
            tpe.map(thread_safe_file_move, file_paths_to_archive)

        dialog = OrganizeArchiveDialog()
        if dialog.exec_():
            self.organize_folder(archive_path)
        else:
            ActionCompleteDialog(
                action="Folder Archiving",
                action_message=f'Finished archiving photos from "{archive_name}" to '
                               f'"{os.path.basename(unarchived_location)}".'
            ).exec_()

    def _get_full_res_photo_path(self, photo_file_path):
        file_name = WhittleFile(photo_file_path).file_name
        return next(
            wf.file_path for wf in self.voting_dict[file_name] if wf.file_extension == JPG_EXTENSION
        )

    def _set_main_photo(self, file_path):
        if not os.path.exists(str(file_path)):
            return
        self.main_photo_file_path = file_path

        pixmap = QPixmap(file_path)
        pixmap = pixmap.scaled(
            self._get_width(MAIN_PHOTO_HEIGHT_AND_WIDTH),
            self._get_height(MAIN_PHOTO_HEIGHT_AND_WIDTH),
            Qt.KeepAspectRatio
        )
        self.selectedImage.setPixmap(pixmap)

        try:
            self.upvote_button.clicked.disconnect()
        except Exception:
            pass
        try:
            self.downvote_button.clicked.disconnect()
        except Exception:
            pass

        self.upvote_button.clicked.connect(self._upvote_main_photo)
        self.downvote_button.clicked.connect(self._downvote_main_photo)
        # Reset the color of all other buttons before setting new button color
        for file_name, photo_tuple in self.photo_picker_dict.items():
            photo_tuple[0].setStyleSheet(PICKER_BUTTON_STYLE)

        # Setting the color of the selected button to be a little lighter, for a nice touch
        photo_button = self.photo_picker_dict[WhittleFile(file_path).file_name][0]
        photo_button.setStyleSheet(SELECTED_PICKER_BUTTON_STYLE)

    def _set_next_photo_as_main(self):
        # Move along photo_picker_dict to set main photos
        if not os.path.exists(str(self.main_photo_file_path)):
            return None

        current_file_name = WhittleFile(self.main_photo_file_path).file_name
        next_file_name = get_next_key(self.photo_picker_dict, current_file_name)
        if next_file_name is None:
            return None

        full_res = next(
            wf.file_path for wf in self.voting_dict[next_file_name] if
            wf.file_extension == JPG_EXTENSION
        )
        self._set_main_photo(full_res)

    def _set_previous_photo_as_main(self):
        # Move along photo_picker_dict to set main photos
        if not os.path.exists(str(self.main_photo_file_path)):
            return None

        current_file_name = WhittleFile(self.main_photo_file_path).file_name
        previous_file_name = get_previous_key(self.photo_picker_dict, current_file_name)
        if previous_file_name is None:
            return None

        full_res = next(
            wf.file_path for wf in self.voting_dict[previous_file_name] if
            wf.file_extension == JPG_EXTENSION
        )
        self._set_main_photo(full_res)

    def _populate_photo_picker(self, photo_file_paths: List):
        def _get_icon(photo_file_path):
            return QIcon(photo_file_path)

        if not photo_file_paths:
            return

        with ThreadPoolExecutor() as tpe:
            results = tpe.map(_get_icon, photo_file_paths)

        icons = list(results)
        for photo_file_path, icon in zip(photo_file_paths, icons):
            photo_button = QPushButton()
            photo_button.setStyleSheet(PICKER_BUTTON_STYLE)
            photo_button.setIcon(icon)

            photo_button.setIconSize(
                QSize(
                    self._get_width(THUMBNAIL_WIDTH),
                    self._get_height(THUMBNAIL_HEIGHT),
                )
            )
            photo_button.setFixedSize(
                self._get_width(PICKER_BUTTON_WIDTH), self._get_height(PICKER_BUTTON_HEIGHT)
            )

            full_res_file_path = self._get_full_res_photo_path(photo_file_path)
            photo_button.clicked.connect(
                lambda checked, _path=full_res_file_path: self._set_main_photo(_path))

            self.photoPickerLayout.addWidget(photo_button)
            self.photo_picker_dict.update(
                {WhittleFile(photo_file_path).file_name: (photo_button, photo_file_path)}
            )

    def _clear_programmatically_populated_layouts(self):
        while self.photoPickerLayout.count():
            child = self.photoPickerLayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.selectedImage.setPixmap(QPixmap())

    def _upvote_main_photo(self):
        if not os.path.exists(str(self.main_photo_file_path)):
            return None

        current_file_name = WhittleFile(self.main_photo_file_path).file_name
        wf_set = self.voting_dict.get(current_file_name)

        if wf_set is None:
            return

        for wf in wf_set:
            wf.edit_file = True
        upvoted_photo_button = self.photo_picker_dict[current_file_name][0]
        thumbnail_file_path = self.photo_picker_dict[current_file_name][1]
        self._update_button_with_vote(
            upvoted_photo_button,
            thumbnail_file_path,
            CHECKMARK_ICON_PATH,
        )
        self.voting_dict[current_file_name] = wf_set
        self._set_stats()

    def _downvote_main_photo(self):
        if not os.path.exists(str(self.main_photo_file_path)):
            return None

        current_file_name = WhittleFile(self.main_photo_file_path).file_name
        wf_set = self.voting_dict.get(current_file_name)

        if wf_set is None:
            return

        for wf in wf_set:
            wf.edit_file = False

        downvoted_photo_button = self.photo_picker_dict[current_file_name][0]
        thumbnail_file_path = self.photo_picker_dict[current_file_name][1]
        self._update_button_with_vote(
            downvoted_photo_button,
            thumbnail_file_path,
            X_MARK_ICON_PATH,
        )
        self.voting_dict[current_file_name] = wf_set
        self._set_stats()

    @staticmethod
    def _threaded_file_move(file_move_tuple):
        current_location = ""
        destination_location = ""
        shutil.move()

    @staticmethod
    def _clean_up_temp():
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

    def _update_button_with_vote(self, button, thumbnail_path, icon_path):
        temp_icon = QIcon()
        main_image_pixmap = QPixmap(thumbnail_path)
        icon_image_pixmap = QPixmap(icon_path)
        result = join_pixmap(
            main_image_pixmap,
            icon_image_pixmap,
            self.screen_width,
            self.screen_height,
        )
        temp_icon.addPixmap(result)
        button.setIcon(temp_icon)
        button.setIconSize(
            QSize(
                self._get_width(THUMBNAIL_WIDTH),
                self._get_height(THUMBNAIL_HEIGHT),
            )
        )

    def _set_stats(self):
        number_of_photos = f"Number of Photos: {len(self.voting_dict.keys())}"
        upvotes = 0
        downvotes = 0
        for file_path, wf_set in self.voting_dict.items():
            if next(wf for wf in wf_set).edit_file == True:
                upvotes += 1
            elif next(wf for wf in wf_set).edit_file == False:
                downvotes += 1

        number_of_upvotes = f"Number of Upvotes: {upvotes}"
        number_of_downvotes = f"Number of Downvotes: {downvotes}"

        stats = (
        f"Whittle Statistics\n"
        f"{number_of_photos}\n"
        f"{number_of_upvotes}\n"
        f"{number_of_downvotes}"
        )
        self.statsLabel.setText(stats)

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
        self._clean_up_temp()
        self.save_state()
        event.accept()
