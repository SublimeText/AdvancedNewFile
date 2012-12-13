import os
import sublime
import sublime_plugin
import re

SETTINGS = [
    "alias",
    "default_initial",
    "use_cursor_text",
    "show_files",
    "show_path",
    "default_root",
    "default_path",
    "os_specific_alias",
    "ignore_case"
]
DEBUG = False
PLATFORM = sublime.platform()
VIEW_NAME = "AdvancedNewFileCreation"
WIN_ROOT_REGEX = r"[a-zA-Z]:(/|\\)"
NIX_ROOT_REGEX = r"^/"


class AdvancedNewFileCommand(sublime_plugin.WindowCommand):
    def run(self, is_python=False):
        self.root = None
        self.top_level_split_char = ":"
        self.is_python = is_python
        self.view = self.window.active_view()

        # Settings will be based on the view
        settings = get_settings(self.view)
        self.aliases = self.get_aliases(settings)
        self.show_path = settings.get("show_path")
        default_root = self.get_default_root(settings.get("default_root"))
        if default_root == "path":
            self.root = os.path.expanduser(settings.get("default_path"))
            default_root = ""
        self.root, path = self.split_path(default_root)

        # Set some default values for the auto complete
        PathAutocomplete.set_show_files(settings.get("show_files"))
        PathAutocomplete.set_aliases(self.aliases)
        PathAutocomplete.set_ignore_case(settings.get("ignore_case"))

        # Search for initial string
        path = settings.get("default_initial", "")
        if settings.get("use_cursor_text", False):
            tmp = self.get_cursor_path()
            if tmp != "":
                path = tmp

        # Get user input
        self.show_filename_input(path)

    def get_aliases(self, settings):
        aliases = settings.get("alias")
        all_os_aliases = settings.get("os_specific_alias")
        for key in all_os_aliases:
            if PLATFORM.lower() in all_os_aliases.get(key):
                aliases[key] = all_os_aliases.get(key).get(PLATFORM.lower())

        return aliases

    def get_default_root(self, string):
        root = ""

        if string == "home":
            root = "~/"
        elif string == "current":
            root = ":"
        elif string == "top_folder":
            pass
        elif string == "path":
            root = "path"
        else:
            print "Invalid specifier for \"default_root\""
        return root

    def split_path(self, path=""):
        HOME_REGEX = r"^~[/\\]"
        root = None
        try:
            # Parse windows root
            if PLATFORM == "windows":
                if re.match(WIN_ROOT_REGEX, path):
                    root = path[0:3]
                    path = path[3:]

            # Parse if alias
            if self.top_level_split_char in path and root == None:
                parts = path.split(self.top_level_split_char, 1)
                root = self.translate_alias(parts[0])
                path = parts[1]
            # Parse if tilde used
            elif re.match(HOME_REGEX, path) and root == None:
                root = os.path.expanduser("~")
                path = path[2:]
            # Default
            elif root == None:
                root = self.root or self.window.folders()[0]
        except IndexError:
            root = os.path.expanduser("~")

        if DEBUG:
            print "AdvancedNewFile[Debug]: root is " + root
            print "AdvancedNewFile[Debug]: path is " + path
        return root, path

    def translate_alias(self, target):
        RELATIVE_REGEX = r"^\.{1,2}[/\\]"
        root = None
        # Special alias - current file
        if target == "" and self.view is not None:
            filename = self.view.file_name()
            if filename is not None:
                root = os.path.dirname(filename)
        else:
            # Folder aliases
            for folder in self.window.folders():
                basename = os.path.basename(folder)
                if basename == target:
                    root = folder
                    break
            # Aliases from settings.
            for alias in self.aliases.keys():
                if alias == target:
                    alias_path = self.aliases.get(alias)
                    if re.search(RELATIVE_REGEX, alias_path) is not None:
                        if self.view.file_name() is not None:
                            alias_root = os.path.dirname(self.view.file_name())
                        else:
                            alias_root = os.path.expanduser("~")
                        root = os.path.join(alias_root, alias_path)
                    else:
                        root = os.path.expanduser(alias_path)
                    break
        # If no alias resolved, return target.
        # Help identify invalid aliases
        if root is None:
            return target

        return os.path.abspath(root)

    def show_filename_input(self, initial=''):
        caption = 'Enter a path for a new file'
        if self.is_python:
            caption = '%s (creates __init__.py in new dirs)' % caption
        view = self.window.show_input_panel(
            caption, initial,
            self.entered_filename, self.update_filename_input, self.clear
        )

        view.set_name(VIEW_NAME)
        temp = view.settings().get("word_separators")
        temp = temp.replace(".", "")
        view.settings().set("word_separators", temp)
        view.settings().set("auto_complete_commit_on_tab", True)
        view.settings().set("tab_completion", True)

        # May be useful to see the popup for debugging
        if DEBUG:
            view.settings().set("auto_complete", True)
            view.settings().set("auto_complete_selector", "text")
        PathAutocomplete.set_view_id(view.id())
        PathAutocomplete.set_root(self.root, True)

    def update_filename_input(self, path_in):
        base, path = self.split_path(path_in)
        if self.top_level_split_char in path_in:
            PathAutocomplete.set_root(base, False)
        else:
            PathAutocomplete.set_root(base, True)

        if self.show_path:
            if self.view != None:
                self.view.set_status("AdvancedNewFile", "Creating file at %s " % \
                    self.generate_creation_path(base, path))
            else:
                sublime.status_message("Unable to fill status bar without view")

        PathAutocomplete.set_path(path)

    def generate_creation_path(self, base, path):
        if PLATFORM == "windows":
            if not re.match(WIN_ROOT_REGEX, base):
                return base + ":" + path
        else:
            if not re.match(NIX_ROOT_REGEX, base):
                return base + ":" + path

        return os.path.abspath(os.path.join(base, path))

    def entered_filename(self, filename):
        # Check if valid root specified for windows.
        if PLATFORM == "windows":
            if re.match(WIN_ROOT_REGEX, filename):
                root = filename[0:3]
                if not os.path.isdir(root):
                    sublime.error_message(root + " is not a valid root.")
                    self.clear()
                    return

        base, path = self.split_path(filename)
        file_path = os.path.join(base, path)
        # Check for invalid alias specified.
        if self.top_level_split_char in filename and \
            not (PLATFORM == "windows" and re.match(WIN_ROOT_REGEX, base)) and \
            not (PLATFORM != "windows" and re.match(NIX_ROOT_REGEX, base)):
            if base == "":
                error_message = "Current file cannot be resolved."
            else:
                error_message = "'" + base + "' is an invalid alias."
            sublime.error_message(error_message)
        else:
            attempt_open = True
            if DEBUG:
                print "AdvancedNewFile[Debug]: Creating file at " + file_path
            if not os.path.exists(file_path):
                try:
                    self.create(file_path)
                except Exception as e:
                    attempt_open = False
                    sublime.error_message("Cannot create '" + file_path + "'. See console for details")
                    print "Exception: %s" % e.strerror
            if attempt_open:
                if os.path.isdir(file_path):
                    if not re.search(r"(/|\\)$", file_path):
                        sublime.error_message("Cannot open view for '" + file_path + "'. It is a directory. ")
                else:
                    self.window.open_file(file_path)
        self.clear()

    def clear(self):
        if self.view != None:
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
            return ""

        view = self.view
        path = ""
        for region in view.sel():
            syntax = view.syntax_name(region.begin())
            if region.begin() != region.end():
                path = view.substr(region)
                break
            if re.match(".*string.quoted.double", syntax) or re.match(".*string.quoted.single", syntax):
                path = view.substr(view.extract_scope(region.begin()))
                path = re.sub('^"|\'', '',  re.sub('"|\'$', '', path.strip()))
                break

        return path


