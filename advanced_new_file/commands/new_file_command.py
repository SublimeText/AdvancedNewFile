import sublime_plugin
import os
from .command_base import AdvancedNewFileBase
from ..anf_util import *

class AdvancedNewFileNew(AdvancedNewFileBase, sublime_plugin.WindowCommand):
    def __init__(self, window):
        super(AdvancedNewFileNew, self).__init__(window)

    def run(self, is_python=False, initial_path=None):
        self.is_python = is_python
        self.run_setup()
        self.show_filename_input(self.generate_initial_path(initial_path))

    def input_panel_caption(self):
        caption = 'Enter a path for a new file'
        if self.is_python:
            caption = '%s (creates __init__.py in new dirs)' % caption
        return caption

    def entered_file_action(self, path):
        attempt_open = True
        if not os.path.exists(path):
            try:
                self.create(path)
            except OSError as e:
                attempt_open = False
                sublime.error_message("Cannot create '" + path + "'. See console for details")
                print("Exception: %s '%s'" % (e.strerror, e.filename))
        if attempt_open:
            self.open_file(path)

    def update_status_message(self, creation_path):
        if self.view != None:
            self.view.set_status("AdvancedNewFile", "Creating file at %s " % \
                creation_path)
        else:
            sublime.status_message("Creating file at %s" % creation_path)

class AdvancedNewFileNewAtCommand(sublime_plugin.WindowCommand):
    def run(self, dirs):
        if len(dirs) != 1:
            return
        path = dirs[0] + os.sep
        self.window.run_command("advanced_new_file_new", {"initial_path": path})

    def is_visible(self, dirs):
        return len(dirs) == 1
