import re
import os

from ..anf_util import *


class WindowsPlatform(object):
    """docstring for WindowsPlatform"""
    def __init__(self, view):
        super(WindowsPlatform, self).__init__()
        self.view = view

    def split(self, path):
        if re.match(WIN_ROOT_REGEX, path):
            return path[0:3], path[3:]
        else:
            return None, path

    def parse_nix_path(self, root, path):
        path_offset = 1
        match = re.match(r"^/([a-zA-Z])/", path)
        if match:
            root = "%s:\\" % match.group(1)
            path_offset = 3
        else:
            root, _ = os.path.splitdrive(self.view.file_name())
            root += "\\"

        return root, path_offset

    def get_alias_absolute_path(self, root, path):
        if re.search(WIN_ROOT_REGEX, path) is None:
            return os.path.join(root, path)
        return None

    def is_absolute_path(self, path):
        return re.match(WIN_ROOT_REGEX, path) is not None
