import os
from datetime import datetime
from glob import glob
import codecs

from constants import INI_COMMENTS, INI_DELIMITERS, STR_DELIMITERS, INI_ENDS, LEVEL_INDENT
from settings_editor import WORLDBUILDER_PATH


# class ItemLevel:
#     """ a class storing a part of an item like an Object or an ObjectCreationList defined in an INI or STR file """
#     def __init__(self, level_class='', order_index=0):
#         # super().__init__()
#         self.parameter = {}
#         self.level_class = level_class
#         self.name = ''
#         self.tag = ''
#         self.content = {'all': ''}
#         self.comment = {'init': '', 'all': ''}
#         self.is_level_open = True
#         self.sublevel = []
#         self.order_index = order_index


class Definition:
    """"""

    def __init__(self, _index=0, _class='void'):
        self._index = _index
        self._class = _class
        self.name = ''
        self.identifier = ''
        self.content = []


def load_items(from_file, mode=0):
    """
     loads and reformats items like an Object or an ObjectCreationList defined in an INI or STR file
    :param from_file: the full path of the source file to read the objects from
    :param mode: mode=1 enables to exit at the first error with the object list created so far
    :return: loaded items in form of a list of ItemLevel objects where the first describes the source file
    """
    current_level = 0
    items = [Definition(_class='file')]
    items[0].name = from_file
    # items[0].is_level_open = False
    file_item_type = []
    if from_file.endswith('.str'):
        file_item_type = STR_DELIMITERS
    elif from_file.endswith('.ini'):
        with open(from_file) as loaded_file:
            while not file_item_type:
                word = loaded_file.readline().split()
                if len(word) > 0:
                    for items_levels in INI_DELIMITERS:
                        if word[0] in items_levels[0]:
                            file_item_type = items_levels
                            break
    file_item_type.append([])
    items[0].content.append({'structure': file_item_type})
    # index_tracker = 0
    initial_comment = ''
    line_counter = 0
    is_level_open = False
    is_definition_open = False
    with open(from_file) as loaded_file:
        file_lines = loaded_file.readlines()
    for file_line in file_lines:
        # try:
        line_counter += 1
        words = file_line.replace('=', ' ').replace(':', ' ').split()
        if file_line.strip() == '':
            continue
        elif file_line.strip()[0] in INI_COMMENTS:
            if not is_definition_open:  # not is_level_open
                initial_comment += ' '.join(file_line.split()) + '\n'
            elif current_level == 1:
                items[-1].content.append({'comment': f"{LEVEL_INDENT * current_level}{' '.join(file_line.split())}\n"})
            elif current_level > 1:
                items[-1].content[-1].content.append(
                    {'comment': f"{LEVEL_INDENT * current_level}{' '.join(file_line.split())}\n"}
                )
        elif words[0] in file_item_type[current_level]:
            if current_level == 0:
                items.append(Definition(_class=words[0]))
                items[-1].content.append({'comment': ''})
                items[-1].content.append({'class': words[0]})
                is_definition_open = True
                if len(words) >= 2:
                    if words[1][0] not in INI_COMMENTS:
                        items[-1].name = words[1]
                        items[-1].content[-1]['name'] = words[1]
                        if len(words) >= 3:
                            if words[2][0] not in INI_COMMENTS:
                                items[-1].identifier = words[2]
                                items[-1].content[-1]['identifier'] = words[2]
                                if len(words) > 3 and words[3][0] in INI_COMMENTS:
                                    items[-1].content[-1].append(
                                        {'comment': f'{LEVEL_INDENT * current_level}'
                                                    f'{file_line[file_line.index(words[3]):]}'}
                                    )
                            elif words[2][0] in INI_COMMENTS:
                                items[-1].content[-1]['comment'] = words[2:]
                    elif words[1][0] in INI_COMMENTS:
                        items[-1].content[-1]['comment'] = words[1:]
            elif current_level == 1:
                items[-1].content.append(Definition(_class=words[0]))
                items[-1].content[-1].content.append({'class': words[0]})
                is_level_open = True
                if len(words) >= 2:
                    if words[1][0] not in INI_COMMENTS:
                        items[-1].content[-1].name = words[1]
                        items[-1].content[-1].content[0]['name'] = words[1]
                        if len(words) >= 3:
                            if words[2][0] not in INI_COMMENTS:
                                items[-1].content[-1].identifier = words[2]
                                items[-1].content[-1].content[0]['identifier'] = words[2]
                                if len(words) > 3 and words[3][0] in INI_COMMENTS:
                                    items[-1].content[-1].content[0]['comment'] = (
                                        f'{LEVEL_INDENT * current_level}'
                                        f'{file_line[file_line.index(words[3]):]}'
                                    )
                            elif words[2][0] in INI_COMMENTS:
                                items[-1].content[-1]['comment'] = words[2:]
                    elif words[1][0] in INI_COMMENTS:
                        items[-1].content[-1]['comment'] = words[1:]
            elif current_level > 1:
                try:
                    if is_level_open:
                        items[-1].content[-1].content.append(
                            {'assignation': f"{LEVEL_INDENT * current_level}{' '.join(file_line.split())}\n"}
                        )
                except AttributeError:
                    items[-1].content.append(
                        {'assignation': f"{LEVEL_INDENT}{' '.join(file_line.split())}\n"}
                    )
            current_level += 1
        elif words[0] in INI_ENDS:
            current_level -= 1
            if current_level == 0:
                items[-1].content[0]['comment'] = initial_comment
                initial_comment = ''
                is_definition_open = False
            elif current_level == 1:
                is_level_open = False
            elif current_level > 1:
                try:
                    if is_level_open:
                        items[-1].content[-1].content.append(
                            {'assignation': f"{LEVEL_INDENT * current_level}{' '.join(file_line.split())}\n"}
                        )
                except AttributeError:  # IndexError:
                    items[-1].content.append(
                        {'assignation': f"{LEVEL_INDENT * current_level}{' '.join(file_line.split())}\n"}
                    )
        elif is_definition_open:
            try:
                if is_level_open:
                    items[-1].content[-1].content.append(
                        {'assignation': f"{LEVEL_INDENT * current_level}{' '.join(file_line.split())}\n"}
                    )
                else:
                    items[-1].content.append(
                        {'assignation': f"{LEVEL_INDENT}{' '.join(file_line.split())}\n"}
                    )
            except AttributeError:
                items[-1].content.append(
                    {'assignation': f"{LEVEL_INDENT}{' '.join(file_line.split())}\n"}
                )
        else:
            if mode == 1:
                return items
            print('exception: ' + file_line)
        # except IndexError:
        #     if mode == 1:
        #         return items
    return items


