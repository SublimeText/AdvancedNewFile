import sublime
import subprocess
import os
from ...anf_util import *


# The Code to find git path is copied verbatim from kemayo's Git plugin.
# https://github.com/kemayo/sublime-text-git
def _test_paths_for_executable(paths, test_file):
    for directory in paths:
        file_path = os.path.join(directory, test_file)
        if os.path.exists(file_path) and os.access(file_path, os.X_OK):
            return file_path


def find_git():
    # It turns out to be difficult to reliably run git, with varying paths
    # and subprocess environments across different platforms. So. Let's hack
    # this a bit.
    # (Yes, I could fall back on a hardline "set your system path properly"
    # attitude. But that involves a lot more arguing with people.)
    path = os.environ.get('PATH', '').split(os.pathsep)
    if os.name == 'nt':
        git_cmd = 'git.exe'
    else:
        git_cmd = 'git'

    git_path = _test_paths_for_executable(path, git_cmd)

    if not git_path:
        # /usr/local/bin:/usr/local/git/bin
        if os.name == 'nt':
            extra_paths = (
                os.path.join(os.environ["ProgramFiles"], "Git", "bin"),
            )
            if IS_X64:
                extra_paths = extra_paths + (
                    os.path.join(
                        os.environ["ProgramFiles(x86)"], "Git", "bin"),
                )
        else:
            extra_paths = (
                '/usr/local/bin',
                '/usr/local/git/bin',
            )
        git_path = _test_paths_for_executable(extra_paths, git_cmd)
    return git_path

GIT = find_git()


# Base for git commands
class GitCommandBase(object):
    def __init__(self, window):
        pass

    # Command specific
    def file_tracked_by_git(self, filepath):
        git = GIT
        if git is not None:
            path, file_name = os.path.split(filepath)
            return self.run_command(
                ["ls-files", file_name, "--error-unmatch"], path) == 0
        else:
            return False

    def run_command(self, args, cwd):
        use_shell = PLATFORM == "windows"
        return subprocess.call([GIT] + args, cwd=cwd, shell=use_shell)
