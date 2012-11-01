# AdvancedNewFile
Advanced file creation for Sublime Text 2

## Overview

This plugin allows for faster file creation within a project. Please see the [Features](https://github.com/skuroda/Sublime-AdvancedNewFile#features) section for more detailed information about advanced features.

## Installation
Clone or copy this repository into the packages directory. By default, they are located at:

* OS X: ~/Library/Application Support/Sublime Text 2/Packages/
* Windows: %APPDATA%/Roaming/Sublime Text 2/Packages/
* Linux: ~/.config/sublime-text-2/Packages/

## Usage
Simply type in the path (along with the new file name), and the entire directory structure will be created if it does not exist. If the newly specified path ends as a directory (e.g. with `/`), then each text entry will be used to generate a directory. For more advanced usage of this plugin, be sure to look at [Advanced Path Usage](https://github.com/skuroda/Sublime-AdvancedNewFile#advanced-path-usage) and [Features](https://github.com/skuroda/Sublime-AdvancedNewFile#features)

**Default directory:**
If the plugin is launched without folders, the default directory will be your home directory. If, however, the plugin is launched in a window that contains open folders, the top most folder in the view will be taken as the default directory.

## Advanced Path Usage
### Home directory:
To begin at the home directory simply start with `~/` like you would in the shell.

### Selecting top level folders:
Top level folders can be specified by typing in the name of the folder followed by a colon. Then specify the path as you would normally.

### Aliases:
You can create an alias to quickly navigate to a directory. Simply type in the alias followed by a colon, as with specifying a top level folder. Then specify the path as you would normally. Note that a top level folder with the same name as an alias will take precedence. For more information, see [Settings](https://github.com/skuroda/Sublime-AdvancedNewFile#settings)

In addition to specifying an alias, you can also simply specify a colon, without any preceding text. This create the directory structure, beginning at the same location as the file currently in the view, if it exists. If the current view does not have a file name, it will default to the first folder in the window.

If an invalid alias and top level directory is specified, the plugin will default to using your home directory as root.

## Features
### __init__.py creation:
This plugin may optionally create `__init__` in the created directories. This can be done by utilizing the correct keymap (`shift+super+alt+n (shift+ctrl+alt+n on windows)`) by default.

### Tab Autocompletion:
After typing in a partial path, simply hit tab to autocomplete it. Continue to hit tab to cycle through the options. Currently, this leverages the built in autocomplete functionality. As such, text in the input field will also include stings seperated by predefined word separators.

## Keymaps

`super+alt+n (ctrl+alt+n on windows)`:

General keymap to create new files.

`shift+super+alt+n (shift+ctrl+alt+n on windows)`:

In addition to creating the folders specified, new folders will also contain an `__init__.py` file.

## Settings
`alias`: 

A dictionary that contains a set of aliases tied to a directory. For each entry, the key represents the alias name and the value represents the path. Paths should be absolute. In addition, that paths specified should match the system style paths. For example, a Windows systems should have a path similar to `C:\\Users\\username\\Desktop` *nix systems should have paths similar to `/home/username/desktop`.

`default_initial`:

A string that will be automatically inserted into the new file creation input.

`use_cursor_text`:

A boolean value determining if text from a buffer, currently bound by single or double quotes, will be auto inserted into the new file generation input field.

`show_files`:

A boolean value determining if regular files should be included in the autocompletion list.

### Project Specific Settings
All of the above settings can also be specified as part of the project specific settings. These values override any previous values set by higher level settings, with aliases being an exception. Alias settings will be merged with higher level configurations for alias. In addition, if the same alias exist for both default/user settings and project settings, the project setting will take precedence.

    "settings":
    {
        "AdvancedNewFile":
        {
            "default_initial": "/project/specific/path"
        }
    }
## Notes
Thanks to Dima Kukushkin ([xobb1t](https://github.com/xobb1t)) for the original work on this plugin.

### Contributors
* [xobb1t](https://github.com/xobb1t)
* [edmundask](https://github.com/edmundask)
* [alirezadot](https://github.com/alirezadot)
* [aventurella](https://github.com/aventurella)
* [skuroda](https://github.com/skuroda)

