class GitCommandBase(object):
    # Command specific
    def file_tracked_by_git(self, filepath):
        if PLATFORM == "windows":
            git_available = (subprocess.call(['where', 'git'], shell=True) == 0)
        else:
            git_available = (subprocess.call(['which', 'git']) == 0)

        if git_available and self.settings.get("vcs_management", False):
            path, file_name = os.path.split(filepath)
            return subprocess.call(['git', 'ls-files', file_name, '--error-unmatch'], cwd=path) == 0
        else:
            return False
