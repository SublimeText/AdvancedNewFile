import sublime
import sys

VERSION = int(sublime.version())

reloader = "advanced_new_file.reloader"

if VERSION > 3000:
    reloader = 'AdvancedNewFile.' + reloader
    from imp import reload


# Make sure all dependencies are reloaded on upgrade
if reloader in sys.modules:
    reload(sys.modules[reloader])

if VERSION > 3000:
    from .advanced_new_file import reloader
    from .advanced_new_file.commands import *
else:
    from advanced_new_file import reloader
    from advanced_new_file.commands import *
