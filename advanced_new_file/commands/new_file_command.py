import sublime
import sublime_plugin
import os
import xml.etree.ElementTree as ET

from .command_base import AdvancedNewFileBase
from ..anf_util import *


class AdvancedNewFileNew(AdvancedNewFileBase, sublime_plugin.WindowCommand):
    def __init__(self, window):
        super(AdvancedNewFileNew, self).__init__(window)

    def run(self, is_python=False, initial_path=None):
        self.is_python = is_python
        self.run_setup()
        self.show_filename_input(self.generate_initial_path(initial_path))

    def input_panel_caption(self):
        caption = 'Enter a path for a new file'
        if self.is_python:
            caption = '%s (creates __init__.py in new dirs)' % caption
        return caption

    def entered_file_action(self, path):
        attempt_open = True
        file_exist = os.path.exists(path)
        if not file_exist:
            try:
                self.create(path)
            except OSError as e:
                attempt_open = False
                sublime.error_message("Cannot create '" + path +
                                      "'. See console for details")
                print("Exception: %s '%s'" % (e.strerror, e.filename))
        if attempt_open:
            file_view = self.open_file(path)
            if not file_exist:
                file_view.settings().set("_anf_new", True)

    def update_status_message(self, creation_path):
        if self.view is not None:
            self.view.set_status("AdvancedNewFile", "Creating file at %s " %
                                 creation_path)
        else:
            sublime.status_message("Creating file at %s" % creation_path)


class AdvancedNewFileNewAtCommand(sublime_plugin.WindowCommand):
    def run(self, dirs):
        if len(dirs) != 1:
            return
        path = dirs[0] + os.sep
        self.window.run_command("advanced_new_file_new",
                                {"initial_path": path})

    def is_visible(self, dirs):
        return len(dirs) == 1


class AdvancedNewFileNewEventListener(sublime_plugin.EventListener):
    def on_load(self, view):
        if view.settings().get("_anf_new", False):
            _, extension = os.path.splitext(view.file_name())
            extension = extension[1:]
            settings = get_settings(view)
            if extension in settings.get(FILE_TEMPLATES_SETTING):
                template = settings.get(FILE_TEMPLATES_SETTING)[extension]
                if type(template) == list:
                    if len(template) == 1:
                        view.run_command("insert_snippet", {"contents": self.get_snippet_from_file(template[0])})
                    else:
                        entries = list(map(self.get_basename, template))
                        self.entries = list(map(self.expand_path, template))
                        self.view = view
                        sublime.set_timeout(lambda: view.window().show_quick_panel(entries, self.quick_panel_selection), 10)
                else:
                    view.run_command("insert_snippet", {"contents": template})
            view.settings().set("_anf_new", "")

    def get_basename(self, path):
        return os.path.basename(os.path.expanduser(path))

    def expand_path(self, path):
        return os.path.expanduser(path)

    def quick_panel_selection(self, index):
        if index < 0:
            return
        self.view.run_command("insert_snippet", {"contents": self.get_snippet_from_file(self.entries[index])})

    def get_snippet_from_file(self, path):
        tree = ET.parse(os.path.expanduser(path))
        content = tree.find("content")
        return content.text
