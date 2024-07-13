from datetime import datetime
import os
import shutil

from file_interpreter import load_items, print_items, comment_out, convert_string
from constants import MODS_FOLDER, INI_FOLDER_PART, INI_COMMENTS, LOG_PATH

# TODO later: reference checker
# TODO: file comparator
# TODO: automated proposition of #include creation or child adopting


def find_text(find, in_file_or_folder, mode=0):
    """ finds a given string in a given file or folder of files.

    In mode 2 returns the first line where the string was found. It returns an empty string if not found"""
    output = ''
    if not find:
        return 'file_editor.find_text() aborted - empty string to find'
    if MODS_FOLDER.replace('/', '\\') not in in_file_or_folder.replace('/', '\\'):
        return 'file_editor.replace_text() aborted - item not in MODS_FOLDER'
    if mode == 0:
        output += f' command: find "{convert_string(find, direction="display")}"\n\tin {in_file_or_folder}.\nresult:'
    find = convert_string(find, direction='process')
    if os.path.isdir(in_file_or_folder):
        file_paths = os.listdir(in_file_or_folder)
        for file_path in file_paths:
            output += find_text(find, f'{in_file_or_folder}/{file_path}', mode=1)
    elif os.path.isfile(in_file_or_folder):
        try:
            # with open(in_file_or_folder, 'r') as file:
            #     file_content = file.read()
            file_content = print_items(load_items(in_file_or_folder))[0]
            if file_content.count(find) > 0:
                if mode < 2:
                    output += f'\tin {in_file_or_folder} found {file_content.count(find)}:\n'
                    file_content_split = file_content.split(find)
                    index_line = 1
                    for content_part in file_content_split[:-1]:
                        index_line += content_part.count('\n')
                        output += f'\t\tin line {index_line}\n'
                else:
                    output = file_content[file_content.rfind('#include', 0, file_content.find(find)):
                                          file_content.find('\n', file_content.find(find))]
                    # output = in_file_or_folder
            elif mode == 0:
                output += f'\tfound {file_content.count(find)}\n'
        except UnicodeDecodeError:
            output += f'file_editor.find_text() error: file {in_file_or_folder} unreadable'
        except ValueError:
            output += f'file_editor.find_text() error: ValueError'
    return output


def replace_text(find, replace_with, in_file_or_folder, mode=0):
    """ replaces a given string by another in a given file or folder of files """
    output = ''
    if not find:
        return 'file_editor.find_text() aborted - empty string to find'
    if MODS_FOLDER.replace('/', '\\') not in in_file_or_folder.replace('/', '\\'):
        return 'file_editor.replace_text() aborted - item not in MODS_FOLDER'
    if mode == 0:
        output += f'{datetime.now()}'
        output += (f' command: replace "{convert_string(find, direction="display")}"'
                   f'\n\twith "{replace_with}"\n\tin {in_file_or_folder}.\nresult:')
    find = convert_string(find, direction='process')
    if os.path.isfile(in_file_or_folder):
        try:
            # with open(in_file_or_folder, 'r') as file:
            #     file_content = file.read()
            file_content = print_items(load_items(in_file_or_folder))[0]
            if file_content.count(find) > 0:
                output += f'\t{file_content.count(find)} replaced in {in_file_or_folder}\n'
                new_file_content = file_content.replace(find, replace_with)
                with open(in_file_or_folder, 'w') as file:
                    file.write(new_file_content)
        except UnicodeDecodeError:
            print(f'file_editor.replace_text() error: file {in_file_or_folder} unreadable')
    elif os.path.isdir(in_file_or_folder):
        file_paths = os.listdir(in_file_or_folder)
        for file_path in file_paths:
            output += replace_text(find, replace_with, f'{in_file_or_folder}/{file_path}', mode=0)
        # if mode == 0:
    try:
        with open(f'{LOG_PATH}/file_changes.txt', 'a') as log_file:
            log_file.write(output + '\n')
    except FileNotFoundError:
        with open(f'{LOG_PATH}/file_changes.txt', 'w') as log_file:
            log_file.write(output + '\n')
    return output


