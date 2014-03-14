"""
MIT License
Copyright (c) 2014 Scott Kuroda <scott.kuroda@gmail.com>

SHA: 623a4c1ec46dbbf3268bd88131bf0dfc845af787
"""
import sublime
import os
import zipfile
import tempfile
import re
import codecs

__all__ = [
    "get_resource",
    "get_binary_resource",
    "find_resource",
    "list_package_files",
    "get_package_and_resource_name",
    "get_packages_list",
    "extract_package",
    "get_sublime_packages"
]


VERSION = int(sublime.version())

def get_resource(package_name, resource, encoding="utf-8"):
    return _get_resource(package_name, resource, encoding=encoding)

def get_binary_resource(package_name, resource):
    return _get_resource(package_name, resource, return_binary=True)

def _get_resource(package_name, resource, return_binary=False, encoding="utf-8"):
    packages_path = sublime.packages_path()
    content = None
    if VERSION > 3013:
        try:
            if return_binary:
                content = sublime.load_binary_resource("Packages/" + package_name + "/" + resource)
            else:
                content = sublime.load_resource("Packages/" + package_name + "/" + resource)
        except IOError:
            pass
    else:
        path = None
        if os.path.exists(os.path.join(packages_path, package_name, resource)):
            path = os.path.join(packages_path, package_name, resource)
            content = _get_directory_item_content(path, return_binary, encoding)

        if VERSION >= 3006:
            sublime_package = package_name + ".sublime-package"

            packages_path = sublime.installed_packages_path()
            if content is None:
                if os.path.exists(os.path.join(packages_path, sublime_package)):
                    content = _get_zip_item_content(os.path.join(packages_path, sublime_package), resource, return_binary, encoding)

            packages_path = os.path.dirname(sublime.executable_path()) + os.sep + "Packages"

            if content is None:
                if os.path.exists(os.path.join(packages_path, sublime_package)):
                    content = _get_zip_item_content(os.path.join(packages_path, sublime_package), resource, return_binary, encoding)

    return content


def find_resource(resource_pattern, package=None):
    file_set = set()
    if package == None:
        for package in get_packages_list():
            file_set.update(find_resource(resource_pattern, package))

        ret_list = list(file_set)
    else:
        file_set.update(_find_directory_resource(os.path.join(sublime.packages_path(), package), resource_pattern))

        if VERSION >= 3006:
            zip_location = os.path.join(sublime.installed_packages_path(), package + ".sublime-package")
            file_set.update(_find_zip_resource(zip_location, resource_pattern))
            zip_location = os.path.join(os.path.dirname(sublime.executable_path()), "Packages", package + ".sublime-package")
            file_set.update(_find_zip_resource(zip_location, resource_pattern))
        ret_list = map(lambda e: package + "/" + e, file_set)

    return sorted(ret_list)


def list_package_files(package, ignore_patterns=[]):
    """
    List files in the specified package.
    """
    package_path = os.path.join(sublime.packages_path(), package, "")
    path = None
    file_set = set()
    file_list = []
    if os.path.exists(package_path):
        for root, directories, filenames in os.walk(package_path):
            temp = root.replace(package_path, "")
            for filename in filenames:
                file_list.append(os.path.join(temp, filename))

    file_set.update(file_list)

    if VERSION >= 3006:
        sublime_package = package + ".sublime-package"
        packages_path = sublime.installed_packages_path()

        if os.path.exists(os.path.join(packages_path, sublime_package)):
            file_set.update(_list_files_in_zip(packages_path, sublime_package))

        packages_path = os.path.dirname(sublime.executable_path()) + os.sep + "Packages"

        if os.path.exists(os.path.join(packages_path, sublime_package)):
           file_set.update(_list_files_in_zip(packages_path, sublime_package))

    file_list = []

    for filename in file_set:
        if not _ignore_file(filename, ignore_patterns):
            file_list.append(_normalize_to_sublime_path(filename))

    return sorted(file_list)

def _ignore_file(filename, ignore_patterns=[]):
    ignore = False
    directory, base = os.path.split(filename)
    for pattern in ignore_patterns:
        if re.match(pattern, base):
            return True

    if len(directory) > 0:
        ignore = _ignore_file(directory, ignore_patterns)

    return ignore


def _normalize_to_sublime_path(path):
    path = os.path.normpath(path)
    path = re.sub(r"^([a-zA-Z]):", "/\\1", path)
    path = re.sub(r"\\", "/", path)
    return path

