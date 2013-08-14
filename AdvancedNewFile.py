import os
import sublime
import sublime_plugin
import re
import logging
import errno

SETTINGS = [
    "alias",
    "default_initial",
    "use_cursor_text",
    "show_files",
    "show_path",
    "default_root",
    "default_path",
    "default_folder_index",
    "os_specific_alias",
    "ignore_case",
    "alias_root",
    "alias_path",
    "alias_folder_index",
    "debug",
    "auto_refresh_sidebar",
    "completion_type",
    "complete_single_entry",
    "use_folder_name"
]
VIEW_NAME = "AdvancedNewFileCreation"
WIN_ROOT_REGEX = r"[a-zA-Z]:(/|\\)"
NIX_ROOT_REGEX = r"^/"
HOME_REGEX = r"^~"
PLATFORM = sublime.platform().lower()
IS_ST3 = int(sublime.version()) > 3000

# Set up logger
logging.basicConfig(format='[AdvancedNewFile] %(levelname)s %(message)s')
logger = logging.getLogger()


class AdvancedNewFileCommand(sublime_plugin.WindowCommand):
    def run(self, is_python=False, initial_path=None):
        PLATFORM = sublime.platform().lower()
        self.root = None
        self.alias_root = None
        self.top_level_split_char = ":"
        self.is_python = is_python
        self.view = self.window.active_view()

        # Settings will be based on the view
        self.settings = get_settings(self.view)
        self.aliases = self.get_aliases()
        self.show_path = self.settings.get("show_path")
        self.default_folder_index = self.settings.get("default_folder_index")
        self.alias_folder_index = self.settings.get("alias_folder_index")
        default_root = self.get_default_root(self.settings.get("default_root"))
        if default_root == "path":
            self.root = os.path.expanduser(self.settings.get("default_path"))
            default_root = ""
        self.root, path = self.split_path(default_root)

        # Search for initial string
        if initial_path is not None:
            path = initial_path
        else:
            path = self.settings.get("default_initial", "")
            if self.settings.get("use_cursor_text", False):
                tmp = self.get_cursor_path()
                if tmp != "":
                    path = tmp

        alias_root = self.get_default_root(self.settings.get("alias_root"), True)
        if alias_root == "path":
            self.alias_root = os.path.expanduser(self.settings.get("alias_path"))
            alias_root = ""
        self.alias_root, tmp = self.split_path(alias_root, True)

        debug = self.settings.get("debug") or False
        if debug:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.ERROR)
        # Get user input
        self.show_filename_input(path)

    def get_aliases(self):
        aliases = self.settings.get("alias")
        all_os_aliases = self.settings.get("os_specific_alias")
        for key in all_os_aliases:
            if PLATFORM in all_os_aliases.get(key):
                aliases[key] = all_os_aliases.get(key).get(PLATFORM)

        return aliases

    def get_default_root(self, string, is_alias=False):
        root = ""

        if string == "home":
            root = "~/"
        elif string == "current":
            root = self.top_level_split_char
        elif string == "project_folder":
            if is_alias:
                folder_index = self.alias_folder_index
            else:
                folder_index = self.default_folder_index
            if len(self.window.folders()) <= folder_index:
                if is_alias:
                    self.alias_folder_index = 0
                else:
                    self.default_folder_index = 0
        elif string == "top_folder":
            if is_alias:
                self.alias_folder_index = 0
            else:
                self.default_folder_index = 0
        elif string == "path":
            root = "path"
        else:
            logger.error("Invalid specifier for \"default_root\"")
        return root

    def split_path(self, path="", is_alias=False):
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
                parts = path.rsplit(self.top_level_split_char, 1)
                root, path = self.translate_alias(parts[0])
                path_list = []
                if path != "":
                    path_list.append(path)
                if parts[1] != "":
                    path_list.append(parts[1])
                path = self.top_level_split_char.join(path_list)
            # Parse if tilde used
            elif re.match(HOME_REGEX, path) and root == None:
                root = os.path.expanduser("~")
                path = path[2:]

            # Default
            if root == None:
                if is_alias:
                    root = self.alias_root
                    folder_index = self.alias_folder_index
                else:
                    root = self.root
                    folder_index = self.default_folder_index
                root = root or self.window.folders()[folder_index]
        except IndexError:
            root = os.path.expanduser("~")
        return root, path

    def translate_alias(self, path):
        root = None
        split_path = None
        if path == "" and self.view is not None:
            filename = self.view.file_name()
            if filename is not None:
                root = os.path.dirname(filename)
        else:
            split_path = path.split(self.top_level_split_char)
            join_index = len(split_path) - 1
            target = path
            root_found = False
            while join_index >= 0 and not root_found:
                # Folder aliases
                for name, folder in get_project_folder_data(self.settings.get("use_folder_name")):
                    if name == target:
                        root = folder
                        root_found = True
                        break
                # Aliases from settings.
                for alias in self.aliases.keys():
                    if alias == target:
                        alias_path = self.aliases.get(alias)
                        if re.search(HOME_REGEX, alias_path) is None:
                            if PLATFORM == "windows":
                                if re.search(WIN_ROOT_REGEX, alias_path) is None:
                                    root = os.path.join(self.alias_root, alias_path)
                                    break
                            else:
                                if re.search(NIX_ROOT_REGEX, alias_path) is None:
                                    root = os.path.join(self.alias_root, alias_path)
                                    break
                        root = os.path.expanduser(alias_path)
                        root_found = True
                        break
                remove = re.escape(split_path[join_index])
                target = re.sub(r":%s$" % remove, "", target)
                join_index -= 1

        if root is None:
            return None, path
        elif split_path is None:
            return os.path.abspath(root), ""
        else:
            # Add to index so we re
            join_index += 2
            return os.path.abspath(root), self.top_level_split_char.join(split_path[join_index:])

    def show_filename_input(self, initial=''):
        caption = 'Enter a path for a new file'
        if self.is_python:
            caption = '%s (creates __init__.py in new dirs)' % caption
        self.input_panel_view = self.window.show_input_panel(
            caption, initial,
            self.entered_filename, self.update_filename_input, self.clear
        )

        self.input_panel_view.set_name(VIEW_NAME)
        self.input_panel_view.settings().set("auto_complete_commit_on_tab", False)
        self.input_panel_view.settings().set("tab_completion", False)
        self.input_panel_view.settings().set("translate_tabs_to_spaces", False)
        self.input_panel_view.settings().set("anf_panel", True)

    def update_filename_input(self, path_in):
        if self.settings.get("completion_type") == "windows":
            if "prev_text" in dir(self) and self.prev_text != path_in:
                self.view.erase_status("AdvancedNewFile2")
        if path_in.endswith("\t"):
            path_in = path_in.replace("\t", "")
            if self.settings.get("completion_type") == "windows":
                path_in = self.windows_completion(path_in)
            elif self.settings.get("completion_type") == "nix":
                path_in = self.nix_completion(path_in)

        base, path = self.split_path(path_in)

        creation_path = self.generate_creation_path(base, path)
        if self.show_path:
            if self.view != None:
                self.view.set_status("AdvancedNewFile", "Creating file at %s " % \
                    creation_path)
            else:
                sublime.status_message("Creating file at %s" % creation_path)
        logger.debug("Creation path is '%s'" % creation_path)

    def generate_completion_list(self, path_in, each_list=False):
        alias_list = []
        dir_list = []
        file_list = []
        self.suggestion_entries = []
        if self.top_level_split_char in path_in or re.match(r"^~[/\\]", path_in):
            pass
        else:
            directory, filename = os.path.split(path_in)
            if len(directory) == 0:
                alias_list += self.generate_alias_auto_complete(filename)
                alias_list += self.generate_project_auto_complete(filename)
        base, path = self.split_path(path_in)
        directory, filename = os.path.split(path)

        directory = os.path.join(base, directory)
        if os.path.isdir(directory):
            for d in os.listdir(directory):
                full_path = os.path.join(directory, d)
                if os.path.isdir(full_path):
                    is_file = False
                elif self.settings.get("show_files"):
                    is_file = True
                else:
                    continue

                if self.compare_entries(d, filename):
                    if is_file:
                        file_list.append(d)
                    else:
                        dir_list.append(d)

        completion_list = alias_list + dir_list + file_list

        return sorted(completion_list), alias_list, dir_list, file_list

    def windows_completion(self, path_in):
        pattern = r"(.*[/\\:])(.*)"
        match = re.match(pattern, path_in)
        if "prev_text" in dir(self) and self.prev_text == path_in:
            self.offset = (self.offset + 1) % len(self.completion_list)
        else:
            # Generate new completion list
            self.completion_list, self.alias_list, self.dir_list, self.file_list = self.generate_completion_list(path_in)
            self.offset = 0

            if len(self.completion_list) == 0:
                if match:
                    self.completion_list = [match.group(2)]
                else:
                    self.completion_list = [path_in]
        match = re.match(pattern, path_in)
        if match :
            completion = self.completion_list[self.offset]
            if self.settings.get("complete_single_entry"):
                if len(self.completion_list) == 1:
                    if completion in self.alias_list:
                        completion += ":"
                    elif completion in self.dir_list:
                        completion += "/"
            new_content = re.sub(pattern, r"\1" , path_in)
            new_content += completion
            first_token = False
        else:
            completion = self.completion_list[self.offset]
            if self.settings.get("complete_single_entry"):
                if len(self.completion_list) == 1:
                    if completion in self.alias_list:
                        completion += ":"
                    elif completion in self.dir_list:
                        completion += "/"
            new_content = completion
            first_token = True

        if len(self.completion_list) > 1:
            if first_token:
                if self.completion_list[self.offset] in self.alias_list:
                    self.view.set_status("AdvancedNewFile2", "Alias Completion")
                elif self.completion_list[self.offset] in self.dir_list:
                    self.view.set_status("AdvancedNewFile2", "Directory Completion")
            self.prev_text = new_content
        else:
            self.prev_text = None
        self.input_panel_view.run_command("anf_replace", {"content": new_content})
        return new_content

    def nix_completion(self, path_in):
        pattern = r"(.*[/\\:])(.*)"

        completion_list, alias_list, dir_list, file_list = self.generate_completion_list(path_in)
        new_content = path_in
        if len(completion_list) > 0:
            common = os.path.commonprefix(completion_list)
            match = re.match(pattern, path_in)
            if match :
                new_content = re.sub(pattern, r"\1", path_in)
                new_content += common
            else:
                new_content = common
            if len(completion_list) > 1:
                dir_list = map(lambda s: s + "/", dir_list)
                alias_list = map(lambda s: s + ":", alias_list)
                status_message_list = sorted(list(dir_list) + list(alias_list) + file_list)
                sublime.status_message(", ".join(status_message_list))
            else:
                if completion_list[0] in alias_list:
                    new_content += ":"
                elif completion_list[0] in dir_list:
                    new_content += "/"
        self.input_panel_view.run_command("anf_replace", {"content": new_content})
        return new_content

    def generate_project_auto_complete(self, base):
        folder_data = get_project_folder_data(self.settings.get("use_folder_name"))
        if len(folder_data) > 1:
            folders = [x[0] for x in folder_data]
            return self.generate_auto_complete(base, folders)
        return []

    def generate_alias_auto_complete(self, base):
        return self.generate_auto_complete(base, self.aliases)

    def generate_auto_complete(self, base, iterable_var):
        sugg = []
        for entry in iterable_var:
            if entry in self.suggestion_entries:
                continue
            self.suggestion_entries.append(entry)
            compare_entry = entry
            compare_base = base
            if self.settings.get("ignore_case"):
                compare_entry = compare_entry.lower()
                compare_base = compare_base.lower()

            if self.compare_entries(compare_entry, compare_base):
                sugg.append(entry)

        return sugg

    def compare_entries(self, compare_entry, compare_base):
        if self.settings.get("ignore_case"):
            compare_entry = compare_entry.lower()
            compare_base = compare_base.lower()

        return compare_entry.startswith(compare_base)


    def generate_creation_path(self, base, path):
        if PLATFORM == "windows":
            if not re.match(WIN_ROOT_REGEX, base):
                return base + self.top_level_split_char + path
        else:
            if not re.match(NIX_ROOT_REGEX, base):
                return base + self.top_level_split_char + path

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
            logger.debug("Creating file at %s", file_path)
            if not os.path.exists(file_path):
                try:
                    self.create(file_path)
                except OSError as e:
                    attempt_open = False
                    sublime.error_message("Cannot create '" + file_path + "'. See console for details")
                    logger.error("Exception: %s '%s'" % (e.strerror, e.filename))
            if attempt_open:
                if os.path.isdir(file_path):
                    if not re.search(r"(/|\\)$", file_path):
                        sublime.error_message("Cannot open view for '" + file_path + "'. It is a directory. ")
                else:
                    self.window.open_file(file_path)
        self.clear()
        self.refresh_sidebar()

    def refresh_sidebar(self):
        if self.settings.get("auto_refresh_sidebar"):
            try:
                self.window.run_command("refresh_folder_list")
            except:
                pass

    def clear(self):
        if self.view != None:
            self.view.erase_status("AdvancedNewFile")
            self.view.erase_status("AdvancedNewFile2")

    def create(self, filename):
        base, filename = os.path.split(filename)
        self.create_folder(base)
        if filename != "":
            open(os.path.join(base, filename), "a").close()

    def create_folder(self, path):
        init_list = []
        if self.is_python:
            temp_path = path
            while not os.path.exists(temp_path):
                init_list.append(temp_path)
                temp_path = os.path.dirname(temp_path)
        try:
            os.makedirs(path)
        except OSError as ex:
            if ex.errno != errno.EEXIST:
                raise

        for entry in init_list:
            open(os.path.join(entry, '__init__.py'), 'a').close()

    def get_cursor_path(self):
        if self.view == None:
            return ""

        view = self.view
        path = ""
        for region in view.sel():
            syntax = view.scope_name(region.begin())
            if region.begin() != region.end():
                path = view.substr(region)
                break
            if re.match(".*string.quoted.double", syntax) or re.match(".*string.quoted.single", syntax):
                path = view.substr(view.extract_scope(region.begin()))
                path = re.sub('^"|\'', '',  re.sub('"|\'$', '', path.strip()))
                break

        return path


