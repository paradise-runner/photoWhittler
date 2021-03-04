import os


class WhittleFile:

    def __init__(self, file_path):
        self.edit_file = None
        self.file_path = file_path
        split_path = os.path.splitext(file_path)
        self.file_extension = split_path[-1].lower()
        self.file_name = split_path[0].split(os.sep)[-1]