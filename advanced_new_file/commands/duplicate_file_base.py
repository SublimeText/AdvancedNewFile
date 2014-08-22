import os
import re
import sublime_plugin

from .command_base import AdvancedNewFileBase
from ..anf_util import *

class DuplicateFileBase(AdvancedNewFileBase, sublime_plugin.WindowCommand):

    def __init__(self, window):
        super(DuplicateFileBase, self).__init__(window)

    def run(self, is_python=False, initial_path=None, rename_file=None):
        self.is_python = is_python
        self.run_setup()
        self.argument_name = rename_file

        path = self.settings.get(self.get_default_setting(), "")
        current_file = self.view.file_name()
        if current_file:
            directory, current_file_name = os.path.split(current_file)
            path = path.replace("<filepath>", current_file)
            path = path.replace("<filedirectory>", directory + os.sep)
        else:
            current_file_name = ""

        path = path.replace("<filename>", current_file_name)
        self.duplicate_setup()
        self.show_filename_input(
            path if len(path) > 0 else self.generate_initial_path())

    def get_argument_name(self):
        return self.argument_name

    def duplicate_setup(self):
        view = self.window.active_view()
        self.original_name = None
        if view is not None:
            view_file_name = view.file_name()
            if view_file_name:
                self.original_name = os.path.basename(view_file_name)

        if self.original_name is None:
            self.original_name = ""

    def update_status_message(self, creation_path):
        status_prefix = self.get_status_prefix()
        if self.is_copy_original_name(creation_path):
            creation_path = os.path.join(creation_path, self.original_name)
        else:
            creation_path = self.try_append_extension(creation_path)
        if self.view is not None:
            self.view.set_status("AdvancedNewFile", "%s %s " %
                                 (status_prefix, creation_path))
        else:
            sublime.status_message("%s %s" %
                                   (status_prefix, creation_path))

    def is_copy_original_name(self, path):
        return (os.path.isdir(path) or
               os.path.basename(path) == "")

    def try_append_extension(self, path):
        append_setting = self.get_append_extension_setting()
        if self.settings.get(append_setting, False):
            if not self.is_copy_original_name(path):
                _, new_path_extension = os.path.splitext(path)
                if new_path_extension == "":
                    argument_name = self.get_argument_name()
                    if argument_name is None:
                        _, extension = os.path.splitext(self.view.file_name())
                    else:
                        _, extension = os.path.splitext(argument_name)
                    path += extension
        return path



