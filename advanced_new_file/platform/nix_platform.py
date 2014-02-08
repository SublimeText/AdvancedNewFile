import re
import os

from ..anf_util import *


class NixPlatform():
    def split(self, path):
        return None, path

    def parse_nix_path(self, root, path):
        return "/", 1

    def get_alias_absolute_path(self, root, path):
        if re.search(NIX_ROOT_REGEX, path) is None:
            return os.path.join(root, path)
        return None

    def is_absolute_path(self, path):
        return re.match(NIX_ROOT_REGEX, path) is not None
