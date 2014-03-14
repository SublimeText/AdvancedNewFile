# Adapted from @wbond's resource loader.

import sys
import sublime

VERSION = int(sublime.version())

mod_prefix = "advanced_new_file"
reload_mods = []

if VERSION > 3000:
    mod_prefix = "AdvancedNewFile." + mod_prefix
    from imp import reload
    for mod in sys.modules:
        if mod[0:15] == 'AdvancedNewFile' and sys.modules[mod] is not None:
            reload_mods.append(mod)
else:

    for mod in sorted(sys.modules):
        if mod[0:17] == 'advanced_new_file' and sys.modules[mod] is not None:
            reload_mods.append(mod)

mods_load_order = [
    '',
    '.anf_util',
    '.completion_base',

    ".lib",
    ".lib.package_resources",

    ".completions",
    '.completions.nix_completion',
    '.completions.windows_completion',

    ".platform",
    ".platform.windows_platform",
    ".platform.nix_platform",

    ".vcs",
    ".vcs.git",
    ".vcs.git.git_command_base",

    ".commands",
    ".commands.command_base",
    ".commands.helper_commands",
    '.commands.new_file_command',
    ".commands.move_file_command",
    ".commands.delete_file_command"
]

for suffix in mods_load_order:
    mod = mod_prefix + suffix
    if mod in reload_mods:
        reload(sys.modules[mod])
