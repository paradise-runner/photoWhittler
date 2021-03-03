import os


JPG_EXTENSION = ".jpg"
RAW_EXTENSIONS = {".cr2"}
VALID_EXTENSIONS = RAW_EXTENSIONS | {JPG_EXTENSION}
BACKGROUND_COLOR = "background-color:rgb(21,20,20)"
BUTTON_COLOR = "background-color:rgb(31,30,30)"
TEXT_COLOR = "color:rgb(255,255,255)"
BUTTON_STYLE = f"{BUTTON_COLOR}; {TEXT_COLOR}"
UPVOTED_FOLDER_NAME = "UPVOTED"
RES_PATH = os.path.join(os.path.abspath(os.getcwd()), "res")
CHECKMARK_ICON_PATH = os.path.join(RES_PATH, "iconmonstr-check-mark-6-240.png")
X_MARK_ICON_PATH = os.path.join(RES_PATH, "iconmonstr-x-mark-4-240.png")
THUMBNAIL_SIZE = 100, 100
SAVE_STATE_PATH = os.path.join(os.path.abspath(os.getcwd()), "state.pkl")


class WhittleFile:

    def __init__(self, file_path):
        self.edit_file = None
        self.file_path = file_path
        split_path = os.path.splitext(file_path)
        self.file_extension = split_path[-1].lower()
        self.file_name = split_path[0].split(os.sep)[-1]\

