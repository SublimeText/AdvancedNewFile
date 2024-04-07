import sublime
import sys

# Clear module cache to force reloading all modules of this package.

# kiss-reloader:
prefix = __package__ + "."  # don't clear the base package
for module_name in [
    module_name
    for module_name in sys.modules
    if module_name.startswith(prefix) and module_name != __name__
]:
    del sys.modules[module_name]
prefix = None

VERSION = int(sublime.version())
if VERSION > 3000:
    from .advanced_new_file.commands import *
else:
    from advanced_new_file.commands import *
