import sublime_plugin
import AdvancedNewFile.advanced_new_file.anf_util
from .anf_base import AdvancedNewFileBase
from .nix_platform import NixPlatform, NixCompletion

class AdvancedNewFileNew(AdvancedNewFileBase, sublime_plugin.WindowCommand):
    def __init__(self, window):
        super(AdvancedNewFileNew, self).__init__(window)

    def run(self, is_python=False, initial_path=None):
        print(dir(self))
        self.is_python = is_python
        self.run_setup()
        self.show_filename_input(self.generate_initial_path())

    def input_panel_caption(self):
        caption = 'Enter a path for a new file'
        if self.is_python:
            caption = '%s (creates __init__.py in new dirs)' % caption
        return caption

    def entered_file_action(self, path):
        attempt_open = True
        logger.debug("Creating file at %s", file_path)
        if not os.path.exists(file_path):
            try:
                self.create(file_path)
            except OSError as e:
                attempt_open = False
                sublime.error_message("Cannot create '" + file_path + "'. See console for details")
                logger.error("Exception: %s '%s'" % (e.strerror, e.filename))
        if attempt_open:
            self.open_file(file_path)

class AdvancedNewFileAtCommand(sublime_plugin.WindowCommand):
    def run(self, dirs):
        if len(dirs) != 1:
            return
        path = dirs[0]
        self.window.run_command("advanced_new_file_new", {"initial_path": path + os.sep})

    def is_visible(self, dirs):
        settings = sublime.load_settings("AdvancedNewFile.sublime-settings")
        return settings.get("show_sidebar_menu", False) and len(dirs) == 1