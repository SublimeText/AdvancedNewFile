import os
import sublime
import sublime_plugin
import copy
import re

SETTINGS = [
    "alias",
    "default_initial",
    "use_cursor_text"
]
DEBUG = False
PLATFORM = sublime.platform()


class AdvancedNewFileCommand(sublime_plugin.TextCommand):

    def run(self, edit, is_python=False):
        self.top_level_split_char = ":"
        self.is_python = is_python
        self.window = self.view.window()
        self.root = self.get_root()
        settings = get_settings(self.view)
        self.aliases = settings.get("alias")
        PathAutocomplete.set_aliases(self.aliases)
        path = settings.get("default_initial", "")
        if settings.get("use_cursor_text", False):
            tmp = self.get_cursor_path()
            if tmp != "":
                path = tmp

        self.show_filename_input(path)

    def get_root(self, target=None):
        try:
            # Default to a folder
            root = self.window.folders()[0]
            if target:
            # If a target exists, search through folders and aliases
            # Folders take precedence over aliases.
                for folder in self.window.folders():
                    basename = os.path.basename(folder)
                    if basename == target:
                        root = folder
                        break
                for alias in self.aliases.keys():
                    if alias == target:
                        root = self.aliases.get(alias)
                        break
        except IndexError:
            # If no folders exists, should create a file at the current directory
            filename = self.view.filename()
            root = os.path.abspath(os.path.dirname(filename))

        if DEBUG:
            print "AdvancedNewFileDebug - root: " + root

        return root

    def show_filename_input(self, initial=''):
        caption = 'Enter a path for a new file'
        if self.is_python:
            caption = '%s (creates __init__.py in new dirs)' % caption
        view = self.window.show_input_panel(
            caption, initial,
            self.entered_filename, self.update_filename_input, self.clear
        )

        view.set_name("AdvancedNewFileCreation")
        view.settings().set("auto_complete", True)
        view.settings().set("tab_size", 0)
        view.settings().set("translate_tabs_to_spaces", True)
        # May be useful to see the popup for debugging
        # view.settings().set("auto_complete_selector", 'text')
        PathAutocomplete.set_root(self.root)

    def update_filename_input(self, path):

        if self.top_level_split_char in path:
            parts = path.split(self.top_level_split_char)
            base = self.get_root(parts[0])
            PathAutocomplete.set_root(base)
            path = self.top_level_split_char.join(parts[1:])
            empty = False
        else:
            PathAutocomplete.set_root(self.get_root())
            empty = True

        PathAutocomplete.set_path(path, empty)

    def entered_filename(self, filename):
        base = self.root

        if self.top_level_split_char in filename:
            parts = filename.split(self.top_level_split_char)
            base = self.get_root(parts[0])
            filename = self.top_level_split_char.join(parts[1:])

        file_path = os.path.join(base, filename)

        if DEBUG:
            print "AdvancedNewFileDebug - Creating file at: " + file_path
        if not os.path.exists(file_path):
            self.create(file_path)
        if not os.path.isdir(file_path):
            self.window.open_file(file_path)
        self.clear()

    def clear(self):
        PathAutocomplete.clear()

    def create(self, filename):
        base, filename = os.path.split(filename)
        self.create_folder(base)
        if filename != "":
            open(os.path.join(base, filename), "a").close()

    def create_folder(self, base):
        if not os.path.exists(base):
            parent = os.path.split(base)[0]
            if not os.path.exists(parent):
                self.create_folder(parent)
            os.mkdir(base)
        if self.is_python:
            open(os.path.join(base, '__init__.py'), 'a').close()

    def get_cursor_path(self):
        view = self.view

        for region in view.sel():
            syntax = view.syntax_name(region.begin())
            if re.match(".*string.quoted.double", syntax) or re.match(".*string.quoted.single", syntax):
                path = view.substr(view.extract_scope(region.begin()))
                path = re.sub('^"|\'', '',  re.sub('"|\'$', '', path.strip()))
            else:
                return ""


class PathAutocomplete(sublime_plugin.EventListener):
    path = ""
    root = ""
    prev_suggestions = []
    prev_base = ""
    prev_directory = ""
    aliases = {}
    path_empty = True

    def map_function(self, val):
        return os.path.basename(val)

    def on_query_completions(self, view, prefix, locations):
        suggestions = []

        if (view.name() == "AdvancedNewFileCreation"):
            sep = os.sep
            root_path = PathAutocomplete.root + sep
            prev_base = PathAutocomplete.prev_base
            prev_directory = PathAutocomplete.prev_directory
            aliases = PathAutocomplete.aliases

            base = os.path.basename(PathAutocomplete.path)
            directory = os.path.dirname(PathAutocomplete.path)

            if base == "" or (base == prev_base and directory == prev_directory):
                if DEBUG:
                    print "AdvancedNewFileDebug - (Prev) Suggestions"
                    print PathAutocomplete.prev_suggestions

                return PathAutocomplete.prev_suggestions

            # Project folders
            if directory == "" and PathAutocomplete.path_empty:
                folders = sublime.active_window().folders()
                folders = map(self.map_function, folders)

                for folder in folders:
                    if folder.find(base) == 0:
                        suggestions.append((folder + ":", folder + ":"))

            # Aliases
                for alias in aliases:
                    if alias.find(base) == 0:
                        suggestions.append((alias + ":", alias + ":"))

            # Directories
            path = os.path.join(root_path, directory)

            for filename in os.listdir(path):
                if os.path.isdir(os.path.join(path, filename)):
                    if filename.find(base) == 0:
                        if base[0] == ".":
                            filename = filename[1:]
                        # Space keeps it from matching previous entries
                        # Kind of a hack of a fix, but seems to work.
                        suggestions.append((" " + filename + sep, filename + sep))
            #suggestions.append((base, base))
            PathAutocomplete.prev_directory = copy.deepcopy(directory)
            PathAutocomplete.prev_base = copy.deepcopy(base)
            PathAutocomplete.prev_suggestions = copy.deepcopy(suggestions)

            if DEBUG:
                print "AdvancedNewFileDebug - Suggestions:"
                print suggestions

        return suggestions

    @staticmethod
    def set_path(path_input, empty):
        PathAutocomplete.path = path_input
        PathAutocomplete.path_empty = empty

    @staticmethod
    def set_root(root_input):
        PathAutocomplete.root = root_input

    @staticmethod
    def clear():
        PathAutocomplete.prev_suggestions = []
        PathAutocomplete.prev_base = ""
        PathAutocomplete.path = ""
        PathAutocomplete.prev_directory = ""

    @staticmethod
    def set_aliases(aliases):
        PathAutocomplete.aliases = aliases


def get_settings(view):
    settings = sublime.load_settings("AdvancedNewFile.sublime-settings")
    project_settings = view.settings().get('AdvancedNewFile', {})
    local_settings = {}

    for setting in SETTINGS:
        local_settings[setting] = settings.get(setting)

    for key in project_settings:
        if key in SETTINGS:
            if key == "alias":
                local_settings[key] = dict(local_settings[key].items() + project_settings.get(key).items())
            else:
                local_settings[key] = project_settings[key]
        else:
            print "AdvancedNewFile: Invalid key '" + key + "' in project settings."

    return local_settings
