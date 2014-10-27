import sublime
import sublime_plugin
import os

from .command_base import AdvancedNewFileBase
from ..anf_util import *


class AdvancedNewFileCutToFile(AdvancedNewFileBase, sublime_plugin.WindowCommand):
    def __init__(self, window):
        super(AdvancedNewFileCutToFile, self).__init__(window)

    def run(self, is_python=False):
        self.is_python = is_python
        self.run_setup()
        self.view.add_regions(REGION_KEY, self.view.sel(), flags=sublime.HIDDEN)

        path = self.settings.get(CUT_TO_FILE_DEFAULT_SETTING, "")
        path = self._expand_default_path(path)

        self.show_filename_input(
            path if len(path) > 0 else self.generate_initial_path())

    def input_panel_caption(self):
        caption = 'Move selection to'
        if self.is_python:
            caption = '%s (creates __init__.py in new dirs)' % caption
        return caption

    def update_status_message(self, creation_path):
        status_base = "Cutting selection to"
        if self.view is not None:
            self.view.set_status("AdvancedNewFile", "%s %s " %
                                 (status_base, creation_path))
        else:
            sublime.status_message("%s %s" % (status_base, creation_path))

    def entered_file_action(self, path):
        file_exist = os.path.exists(path)
        attempt_open = True
        if not file_exist:
            attempt_open = self._create_new_file(path)
        if attempt_open:
            self._open_and_add_content_to_file(path)
        self.view.run_command("anf_remove_region_content_and_region", { "region_key": REGION_KEY})
        self.open_file(path)


    def _create_new_file(self, path):
        attempt_open = True

        try:
            self.create(path)
        except OSError as e:
            attempt_open = False
            sublime.error_message("Cannot create '" + path +
                                  "'. See console for details")
        return attempt_open

    def _open_and_add_content_to_file(self, path):
        if os.path.isfile(path):
            content = ""
            for region in self.view.get_regions(REGION_KEY):
                content += self.view.substr(region)
                content += "\n"

            with open(path, "a") as file_obj:
                file_obj.write(content)

    def is_enabled(self):
        view = self.window.active_view()
        cursors = view.sel()
        for cursor in cursors:
            if not cursor.empty():
                return True

        return False