class PathAutocomplete(sublime_plugin.EventListener):
    aliases = {}
    show_files = False
    ignore_case = False

    path = ""
    root = ""
    default_root = True
    view_id = None

    prev_suggestions = []
    prev_base = ""
    prev_directory = ""
    path_empty = True
    prev_root = ""
    prev_prefix = ""
    prev_locations = []

    def on_query_context(self, view, key, operator, operand, match_all):
        if key == "advanced_new_file_completion" and PathAutocomplete.view_id != None and view.id() == PathAutocomplete.view_id:
            return True
        return None

    def continue_previous_autocomplete(self):
        pac = PathAutocomplete
        sep = os.sep
        root_path = pac.root + sep
        prev_base = pac.prev_base
        prev_directory = pac.prev_directory
        prev_root = pac.prev_root

        base = os.path.basename(pac.path)
        directory = os.path.dirname(pac.path)

        # If base is empty, we may be cycling through directory options
        if base == "":
            return True

        # Ensures the correct directory is used if the default root is specified
        # using an alias.
        if base == prev_base and \
        directory == prev_directory and \
        prev_root == root_path and \
        pac.default_root:
            return True
        # Continue completions if file names are completed.
        if os.path.isfile(os.path.join(root_path, pac.path)):
            return True
        return False

    def on_query_completions(self, view, prefix, locations):
        pac = PathAutocomplete
        if pac.view_id == None or view.id() != pac.view_id:
            return []

        auto_complete_prefix = ""
        if self.continue_previous_autocomplete() and prefix != "":
            if DEBUG:
                print "AdvancedNewFile[Debug]: (Prev) Suggestions"
                print pac.prev_suggestions
            if len(pac.prev_suggestions) > 1:
                return (pac.prev_suggestions, sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)
            elif len(pac.prev_suggestions) == 1:
                auto_complete_prefix = pac.prev_suggestions[0][1]

        suggestions = []
        suggestions_w_spaces = []
        root_path = pac.root + os.sep
        directory, base = os.path.split(pac.path)

        if directory == "" and pac.default_root:
            # Project folders
            sugg, sugg_w_spaces = self.generate_project_auto_complete(base)
            suggestions += sugg
            suggestions_w_spaces += sugg_w_spaces
            # Aliases
            sugg, sugg_w_spaces = self.generate_alias_auto_complete(base)
            suggestions += sugg
            suggestions_w_spaces += sugg_w_spaces

        # Directories
        path = os.path.join(root_path, directory)
        if os.path.exists(path):
            sugg, sugg_w_spaces = self.generate_relative_auto_complete(path, base, auto_complete_prefix)
            suggestions += sugg
            suggestions_w_spaces += sugg_w_spaces
        # If suggestions exist, use complete name
        # else remove base prefix
        if len(suggestions) > 0:
            for name in suggestions_w_spaces:
                suggestions.append((" " + name, name))
        else:
            for name in suggestions_w_spaces:
                temp = name
                name = name[len(base) - 1:]
                suggestions.append((" " + temp, name))

        if len(suggestions) == 0 and locations == pac.prev_locations:
            return (pac.prev_suggestions, sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)
        # Previous used to determine cycling through entries.
        pac.prev_directory = directory
        pac.prev_base = base
        pac.prev_suggestions = suggestions
        pac.prev_root = root_path
        pac.prev_prefix = prefix
        pac.prev_locations = locations
        if DEBUG:
            print "AdvancedNewFile[Debug]: Suggestions:"
            print suggestions
        return (suggestions, sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)

    def generate_project_auto_complete(self, base):
        folders = sublime.active_window().folders()
        folders = map(lambda f: os.path.basename(f), folders)
        return self.generate_auto_complete(base, folders)

    def generate_alias_auto_complete(self, base):
        return self.generate_auto_complete(base, PathAutocomplete.aliases)

    def generate_auto_complete(self, base, iterable_var):
        sugg = []
        sugg_w_spaces = []

        for entry in iterable_var:
            compare_entry = entry
            compare_base = base
            if PathAutocomplete.ignore_case:
                compare_entry = compare_entry.lower()
                compare_base = compare_base.lower()

            if compare_entry.find(compare_base) == 0:
                if " " in base:
                    sugg_w_spaces.append(entry + ":")
                else:
                    sugg.append((entry + ":", entry + ":"))
        return sugg, sugg_w_spaces

    def generate_relative_auto_complete(self, path, base, auto_complete_prefix):
        sep = os.sep
        sugg = []
        sugg_w_spaces = []

        # Attempt to prevent searching the same path when a path has been specified
        # Problems occur when using tab to complete entry with single completion
        # followed by ctrl + space
        if ":" in auto_complete_prefix:
            compare_prefix = auto_complete_prefix.split(":", 1)[1]
        else:
            compare_prefix = auto_complete_prefix

        if re.search(r"[/\\]$", auto_complete_prefix) and not path.endswith(compare_prefix[0:-1]):
            path = os.path.join(path, compare_prefix)

        for filename in os.listdir(path):
            if PathAutocomplete.show_files or os.path.isdir(os.path.join(path, filename)):
                compare_base = base
                compare_filename = filename
                if PathAutocomplete.ignore_case:
                    compare_base = compare_base.lower()
                    compare_filename = filename.lower()

                if compare_filename.find(compare_base) == 0:
                    # Need to find a better way to do the auto complete.
                    if " " in compare_base:
                        if os.path.isdir(os.path.join(path, filename)):
                            sugg_w_spaces.append(auto_complete_prefix + filename + sep)
                        else:
                            sugg_w_spaces.append(auto_complete_prefix + filename)
                    else:
                        if os.path.isdir(os.path.join(path, filename)):
                            sugg.append((" " + auto_complete_prefix + filename + sep, auto_complete_prefix + filename + sep))
                        else:
                            sugg.append((" " + auto_complete_prefix + filename, auto_complete_prefix + filename))

        return sugg, sugg_w_spaces

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
        PathAutocomplete.prev_prefix = ""
        PathAutocomplete.prev_locations = []
        PathAutocomplete.view_id = None

    @staticmethod
    def set_aliases(aliases):
        PathAutocomplete.aliases = aliases

    @staticmethod
    def set_show_files(show_files):
        PathAutocomplete.show_files = show_files

    @staticmethod
    def set_ignore_case(ignore_case):
        PathAutocomplete.ignore_case = ignore_case

    @staticmethod
    def set_view_id(view_id):
        PathAutocomplete.view_id = view_id


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
