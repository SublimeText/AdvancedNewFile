import sublime
import re
import os

ALIAS_SETTING = "alias"
DEFAULT_INITIAL_SETTING = "default_initial"
USE_CURSOR_TEXT_SETTING = "use_cursor_text"
SHOW_FILES_SETTING = "show_files"
SHOW_PATH_SETTING = "show_path"
DEFAULT_ROOT_SETTING = "default_root"
DEFAULT_PATH_SETTING = "default_path"
DEFAULT_FOLDER_INDEX_SETTING = "default_folder_index"
OS_SPECIFIC_ALIAS_SETTING = "os_specific_alias"
IGNORE_CASE_SETTING = "ignore_case"
ALIAS_ROOT_SETTING = "alias_root"
ALIAS_PATH_SETTING = "alias_path"
ALIAS_FOLDER_INDEX_SETTING = "alias_folder_index"
DEBUG_SETTING = "debug"
AUTO_REFRESH_SIDEBAR_SETTING = "auto_refresh_sidebar"
COMPLETION_TYPE_SETTING = "completion_type"
COMPLETE_SINGLE_ENTRY_SETTING = "complete_single_entry"
USE_FOLDER_NAME_SETTING = "use_folder_name"
RELATIVE_FROM_CURRENT_SETTING = "relative_from_current"
DEFAULT_EXTENSION_SETTING = "default_extension"
FILE_PERMISSIONS_SETTING = "file_permissions"
FOLDER_PERMISSIONS_SETTING = "folder_permissions"
RENAME_DEFAULT_SETTING = "rename_default"
VCS_MANAGEMENT_SETTING = "vcs_management"
FILE_TEMPLATES_SETTING = "file_templates"
SHELL_INPUT_SETTING = "shell_input"
APPEND_EXTENSION_ON_MOVE_SETTING = "append_extension_on_move"
RELATIVE_FALLBACK_INDEX_SETTING = "relative_fallback_index"

SETTINGS = [
    ALIAS_SETTING,
    DEFAULT_INITIAL_SETTING,
    USE_CURSOR_TEXT_SETTING,
    SHOW_FILES_SETTING,
    SHOW_PATH_SETTING,
    DEFAULT_ROOT_SETTING,
    DEFAULT_PATH_SETTING,
    DEFAULT_FOLDER_INDEX_SETTING,
    OS_SPECIFIC_ALIAS_SETTING,
    IGNORE_CASE_SETTING,
    ALIAS_ROOT_SETTING,
    ALIAS_PATH_SETTING,
    ALIAS_FOLDER_INDEX_SETTING,
    DEBUG_SETTING,
    AUTO_REFRESH_SIDEBAR_SETTING,
    COMPLETION_TYPE_SETTING,
    COMPLETE_SINGLE_ENTRY_SETTING,
    USE_FOLDER_NAME_SETTING,
    RELATIVE_FROM_CURRENT_SETTING,
    DEFAULT_EXTENSION_SETTING,
    FILE_PERMISSIONS_SETTING,
    FOLDER_PERMISSIONS_SETTING,
    RENAME_DEFAULT_SETTING,
    VCS_MANAGEMENT_SETTING,
    FILE_TEMPLATES_SETTING,
    SHELL_INPUT_SETTING,
    APPEND_EXTENSION_ON_MOVE_SETTING,
    RELATIVE_FALLBACK_INDEX_SETTING
]

NIX_ROOT_REGEX = r"^/"
WIN_ROOT_REGEX = r"[a-zA-Z]:(/|\\)"
HOME_REGEX = r"^~"
PLATFORM = sublime.platform()
TOP_LEVEL_SPLIT_CHAR = ":"
IS_ST3 = int(sublime.version()) > 3000
IS_X64 = sublime.arch() == "x64"


def generate_creation_path(settings, base, path, append_extension=False):
        if PLATFORM == "windows":
            if not re.match(WIN_ROOT_REGEX, base):
                return base + TOP_LEVEL_SPLIT_CHAR + path
        else:
            if not re.match(NIX_ROOT_REGEX, base):
                return base + TOP_LEVEL_SPLIT_CHAR + path

        tokens = re.split(r"[/\\]", base) + re.split(r"[/\\]", path)
        if tokens[0] == "":
            tokens[0] = "/"
        if PLATFORM == "windows":
            tokens[0] = base[0:3]

        full_path = os.path.abspath(os.path.join(*tokens))
        if re.search(r"[/\\]$", path) or len(path) == 0:
            full_path += os.path.sep
        elif re.search(r"\.", tokens[-1]):
            if re.search(r"\.$", tokens[-1]):
                full_path += "."
        elif append_extension:
            filename = os.path.basename(full_path)
            if not os.path.exists(full_path):
                full_path += settings.get(DEFAULT_EXTENSION_SETTING)
        return full_path


def get_settings(view):
    settings = sublime.load_settings("AdvancedNewFile.sublime-settings")
    project_settings = {}
    local_settings = {}
    if view is not None:
        project_settings = view.settings().get('AdvancedNewFile', {})

    for setting in SETTINGS:
        local_settings[setting] = settings.get(setting)

    if type(project_settings) != dict:
        print("Invalid type %s for project settings" % type(project_settings))
        return local_settings

    for key in project_settings:
        if key in SETTINGS:
            if key == "alias":
                if IS_ST3:
                    local_settings[key] = dict(
                        local_settings[key].items() |
                        project_settings.get(key).items()
                    )
                else:
                    local_settings[key] = dict(
                        local_settings[key].items() +
                        project_settings.get(key).items()
                    )
            else:
                local_settings[key] = project_settings[key]
        else:
            print("AdvancedNewFile[Warning]: Invalid key " +
                  "'%s' in project settings.", key)

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
