import sublime_plugin

class AdvancedNewFileDelete(AdvancedNewFileBase, GitCommandBase, sublime_plugin.WindowCommand):
    """docstring for AdvancedNewFileDelete"""
    def __init__(self, arg):
        super(AdvancedNewFileDelete, self).__init__()
        self.arg = arg

    def git_rm(self, filepath):
        path, filename = os.path.split(filepath)
        result = subprocess.call(['git', 'rm', filename], cwd=path)
        if result != 0:
            sublime.error_message("Git remove of %s failed." % (filepath))

    def delete_current_file(self):
        filepath = self.window.active_view().file_name()
        if not filepath or not os.path.isfile(filepath):
            return

        if not sublime.ok_cancel_dialog("Delete this file?\n%s" % os.path.basename(filepath)):
            return

        if self.file_tracked_by_git(filepath):
            self.git_rm(filepath)
        else:
            self.window.run_command("delete_file", {"files": [filepath]})

        self.refresh_sidebar()