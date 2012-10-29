# AdvancedNewFile -- Advanced file creation for Sublime Text 2

## Overview

This plugin allows for faster file creation within a project. Please see the "Features" section for more detailed information about advanced features.

## Installation
Clone or copy this repository into:

* OS X: ~/Library/Application Support/Sublime Text 2/Packages/
* Windows: %APPDATA%/Roaming/Sublime Text 2/Packages/
* Linux: ~/.config/sublime-text-2/Packages/

## Usage
Simply type in the path (along with the new file name), and the entire directory structure will be created if it does not exist. Note, by default, this plugin takes an arbitrary folder from the project. If you have more than one folder in the project, you will need to specify it. For more information on this, see "Selecting top level folders" in the Features section.

## Features
### __init__.py creation:
This plugin may optionally create `__init__` in the created directories. This can be done by utilizing the correct keymap (`shift+super+alt+n (shift+ctrl+alt+n on windows)`) by default.

### Selecting top level folders:
Top level folders can be specified by typing in the name of the folder followed by a colon. 

### Tab Autocompletion:
After typing in a partial path, simply hit tab to autocomplete it. Continue to hit tab to cycle through the options.

## Keymaps

`super+alt+n (ctrl+alt+n on windows)`:
Create files relative to the current project.

`shift+super+alt+n (shift+ctrl+alt+n on windows)`:
Create files relative to the current project. In addition, creates `__init__.py` in all new folders.

## Notes
Thanks to Dima Kukushkin ([xobb1t](https://github.com/xobb1t)) for the original work on this plugin.

### Contributors
* [xobb1t](https://github.com/xobb1t)
* [edmundask](https://github.com/edmundask)
* [alirezadot](https://github.com/alirezadot)
* [aventurella](https://github.com/aventurella)
* [skuroda](https://github.com/skuroda)

