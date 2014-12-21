import os
import re
import shutil
import sublime_plugin

from .duplicate_file_base import DuplicateFileBase
from ..anf_util import *

class AdvancedNewFileCopy(DuplicateFileBase):
    def __init__(self, window):
        super(AdvancedNewFileCopy, self).__init__(window)

    def get_default_setting(self):
        return COPY_DEFAULT_SETTING

    def input_panel_caption(self):
        caption = 'Enter a new path to copy file'
        if self.is_python:
            caption = '%s (creates __init__.py in new dirs)' % caption
        return caption

    def entered_file_action(self, path):
        attempt_copy = True
        path = self.try_append_extension(path)

        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            try:
                self.create_folder(directory)
            except OSError as e:
                attempt_copy = False
                sublime.error_message("Cannot create '" + path + "'." +
                                      " See console for details")
                print("Exception: %s '%s'" % (e.strerror, e.filename))

        if attempt_copy:
            copy_success, new_file = self._copy_file(path)
            if copy_success:
                self.open_file(new_file)

    def _copy_file(self, path):
        if os.path.isdir(path) or re.search(r"(/|\\)$", path):
            # use original name if a directory path has been passed in.
            path = os.path.join(path, self.original_name)

        window = self.window
        copied = True
        if self.get_argument_name():
            self.copy_from_argument(path)
        elif self.view is not None:
            self.copy_from_view(self.view, path)
        else:
            copied = False
            sublime.error_message("Unable to copy file. No source file to move")

        return (copied, path)

    def copy_from_view(self, source_view, target):
        source = source_view.file_name()
        if source is None:
            self.copy_file_from_buffer(source_view, target)
        else:
            self.copy_file_from_disk(source, target)

    def copy_file_from_buffer(self, source_view, target):
        content = self.view.substr(sublime.Region(0, self.view.size()))
        with open(target, "w") as file_obj:
            file_obj.write(content)

    def copy_file_from_disk(self, source, target):
        self._copy_file_action(source, target)

    def copy_from_argument(self, target):
        source_name = self.get_argument_name()
        file_view = self._find_open_file(source_name)

        self._copy_file_action(source_name, target)


    def _copy_file_action(self, source, target):
        shutil.copy(source, target)

    def get_status_prefix(self):
        return "Copying file to"

    def get_append_extension_setting(self):
        return APPEND_EXTENSION_ON_COPY_SETTING

    def get_default_root_setting(self):
        return COPY_FILE_DEFAULT_ROOT_SETTING


class AdvancedNewFileCopyAtCommand(sublime_plugin.WindowCommand):
    def run(self, files):
        if len(files) != 1:
            return
        self.window.run_command("advanced_new_file_copy",
                                {"rename_file": files[0]})

    def is_visible(self, files):
        return len(files) == 1