def update_reference(new_path, in_file_or_folder, mode=0):
    """
    internal function triggered when a .inc file is moved.
     needs to be a separate function to call itself without triggering the rest of the move function
    :param new_path:
    :param in_file_or_folder:
    :param mode:
    :return: logs of updated #include paths
    """
    output = ''
    line_include = ''
    old_path = ''
    if os.path.isdir(in_file_or_folder):
        folders_paths = os.listdir(in_file_or_folder)
        for folder_path in folders_paths:
            output += update_reference(new_path=new_path, in_file_or_folder=f'{in_file_or_folder}/{folder_path}')
    elif os.path.isfile(in_file_or_folder):
        line_include += find_text(new_path.split('/')[-1], in_file_or_folder, mode=2)
        if line_include:
            old_path = in_file_or_folder
    if old_path:
        output += f'in file {in_file_or_folder}:\n'
        with open(in_file_or_folder) as file_checked:
            lines = file_checked.readlines()
        new_content = ''
        line_counter = 0
        for line in lines:
            line_counter += 1
            if "#include" in line.strip() and line.strip()[0] not in INI_COMMENTS:
                path_old_include, path_new_include = '', ''
                if line_include in line:
                    path_old_include = line_include.strip()[len('#include "'):line_include.strip().rfind('"')]
                    path_absolute_include = new_path
                    path_new_include = os.path.relpath(path_absolute_include, '/'.join(old_path.split('/')[:-1]))
                elif line_include not in line:
                    path_old_include = line.strip()[len('#include "'):line.strip().rfind('"')]
                    path_absolute_include = os.path.normpath(os.path.join(os.path.dirname(old_path), path_old_include))
                    path_new_include = os.path.relpath(path_absolute_include, '/'.join(old_path.split('/')[:-1]))
                if path_old_include != path_new_include:
                    new_content += line.replace(path_old_include, path_new_include)
                    output += (f'\tin line {line_counter} updated #include "{path_old_include}"'
                               f'\n\t\tto "{path_new_include}"\n')
                else:
                    new_content += line
                    output += f'\tin line {line_counter} #include "{path_old_include}" left unchanged.\n'
            else:
                new_content += line
        if ''.join(lines) != new_content and mode == 0:
            with open(new_path, 'w') as file_overwritten:
                file_overwritten.write(new_content)
    return output


def update_single_reference(old_path, new_path, mode=0):
    """
    internal function triggered when a .ini file is moved
    :param old_path:
    :param new_path:
    :param mode:
    :return:
    """
    file_to_open = ''
    if mode == 1:
        file_to_open = old_path
    output = f'in file {file_to_open or new_path}:\n'
    with open(file_to_open or new_path) as file_checked:
        lines = file_checked.readlines()
    new_content = ''
    line_counter = 0
    for line in lines:
        line_counter += 1
        if "#include" in line.strip() and line.strip()[0] not in INI_COMMENTS:
            path_old_include = line.strip()[len('#include "'):line.strip().rfind('"')]
            path_absolute_include = os.path.normpath(os.path.join(os.path.dirname(old_path), path_old_include))
            path_new_include = os.path.relpath(path_absolute_include, '/'.join(new_path.split('/')[:-1]))
            if path_old_include != path_new_include:
                new_content += line.replace(path_old_include, path_new_include)
                output += (f'\tin line {line_counter} updated #include "{path_old_include}"'
                           f'\n\t\tto "{path_new_include}"\n')
            else:
                new_content += line
                output += f'\tin line {line_counter} #include "{path_old_include}" left unchanged.\n'
        else:
            new_content += line
    if ''.join(lines) != new_content and mode == 0:
        with open(new_path, 'w') as file_overwritten:
            file_overwritten.write(new_content)
    return output


