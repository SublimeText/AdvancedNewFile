# Changelog for AdvancedNewFile
- 2 September 2013
    - Add setting to begin all relative paths from current working directory if available.

- 14 August 2013
    - Prompt completion type for first token when using Windows completion.
    - Fix bug with path autocompletion.
    - Fix bug for tab completion with no view.

- 27 July 2013
    - Rewrite autocomplete functionality.
    - Bug Fixes
        - Snippets no longer appear when entering completions.

- 22 April 2013
    - Add option to refresh sidebar after creating a file.
    - Add side bar context menu.
    - Bug Fixes
        - Multiple autocomplete issues.
        - Creation of __init__.py files.
        - Filling text with cursor values.

- 2 February 2013
    - Update to be compatible with Sublime Text 3.

- 14 January 2013
    - Add `alias_root` setting, used with aliases with relative paths.
    - Add setting to allow user to specify which folder from the project should be used.
    - Bug fixes
        - Do not require relative alias paths to begin with `./`
        - Prevent duplicate entries from appearing in auto complete list.

- 17 December 2012
    - Allow selected text to fill entry window.
    - Basic work for continued autocompletion (Only applies if there is a single completion option)
    - Bug fixes
        - Properly display completions when using "ctrl+space" to manually display auto complete options.
        - Prevent error pop up from occuring when explicitly creating a directory structure.
        - Fix bug where using cursor text causes an error.
        - Prevent spaces from being inserted when tab is without a possible completion.

- 26 November 2012
    - Add setting to display path for file to be created in status bar.
    - Add setting to set default base path (home, current, top_folder, path).
    - Add setting to ignore case for auto completion.
    - Add support for relative paths in alias.
    - Add OS Specific Aliases to settings.
    - Display an error when attempting to use an invalid alias.
    - Display an error when attempting to open a directory in a view.
    - Display an error if path creation fails.
    - Bug Fixes
        - Auto complete bug for files with spaces in their name
        - Status bar update causing errors when no view is present.
        - Specifying absolute paths for Windows produced unexpected behavior.

- 30 October 2012
    - Initial work for tab autocompletion
    - Files created when path entered
    - Add setting to fill with a default value.
    - Setting to prefill entry box with text in quotes.
    - Add setting to display non directory files
    - Add user defined aliases.
    - Bug fixes.
        - Prevent buffer from being opened when a directory is specified.

- 20 April 2012
    - Add ability to specify top level folders
    - Bug fixes
        - Fix Windows keybindings
        - Fix save issue on Windows

- 29 October 2011
    - Initial release of AdvancedNewFile plugin
