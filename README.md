# AdvancedNewFile
Advanced file creation for Sublime Text 2

## Overview

This plugin allows for faster file creation within a project. Please see the [Features](https://github.com/skuroda/Sublime-AdvancedNewFile#features) section for more detailed information about advanced features.

## Installation
### Package Control
Installation through [package control](http://wbond.net/sublime_packages/package_control) is recommended. It will handle updating your packages as they become available. To install, do the following.

* In the Command Palette, enter `Package Control: Install Package`
* Search for `AdvancedNewFile`

### Manual
Clone or copy this repository into the packages directory. By default, they are located at:

* OS X: ~/Library/Application Support/Sublime Text 2/Packages/
* Windows: %APPDATA%/Roaming/Sublime Text 2/Packages/
* Linux: ~/.config/sublime-text-2/Packages/

## Usage
Simply type in the path (along with the new file name), and the entire directory structure will be created if it does not exist. If the newly specified path ends as a directory (e.g. with `/`), then each text entry will be used to generate a directory. For more advanced usage of this plugin, be sure to look at [Advanced Path Usage](https://github.com/skuroda/Sublime-AdvancedNewFile#advanced-path-usage) and [Features](https://github.com/skuroda/Sublime-AdvancedNewFile#features)

**Default directory:**
If the plugin is launched without folders, the default directory will be your home directory. If, however, the plugin is launched in a window that contains open folders, the top most folder in the view will be taken as the default directory.

## Keymaps
If you have issues with keymaps, consider running [FindKeyConflicts](https://github.com/skuroda/FindKeyConflicts), also available through the package manager.

### Windows
There is a known coflict with the popular plugin [ZenCoding](https://github.com/sublimator/ZenCoding). 

`ctrl+alt+n`: General keymap to create new files.

`ctrl+shift+alt+n`: In addition to creating the folders specified, new folders will also contain an `__init__.py` file.

### OS X and Linux
The super keys for Linux and OS X are the Windows and command key respectively.

`super+alt+n`: General keymap to create new files. 

`shift+super+alt+n`: In addition to creating the folders specified, new folders will also contain an `__init__.py` file.

## Advanced Path Usage
### Home directory:
To begin at the home directory simply start with `~/` like you would in the shell.

### Selecting top level folders:
Top level folders can be specified by typing in the name of the folder followed by a colon. Then specify the path as you would normally.

### Aliases:
You can create an alias to quickly navigate to a directory. Simply type in the alias followed by a colon, as with specifying a top level folder. Then specify the path as you would normally. Note that a top level folder with the same name as an alias will take precedence. For more information, see [Settings](https://github.com/skuroda/Sublime-AdvancedNewFile#settings)

Alias paths may be relative or absolute. If relative, the current view will be used as the base location. If the current view does not exist on disk, the home directory will be used as the base. When specifying absolute paths, be sure to use the system specific style (e.g. Windows `C:\\Users\\username\\Desktop`, *nix `/home/username/desktop/`). In addition, you may specify an alias from the home directory by using `~/`.

In addition to specifying an alias, you can also simply specify a colon, without any preceding text. Using this will use the current working directory as the path base, if a view exists and is saved on disk. If the current view does not exist on disk, it will default to the first folder in the window or to the home directory if no folders exist in the window.

If an invalid alias and top level directory is specified, the plugin will default to using your home directory as root.

Sample aliases:

    {
        "alias": {
            "Desktop": "~/Desktop/"
        }
    }

To use the above alias, when specifying a new file enter `Desktop:testDir/testFile`, which would then create a file at `<home_directory>/testDir/testFile`.
    
## Features
### __init__.py creation:
This plugin may optionally create `__init__` in the created directories. Please reference [Key Maps](https://github.com/skuroda/Sublime-AdvancedNewFile#keymaps) to see the default key bindings to do this.

### Tab Autocompletion:
After typing in a partial path, simply hit tab to autocomplete it. Continue to hit tab to cycle through the options. Currently, this leverages the built in autocomplete functionality. As such, text in the input field will also include stings seperated by predefined word separators.

## Settings
`alias`: 

A dictionary that contains a set of aliases tied to a directory. For more information, see [Aliases](https://github.com/skuroda/Sublime-AdvancedNewFile#aliases)

`default_initial`:

A string that will be automatically inserted into the new file creation input.

`use_cursor_text`:

A boolean value determining if text from a buffer, currently bound by single or double quotes, will be auto inserted into the new file generation input field.

`show_files`:

A boolean value determining if regular files should be included in the autocompletion list.

`show_path`:

A boolean value used to determine if the path of the file to be created should be displayed in the status bar.
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