class AnfReplaceCommand(sublime_plugin.TextCommand):
    def run(self, edit, content):
        self.view.replace(edit, sublime.Region(0, self.view.size()), content)


class AdvancedNewFileAtCommand(sublime_plugin.WindowCommand):
    def run(self, dirs):
        if len(dirs) != 1:
            return
        path = dirs[0]
        self.window.run_command("advanced_new_file", {"initial_path": path + os.sep})


    def is_visible(self, dirs):
        settings = sublime.load_settings("AdvancedNewFile.sublime-settings")
        return settings.get("show_sidebar_menu", False) and len(dirs) == 1


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
            logger.error("AdvancedNewFile[Warning]: Invalid key '%s' in project settings.", key)

    return local_settings

def get_project_folder_data(use_folder_name):
    folders = []
    folder_entries = []
    window = sublime.active_window()
    project_folders = window.folders()

    if IS_ST3:
        project_data = window.project_data()

        if project_data is not None:
            if use_folder_name:
                for folder in project_data.get("folders", []):
                    folder_entries.append({})
            else:
                folder_entries = project_data.get("folders", [])
    else:
        for folder in project_folders:
            folder_entries.append({})
    for index in range(len(folder_entries)):
        folder_path = project_folders[index]
        folder_entry = folder_entries[index]
        if "name" in folder_entry:
            folders.append((folder_entry["name"], folder_path))
        else:
            folders.append((os.path.basename(folder_path), folder_path))

    return folders
