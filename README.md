# AdvancedNewFile
Advanced file creation for Sublime Text 2

## Overview

This plugin allows for faster file creation within a project. Please see the [Features](https://github.com/skuroda/Sublime-AdvancedNewFile#features) section for more detailed information about advanced features.

## Installation
Note with either method, you may need to restart Sublime Text 2 for the plugin to load.

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
Simply bring up the AdvancedNewFile input through the appropriate [key binding](https://github.com/skuroda/Sublime-AdvancedNewFile). Then, enter the path, along with the file name into the input field. Upon pressing enter, the file will be created. In addition, if the directories specified do not yet exists, they will also be created. For more advanced usage of this plugin, be sure to look at [Advanced Path Usage](https://github.com/skuroda/Sublime-AdvancedNewFile#advanced-path-usage). By default, the path to the file being created will be filled shown in the status bar as you enter the path information.

**Default directory:**
The default directory is specified by the `default_root` setting. By default, it will be the top directory of the folders listed in the window. If this cannot be resolved, the home directory will be used. See [Settings](https://github.com/skuroda/Sublime-AdvancedNewFile#settings) (`default_root`) for more information.

## Keymaps
If you have issues with keymaps, consider running [FindKeyConflicts](https://github.com/skuroda/FindKeyConflicts), also available through the package manager.

### Windows
There is a known conflict with the popular plugin [ZenCoding](https://github.com/sublimator/ZenCoding).

`ctrl+alt+n`: General keymap to create new files.

`ctrl+shift+alt+n`: In addition to creating the folders specified, new folders will also contain an `__init__.py` file.

### OS X and Linux
The super keys for Linux and OS X are the Windows and command key respectively.

`super+alt+n`: General keymap to create new files.

`shift+super+alt+n`: In addition to creating the folders specified, new folders will also contain an `__init__.py` file.

## Settings
`alias`:

A dictionary that contains a set of aliases tied to a directory. For more information, see [Aliases](https://github.com/skuroda/Sublime-AdvancedNewFile#aliases)

`os_specific_alias`:

A dictionary containing a set of aliases tied to a directory. These aliases will be platform specific. For more information, see [Platform Specific Aliases](https://github.com/skuroda/Sublime-AdvancedNewFile#platform-specific-aliases)

`default_initial`:

A string that will be automatically inserted into the new file creation input.

`use_cursor_text`:

A boolean value determining if text from a buffer, bound by quotes or a selected region, will be auto inserted into the new file generation input field. If multiple cursors are used, the first entry either contained in quotes, are a selected region, will be used.

`show_files`:

A boolean value determining if regular files should be included in the autocompletion list.

`show_path`:

A boolean value used to determine if the path of the file to be created should be displayed in the status bar.

`default_root`:

This value is used to determine the default root when using AdvancedNewFile. It must be one of the following values:

* `top_folder`- The default path will be the top level folder in the window. Note this is the Default value on a clean install.
* `current_view` - The default path will be the directory of the current active view.
* `home` - The default path will be your home directory.
* `path` - The default path will be defined by the setting `default_path`

If the current view's directory cannot be resolved, the top level folder in the window will be used. If the top level folder in the window cannot be resolved either, the home directory will be used.

`default_path`:

This path is used as the default if `path` has been specified for the setting `default_root`.

`ignore_case`:

A boolean specifying if case should be ignored when building auto complete list.

### Project Specific Settings
All of the above settings can also be specified as part of the project specific settings. These values override any previous values set by higher level settings, with aliases being an exception. Alias settings will be merged with higher level configurations for alias. In addition, if the same alias exist for both default/user settings and project settings, the project setting will take precedence.

    "settings":
    {
        "AdvancedNewFile":
        {
            "default_initial": "/project/specific/path"
        }
    }


## Features
#### __init__.py creation:
This plugin may optionally create `__init__` in the created directories. Please reference [Key Maps](https://github.com/skuroda/Sublime-AdvancedNewFile#keymaps) to see the default key bindings to do this.

#### Tab Autocompletion:
After typing in a partial path, simply press tab to autocomplete it. Continue to press tab to cycle through the options.

### Advanced Path Usage
#### Home directory:
To begin at the home directory simply start with `~/` like you would in the shell.

#### Aliases:
You can create an alias to quickly navigate to a directory. Simply type in the alias followed by a colon. Then specify the path as you would normally. Note, in an event a specified alias conflicts with a [predefined alias](https://github.com/skuroda/Sublime-AdvancedNewFile#predefined-aliases), the predefined alias will take precedence.

Alias paths may be relative or absolute. If relative, the current view will be used as the base location. If the current view does not exist on disk, the home directory will be used as the base. When specifying absolute paths, be sure to use the system specific style (e.g. Windows `C:\\Users\\username\\Desktop`, OS X and Linix `/home/username/desktop/`). In addition, you may specify an alias from the home directory by using `~/`.

If an invalid alias is specified, an error pop up will be displayed when trying to create the file.

Sample aliases:

    {
        "alias": {
            "Desktop": "~/Desktop/"
        }
    }

To use the above alias, when specifying a new file enter `Desktop:testDir/testFile`, which would then create a file at `<home_directory>/Desktop/testDir/testFile`.

##### Platform Specific Aliases
You can also create aliases that are platform specific. These follow a similar set of rules as aliases. However, rather than specifying a string path to use, a dictionary is specified. This dictionary may contain the following keys: `windows`, `linux`, and `osx`. The path for this particular alias will be used based on the operating system in use. If the same alias is specified in both `alias` and `os_specific_alias`, the path in `os_specific_alias` will be used.

Sample OS Specific Aliases:

    {
        "os_specific_alias": {
            "subl_packages" {
                "windows": "~\\AppData\\Roaming\\Sublime Text 2\\Packages",
                "linux": "~/.config/sublime-text-2/Packages",
                "osx": "~/Library/Application Support/Sublime Text 2/Packages"
            }
        }
    }

##### Predefined Aliases
###### Top level folders in window
Top level folders can be specified by typing in the name of the folder followed by a colon. Then specify the path as you would normally.

###### Current Working Directory
To specify the current working directory, simply type a colon, without any preceding text.

## Notes
Thanks to Dima Kukushkin ([xobb1t](https://github.com/xobb1t)) for the original work on this plugin. Also, thank you to [facelessuser](https://github.com/facelessuser), and by extension biermeester and matthjes for the idea of platform specific settings.

### Contributors
* [xobb1t](https://github.com/xobb1t)
* [edmundask](https://github.com/edmundask)
* [alirezadot](https://github.com/alirezadot)
* [aventurella](https://github.com/aventurella)
* [skuroda](https://github.com/skuroda)

