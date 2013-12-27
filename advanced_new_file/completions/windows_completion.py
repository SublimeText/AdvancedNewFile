import re
from .completion_base import GenerateCompletionListBase
from ..anf_util import *


class WindowsCompletion(GenerateCompletionListBase):
    def __init__(self, command):
        super(WindowsCompletion, self).__init__(command)
        self.view = command.view

    def completion(self, path_in):
        pattern = r"(.*[/\\:])(.*)"
        match = re.match(pattern, path_in)
        if "prev_text" in dir(self) and self.prev_text == path_in:
            self.offset = (self.offset + 1) % len(self.completion_list)
        else:
            # Generate new completion list
            (self.completion_list, self.alias_list, self.dir_list,
                self.file_list) = self.generate_completion_list(path_in)
            self.offset = 0

            if len(self.completion_list) == 0:
                if match:
                    self.completion_list = [match.group(2)]
                else:
                    self.completion_list = [path_in]
        match = re.match(pattern, path_in)
        if match:
            completion = self.completion_list[self.offset]
            if self.settings.get(COMPLETE_SINGLE_ENTRY_SETTING):
                if len(self.completion_list) == 1:
                    if completion in self.alias_list:
                        completion += ":"
                    elif completion in self.dir_list:
                        completion += "/"
            new_content = re.sub(pattern, r"\1", path_in)
            new_content += completion
            first_token = False
        else:
            completion = self.completion_list[self.offset]
            if self.settings.get(COMPLETE_SINGLE_ENTRY_SETTING):
                if len(self.completion_list) == 1:
                    if completion in self.alias_list:
                        completion += ":"
                    elif completion in self.dir_list:
                        completion += "/"
            new_content = completion
            first_token = True

        if len(self.completion_list) > 1:
            if first_token:
                if self.view is not None:
                    if completion in self.alias_list:
                        self.view.set_status(
                            "AdvancedNewFile2", "Alias Completion")
                    elif completion in self.dir_list:
                        self.view.set_status(
                            "AdvancedNewFile2", "Directory Completion")
            self.prev_text = new_content
        else:
            self.prev_text = None

        return new_content
