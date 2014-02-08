import os
import sublime
import sublime_plugin
import sys
from ..anf_util import *
from ..vcs.git.git_command_base import GitCommandBase
from .command_base import AdvancedNewFileBase


class AdvancedNewFileDelete(AdvancedNewFileBase, sublime_plugin.WindowCommand,
                            GitCommandBase):
    def __init__(self, window):
        super(AdvancedNewFileDelete, self).__init__(window)

    def run(self, current=False):
        self.run_setup()
        if current:
            self._delete_current_file()
        else:
            self.settings[SHOW_FILES_SETTING] = True
            self.show_filename_input("")

    def input_panel_caption(self):
        return 'Enter path of file to delete'

    def entered_file_action(self, path):
        self._delete_file(path)

    def update_status_message(self, creation_path):
        if self.view is not None:
            self.view.set_status("AdvancedNewFile", "Delete file at %s " %
                                 creation_path)
        else:
            sublime.status_message("Delete file at %s" % creation_path)

    def _git_rm(self, filepath):
        path, filename = os.path.split(filepath)
        result = self.run_command(["rm", filename], path)
        if result != 0:
            sublime.error_message("Git remove of %s failed." % (filepath))

    def _delete_current_file(self):
        filepath = self.window.active_view().file_name()
        self._delete_file(filepath)

    def _delete_file(self, filepath):
        if not filepath:
            return
        elif not os.path.isfile(filepath):
            sublime.error_message("%s is not a file" % filepath)
            return

        if not sublime.ok_cancel_dialog("Delete this file?\n%s" % filepath):
            return

        vcs_tracking = (self.file_tracked_by_git(filepath) and
                        self.settings.get(VCS_MANAGEMENT_SETTING))

        self.close_view(filepath)

        if vcs_tracking:
            self._git_rm(filepath)
        else:
            self._execute_delete_file(filepath)

        self.refresh_sidebar()

    def _execute_delete_file(self, filepath):
        if IS_ST3 and self._side_bar_enhancements_installed():
            import Default.send2trash as send2trash
            send2trash.send2trash(filepath)
        else:
            self.window.run_command("delete_file", {"files": [filepath]})

    def _side_bar_enhancements_installed(self):
        return "SideBarEnhancements.SideBar" in sys.modules

    def close_view(self, filepath):
        file_view = self._find_open_file(filepath)

        if file_view is not None:
            file_view.set_scratch(True)
            self.window.focus_view(file_view)
            self.window.run_command("close")
