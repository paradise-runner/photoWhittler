import os


JPG_EXTENSION = ".jpg"
RAW_EXTENSIONS = {".cr2"}
VALID_EXTENSIONS = RAW_EXTENSIONS | {JPG_EXTENSION}


LIGHT_GREY = "52,52,52"
LIGHT_BLACK = "31,30,30"
DARK_BLACK = "21,20,20"
WHITE = "255,255,255"
WHITTLE_RED = "255,66,72"
WHITTLE_PURPLE = "199,143,235"
WHITTLE_GREEN = "173,197,84"


BACKGROUND_COLOR = f"background-color:rgb({DARK_BLACK})"

LIGHT_TEXT_COLOR = f"color:rgb({WHITE})"
DARK_TEXT_COLOR = f"color:rgb({DARK_BLACK})"

SELECT_BUTTON_COLOR = f"background-color:rgb({LIGHT_GREY})"
BUTTON_COLOR = f"background-color:rgb({LIGHT_BLACK})"

UPVOTE_BUTTON_COLOR = f"background-color:rgb({WHITTLE_GREEN})"
DOWNVOTE_BUTTON_COLOR = f"background-color:rgb({WHITTLE_RED})"
WHITTLE_BUTTON_COLOR = f"background-color:rgb({WHITTLE_PURPLE})"


WHITTLE_BUTTON_STYLE = f"{WHITTLE_BUTTON_COLOR}; {DARK_TEXT_COLOR}"
BUTTON_STYLE = f"{BUTTON_COLOR}; {LIGHT_TEXT_COLOR}"
UPVOTE_BUTTON_STYLE = f"{UPVOTE_BUTTON_COLOR}; {DARK_TEXT_COLOR}"
DOWNVOTE_BUTTON_STYLE = f"{DOWNVOTE_BUTTON_COLOR}; {DARK_TEXT_COLOR}"
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
WINDOW_WIDTH = 1300
WINDOW_HEIGHT = 800