def print_items(items):
    """
     concatenates a string from loaded items like an Object or an ObjectCreationList defined in an INI or STR file
    :param items: loaded items as a list of object returned by the load_items() function
    :return: printable string being the reformatted content of a file
    """
    output = ''
    levels_list = []
    splitter = ' '
    for item in items:
        if item._class == 'file':
            levels_list = item.content[0]['structure']
            if item.name.endswith('.str'):
                splitter = ':'
        elif item._class in levels_list[0]:
            # output += '\n' + item.content[0]['comment'] + item._class
            # # if item.identifier != '':
            # #     output += splitter + item.name + splitter + item.identifier
            # # elif item.name != '':
            # #     output += splitter + item.name
            # for key in item.content[1]:
            #     if key == 'comment':
            #         output += f' {item.content[1][key]}'
            #     else:
            #         output += f'{splitter}{item.content[1][key]}'
            # output += '\n'
            # for param in item.parameter:
            #     output += f'{LEVEL_INDENT}{param} = {item.parameter[param]}\n'
            for index in range(len(item.content)):
                try:
                    # if index in item.content:
                    #     output += item.content[index]
                    # elif key in item.comment:
                    #     output += item.comment[key]
                    # else:
                    #     for sublevel in item.sublevel:
                    #         if sublevel.order_index == key:
                    #             if sublevel.comment['all'] != '':
                    #                 output += f'\n{LEVEL_INDENT}' + sublevel.comment['all']
                    #             output += LEVEL_INDENT + sublevel.level_class
                    #             if sublevel.name != '':
                    #                 if sublevel.name == 'LifetimeUpdate':
                    #                     output += ' ' + sublevel.name
                    #                 else:
                    #                     output += ' = ' + sublevel.name
                    #                 if sublevel.tag != '':
                    #                     output += splitter + sublevel.tag
                    #             output += '\n'
                    #             output += sublevel.content['all']
                    #             output += f'{LEVEL_INDENT}End\n'
                    if type(item.content[index]) is Definition:
                        for level_index in range(len(item.content[index].content)):
                            if type(item.content[index].content[level_index]) is dict:
                                line = ''  # LEVEL_INDENT
                                for key in item.content[index].content[level_index]:
                                    line += ' ' + item.content[index].content[level_index][key]
                                if line[0:len(LEVEL_INDENT)] != LEVEL_INDENT:
                                    line = LEVEL_INDENT + line
                                if line[-1] != '\n':
                                    line += '\n'
                                output += line[1:]
                            else:
                                output += item.content[index].content[level_index]
                        output += '\tEnd\n'
                    elif type(item.content[index]) is dict:
                        line = ''
                        for key in item.content[index]:
                            line += ' ' + item.content[index][key]
                        if line[-1] != '\n':
                            line += '\n'
                        output += line[1:]
                    else:
                        output += item.content[index]
                except KeyError:
                    print('file_interpreter: print_items() error: KeyError')
            output += 'End\n\n'
    return output, levels_list