def move_file(full_path, to_folder, mode=0):
    """moves a given file to a given folder and updates the references to or in this file."""
    output = ''
    file_name = full_path.replace('\\', '/').split('/')[-1]
    if MODS_FOLDER not in to_folder:
        return 'file_editor.move_file aborted - destination path not in MODS_FOLDER'
    try:
        if mode == 0:
            output += f'{datetime.now()}'
            output += f' command: move {full_path}\n\tto {to_folder}\n'
            shutil.move(full_path, f'{to_folder}/{file_name}')
        if file_name.endswith('.inc'):
            ini_folder = to_folder[:to_folder.find(INI_FOLDER_PART) + len(INI_FOLDER_PART)]
            output += update_reference(new_path=f'{to_folder}/{file_name}', in_file_or_folder=ini_folder)
        elif file_name.endswith('.ini'):
            output += update_single_reference(old_path=full_path, new_path=f'{to_folder}/{file_name}', mode=mode)
    except shutil.Error:
        output += 'file_editor.move_file error: erroneous path'
    try:
        with open(f'{LOG_PATH}/file_changes.txt', 'a') as log_file:
            log_file.write(output + '\n')
    except FileNotFoundError:
        with open(f'{LOG_PATH}/file_changes.txt', 'w') as log_file:
            log_file.write(output + '\n')
    return output


# TODO: comment a part of the displayed text
# TODO: look for duplicates in other files too. Objects can be overwritten.
def duplicates_commenter(in_file):
    """
    finds the duplicates in a given file
    :param in_file: string path of the file to load
    :return: logs of the values commented out
    """
    new_content = ''
    output = f'{datetime.now()}'
    output += f' command: comment out duplicates in {in_file}:\n'
    items = load_items(in_file)
    items_number = len(items)
    remaining_items_index = 1
    for item_index in range(1, items_number):
        to_comment = False
        remaining_items_index += 1
        for remaining_item_index in range(remaining_items_index, items_number):
            if items[item_index].name.capitalize() == items[remaining_item_index].name.capitalize():
                if items[item_index].level_class == items[remaining_item_index].level_class:
                    to_comment = True
        if to_comment:
            new_content += comment_out(print_items([items[0], items[item_index]])[0])
            output += print_items([items[0], items[item_index]])
        else:
            new_content += print_items([items[0], items[item_index]])
    try:
        with open(f'{LOG_PATH}/file_changes.txt', 'a') as log_file:
            log_file.write(output + '\n')
    except FileNotFoundError:
        with open(f'{LOG_PATH}/file_changes.txt', 'w') as log_file:
            log_file.write(output + '\n')
    with open(in_file, 'w') as new_file:
        new_file.write(new_content)
    return output


# from tkinter.filedialog import askopenfilename, askdirectory
# print(move_file(askopenfilename(), askdirectory(), mode=1))


def load_file(full_path):
    """

    :param full_path: absolute path of the file to load into the text editor
    :return: the file content
    """
    if full_path.endswith('.ini') or full_path.endswith('.str'):
        file_content, file_levels = print_items(load_items(full_path))
        return file_content, file_levels
    elif full_path.endswith('.txt') or full_path.endswith('.inc'):
        with open(full_path) as loaded_file:
            file_content = loaded_file.read()
            return file_content, []


def load_directories(full_path, mode=0):
    """

    :param full_path:
    :param mode: mode=0 makes the function omit the full path,
     mode=1 makes the function provide the full path of each item
    :return: a tuple of two lists of folders and files contained in the given directory
    """
    output_folders = []
    output_files = []
    items = os.listdir(full_path)
    for item in items:
        if os.path.isdir(f'{full_path}/{item}'):
            output_folders.append(f'{(full_path + "/") * mode}{item}')
            if mode == 1:
                add_folders, add_files = load_directories(output_folders[-1], mode=1)
                if add_folders:
                    output_folders.append(add_folders)
                if add_files:
                    output_files.append(add_files)
        elif os.path.isfile(f'{full_path}/{item}'):
            output_files.append(f'{(full_path + "/") * mode}{item}')
    return output_folders, output_files


# sure = load_directories(inspected_folder, mode=0)
# print(sure)
