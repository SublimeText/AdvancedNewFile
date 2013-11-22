from .completion_base import GenerateCompletionListBase

WIN_ROOT_REGEX = r"[a-zA-Z]:(/|\\)"

class WindowsPlatform(object):
    """docstring for WindowsPlatform"""
    def __init__(self, view):
        super(WindowsPlatform, self).__init__()
        self.view = view

    def split(self, path):
        if re.match(WIN_ROOT_REGEX, path):
            return path[0:3], path[3:]
        else:
            return None, path

    def parse_nix_path(self, root, path):
        path_offset = 1
        match = re.match(r"^/([a-zA-Z])/", path)
        if match:
            root = "%s:\\" % match.group(1)
            path_offset = 3
        else:
            root, _ = os.path.splitdrive(self.view.file_name())
            root += "\\"

        return root, path_offset

class WindowsCompletion(GenerateCompletionListBase):
    def __init__(self, settings, view):
        super(WindowsCompletion, self).__init__(settings)
        self.view = view

    def completion(self, path_in):
        pattern = r"(.*[/\\:])(.*)"
        match = re.match(pattern, path_in)
        if "prev_text" in dir(self) and self.prev_text == path_in:
            self.offset = (self.offset + 1) % len(self.completion_list)
        else:
            # Generate new completion list
            self.completion_list, alias_list, dir_list, file_list = self.__generate_completion_list(path_in)
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
                    if completion in alias_list:
                        completion += ":"
                    elif completion in dir_list:
                        completion += "/"
            new_content = re.sub(pattern, r"\1" , path_in)
            new_content += completion
            first_token = False
        else:
            completion = self.completion_list[self.offset]
            if self.settings.get("complete_single_entry"):
                if len(self.completion_list) == 1:
                    if completion in alias_list:
                        completion += ":"
                    elif completion in dir_list:
                        completion += "/"
            new_content = completion
            first_token = True

        if len(self.completion_list) > 1:
            if first_token:
                if self.view is not None:
                    if self.completion_list[self.offset] in alias_list:
                        self.view.set_status("AdvancedNewFile2", "Alias Completion")
                    elif self.completion_list[self.offset] in dir_list:
                        self.view.set_status("AdvancedNewFile2", "Directory Completion")
            self.prev_text = new_content
        else:
            self.prev_text = None

        return new_content