from tkinter.filedialog import askopenfilename

print(print_items(load_items(askopenfilename()))[0])


def comment_out(lines):
    """ comments out a few lines in a loaded and printed item"""
    output = ''
    for line in lines.split('\n'):
        output += f';;;{line}\n'
    return output


def convert_string(string, direction='automatic'):
    """
    converts the \n \t \r characters for reading or for finding the string in a file
    :param string: str to convert
    :param direction: 'automatic', 'process', 'display'
    :return: converted string
    """
    to_convert = {
        '\n': '\\n',
        '\t': '\\t',
        '\r': '\\r',
        ' ': '·'
    }
    for key in to_convert:
        if direction == 'process' or to_convert[key] in string and direction != 'display':
            for character in to_convert:
                string = string.replace(to_convert[character], character)
            return string
        elif key in string or direction == 'display':
            for character in to_convert:
                string = string.replace(character, to_convert[character])
            return string
        else:
            return string


counter = 1
object_override_path = r'O:\_MODULES\AotR8-INI_remake (ongoing)\AotR\aotr\data\ini\object\zealous_override\all_objects.txt'
default_object_path = r'O:\_MODULES\AotR8-INI_remake (ongoing)\AotR\aotr\data\ini\object'


def list_objects(file_or_folder=default_object_path, object_list_path=object_override_path, mode=0):
    """
    creates or overwrites a file where all objects are listed
    :param file_or_folder: source directory to get the objects from
    :param object_list_path: destination path for saving the list into
    :param mode: mode=0 .txt file | mode=1 .ini file with valid objects
    :return: a list of objects wrote to the file
    """
    global counter
    items_name_list = []
    # object_blocks = []
    # for item in loaded_items[1:]:
    #     items_name_list.append(item.name)
    if os.path.isfile(file_or_folder) and file_or_folder.endswith('.ini'):
        with open(file_or_folder) as read_file:
            file_lines = read_file.readlines()
        for file_line in file_lines:
            try:
                if file_line.strip().split()[0] in INI_DELIMITERS[4][0]:
                    if mode == 0:
                        items_name_list.append(f'{file_line.strip()}\n')
                    elif mode == 1:
                        counter_string = '0' * (5 - len(str(counter))) + str(counter)
                        items_name_list.append(f';{counter_string}; {file_or_folder}\n{file_line.strip()}\n\nEnd\n\n')
                        counter += 1
            except IndexError:
                pass
    elif os.path.isdir(file_or_folder):
        list_dir = os.listdir(file_or_folder)
        for item in list_dir:
            items_name_list += list_objects(f'{file_or_folder}/{item}', mode=mode)
    if mode == 1:
        object_list_path = object_list_path.replace('.txt', '.ini')
    with open(object_list_path, 'w') as override_file:
        override_file.write(f';;;{str(datetime.now()).split(".")[0]}\n')  # .replace(":", "_")
        for object_block in items_name_list:
            override_file.write(object_block)
    return items_name_list


