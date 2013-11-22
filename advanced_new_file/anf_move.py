import sublime_plugin

class AdvancedNewFileMove(AdvancedNewFileBase, GitCommandBase, sublime_plugin.WindowCommand):
	def __init__(self, arg):
		super(AdvancedNewFileMove, self).__init__()
		self.arg = arg

    def run(self, is_python=False, initial_path=None, rename_file=None):
        self.is_python = is_python
        self.run_setup()
        self.rename_filename = rename_file
        if rename:
            path = self.settings.get(anf_util.RENAME_DEFAULT_SETTING)
            current_file = self.view.file_name()
            current_file_name = os.path.basename(self.view.file_name()) if current_file else ""
            path = path.replace("<current>", current_file_name)
        self.show_filename_input(path if len(path) > 0 else self.generate_initial_path())

    def input_panel_caption(self):
        if self.rename:
            caption = 'Enter a new path for current file'
            view = self.window.active_view()
            if view is not None:
                self.original_name = view.file_name() if view.file_name is not None else ""
            else:
                self.original_name = ""
        if self.is_python:
            caption = '%s (creates __init__.py in new dirs)' % caption

    def git_mv(self, from_filepath, to_filepath):
        path, filename = os.path.split(from_filepath)
        args = ["git", "mv", filename, to_filepath]
        result =  subprocess.call(args, cwd=path)
        if result != 0:
            sublime.error_message("Git move of %s to %s failed" % (from_filepath, to_filepath))

    def entered_filename_action(self, path):
        attempt_open = True
        logger.debug("Creating file at %s", file_path)
        path = os.path.dirname(file_path)
        if not os.path.exists(path):
            try:
                self.create_folder(path)
            except OSError as e:
                attempt_open = False
                sublime.error_message("Cannot create '" + file_path + "'. See console for details")
                logger.error("Exception: %s '%s'" % (e.strerror, e.filename))

        if attempt_open:
            self.rename_file(file_path)

    def rename_file(self, file_path):
        if os.path.isdir(file_path) or re.search(r"(/|\\)$", file_path):
            # use original name if a directory path has been passed in.
            file_path = os.path.join(file_path, self.original_name)

        window = self.window
        if self.rename_filename:
            tracked_by_git = self.file_tracked_by_git(self.rename_filename)
            if tracked_by_git:
                self.git_mv(self.rename_filename, file_path)
            else:
                shutil.move(self.rename_filename, file_path)
            file_view = self.find_open_file(self.rename_filename)
            if file_view is not None:
                window.focus_view(file_view)
                window.run_command("close")
                self.open_file(file_path)

        elif self.view is not None and self.view.file_name() is not None:
            filename = self.view.file_name()
            tracked_by_git = self.file_tracked_by_git(filename)
            if filename:
                self.view.run_command("save")
                window.focus_view(self.view)
                window.run_command("close")
                if tracked_by_git:
                    self.git_mv(filename, file_path)
                else:
                    shutil.move(filename, file_path)
            else:
                content = self.view.substr(sublime.Region(0, self.view.size()))
                self.view.set_scratch(True)
                self.view.run_command("close")
                window.focus_view(self.view)
                window.run_command("close")
                with open(file_path, "w") as file_obj:
                    file_obj.write(content)
            self.open_file(file_path)
        else:
            sublime.error_message("Unable to move file. No file to move.")

    def find_open_file(self, file_name):
        window = self.window
        if IS_ST3:
            return window.find_open_file(file_name)
        else:
            for view in window.views():
                view_name = view.file_name()
                if view_name != "" and view_name == file_name:
                    return view
        return None

class AdvancedNewFileRenameAtCommand(sublime_plugin.WindowCommand):
    def run(self, files):
        self.window.run_command("advanced_new_file_move", {"rename_file": files[0]})

    def is_visible(self, files):
        return len(files) == 1