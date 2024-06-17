from datetime import datetime
import os
import shutil

from file_interpreter import load_items, print_items, comment_out  # LOG_PATH,
# from common import MODS_FOLDER

inspected_folder = "O:/_MODULES/AotR8-INI_remake (ongoing)/AotR/aotr/data/ini"

# TODO: reference checker


def find_text(find="test", in_file_or_folder=inspected_folder):
    local_output = ''
    if in_file_or_folder == inspected_folder:
        local_output += f' command: find "{find}"\n\tin {in_file_or_folder}:\n'
    if not os.path.isfile(in_file_or_folder):
        file_paths = os.listdir(in_file_or_folder)
        for file_path in file_paths:
            find_text(find, f'{in_file_or_folder}/{file_path}')
    elif os.path.isfile(in_file_or_folder):
        try:
            with open(in_file_or_folder, 'r') as file:
                file_content = file.read()
            if file_content.count(find) > 0:
                local_output += f'\t{file_content.count(find)} found in {in_file_or_folder}\n'
                file_content_split = file_content.split(find)
                index_line = 1
                for content_part in file_content_split[:-1]:
                    index_line += content_part.count('\n')
                    local_output += f'\t\tin line {index_line}\n'
        except UnicodeDecodeError:
            print("error file_editor.find_text(): file unreadable")
    return local_output


def replace_text(find, replace_with, in_file_or_folder=inspected_folder, first_run=True):
    output = ''
    if '_MODULES' not in in_file_or_folder:
        print("alter mods only!")
    elif first_run:
        output += f'{datetime.now()}'
        output += f' command: replace "{find}"\n\twith "{replace_with}"\n\tin {in_file_or_folder}:\n'
    if os.path.isfile(in_file_or_folder):
        try:
            with open(in_file_or_folder, 'r') as file:
                file_content = file.read()
            if file_content.count(find) > 0:
                output += f'\t{file_content.count(find)} replaced in {in_file_or_folder}\n'
                new_file_content = file_content.replace(find, replace_with)
                with open(in_file_or_folder, 'w') as file:
                    file.write(new_file_content)
        except UnicodeDecodeError:
            print(f'error file_editor.replace_text(): file {in_file_or_folder} unreadable')
    elif os.path.isdir(in_file_or_folder):
        file_paths = os.listdir(in_file_or_folder)
        for file_path in file_paths:
            output += replace_text(find, replace_with, f'{in_file_or_folder}/{file_path}', first_run=False)
    # if first_run:
    #     with open(LOG_PATH, 'a') as log_file:
    #         log_file.write(output + '\n')
    return output


def move_file(full_path, to_folder):
    # TODO: to optimise using os common path and not using replace_text
    output = f'{datetime.now()}'
    output += f' command: move {full_path}\n\tto {to_folder}\n'
    file_name = full_path.replace('\\', '/').split('/')[-1]
    shutil.move(full_path, f'{to_folder}/{file_name}')
    # with open(LOG_PATH, 'a') as log_file:
    #     log_file.write(output)
    level_back = 0
    to_folder_relative = ''
    from_folder_relative = ''
    if file_name.endswith('.inc'):  # would work better in cooperation with each file
        to_folder_relative += to_folder.replace('/', '\\') + '\\'
        from_folder_relative += full_path.replace(f'\\{file_name}', '') + '\\'
        for path_part in full_path.split('\\'):
            if path_part in to_folder.split('\\'):
                from_folder_relative = from_folder_relative.replace(f'{path_part}\\', '')
                to_folder_relative = to_folder_relative.replace(f'{path_part}\\', '')
        for _ in range(5):
            old_include = '#include "' + "..\\" * _ + f'{from_folder_relative}{file_name}"'
            new_include = '#include "' + "..\\" * _ + f'{to_folder_relative}{file_name}"'
            output += replace_text(old_include, new_include)
    elif file_name.endswith('.ini'):  # would work better if evaluating if the include could be shorter
        old_includes = []
        level_back += len(to_folder.split('\\')) - len(full_path.split('\\')[:-1])
        with open(f'{to_folder}/{file_name}') as file_checked:  # file_named
            lines = file_checked.readlines()
        for line in lines:
            if "#include" in line.strip():
                if line.strip()[0] != ';':
                    old_includes.append(line)
        for old_include in old_includes:
            new_include = ('\t#include "' + "..\\" * (old_include.count('..\\') + level_back)
                           + old_include.strip().replace('#include "', '').replace('..\\', '')
                           + '\n')
            output += replace_text(old_include, new_include, f'{to_folder}/{file_name}')
    return output


def duplicates_commenter(in_file):
    new_content = ''
    commented_out = f'{datetime.now()}'
    commented_out += f' command: comment out duplicates in {in_file}:\n'
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
            commented_out += print_items([items[0], items[item_index]])
        else:
            new_content += print_items([items[0], items[item_index]])
    # with open(LOG_PATH, 'a') as log_file:
    #     log_file.write(commented_out + '\n')
    with open(in_file, 'w') as new_file:
        new_file.write(new_content)
    return commented_out


# print(duplicates_commenter(askopenfilename()))


def load_file(full_path):
    if full_path.endswith('.ini') or full_path.endswith('.str'):
        file_content, file_levels = print_items(load_items(full_path))
        return file_content, file_levels
    elif full_path.endswith('.txt') or full_path.endswith('.inc'):
        with open(full_path) as loaded_file:
            file_content = loaded_file.read()
            return file_content, []


def load_directories(full_path):
    output_folders = []
    output_files = []
    items = os.listdir(full_path)
    for item in items:
        if os.path.isdir(f'{full_path}/{item}'):
            output_folders.append(item)
        elif os.path.isfile(f'{full_path}/{item}'):
            output_files.append(item)
    return output_folders, output_files


# print(load_directories(MODS_FOLDER + '/' + "AotR8-INI_remake (ongoing)"))