# list_objects(mode=0)


def compare_object_lists(object_list1, object_list2):
    """
    unfinished
    :param object_list1:
    :param object_list2:
    :return:
    """
    with open(object_list1) as object_file1:
        object_lines1 = object_file1.readlines()
    with open(object_list2) as object_file2:
        object_lines2 = object_file2.readlines()
    for object_line1 in object_lines1:
        for object_line2 in object_lines2:
            if object_line1 == object_line2:
                pass


def test_compare_object_lists(mode=0):
    """
    unfinished
    :param mode:
    :return:
    """
    global object_override_path
    file_type = '.>type<'
    if mode == 0:
        file_type = '.txt'
    elif mode == 1:
        file_type = '.ini'
    object_list_path_1 = object_override_path.replace(file_type, f'_1{file_type}')
    list_objects(object_list_path=object_list_path_1, mode=mode)
    object_list_path_2 = object_override_path.replace(f'_1{file_type}', f'_2{file_type}')
    list_objects(object_list_path=object_list_path_2, mode=mode)
    compare_object_lists(object_list_path_1, object_list_path_2)


ERROR_TYPES = ["Error parsing field 'End' in block 'Object' in file",
               "Error parsing block 'Object' in file",
               "Error parsing INI block 'ChildObject' in file"]


def launch_and_read_last_dump():
    os.system(WORLDBUILDER_PATH)
    all_dumps = glob(WORLDBUILDER_PATH[:WORLDBUILDER_PATH.rfind('worldbuilder.exe')] + "DUMP_*.dmp")
    last_dump = max(all_dumps, key=os.path.getctime)
    with (codecs.open(last_dump, 'rb') as error_content_file):
        error_content = error_content_file.read()
        readable_content = ''
        for character in error_content:
            # try:
            if character in range(32, 123):
                readable_content += f'{character:c}'
            # except:
            #     pass
        line_index_start = 0
        for error_string in ERROR_TYPES:
            if error_string in readable_content:
                try:
                    line_index_start = (readable_content.index(error_string) + len(error_string) + 2)
                except ValueError:
                    print('unrecognized error')
                finally:
                    break
        line_index_end = readable_content.find('.ini') + len('.ini')
        if line_index_start == 0:
            line_index_start = line_index_end - 200 + readable_content[(line_index_end - 200):line_index_end].find(
                'data')
        partial_path = readable_content[line_index_start:line_index_end]
    full_path = f"{WORLDBUILDER_PATH[:WORLDBUILDER_PATH.rfind('worldbuilder.exe')]}{partial_path}"  # .replace('\\', '/')
    try:
        with open(full_path, 'r') as erroneous_file:
            erroneous_file.read()
            print(f'file {full_path} exists and is readable')
            # check_includes(full_path)
    except FileNotFoundError:
        # with open(full_path, "w") as missing_file:
        #     missing_file.write(";;; moved")
        # append_undeletable_log([full_path])
        print(f'file {full_path} recreated as empty')
        launch_and_read_last_dump()
    except PermissionError:
        # launch_and_read_last_dump()
        pass
