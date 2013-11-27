import os
import re
import shutil
import sublime_plugin

from .git.git_command_base import GitCommandBase
from .command_base import AdvancedNewFileBase
from ..anf_util import *

class AdvancedNewFileMove(AdvancedNewFileBase, sublime_plugin.WindowCommand, GitCommandBase):
    def __init__(self, window):
        super(AdvancedNewFileMove, self).__init__(window)

    def run(self, is_python=False, initial_path=None, rename_file=None):
        self.is_python = is_python
        self.run_setup()
        self.rename_filename = rename_file

        path = self.settings.get(RENAME_DEFAULT_SETTING)
        current_file = self.view.file_name()
        current_file_name = os.path.basename(self.view.file_name()) if current_file else ""
        path = path.replace("<filepath>", current_file)
        path = path.replace("<filename>", current_file_name)
        self.show_filename_input(path if len(path) > 0 else self.generate_initial_path())

    def input_panel_caption(self):
        caption = 'Enter a new path for current file'
        view = self.window.active_view()
        if view is not None:
            self.original_name = os.path.basename(view.file_name()) if view.file_name is not None else ""
        else:
            self.original_name = ""
        if self.is_python:
            caption = '%s (creates __init__.py in new dirs)' % caption
        return caption

    def _git_mv(self, from_filepath, to_filepath):
        path, filename = os.path.split(from_filepath)
        args = ["mv", filename, to_filepath]
        result = self.run_command(args, path)
        if result != 0:
            sublime.error_message("Git move of %s to %s failed" % (from_filepath, to_filepath))

    def entered_file_action(self, path):
        attempt_open = True
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            try:
                self.create_folder(directory)
            except OSError as e:
                attempt_open = False
                sublime.error_message("Cannot create '" + path + "'. See console for details")
                print("Exception: %s '%s'" % (e.strerror, e.filename))

        if attempt_open:
            self._rename_file(path)

    def _rename_file(self, file_path):
        if os.path.isdir(file_path) or re.search(r"(/|\\)$", file_path):
            # use original name if a directory path has been passed in.
            file_path = os.path.join(file_path, self.original_name)

        window = self.window
        if self.rename_filename:
            file_view = self._find_open_file(self.rename_filename)
            if file_view is not None:
                self.view.run_command("save")
                window.focus_view(file_view)
                window.run_command("close")

            self._move_action(self.rename_filename, file_path)

            if file_view is not None:
                self.open_file(file_path)

        elif self.view is not None and self.view.file_name() is not None:
            filename = self.view.file_name()
            if filename:
                self.view.run_command("save")
                window.focus_view(self.view)
                window.run_command("close")
                self._move_action(filename, file_path)
            else:
                content = self.view.substr(sublime.Region(0, self.view.size()))
                self.view.set_scratch(True)
                self.view.run_command("close")
                window.focus_view(self.view)
                window.run_command("close")
                with open(file_path, "w") as file_obj:
                    file_obj.write(content)
            self.open_file(file_path)
        else:
            sublime.error_message("Unable to move file. No file to move.")

    def _move_action(self, from_file, to_file):
        tracked_by_git = self.file_tracked_by_git(from_file)
        if tracked_by_git and self.settings.get(VCS_MANAGEMENT_SETTING):
            self._git_mv(from_file, to_file)
        else:
            shutil.move(from_file, to_file)

    def _find_open_file(self, file_name):
        window = self.window
        if IS_ST3:
            return window.find_open_file(file_name)
        else:
            for view in window.views():
                view_name = view.file_name()
                if view_name != "" and view_name == file_name:
                    return view
        return None

    def update_status_message(self, creation_path):
        if self.view != None:
            if os.path.isdir(creation_path) or os.path.basename(creation_path) == "" :
                creation_path = os.path.join(creation_path, self.original_name)
            self.view.set_status("AdvancedNewFile", "Moving file to %s " % \
                creation_path)
        else:
            sublime.status_message("Moving file to %s" % creation_path)

class AdvancedNewFileMoveAtCommand(sublime_plugin.WindowCommand):
    def run(self, files):
        if len(files) != 1:
            return
        self.window.run_command("advanced_new_file_move", {"rename_file": files[0]})

    def is_visible(self, files):
        return len(files) == 1
