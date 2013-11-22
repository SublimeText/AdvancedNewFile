import os
import sublime
import sublime_plugin
import re
import logging
import errno
import shutil
import subprocess

import AdvancedNewFile.advanced_new_file.anf_util as anf_util
from .nix_platform import NixPlatform, NixCompletion
from .anf_windows_platform import WindowsPlatform, WindowsCompletion

VIEW_NAME = "AdvancedNewFileCreation"
WIN_ROOT_REGEX = r"[a-zA-Z]:(/|\\)"
NIX_ROOT_REGEX = r"^/"
HOME_REGEX = r"^~"
PLATFORM = sublime.platform().lower()
IS_ST3 = int(sublime.version()) > 3000

# Set up logger
logging.basicConfig(format='[AdvancedNewFile] %(levelname)s %(message)s')
logger = logging.getLogger()

class AdvancedNewFileBase(object):

    def __init__(self, window):
        print("FASFD")
        super(AdvancedNewFileBase, self).__init__(window)

        self.top_level_split_char = ":"
        if PLATFORM == "windows":
            self.platform = WindowsPlatform()
        else:
            self.platform = NixPlatform()


    def __generate_default_root(self):
        default_root = self.__get_default_root(self.settings.get(anf_util.DEFAULT_ROOT_SETTING))
        if default_root == "path":
            self.root = os.path.expanduser(self.settings.get(anf_util.DEFAULT_PATH_SETTING))
            default_root = ""
        return self.__split_path(default_root)

    def __generate_alias_root(self):
        alias_root = self.__get_default_root(self.settings.get(anf_util.ALIAS_ROOT_SETTING), True)
        if alias_root == "path":
            self.alias_root = os.path.expanduser(self.settings.get(anf_util.ALIAS_PATH_SETTING))
            alias_root = ""
        return self.__split_path(alias_root, True)

    def generate_initial_path(self):
        _, path = self.__generate_default_root()

        # Search for initial string

        if initial_path is not None:
            path = initial_path
        else:
            if path == "":
                path = self.settings.get(anf_util.DEFAULT_ROOT_SETTING)
            if self.settings.get(anf_util.USE_CURSOR_TEXT_SETTING, False):
                cursor_text = self.get_cursor_path()
                if cursor_text != "":
                    path = cursor_text

        return path

    def run_setup(self):
        self.view = self.window.active_view()
        self.settings = anf_util.get_settings(self.view)
        self.root = None
        self.alias_root = None
        self.aliases = self.__get_aliases()

        self.root, _ = self.__generate_default_root()
        self.alias_root, _ = self.__generate_alias_root()

        # Need to fix this
        debug = self.settings.get("debug") or False
        if debug:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.ERROR)

        print(self.settings.get(anf_util.COMPLETION_TYPE_SETTING))
        completion_type = self.settings.get(anf_util.COMPLETION_TYPE_SETTING)
        if completion_type == "windows":
            self.completion = WindowsCompletion(self.settings, self.view)
        else:
            self.completion = NixCompletion(self.settings)

    def __get_aliases(self):
        aliases = self.settings.get("alias")
        all_os_aliases = self.settings.get("os_specific_alias")
        for key in all_os_aliases:
            if PLATFORM in all_os_aliases.get(key):
                aliases[key] = all_os_aliases.get(key).get(PLATFORM)

        return aliases

    def __get_default_root(self, string, is_alias=False):
        root = ""
        if string == "home":
            root = "~/"
        elif string == "current":
            root = self.top_level_split_char
        elif string == "project_folder":
            num_folders = len(self.window.folders())
            if is_alias:
                folder_index = self.settings.get("alias_folder_index")
                self.alias_folder_index = 0 if num_folders <= folder_index else folder_index
            else:
                folder_index = self.settings.get("default_folder_index")
                self.default_folder_index = 0 if num_folders <= folder_index else folder_index
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

    def __split_path(self, path="", is_alias=False):
        HOME_REGEX = r"^~[/\\]"
        root = None
        try:
            root, path = self.platform.split(path)
            # Parse if alias
            if self.top_level_split_char in path and root == None:
                parts = path.rsplit(self.top_level_split_char, 1)
                root, path = self.__translate_alias(parts[0])
                path_list = []
                if path != "":
                    path_list.append(path)
                if parts[1] != "":
                    path_list.append(parts[1])
                path = self.top_level_split_char.join(path_list)
            elif re.match(r"^/", path):
                root, path_offset = self.platform.parse_nix_path(root, path)
                path = path[path_offset:]
            # Parse if tilde used
            elif re.match(HOME_REGEX, path) and root == None:
                root = os.path.expanduser("~")
                path = path[2:]
            elif re.match(r"^\.{1,2}[/\\]", path) and self.settings.get("relative_from_current", False):
                path_index = 2
                root = os.path.dirname(self.view.file_name())
                if re.match(r"^\.{2}[/\\]", path):
                    root = os.path.dirname(root)
                    path_index = 3
                path = path[path_index:]

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

    def __translate_alias(self, path):
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
                            root = self.platform.get_alias_absolute_path(alias_path)
                            if root is not None:
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

    def input_panel_caption(self):
        return ""

    def show_filename_input(self, caption="", initial=''):
        self.input_panel_view = self.window.show_input_panel(
            self.input_panel_caption(), initial,
            self.entered_filename, self.__update_filename_input, self.clear
        )

        self.input_panel_view.set_name(VIEW_NAME)
        self.input_panel_view.settings().set("auto_complete_commit_on_tab", False)
        self.input_panel_view.settings().set("tab_completion", False)
        self.input_panel_view.settings().set("translate_tabs_to_spaces", False)
        self.input_panel_view.settings().set("anf_panel", True)

    # Auto complete and path resolution common to all commands
    def __update_filename_input(self, path_in):
        if self.settings.get("completion_type") == "windows":
            if "prev_text" in dir(self) and self.prev_text != path_in:
                if self.view is not None:
                    self.view.erase_status("AdvancedNewFile2")
        if path_in.endswith("\t"):
            path_in = path_in.replace("\t", "")
            if self.settings.get("completion_type") == "windows":
                path_in = self.__windows_completion(path_in)
            elif self.settings.get("completion_type") == "nix":
                path_in = self.__nix_completion(path_in)
        self.input_panel_view.run_command("anf_replace", {"content": path_in})
        base, path = self.__split_path(path_in)

        creation_path = self.__generate_creation_path(base, path, True)
        if self.settings.get(and_util.SHOW_PATH_SETTING, False):
            if self.view != None:
                if self.rename:
                    if os.path.isdir(creation_path):
                        creation_path = os.path.join(creation_path, self.original_name)
                    self.view.set_status("AdvancedNewFile", "Moving file to %s " % \
                        creation_path)
                else:
                    self.view.set_status("AdvancedNewFile", "Creating file at %s " % \
                        creation_path)
            else:
                if self.rename:
                    sublime.status_message("Moving file to %s" % creation_path)
                else:
                    sublime.status_message("Creating file at %s" % creation_path)
        logger.debug("Creation path is '%s'" % creation_path)

    def entered_file_action(self, path):
        pass

    def entered_filename(self, filename):
        # Check if valid root specified for windows.
        if PLATFORM == "windows":
            if re.match(WIN_ROOT_REGEX, filename):
                root = filename[0:3]
                if not os.path.isdir(root):
                    sublime.error_message(root + " is not a valid root.")
                    self.clear()
                    return

        base, path = self.__split_path(filename)
        file_path = self.__generate_creation_path(base, path, True)
        # Check for invalid alias specified.
        if self.top_level_split_char in filename and \
            not (PLATFORM == "windows" and re.match(WIN_ROOT_REGEX, base)) and \
            not (PLATFORM != "windows" and re.match(NIX_ROOT_REGEX, base)):
            if base == "":
                error_message = "Current file cannot be resolved."
            else:
                error_message = "'" + base + "' is an invalid alias."
            sublime.error_message(error_message)

        self.entered_file_action(file_path)

        self.clear()
        self.refresh_sidebar()

    def open_file(self, file_path):
        new_view = None
        if os.path.isdir(file_path):
            if not re.search(r"(/|\\)$", file_path):
                sublime.error_message("Cannot open view for '" + file_path + "'. It is a directory. ")
        else:
            new_view = self.window.open_file(file_path)
        return new_view

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
            creation_path = os.path.join(base, filename)
            self.create_file(creation_path)

    def create_file(self, name):
        open(name, "a").close()
        if self.settings.get("file_permissions", "") != "":
            file_permissions = self.settings.get("file_permissions", "")
            os.chmod(name, int(file_permissions, 8))

    def create_folder(self, path):
        init_list = []
        temp_path = path
        while not os.path.exists(temp_path):
            init_list.append(temp_path)
            temp_path = os.path.dirname(temp_path)
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except OSError as ex:
            if ex.errno != errno.EEXIST:
                raise

        file_permissions = self.settings.get("file_permissions", "")
        folder_permissions = self.settings.get("folder_permissions", "")
        for entry in init_list:
            if self.is_python:
                creation_path = os.path.join(entry, '__init__.py')
                open(creation_path, 'a').close()
                if  file_permissions != "":
                    os.chmod(creation_path, int(file_permissions, 8))
            if  folder_permissions != "":
                os.chmod(entry, int(folder_permissions, 8))


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