def get_package_and_resource_name(path):
    """
    This method will return the package name and resource name from a path.

    Arguments:
    path    Path to parse for package and resource name.
    """
    package = None
    resource = None
    path = _normalize_to_sublime_path(path)
    if os.path.isabs(path):
        packages_path = _normalize_to_sublime_path(sublime.packages_path())
        if path.startswith(packages_path):
            package, resource = _search_for_package_and_resource(path, packages_path)

        if int(sublime.version()) >= 3006:
            packages_path = _normalize_to_sublime_path(sublime.installed_packages_path())
            if path.startswith(packages_path):
                package, resource = _search_for_package_and_resource(path, packages_path)

            packages_path = _normalize_to_sublime_path(os.path.dirname(sublime.executable_path()) + os.sep + "Packages")
            if path.startswith(packages_path):
                package, resource = _search_for_package_and_resource(path, packages_path)
    else:
        path = re.sub(r"^Packages/", "", path)
        split = re.split(r"/", path, 1)
        package = split[0]
        package = package.replace(".sublime-package", "")
        resource = split[1]

    return (package, resource)

def get_packages_list(ignore_packages=True, ignore_patterns=[]):
    """
    Return a list of packages.
    """
    package_set = set()
    package_set.update(_get_packages_from_directory(sublime.packages_path()))

    if int(sublime.version()) >= 3006:
        package_set.update(_get_packages_from_directory(sublime.installed_packages_path(), ".sublime-package"))

        executable_package_path = os.path.dirname(sublime.executable_path()) + os.sep + "Packages"
        package_set.update(_get_packages_from_directory(executable_package_path, ".sublime-package"))


    if ignore_packages:
        ignored_list = sublime.load_settings(
            "Preferences.sublime-settings").get("ignored_packages", [])
    else:
        ignored_list = []

    for package in package_set:
        for pattern in ignore_patterns:
            if re.match(pattern, package):
                ignored_list.append(package)
                break

    for ignored in ignored_list:
        package_set.discard(ignored)

    return sorted(list(package_set))

def get_sublime_packages(ignore_packages=True, ignore_patterns=[]):
    package_list = get_packages_list(ignore_packages, ignore_patterns)
    extracted_list = _get_packages_from_directory(sublime.packages_path())
    return [x for x in package_list if x not in extracted_list]

def _get_packages_from_directory(directory, file_ext=""):
    package_list = []
    for package in os.listdir(directory):
        if not package.endswith(file_ext):
            continue
        else:
            package = package.replace(file_ext, "")

        package_list.append(package)
    return package_list

def _search_for_package_and_resource(path, packages_path):
    """
    Derive the package and resource from  a path.
    """
    relative_package_path = path.replace(packages_path + "/", "")

    package, resource = re.split(r"/", relative_package_path, 1)
    package = package.replace(".sublime-package", "")
    return (package, resource)


def _list_files_in_zip(package_path, package):
    if not os.path.exists(os.path.join(package_path, package)):
        return []

    ret_value = []
    with zipfile.ZipFile(os.path.join(package_path, package)) as zip_file:
        ret_value = zip_file.namelist()
    return ret_value

def _get_zip_item_content(path_to_zip, resource, return_binary, encoding):
    if not os.path.exists(path_to_zip):
        return None

    ret_value = None

    with zipfile.ZipFile(path_to_zip) as zip_file:
        namelist = zip_file.namelist()
        if resource in namelist:
            ret_value = zip_file.read(resource)
            if not return_binary:
                ret_value = ret_value.decode(encoding)

    return ret_value

def _get_directory_item_content(filename, return_binary, encoding):
    content = None
    if os.path.exists(filename):
        if return_binary:
            mode = "rb"
            encoding = None
        else:
            mode = "r"
        with codecs.open(filename, mode, encoding=encoding) as file_obj:
            content = file_obj.read()
    return content

def _find_zip_resource(path_to_zip, pattern):
    ret_list = []
    if os.path.exists(path_to_zip):
        with zipfile.ZipFile(path_to_zip) as zip_file:
            namelist = zip_file.namelist()
            for name in namelist:
                if re.search(pattern, name):
                    ret_list.append(name)

    return ret_list

def _find_directory_resource(path, pattern):
    ret_list = []
    if os.path.exists(path):
        path = os.path.join(path, "")
        for root, directories, filenames in os.walk(path):
            temp = root.replace(path, "")
            for filename in filenames:
                if re.search(pattern, os.path.join(temp, filename)):
                    ret_list.append(os.path.join(temp, filename))
    return ret_list

def extract_zip_resource(path_to_zip, resource, extract_dir=None):
    if extract_dir is None:
        extract_dir = tempfile.mkdtemp()

    file_location = None
    if os.path.exists(path_to_zip):
        with zipfile.ZipFile(path_to_zip) as zip_file:
            file_location = zip_file.extract(resource, extract_dir)

    return file_location

def extract_package(package):
    if VERSION >= 3006:
        package_location = os.path.join(sublime.installed_packages_path(), package + ".sublime-package")
        if not os.path.exists(package_location):
            package_location = os.path.join(os.path.dirname(sublime.executable_path()), "Packages", package + ".sublime-package")
            if not os.path.exists(package_location):
                package_location = None
        if package_location:
            with zipfile.ZipFile(package_location) as zip_file:
                extract_location = os.path.join(sublime.packages_path(), package)
                zip_file.extractall(extract_location)

