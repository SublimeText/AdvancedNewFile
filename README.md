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
Simply type in the path (along with the new file name), and the entire directory structure will be created if it does not exist. Note, by default, this plugin takes an arbitrary folder from the project. If you have more than one folder in the project, you will need to specify it. For more information on this, see [Selecting top level folders](https://github.com/skuroda/Sublime-AdvancedNewFile#selecting-top-level-folders) in the Features section.

## Features
### __init__.py creation:
This plugin may optionally create `__init__` in the created directories. This can be done by utilizing the correct keymap (`shift+super+alt+n (shift+ctrl+alt+n on windows)`) by default.

### Selecting top level folders:
Top level folders can be specified by typing in the name of the folder followed by a colon. Then specify the path as you would normally.

### Aliases:
You can create an alias to quickly navigate to a directory. Simply type in the alias followed by a colon, as with specifying a top level folder. Then specify the path as you would normally. Note that a top level folder with the same name as an alias will take precedence. For more information, see "Settings"

### Tab Autocompletion:
After typing in a partial path, simply hit tab to autocomplete it. Continue to hit tab to cycle through the options. Currently, this leverages the built in autocomplete functionality. Future may leverage a custom completion. As such, text in the input field will also include stings seperated by predefined word separators.

## Keymaps

`super+alt+n (ctrl+alt+n on windows)`:
Create files relative to the current project.

`shift+super+alt+n (shift+ctrl+alt+n on windows)`:
Create files relative to the current project. In addition, creates `__init__.py` in all new folders.

## Settings
`alias`: 
A dictionary that contains a set of aliases tied to a directory. For each entry, the key represents the alias name and the value represents the path. Paths should be absolute. In addition, that paths specified should match the system style paths. For example, a Windows systems should have a path similar to `C:\\Users\\username\\Desktop` *nix systems should have paths similar to `/home/username/desktop`.

`default_initial`:
A string that will be automatically inserted into the new file creation input.

`use_cursor_text`:
A boolean value determining if text from a buffer, currently bound by single or double quotes, will be auto inserted into the new file generation input field.

`show_files`:
A boolean value determining if regular files should be included in the autocompletion list.

## Notes
Thanks to Dima Kukushkin ([xobb1t](https://github.com/xobb1t)) for the original work on this plugin.

### Contributors
* [xobb1t](https://github.com/xobb1t)
* [edmundask](https://github.com/edmundask)
* [alirezadot](https://github.com/alirezadot)
* [aventurella](https://github.com/aventurella)
* [skuroda](https://github.com/skuroda)

