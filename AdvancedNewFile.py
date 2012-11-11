import os
import sublime
import sublime_plugin
import re

SETTINGS = [
    "alias",
    "default_initial",
    "use_cursor_text",
    "show_files",
    "show_path"
]
DEBUG = False
PLATFORM = sublime.platform()


class AdvancedNewFileCommand(sublime_plugin.WindowCommand):

    def run(self, is_python=False):
        self.top_level_split_char = ":"
        self.is_python = is_python
        self.root, path = self.split_path()
        self.view = self.window.active_view()

        # Settings will be based on the view
        settings = get_settings(self.view)
        self.aliases = settings.get("alias")
        self.show_path = settings.get("show_path")
        # Set some default values for the auto complete
        PathAutocomplete.set_show_files(settings.get("show_files"))
        PathAutocomplete.set_aliases(self.aliases)

        # Search for initial string
        path = settings.get("default_initial", "")
        if settings.get("use_cursor_text", False):
            tmp = self.get_cursor_path()
            if tmp != "":
                path = tmp

        # Get user input
        self.show_filename_input(path)

    def split_path(self, path=""):
        try:
            if self.top_level_split_char in path:
                parts = path.split(self.top_level_split_char, 1)
                root = self.translate_alias(parts[0])
                path = parts[1]
            elif "~/" == path[0:2] or "~\\" == path[0:2]:
                root = os.path.expanduser("~")
                path = path[2:]
            else:
                root = self.window.folders()[0]
        except IndexError:
            root = os.path.expanduser("~")

        if DEBUG:
            print "AdvancedNewFile[Debug]: root is " + root
            print "AdvancedNewFile[Debug]: path is " + path

        return root, path

    def translate_alias(self, target):
        root = None
        if target == "" and self.view != None:
            filename = self.view.file_name()
            if filename != None:
                root = os.path.dirname(filename)
        else:
            for folder in self.window.folders():
                basename = os.path.basename(folder)
                if basename == target:
                    root = folder
                    break
            for alias in self.aliases.keys():
                if alias == target:
                    alias_path = self.aliases.get(alias)
                    if re.search(r"^\.{1,2}[/\\]", alias_path) != None:
                        if self.view.file_name() != None:
                            alias_root = os.path.dirname(self.view.file_name())
                        else:
                            alias_root = os.path.expanduser("~")
                        root = os.path.join(alias_root, alias_path)
                    else:
                        root = os.path.expanduser(alias_path)
                    break
        if root == None:
            root = os.path.expanduser("~")
            print "AdvancedNewFile[Warning]: No alias found for '" + target + "'"

        return os.path.abspath(root)

    def show_filename_input(self, initial=''):
        caption = 'Enter a path for a new file'
        if self.is_python:
            caption = '%s (creates __init__.py in new dirs)' % caption
        view = self.window.show_input_panel(
            caption, initial,
            self.entered_filename, self.update_filename_input, self.clear
        )

        view.set_name("AdvancedNewFileCreation")
        view.settings().set("tab_size", 0)
        view.settings().set("translate_tabs_to_spaces", True)
        temp = view.settings().get("word_separators")
        temp = temp.replace(".", "")
        view.settings().set("word_separators", temp)
        # May be useful to see the popup for debugging
        # if DEBUG:
        #     view.settings().set("auto_complete", True)
        #     view.settings().set("auto_complete_selector", "text")

        PathAutocomplete.set_root(self.root, True)

    def update_filename_input(self, path_in):
        base, path = self.split_path(path_in)
        if self.top_level_split_char in path_in:
            PathAutocomplete.set_root(base, False)
        else:
            PathAutocomplete.set_root(base, True)

        if self.show_path:
            self.view.set_status("AdvancedNewFile", "Creating file at %s " % \
                os.path.abspath(os.path.join(base, path)))

        PathAutocomplete.set_path(path)

    def entered_filename(self, filename):
        base, path = self.split_path(filename)
        file_path = os.path.join(base, path)

        if DEBUG:
            print "AdvancedNewFile[Debug]: Creating file at " + file_path
        if not os.path.exists(file_path):
            self.create(file_path)
        if not os.path.isdir(file_path):
            self.window.open_file(file_path)

        self.clear()

    def clear(self):
        self.view.erase_status("AdvancedNewFile")
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
        if self.view == None:
            return

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
    prev_root = ""
    default_root = True
    show_files = False

    def map_function(self, val):
        return os.path.basename(val)

    def continue_previous_autocomplete(self):
        sep = os.sep
        root_path = PathAutocomplete.root + sep
        prev_base = PathAutocomplete.prev_base
        prev_directory = PathAutocomplete.prev_directory
        prev_root = PathAutocomplete.prev_root

        base = os.path.basename(PathAutocomplete.path)
        directory = os.path.dirname(PathAutocomplete.path)

        # If base is empty, we may be cycling through directory options
        if base == "":
            return True
        # Ensures the correct directory is used if the default root is specified
        # using an alias.
        if base == prev_base and \
        directory == prev_directory and \
        prev_root == root_path and \
        PathAutocomplete.default_root:
            return True
        # Continue completions if file names are completed.
        if os.path.isfile(os.path.join(root_path, PathAutocomplete.path)):
            return True
        return False

    def on_query_completions(self, view, prefix, locations):
        suggestions = []
        if (view.name() == "AdvancedNewFileCreation"):
            sep = os.sep
            root_path = PathAutocomplete.root + sep
            aliases = PathAutocomplete.aliases

            base = os.path.basename(PathAutocomplete.path)
            directory = os.path.dirname(PathAutocomplete.path)

            if self.continue_previous_autocomplete():
                if DEBUG:
                    print "AdvancedNewFile[Debug]: (Prev) Suggestions"
                    print PathAutocomplete.prev_suggestions

                return PathAutocomplete.prev_suggestions

            # Project folders
            if directory == "" and PathAutocomplete.default_root:
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
            if os.path.exists(path):
                for filename in os.listdir(path):
                    if PathAutocomplete.show_files or os.path.isdir(os.path.join(path, filename)):
                        if filename.find(base) == 0:
                            # Need to find a better way to do the auto complete.
                            if os.path.isdir(os.path.join(path, filename)):
                                suggestions.append((" " + filename + sep, filename + sep))
                            else:
                                suggestions.append((" " + filename, filename))
                #suggestions.append((base, base))
                PathAutocomplete.prev_directory = directory
                PathAutocomplete.prev_base = base
                PathAutocomplete.prev_suggestions = suggestions
                PathAutocomplete.prev_root = root_path
                if DEBUG:
                    print "AdvancedNewFile[Debug]: Suggestions:"
                    print suggestions

        return suggestions

    @staticmethod
    def set_path(path_input):
        PathAutocomplete.path = path_input

    @staticmethod
    def set_root(root_input, default_root):
        PathAutocomplete.root = root_input
        PathAutocomplete.default_root = default_root

    @staticmethod
    def clear():
        PathAutocomplete.path = ""
        PathAutocomplete.root = ""
        PathAutocomplete.prev_suggestions = []
        PathAutocomplete.prev_base = ""
        PathAutocomplete.prev_directory = ""
        PathAutocomplete.aliases = {}
        PathAutocomplete.path_empty = True
        PathAutocomplete.prev_root = ""
        PathAutocomplete.default_root = True
        PathAutocomplete.show_files = False

    @staticmethod
    def set_aliases(aliases):
        PathAutocomplete.aliases = aliases

    @staticmethod
    def set_show_files(show_files):
        PathAutocomplete.show_files = show_files


def get_settings(view):
    settings = sublime.load_settings("AdvancedNewFile.sublime-settings")
    project_settings = {}
    local_settings = {}
    if view != None:
        project_settings = view.settings().get('AdvancedNewFile', {})

    for setting in SETTINGS:
        local_settings[setting] = settings.get(setting)

    for key in project_settings:
        if key in SETTINGS:
            if key == "alias":
                local_settings[key] = dict(local_settings[key].items() + project_settings.get(key).items())
            else:
                local_settings[key] = project_settings[key]
        else:
            print "AdvancedNewFile[Warning]: Invalid key '" + key + "' in project settings."

    return local_settings
