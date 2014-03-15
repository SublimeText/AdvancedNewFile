# AdvancedNewFile
Advanced file creation for Sublime Text 2 and Sublime Text 3.

## Overview

This plugin allows for faster file creation within a project. Please see the [Features](https://github.com/skuroda/Sublime-AdvancedNewFile#features) section for more detailed information about advanced features.

## Installation
Note with either method, you may need to restart Sublime Text 2 for the plugin to load.

### Package Control
Installation through [package control](http://wbond.net/sublime_packages/package_control) is recommended. It will handle updating your packages as they become available. To install, do the following.

* In the Command Palette, enter `Package Control: Install Package`
* Search for `AdvancedNewFile`

### Manual
Clone or copy this repository into the packages directory. You will need to rename the folder to `AdvancedNewFile` if using this method. By default, the Package directory is located at:

* OS X: ~/Library/Application Support/Sublime Text 2/Packages/
* Windows: %APPDATA%/Roaming/Sublime Text 2/Packages/
* Linux: ~/.config/sublime-text-2/Packages/

or

* OS X: ~/Library/Application Support/Sublime Text 3/Packages/
* Windows: %APPDATA%/Roaming/Sublime Text 3/Packages/
* Linux: ~/.config/sublime-text-3/Packages/

## Usage
Simply bring up the AdvancedNewFile input through the appropriate [key binding](https://github.com/skuroda/Sublime-AdvancedNewFile). Then, enter the path, along with the file name into the input field. Upon pressing enter, the file will be created. In addition, if the directories specified do not yet exists, they will also be created. For more advanced usage of this plugin, be sure to look at [Advanced Path Usage](https://github.com/skuroda/Sublime-AdvancedNewFile#advanced-path-usage). By default, the path to the file being created will be filled shown in the status bar as you enter the path information.

**Default directory:**
The default directory is specified by the `default_root` setting. By default, it will be the top directory of the folders listed in the window. If this cannot be resolved, the home directory will be used. See [Settings](https://github.com/skuroda/Sublime-AdvancedNewFile#settings) (`default_root`) for more information.

### Commands with no Default Bindings
The plugin supports renaming and deleting files. However, these are not, by default bound to any key binding. For more information on the available commands, see the GitHub [wiki](https://github.com/skuroda/Sublime-AdvancedNewFile/wiki/Commands) page.

### Adding Commands to Menu
The plugin does not contain any menu commands by default. To add them yourself, please see the GitHub[wiki](https://github.com/skuroda/Sublime-AdvancedNewFile/wiki/Menu-Entries)

## Keymaps
If you have issues with keymaps, consider running [FindKeyConflicts](https://github.com/skuroda/FindKeyConflicts), also available through the package manager. Alternatively, set command logging to true by entering `sublime.log_commands(True)` in the Sublime Text console.

### Windows
`ctrl+alt+n`: General keymap to create new files.

`ctrl+shift+alt+n`: In addition to creating the folders specified, new folders will also contain an `__init__.py` file.

### OS X and Linux
The super keys for Linux and OS X are the Windows and command key respectively.

`super+alt+n`: General keymap to create new files.

`shift+super+alt+n`: In addition to creating the folders specified, new folders will also contain an `__init__.py` file.

## Settings
Default settings can be seen by navigating to `Preferences -> Packages Settings -> AdvancedNewFile - Default`. To modify the default settings, navigate to `Preferences -> Packages Settings -> AdvancedNewFile -> User`.

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

* `project_folder`- The default path will be the folder specified by the 'default_folder_index' setting.
* `current` - The default path will be the directory of the current active view.
* `home` - The default path will be your home directory.
* `path` - The default path will be defined by the setting `default_path`

If the current view's directory cannot be resolved, the top level folder in the window will be used. If the top level folder in the window cannot be resolved either, the home directory will be used.

`default_path`:

This path is used as the default if `path` has been specified for the setting `default_root`. This path should be absolute. If a relative path is specified, it will be relative to the AdvancedNewFile package directory.

`default_folder_index`:

An integer value representing a folder index to be used when "folder" is specified for "default_root". If an index outside of the range of existing folders is used, it will default to 0 (the top level folder).

`alias_root`:

This entry defines the root that will be used when resolving aliases defined as relative paths. For more information about valid entries, see `default_root`. Note that for path, `alias_path` will be specified.

`alias_path`:

This path is used as the default if `path` has been specified for the setting `alias_root`.

`alias_folder_index`:

An integer value representing the folder index to use when "folder" is specified for "alias_root". If an index outside of the range of the existing folders is used, it will default to 0.

`ignore_case`:

A boolean specifying if case should be ignored when building auto complete list.

`auto_refresh_sidebar`:

A boolean specifying if folders should automatically refresh and update the sidebar. In some builds, the sidebar does not refresh when contents of project folder are updated. This setting is required to refresh the sidebar in these circumstances. False by default.

`completion_type`:

A string specifying the type of auto completion to use. Valid values are "windows" or "nix".

`complete_single_entry`

A boolean setting specifying if a separator should be inserted when there is only one completion and completion type is "windows"

`use_folder_name`:

A boolean setting specifying if the folder name should be used or the name specified in the project. This setting only applies to ST3.

`relative_from_current`:

Boolean setting specifying if relative paths should be based on the current working directory.

`default_extension`:

String containing the default file extension. Note the extension is only applied if the specified path does not contain a dot (.) character.

`folder_permissions`:

String representing permissions to be applied to newly created folders. E.g. "777" -> RWX for user, group, and other.

`file_permissions`:

String representing permissions to be applied to newly created files. E.g. "777" -> RWX for user, group, and other.

`rename_default`:

Default input for renaming a file. Special value `<filename>` will be replaced with the current file name. Special value `<filepath>` will be replaced with the absolute path of the current file.

`vcs_management`:

Setting to control if VCS management is used when moving and removing files.

`file_templates`:

An object containing information to use for templates when creating new files. The key values for this object should be a file extension. The value may either be a string of the content to be inserted or a list of paths. If a list of paths is specified, the name of the file will be displayed during selection. The paths must either be absolute, from the home directory of the user (`~/`), or relative to the Packages directory. These relative files should have the form "Packages/User/mytest.sublime-snippet". If a string is used, or the list contains a single entry, it will be automatically inserted into any newly created files.

`posix_input`:

Setting this value to true will allow you to escape characters as you normally would when using a shell. For example, given the input string "foo\ bar", false would result in a file named " bar" in the foo directory. With the value set to true, a file named "foo bar" would be created. In addition, setting this value to true will allow for curly brace expansion. Currently, only comma separated entries are supported.

`append_extension_on_move`:

Setting to control if the extension will be automatically applied to renamed files.

`relative_fallback_index`:

An integer value representing a folder index to be used when a relative path cannot be resolved from the current active view. If an index outside of the range  of existing folders is used, it will default to 0 (the top level folder). If no  folders exist as part of the project the home directory will be used.

### Project Specific Settings
All of the above settings can also be specified as part of the project specific settings. These values override any previous values set by higher level settings, with aliases being an exception. Alias settings will be merged with higher level configurations for alias. In addition, if the same alias exist for both default/user settings and project settings, the project setting will take precedence.

    "settings": {
        "AdvancedNewFile": {
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
You can create an alias to quickly navigate to a directory. Simply type in the alias followed by a colon. Then specify the path as you would normally. Note, in an event a specified alias conflicts with a [predefined alias](https://github.com/skuroda/Sublime-AdvancedNewFile#predefined-aliases), the specified alias will take precedence.

Alias paths may be relative or absolute. If a relative path is specified, the `alias_root` setting will be used as the base. When specifying absolute paths, be sure to use the system specific style (e.g. Windows `C:\\Users\\username\\Desktop`, OS X and Linix `/home/username/desktop/`). In addition, you may specify an alias from the home directory by using `~/`.

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
            "subl_packages": {
                "windows": "~\\AppData\\Roaming\\Sublime Text 2\\Packages",
                "linux": "~/.config/sublime-text-2/Packages",
                "osx": "~/Library/Application Support/Sublime Text 2/Packages"
            }
        }
    }

##### Predefined Aliases
###### Top level folders in window
Top level folders can be specified by typing in the name of the folder followed by a colon. Then specify the path as you would normally.

**Note**

In Sublime Text 2, the name of the folder will be the actual name of the folder, not an arbitrary name specified in the project. However, due to an API update, folder names in Sublime Text 3 will match the Side Bar names. To achieve a similar behavior in Sublime Text 2, you can create `Project Specific Settings` for `alias`.

###### Current Working Directory
To specify the current working directory, simply type a colon, without any preceding text. Alternatively, set `relative_from_current` to `true` in your settings. Paths specified as relative paths will then begin from the current working directory.

## Notes
Thanks to Dima Kukushkin ([xobb1t](https://github.com/xobb1t)) for the original work on this plugin. Also, thank you to [facelessuser](https://github.com/facelessuser), and by extension biermeester and matthjes for the idea of platform specific settings. Additional thanks to [kemayo](https://github.com/kemayo) for the work in identifying git executable.

### Contributors
* [alirezadot](https://github.com/alirezadot)
* [aventurella](https://github.com/aventurella)
* [btsai](https://github.com/btsai)
* [edmundask](https://github.com/edmundask)
* [skuroda](https://github.com/skuroda)
* [xobb1t](https://github.com/xobb1t)

