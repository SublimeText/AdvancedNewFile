import re
import os

from ..anf_util import *
from .pinyin_lib import *

from .fuzzy_sort import sort_by_fuzzy


class GenerateCompletionListBase(object):
    """docstring for GenerateCompletionListBase"""
    def __init__(self, command):
        super().__init__()
        self.top_level_split_char = ":"
        self.command = command
        self.aliases = command.aliases
        self.settings = command.settings

    def is_home(self, path):
        return re.match(r"^~[/\\]", path)

    def is_alias(self, path):
        return self.top_level_split_char in path

    def generate_completion_list(self, path_in):
        alias_list = []
        dir_list = []
        file_list = []
        if self.is_alias(path_in) or self.is_home(path_in):
            pass
        else:
            directory, filename = os.path.split(path_in)
            if len(directory) == 0:
                alias_list += self.generate_alias_auto_complete(filename)
                alias_list += self.generate_project_auto_complete(filename)
        base, path = self.command.split_path(path_in)
        # print("base,path", path_in, base, path)
        full_path = generate_creation_path(self.settings, base, path)

        directory, filename = os.path.split(full_path)
        if os.path.isdir(directory):
            for d in os.listdir(directory):
                if not self.filter_file(d):
                    continue
                full_path = os.path.join(directory, d)
                if os.path.isdir(full_path):
                    is_file = False
                elif self.settings.get(SHOW_FILES_SETTING):
                    is_file = True
                else:
                    continue

                if self.compare_entries(d, filename):
                    if is_file:
                        file_list.append(d)
                    else:
                        dir_list.append(d)

        completion_list = alias_list + dir_list + file_list

        return sort_by_fuzzy(filename, completion_list, 20), alias_list, dir_list, file_list

    def filter_file(self, fname):
        """
        Returns False if a file should be ignored: If the file matched any of the regular expressions
        on the settings file
        """
        fname = os.path.basename(fname)
        for regex in self.settings.get('filter_regex', list()):
            regex = regex.replace('\\\\', '\\')  # Fix backslash escaping on json
            p = re.compile(regex)
            if p.match(fname) is not None:
                return False
        return True

    def generate_project_auto_complete(self, base):
        folder_data = get_project_folder_data(
            self.settings.get(USE_FOLDER_NAME_SETTING))
        if len(folder_data) > 1:
            folders = [x[0] for x in folder_data]
            return self.generate_auto_complete(base, folders)
        return []

    def generate_alias_auto_complete(self, base):
        return self.generate_auto_complete(base, self.aliases)

    def generate_auto_complete(self, base, iterable_var):
        sugg = []
        for entry in iterable_var:
            compare_entry = entry
            compare_base = base
            if self.settings.get(IGNORE_CASE_SETTING):
                compare_entry = compare_entry.lower()
                compare_base = compare_base.lower()

            if self.compare_entries(compare_entry, compare_base):
                if entry not in sugg:
                    sugg.append(entry)
        return sugg

    def compare_entries(self, compare_entry, compare_base):
        # if self.settings.get(IGNORE_CASE_SETTING):
        #     compare_entry = compare_entry.lower()
        #     compare_base = compare_base.lower()

        # return compare_entry.startswith(compare_base)
        # turn to fuzzy match
        pattern = get_str_pattern(compare_base, self.settings.get(IGNORE_CASE_SETTING, True))
        return re.match(pattern, compare_entry) is not None

    def complete_for_folder(self, path_in):
        (completion_list, alias_list,
            dir_list, file_list) = self.generate_completion_list(path_in)
        new_completion_list = []
        if len(completion_list) > 0:
            for path in completion_list:
                if path in dir_list:
                    path += "/"
                elif path in alias_list:
                    path += ":"
                new_completion_list.append(path)
        return new_completion_list


    def complete_for_project(self, path_in):
        directory = self.command.get_project_folder()

        completion_list = []
        if os.path.isdir(directory):
            files = self.command.get_input_view_project_files()
            if not files:
                files = self.get_files_recursively(directory, self.filter_file)
                self.command.set_input_view_project_files(files)
            else:
                print("use the old files", str(len(files)))
            for file in files:
                if self.compare_entries(os.path.basename(file), path_in):
                    completion_list.append(file)

        return sort_by_fuzzy(path_in, completion_list, 20)

    def get_files_recursively(self, dir, filter_func=None):
        if not os.path.isdir(dir):
            return list(dir)
        dirlist = os.walk(dir)
        result = []
        for root, _, files in dirlist:
            rel_path = os.path.relpath(root, dir)
            for file in files:
                rel_file = os.path.join(rel_path, file)
                if filter_func:
                    if filter_func(rel_file):
                        result.append(rel_file)
                else:
                    result.append(rel_file)
        return result