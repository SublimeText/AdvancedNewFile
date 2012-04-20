import os
import sublime, sublime_plugin


class AdvancedNewFileCommand(sublime_plugin.TextCommand):

    def run(self, edit, is_python=False):
        self.count = 0
        self.window = self.view.window()
        self.root = self.get_root()
        self.is_python = is_python
        self.show_filename_input()
        self.top_level_split_char = ":"

    def get_root(self, target=None):
        try:
            root = self.window.folders()[0]
            
            if target:
                for folder in self.window.folders():
                    basename = os.path.basename(folder)
                    if basename == target:
                        root = folder
        except IndexError:
            root = os.path.abspath(os.path.dirname(self.view.file_name()))
        return root

    def show_filename_input(self, initial=''):
        caption = 'Enter a path for a new file'
        if self.is_python:
            caption = '%s (creates __init__.py in new dirs)' % caption
        self.window.show_input_panel(
            caption, initial,
            self.entered_filename, self.update_filename_input, None
        )
    
    def update_filename_input(self, path):
        # TODO: Autocomplete feature
        pass

    def entered_filename(self, filename):
        base = self.root
        
        if self.top_level_split_char in filename:
            parts = filename.split(self.top_level_split_char)
            base = self.get_root(parts[0])
            filename = self.top_level_split_char.join(parts[1:])

        file_path = os.path.join(base, filename)

        if not os.path.exists(file_path):
            self.create(file_path)
        self.window.run_command('open_file', {"file": file_path})
        
    def create(self, filename):
        base, filename = os.path.split(filename)
        self.create_folder(base)

    def create_folder(self, base):
        if not os.path.exists(base):
            parent = os.path.split(base)[0]
            if not os.path.exists(parent):
                self.create_folder(parent)
            os.mkdir(base)
        if self.is_python:
            open(os.path.join(base, '__init__.py'), 'w').close()
