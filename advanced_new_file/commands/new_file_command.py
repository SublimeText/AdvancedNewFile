import sublime
import sublime_plugin
import os
import re
import xml.etree.ElementTree as ET

from .command_base import AdvancedNewFileBase
from ..lib.package_resources import get_resource
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
        if self.settings.get(SHELL_INPUT_SETTING, False):
            self.multi_file_action(self.curly_brace_expansion(path))
        else:
            self.single_file_action(path)

    def multi_file_action(self, paths):
        for path in paths:
            self.single_file_action(path, False)

    def single_file_action(self, path, apply_template=True):
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
        if attempt_open and os.path.isfile(path):
            file_view = self.open_file(path)
            if not file_exist and apply_template:
                file_view.settings().set("_anf_new", True)

    def curly_brace_expansion(self, path):
        if not self.curly_braces_balanced(path) or "{" not in path:
            return [path]
        paths = self.expand_single_curly_brace(path)

        while True:
            path_len = len(paths)
            temp_paths = []
            for expanded_path in paths:
                temp_paths.append(self.expand_single_curly_brace(expanded_path))
            paths = self.flatten_list(temp_paths)
            if path_len == len(paths):
                break

        return self.flatten_list(paths)

    def flatten_list(self, initial_list):
        if isinstance(initial_list, list):
            return [flattened for entry in initial_list for flattened in self.flatten_list(entry)]
        else:
            return [initial_list]


    # Assumes curly braces are balanced
    def expand_single_curly_brace(self, path):
        if "{" not in path:
            return [path]
        start, end = self.curly_brace_indecies(path)
        all_tokens = path[start + 1:end]
        paths = []
        for token in all_tokens.split(","):
            temp = path[0:start] + token + path[end + 1:]
            paths.append(temp)
        return paths

    # Assumes curly braces are balanced.
    def curly_brace_indecies(self, path, count=0,open_index=None):
        if len(path) == 0:
            return None
        c = path[0]
        if c == "{":
            return self.curly_brace_indecies(path[1:], count + 1, count)
        elif c == "}":
            return open_index, count
        else:
            return self.curly_brace_indecies(path[1:], count + 1, open_index)

    def curly_braces_balanced(self, path, count=0):
        if len(path) == 0 or count < 0:
            return count == 0

        c = path[0]
        if c == "{":
            return self.curly_braces_balanced(path[1:], count + 1)
        elif c == "}":
            return self.curly_braces_balanced(path[1:], count - 1)
        else:
            return self.curly_braces_balanced(path[1:], count)

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
        match = re.match(r"Packages/([^/]+)/(.+)", path)
        if match:
            tree = ET.fromstring(get_resource(match.group(1), match.group(2)))
        else:
            tree = ET.parse(os.path.expanduser(path))
        content = tree.find("content")
        return content.text
