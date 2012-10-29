import os
import sublime
import sublime_plugin
import copy


class AdvancedNewFileCommand(sublime_plugin.TextCommand):

    def run(self, edit, is_python=False):
        self.top_level_split_char = ":"
        self.is_python = is_python
        self.window = self.view.window()
        self.root = self.get_root()
        self.show_filename_input()

    def get_root(self, target=None):
        try:
            root = self.window.folders()[0]
            if target:
                for folder in self.window.folders():
                    basename = os.path.basename(folder)
                    if basename == target:
                        root = folder
        except IndexError:
            root = os.path.abspath(os.path.dirname(self.view.file_name()))
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

        PathAutocomplete.set_root(self.root)

    def update_filename_input(self, path):
        if self.top_level_split_char in path:
            parts = path.split(self.top_level_split_char)
            base = self.get_root(parts[0])
            PathAutocomplete.set_root(base)
            path = self.top_level_split_char.join(parts[1:])
        else:
            PathAutocomplete.set_root(self.get_root())

        PathAutocomplete.set_path(path)

    def entered_filename(self, filename):
        base = self.root

        if self.top_level_split_char in filename:
            parts = filename.split(self.top_level_split_char)
            base = self.get_root(parts[0])
            filename = self.top_level_split_char.join(parts[1:])

        file_path = os.path.join(base, filename)

        if not os.path.exists(file_path):
            self.create(file_path)
        if not os.path.isdir(file_path):
            view = self.window.open_file(file_path)
        self.clear()

    def clear(self):
        PathAutocomplete.clear()

    def create(self, filename):
        base, filename = os.path.split(filename)
        self.create_folder(base)
        open(os.path.join(base, filename), "a").close()

    def create_folder(self, base):
        if not os.path.exists(base):
            parent = os.path.split(base)[0]
            if not os.path.exists(parent):
                self.create_folder(parent)
            os.mkdir(base)
        if self.is_python:
            open(os.path.join(base, '__init__.py'), 'a').close()


class PathAutocomplete(sublime_plugin.EventListener):
    path = ""
    root = ""
    prev_suggestions = []
    prev_base = ""
    prev_directory = ""

    def map_function(self, val):
        return os.path.basename(val)

    def on_query_completions(self, view, prefix, locations):
        suggestions = []

        if (view.name() == "AdvancedNewFileCreation"):
            root_path = PathAutocomplete.root + "/"
            prev_base = PathAutocomplete.prev_base
            prev_directory = PathAutocomplete.prev_directory

            base = os.path.basename(PathAutocomplete.path)
            directory = os.path.dirname(PathAutocomplete.path)
            if base == "" or (base == prev_base and directory == prev_directory):
                return PathAutocomplete.prev_suggestions

            # Project folders
            if directory == "":
                folders = sublime.active_window().folders()
                folders = map(self.map_function, folders)

                for folder in folders:
                    if folder.find(base) == 0:
                        suggestions.append((folder + ":", folder + ":"))

            # Directories
            path = os.path.join(root_path, directory)

            for filename in os.listdir(path):
                if os.path.isdir(os.path.join(path, filename)):
                    if filename.find(base) == 0:
                        suggestions.append((filename + "/", filename + "/"))
            #suggestions.append((base, base))
            PathAutocomplete.prev_directory = copy.deepcopy(directory)
            PathAutocomplete.prev_base = copy.deepcopy(base)
            PathAutocomplete.prev_suggestions = copy.deepcopy(suggestions)

        return suggestions

    @staticmethod
    def set_path(path_input):
        PathAutocomplete.path = path_input

    @staticmethod
    def set_root(root_input):
        PathAutocomplete.root = root_input

    @staticmethod
    def clear():
        PathAutocomplete.prev_suggestions = []
        PathAutocomplete.prev_base = ""
        PathAutocomplete.path = ""
        PathAutocomplete.prev_directory = ""
