import os
import re
import sublime

from .completion_base import GenerateCompletionListBase
from ..anf_util import *


class NixCompletion(GenerateCompletionListBase):
    def __init__(self, command):
        super(NixCompletion, self).__init__(command)

    def completion(self, path_in):
        pattern = r"(.*[/\\:])(.*)"

        (completion_list, alias_list,
            dir_list, file_list) = self.generate_completion_list(path_in)
        new_content = path_in
        if len(completion_list) > 0:
            common = os.path.commonprefix(completion_list)
            match = re.match(pattern, path_in)
            if match:
                new_content = re.sub(pattern, r"\1", path_in)
                new_content += common
            else:
                new_content = common
            if len(completion_list) > 1:
                dir_list = map(lambda s: s + "/", dir_list)
                alias_list = map(lambda s: s + ":", alias_list)
                status_message_list = sorted(list(dir_list) +
                                             list(alias_list) + file_list)
                sublime.status_message(", ".join(status_message_list))
            else:
                if completion_list[0] in alias_list:
                    new_content += ":"
                elif completion_list[0] in dir_list:
                    new_content += "/"

        return new_content
