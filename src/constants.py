import os


JPG_EXTENSION = ".jpg"
RAW_EXTENSIONS = {".cr2"}
VALID_EXTENSIONS = RAW_EXTENSIONS | {JPG_EXTENSION}
BACKGROUND_COLOR = "background-color:rgb(21,20,20)"
BUTTON_COLOR = "background-color:rgb(31,30,30)"
SELECT_BUTTON_COLOR = "background-color:rgb(52,52,52)"
TEXT_COLOR = "color:rgb(255,255,255)"
BUTTON_STYLE = f"{BUTTON_COLOR}; {TEXT_COLOR}"
PICKER_BUTTON_STYLE = f"{BUTTON_COLOR}; border-style: double"
SELECTED_PICKER_BUTTON_STYLE = f"{SELECT_BUTTON_COLOR}; border-style: double"
UPVOTED_FOLDER_NAME = "UPVOTED"
RES_PATH = os.path.join(os.path.abspath(os.getcwd()), "res")
CHECKMARK_ICON_PATH = os.path.join(RES_PATH, "iconmonstr-check-mark-6-240.png")
X_MARK_ICON_PATH = os.path.join(RES_PATH, "iconmonstr-x-mark-4-240.png")
SAVE_STATE_PATH = os.path.join(os.path.abspath(os.getcwd()), "state.pkl")
RAW_UNEDITED_FOLDER_NAME = "raw_unedited"
JPG_UNEDITED_FOLDER_NAME = "jpeg_unedited"
TEMP_PATH = os.path.join(os.getcwd(), "_temp")

# Various Sizes
THUMBNAIL_WIDTH = 120
THUMBNAIL_HEIGHT = 120
PICKER_BUTTON_WIDTH = 130
PICKER_BUTTON_HEIGHT = 110

MAIN_PHOTO_HEIGHT_AND_WIDTH = 1000

PHOTO_PICKER_HEIGHT = 140
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 800
