import errno
import os
import re
import sublime
import sublime_plugin
import shlex
import json

from ..anf_util import *
from ..platform.windows_platform import WindowsPlatform
from ..platform.nix_platform import NixPlatform
from ..completions.nix_completion import NixCompletion
from ..completions.windows_completion import WindowsCompletion

if not IS_ST3:
    if PLATFORM == "windows":
        import sys
        sys.path.append(os.path.dirname(sys.executable))
    from ..lib.ushlex import split as st2_shlex_split


VIEW_NAME = "AdvancedNewFileCreation"


class AdvancedNewFileBase(object):
    def __init__(self, window):
        super()
        self.window = window
        self.prev_text = None

        if PLATFORM == "windows":
            self.platform = WindowsPlatform(window.active_view())
        else:
            self.platform = NixPlatform()

    def __generate_default_root(self):
        root_setting = self._get_default_root()
        path, folder_index = self.__parse_path_setting(
            root_setting, DEFAULT_FOLDER_INDEX_SETTING)
        if path is None and folder_index is None:
            return os.path.expanduser(self.settings.get(DEFAULT_PATH_SETTING))
        elif path is None:
            return self.__project_folder_from_index(folder_index)
        return path

    def __generate_alias_root(self):
        path, folder_index = self.__parse_path_setting(
            self.settings.get(ALIAS_ROOT_SETTING), ALIAS_FOLDER_INDEX_SETTING)
        if path is None and folder_index is None:
            return os.path.expanduser(self.settings.get(ALIAS_PATH_SETTING))
        elif path is None:
            if folder_index >= 0:
                return self.window.folders()[folder_index]
            else:
                return os.path.expanduser("~/")
        return path

    def generate_initial_path(self, initial_path=None):
        path = None
        # Search for initial string
        if initial_path is not None:
            path = initial_path
        else:
            if self.settings.get(USE_CURSOR_TEXT_SETTING, False):
                cursor_text = self.get_cursor_path()
                if cursor_text != "":
                    path = cursor_text

            if path is None:
                path = self.settings.get(DEFAULT_INITIAL_SETTING)

        return path

    def run_setup(self):
        self.view = self.window.active_view()
        self.settings = get_settings(self.view)
        self.root = None
        self.alias_root = None
        self.aliases = self.__get_aliases()

        self.root = self.__generate_default_root()
        self.alias_root = self.__generate_alias_root()

        # Need to fix this
        debug = self.settings.get(DEBUG_SETTING) or False

        completion_type = self.settings.get(COMPLETION_TYPE_SETTING)
        if completion_type == "windows":
            self.completion = WindowsCompletion(self)
        else:
            self.completion = NixCompletion(self)

    def __get_aliases(self):
        aliases = self.settings.get(ALIAS_SETTING)
        all_os_aliases = self.settings.get(OS_SPECIFIC_ALIAS_SETTING)
        if all_os_aliases is not None and aliases is not None:
            for key in all_os_aliases:
                if PLATFORM in all_os_aliases.get(key):
                    aliases[key] = all_os_aliases.get(key).get(PLATFORM)

        return aliases

    def __parse_path_setting(self, setting, index_setting):
        root = None
        folder_index = None
        if setting == "home":
            root = os.path.expanduser("~/")
        elif setting == "current":
            if self.view is not None:
                filename = self.view.file_name()
                if filename is not None:
                    root = os.path.dirname(filename)
            if root is None:
                if self.settings.get(CURRENT_FALLBACK_TO_PROJECT_SETTING, False):
                    folder_index = self.__validate_folder_index(0)
                    if folder_index == -1:
                        root = os.path.expanduser("~/")
                else:
                    root = os.path.expanduser("~/")
        elif setting == "project_folder":
            folder_index = self.settings.get(index_setting)
            folder_index = self.__validate_folder_index(folder_index)
        elif setting == "top_folder":
            folder_index = self.__validate_folder_index(0)
        elif setting == "path":
            pass
        else:
            print("Invalid root specifier")

        return (root, folder_index)

    def __validate_folder_index(self, folder_index):
        num_folders = len(self.window.folders())
        if num_folders == 0:
            folder_index = -1
        elif num_folders < folder_index:
            folder_index = 0
        return folder_index

    def __parse_for_shell_input(self, path):
        if not IS_ST3 and self.__contains_non_ascii(path):
            split_path = self.__split_shell_input_for_st2_non_ascii(path)
        else:
            split_path = shlex.split(str(path))

        return " ".join(split_path)

    def __split_shell_input_for_st2_non_ascii(self, path):
        return st2_shlex_split(path)

    def __contains_non_ascii(self, string):
        # Don't really like this....
        try:
            string.decode("ascii")
        except UnicodeEncodeError:
            return True
        return False

    def split_path(self, path=""):
        HOME_REGEX = r"^~[/\\]"
        root = None
        try:
            root, path = self.platform.split(path)
            if self.settings.get(SHELL_INPUT_SETTING, False) and len(path) > 0:
                path = self.__parse_for_shell_input(path)
            # Parse if alias
            if TOP_LEVEL_SPLIT_CHAR in path and root is None:
                parts = path.rsplit(TOP_LEVEL_SPLIT_CHAR, 1)
                root, path = self.__translate_alias(parts[0])
                path_list = []
                if path != "":
                    path_list.append(path)
                if parts[1] != "":
                    path_list.append(parts[1])
                path = TOP_LEVEL_SPLIT_CHAR.join(path_list)
            elif re.match(r"^/", path):
                root, path_offset = self.platform.parse_nix_path(root, path)
                path = path[path_offset:]
            # Parse if tilde used
            elif re.match(HOME_REGEX, path) and root is None:
                root = os.path.expanduser("~")
                path = path[2:]
            elif (re.match(r"^\.{1,2}[/\\]", path) and
                  self.settings.get(RELATIVE_FROM_CURRENT_SETTING, False)):
                path_index = 2
                if self.view.file_name() is not None:
                    root = os.path.dirname(self.view.file_name())
                else:
                    folder_index = self.settings.get(
                        RELATIVE_FALLBACK_INDEX_SETTING, 0)
                    folder_index = self.__validate_folder_index(folder_index)
                    root = self.__project_folder_from_index(folder_index)
                if re.match(r"^\.{2}[/\\]", path):
                    root = os.path.dirname(root)
                    path_index = 3
                path = path[path_index:]

            # Default
            if root is None:
                root = self.root
        except IndexError:
            root = os.path.expanduser("~")

        return root, path

    def __project_folder_from_index(self, folder_index):
        if folder_index >= 0:
            return self.window.folders()[folder_index]
        else:
            return os.path.expanduser("~/")

    def bash_expansion(self, path):
        if len(path) == 0:
            return path

        split_path = shlex.split(path)
        new_path = " ".join(split_path)
        return new_path

    def __translate_alias(self, path):
        root = None
        split_path = None
        if path == "" and self.view is not None:
            filename = self.view.file_name()
            if filename is not None:
                root = os.path.dirname(filename)
        else:
            split_path = path.split(TOP_LEVEL_SPLIT_CHAR)
            join_index = len(split_path) - 1
            target = path
            root_found = False
            use_folder_name = self.settings.get(USE_FOLDER_NAME_SETTING)
            while join_index >= 0 and not root_found:
                # Folder aliases
                for name, folder in get_project_folder_data(use_folder_name):
                    if name == target:
                        root = folder
                        root_found = True
                        break
                # Aliases from settings.
                for alias in self.aliases.keys():
                    if alias == target:
                        alias_path = self.aliases.get(alias)
                        if re.search(HOME_REGEX, alias_path) is None:
                            root = self.platform.get_alias_absolute_path(
                                self.alias_root, alias_path)
                            if root is not None:
                                break
                        root = os.path.expanduser(alias_path)
                        root_found = True
                        break
                remove = re.escape(split_path[join_index])
                target = re.sub(r":%s$" % remove, "", target)
                join_index -= 1

        if root is None:
            # Nothing found
            return None, path
        elif split_path is None:
            # Current directory as alias
            return os.path.abspath(root), ""
        else:
            # Add to index so we re
            join_index += 2
            return (os.path.abspath(root),
                    TOP_LEVEL_SPLIT_CHAR.join(split_path[join_index:]))

    def input_panel_caption(self):
        return ""

    def get_active_window_settings(self):
        return sublime.active_window().settings()

    def set_input_view(self, input_view):
        self.get_active_window_settings().set("anf_input_view", input_view.id())

    def get_input_view(self):
        return sublime.View(self.get_active_window_settings().get("anf_input_view"))


    def get_active_view_settings(self):
        view = self.get_input_view()
        if view:
            return view.settings()
        else:
            return self.get_active_window_settings()

    def clear_input_view(self):
        self.get_active_view_settings().erase("anf_input_view")

    def set_input_view_content(self, content):
        self.get_active_view_settings().set("anf_input_view_content", content)

    def get_input_view_content(self):
        return self.get_active_view_settings().get("anf_input_view_content")

    def clear_input_view_content(self):
        self.get_active_view_settings().erase("anf_input_view_content")

    def clear_input_view_project_files(self):
        self.get_active_view_settings().erase("anf_input_view_project_files")

    def show_filename_input(self, initial):
        caption = self.input_panel_caption()

        self.input_panel_view = self.window.show_input_panel(
            caption, initial,
            self.on_done, self.__update_filename_input, self.clear
        )

        self.input_panel_view.set_name(VIEW_NAME)
        self.input_panel_view.settings().set("auto_complete_commit_on_tab",
                                             False)
        self.input_panel_view.settings().set("tab_completion", False)
        self.input_panel_view.settings().set("translate_tabs_to_spaces", False)
        self.input_panel_view.settings().set("anf_panel", True)
        if self.settings.get(CURSOR_BEFORE_EXTENSION_SETTING):
            self.__place_cursor_before_extension(self.input_panel_view)
        self.set_input_view(self.input_panel_view)
        self.__update_filename_input(initial)

    def __update_filename_input(self, path_in):
        new_content = path_in
        if self.settings.get(COMPLETION_TYPE_SETTING) == "windows":
            if "prev_text" in dir(self) and self.prev_text != path_in:
                if self.view is not None:
                    self.view.erase_status("AdvancedNewFile2")

        input_view = self.get_input_view()
        if path_in.endswith("\t"):
            creation_path, candidate, completion_list = self.get_input_view_content()
            new_content = self.completion_input(path_in.replace("\n", "").replace("\t", ""), candidate)
        elif path_in.endswith("\n"):
            path_in = path_in.replace("\n", "")
            if input_view:
                # print("visible", input_view.is_popup_visible())
                if input_view.is_popup_visible():
                    input_view.run_command("insert", {"characters": "\t"})
                else:
                    # print("end panel")
                    self.on_done(path_in)
                    self.window.run_command("hide_panel", {"cancel": True})
            return
        else:
            completion_list = self.get_completion_list(path_in)
            if completion_list:
                candidate = completion_list[0]
                completion_list.remove(candidate)
            else:
                candidate = ''

        if input_view:
            try:
                input_view.hide_popup()
            except Exception as e:
                print("hide_popup", e)
        if input_view and new_content != path_in:
            input_view.run_command("anf_replace", {"content": new_content})
        else:
            base, path = self.split_path(path_in)
            creation_path = generate_creation_path(self.settings, base, path, True)
            status_line = self.create_status_line(creation_path, candidate, completion_list)
            self.set_input_view_content((creation_path, candidate, completion_list))

            if self.settings.get(SHOW_PATH_SETTING, False):
                self.update_status_message(status_line)
            if not new_content.endswith(candidate):
                self.show_input_popup(candidate, completion_list)

    def show_input_popup(self, candidate, completion_list):
        try:
            input_view = self.get_input_view()
            if input_view and candidate:
                input_view.show_popup('<strong>' + candidate + '</strong><br/>' + '<br/>'.join(completion_list), max_width=1024)
        except Exception as e:
            print("show_popup", e)

    def get_completion_list(self, path_in):
        return self.completion.complete_for_folder(path_in)

    def completion_input(self, path_in, candidate):
        pattern = r"(.*[/\\:])(.*)"

        match = re.match(pattern, path_in)
        if match:
            new_content = re.sub(pattern, r"\1", path_in)
            new_content += candidate
        else:
            new_content = candidate
        return new_content

    def entered_file_action(self, path):
        pass

    def empty_file_action(self):
        pass

    def on_done(self, input_string):
        if len(input_string) != 0:
            self.entered_filename(input_string)
        elif self.settings.get(DEFAULT_NEW_FILE, False):
            self.empty_file_action()

        self.clear()
        self.refresh_sidebar()

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
        file_path = generate_creation_path(self.settings, base, path, True)
        # Check for invalid alias specified.
        is_valid = (TOP_LEVEL_SPLIT_CHAR in filename and
                    not self.platform.is_absolute_path(base))
        if is_valid:
            if base == "":
                error_message = "Current file cannot be resolved."
            else:
                error_message = "'" + base + "' is an invalid alias."
            sublime.error_message(error_message)

        self.entered_file_action(file_path)

    def open_file(self, file_path):
        new_view = None
        if os.path.isdir(file_path):
            if not re.search(r"(/|\\)$", file_path):
                sublime.error_message("Cannot open view for '" + file_path +
                                      "'. It is a directory. ")
        else:
            new_view = self.window.open_file(file_path)
        return new_view

    def refresh_sidebar(self):
        if self.settings.get(AUTO_REFRESH_SIDEBAR_SETTING):
            try:
                self.window.run_command("refresh_folder_list")
            except:
                pass

    def clear(self):
        if self.view is not None:
            self.view.erase_status("AdvancedNewFile")
            self.view.erase_status("AdvancedNewFile2")
        self.clear_input_view()
        self.clear_input_view_content()
        self.clear_input_view_project_files()

    def create(self, filename):
        base, filename = os.path.split(filename)
        self.create_folder(base)
        if filename != "":
            creation_path = os.path.join(base, filename)
            self.create_file(creation_path)

    def create_file(self, name):
        open(name, "a").close()
        if self.settings.get(FILE_PERMISSIONS_SETTING, "") != "":
            file_permissions = self.settings.get(FILE_PERMISSIONS_SETTING, "")
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

        file_permissions = self.settings.get(FILE_PERMISSIONS_SETTING, "")
        folder_permissions = self.settings.get(FOLDER_PERMISSIONS_SETTING, "")
        for entry in init_list:
            if self.is_python:
                creation_path = os.path.join(entry, '__init__.py')
                open(creation_path, 'a').close()
                if file_permissions != "":
                    os.chmod(creation_path, int(file_permissions, 8))
            if folder_permissions != "":
                os.chmod(entry, int(folder_permissions, 8))

    def get_cursor_path(self):
        if self.view is None:
            return ""

        view = self.view
        path = ""
        for region in view.sel():
            syntax = view.scope_name(region.begin())
            if region.begin() != region.end():
                path = view.substr(region)
                break
            if (re.match(".*string.quoted.double", syntax) or
                    re.match(".*string.quoted.single", syntax)):
                point = region.begin()
                if (re.match(".*punctuation.definition.string.end", syntax)):
                    point -= 1
                path = view.substr(view.extract_scope(point))
                path = re.sub('^"|\'', '',  re.sub('"|\'$', '', path.strip()))
                break

        return path

    def _expand_default_path(self, path):
        current_file = self.view.file_name()
        if current_file:
            directory, current_file_name = os.path.split(current_file)
            path = path.replace("<filepath>", current_file)
            path = path.replace("<filedirectory>", directory + os.sep)
        else:
            current_file_name = ""

        path = path.replace("<filename>", current_file_name)
        return path

    def _find_open_file(self, file_name):
        window = self.window
        if IS_ST3:
            return window.find_open_file(file_name)
        else:
            for view in window.views():
                view_name = view.file_name()
                if view_name != "" and view_name == file_name:
                    return view
        return None

    ## Should be overridden by sub class
    def get_default_root_setting(self):
        return DEFAULT_ROOT_SETTING

    def _get_default_root(self):
        root_setting_value = self.get_default_root_setting()
        root_setting = self.settings.get(root_setting_value)
        if root_setting == DEFAULT_ROOT_SETTING:
            return self.settings.get(DEFAULT_ROOT_SETTING)
        return root_setting

    def __place_cursor_before_extension(self, view):
        if view.settings().get("anf_panel", False):
            cursors = view.sel()
            cursor = cursors[0]
            line_region = view.line(cursor)
            content = view.substr(line_region)
            matcher = re.match(r"(.+)\..+", content)
            if matcher:
                initial_position = len(matcher.group(1))
                cursors.clear()
                cursors.add(sublime.Region(initial_position, initial_position))

    def update_status_message(self, creation_path):
        if self.view is not None:
            self.view.set_status("AdvancedNewFile", creation_path)
        else:
            sublime.status_message(creation_path)

    def get_status_prefix(self):
        pass

    def create_status_line(self, creation_path, candidate, completion_list):
        return creation_path + '|' + candidate + str(completion_list)

    def next_candidate(self, candidate, completion_list):
        if candidate and completion_list:
            # replace the candidate with the first, and append the old candidate to the last
            completion_list.append(candidate)
            candidate = completion_list[0]
            completion_list.remove(candidate)

        return (candidate, completion_list)

    def prev_candidate(self, candidate, completion_list):
        if candidate and completion_list:
            # replace the candidate with the last, and insert the old candidate to the first
            completion_list.insert(0, candidate)
            candidate = completion_list.pop()

        return (candidate, completion_list)

    def create_next_status_line(self, creation_path, candidate, completion_list):
        if candidate and completion_list:
            candidate, completion_list = self.next_candidate(candidate, completion_list)
            return self.create_status_line(creation_path, candidate, completion_list)
        else:
            # case1: origin completion_list is empty. case2: origin completion_list contains only 1 item
            sublime.status_message("Completion list is empty.")

    def create_prev_status_line(self, creation_path, candidate, completion_list):
        if candidate and completion_list:
            candidate, completion_list = self.prev_candidate(candidate, completion_list)
            return self.create_status_line(creation_path, candidate, completion_list)
        else:
            # case1: origin completion_list is empty. case2: origin completion_list contains only 1 item
            sublime.status_message("Completion list is empty.")