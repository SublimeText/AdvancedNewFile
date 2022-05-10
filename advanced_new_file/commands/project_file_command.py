import sublime
import sublime_plugin
import os
import re
import xml.etree.ElementTree as ET

from .new_file_command import AdvancedNewFileNew
from ..lib.package_resources import get_resource
from ..anf_util import *


class AdvancedNewFileProjectFileCommand(AdvancedNewFileNew, sublime_plugin.WindowCommand):
    def __init__(self, window):
        super().__init__(window)

    def run(self, is_python=False, initial_path=None):
        self.is_python = is_python
        self.run_setup()
        print(self.settings)
        completion_delay = self.settings.get(COMPLETION_DELAY_SETTING, 100)
        print(completion_delay)
        self.show_filename_input(self.generate_initial_path(initial_path), completion_delay)

    def get_project_folder(self):
        return sublime.active_window().folders()[0]

    def split_path(self, path_in):
        return (self.get_project_folder(), path_in)

    def entered_file_action(self, path):
        if self.settings.get(SHELL_INPUT_SETTING, False):
            self.multi_file_action(self.curly_brace_expansion(path))
        else:
            self.single_file_action(path)

    def input_panel_caption(self):
        caption = 'Enter a path for a project file'
        return caption

    def update_status_message(self, creation_path):
        if self.view is not None:
            self.view.set_status("AdvancedNewFile", "Project file at %s" % creation_path)
        else:
            sublime.status_message("Project file at %s" % creation_path)

    def get_completion_list(self, path_in):
        return self.completion.complete_for_project(path_in)

    def set_input_view_project_files(self, project_files):
        self.get_active_view_settings().set("anf_input_view_project_files", project_files)

    def get_input_view_project_files(self):
        return self.get_active_view_settings().get("anf_input_view_project_files")


