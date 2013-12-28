import re
import os
from ..anf_util import *


class GenerateCompletionListBase(object):
    """docstring for GenerateCompletionListBase"""
    def __init__(self, command):
        super(GenerateCompletionListBase, self).__init__()
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
        full_path = generate_creation_path(self.settings, base, path)

        directory, filename = os.path.split(full_path)
        if os.path.isdir(directory):
            for d in os.listdir(directory):
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

        return sorted(completion_list), alias_list, dir_list, file_list

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
        if self.settings.get(IGNORE_CASE_SETTING):
            compare_entry = compare_entry.lower()
            compare_base = compare_base.lower()

        return compare_entry.startswith(compare_base)
