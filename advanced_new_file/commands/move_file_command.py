import os
import re
import shutil
import sublime_plugin

from .duplicate_file_base import DuplicateFileBase
from ..anf_util import *
from ..vcs.git.git_command_base import GitCommandBase


class AdvancedNewFileMove(DuplicateFileBase, GitCommandBase):
    def __init__(self, window):
        super(AdvancedNewFileMove, self).__init__(window)

    def get_default_setting(self):
        return RENAME_DEFAULT_SETTING

    def input_panel_caption(self):
        caption = 'Enter a new path for current file'
        if self.is_python:
            caption = '%s (creates __init__.py in new dirs)' % caption
        return caption

    def _git_mv(self, from_filepath, to_filepath):
        path, filename = os.path.split(from_filepath)
        args = ["mv", filename, to_filepath]
        result = self.run_command(args, path)
        if result != 0:
            sublime.error_message("Git move of %s to %s failed" %
                                 (from_filepath, to_filepath))

    def entered_file_action(self, path):
        attempt_open = True
        path = self.try_append_extension(path)

        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            try:
                self.create_folder(directory)
            except OSError as e:
                attempt_open = False
                sublime.error_message("Cannot create '" + path + "'." +
                                      " See console for details")
                print("Exception: %s '%s'" % (e.strerror, e.filename))

        if attempt_open:
            self._rename_file(path)

    def get_append_extension_setting(self):
        return APPEND_EXTENSION_ON_MOVE_SETTING

    def _rename_file(self, file_path):
        if os.path.isdir(file_path) or re.search(r"(/|\\)$", file_path):
            # use original name if a directory path has been passed in.
            file_path = os.path.join(file_path, self.original_name)

        window = self.window
        rename_filename = self.get_argument_name()
        if rename_filename:
            self.move_from_argument(rename_filename, file_path)
        elif self.view is not None:
            self.move_from_view(self.view, file_path)
        else:
            sublime.error_message("Unable to move file. No file to move.")

    def move_from_argument(self, source, target):
        file_view = self._find_open_file(source)
        if file_view is not None:
            self.view.run_command("save")
            window.focus_view(file_view)
            window.run_command("close")

        self._move_action(source, target)

        if file_view is not None:
            self.open_file(target)

    def move_from_view(self, source_view, target):
        source = source_view.file_name()
        if source is None:
            self.move_file_from_buffer(source_view, target)
        else:
            self.move_file_from_disk(source, target)
        self.open_file(target)

    def move_file_from_disk(self, source, target):
        window = self.window
        self.view.run_command("save")
        window.focus_view(self.view)
        window.run_command("close")
        self._move_action(source, target)

    def move_file_from_buffer(self, source_view, target):
        window = self.window
        content = self.view.substr(sublime.Region(0, self.view.size()))
        self.view.set_scratch(True)
        window.focus_view(self.view)
        window.run_command("close")
        with open(target, "w") as file_obj:
            file_obj.write(content)

    def _move_action(self, from_file, to_file):
        tracked_by_git = self.file_tracked_by_git(from_file)
        if tracked_by_git and self.settings.get(VCS_MANAGEMENT_SETTING):
            self._git_mv(from_file, to_file)
        else:
            shutil.move(from_file, to_file)

    def get_status_prefix(self):
        return "Moving file to"


class AdvancedNewFileMoveAtCommand(sublime_plugin.WindowCommand):
    def run(self, files):
        if len(files) != 1:
            return
        self.window.run_command("advanced_new_file_move",
                                {"rename_file": files[0]})

    def is_visible(self, files):
        return len(files) == 1
