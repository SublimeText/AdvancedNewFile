import sublime
import sublime_plugin


class AnfReplaceCommand(sublime_plugin.TextCommand):
    def run(self, edit, content):
        self.view.replace(edit, sublime.Region(0, self.view.size()), content)


class AdvancedNewFileCommand(sublime_plugin.WindowCommand):
    def run(self, is_python=False, initial_path=None,
            rename=False, rename_file=None):
        args = {}
        if rename:
            args["is_python"] = is_python
            args["initial_path"] = initial_path
            args["rename_file"] = rename_file
            self.window.run_command("advanced_new_file_move", args)
        else:
            args["is_python"] = is_python
            args["initial_path"] = initial_path
            self.window.run_command("advanced_new_file_new", args)
