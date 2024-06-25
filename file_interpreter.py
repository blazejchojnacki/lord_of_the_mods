from constants import INI_COMMENTS, INI_DELIMITERS, STR_DELIMITERS, INI_ENDS, LEVEL_INDENT


class ItemLevel:
    """ a class storing a part of an item like an Object or an ObjectCreationList defined in an INI or STR file"""
    def __init__(self, level_class='', order_index=0):
        super().__init__()
        self.parameter = {}
        self.level_class = level_class
        self.name = ''
        self.tag = ''
        self.content = {'all': ''}
        self.comment = {'init': '',
                        'all': ''}
        self.is_level_open = True
        self.sublevel = []
        self.order_index = order_index


def load_items(from_file):
    """ loads and reformats items like an Object or an ObjectCreationList defined in an INI or STR file"""
    current_level = 0
    items = [ItemLevel('file')]
    items[0].name = from_file
    items[0].is_level_open = False
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
            # file_lines = loaded_file.readlines()
            # for file_line in file_lines:
            #     word = file_line.split()
            #     if len(word) > 0 and not file_item_type:
            #         for items_levels in INI_DELIMITERS:
            #             if word[0] in items_levels[0] and items_levels not in file_item_type:
            #                 file_item_type = items_levels
            #                 break
            #     elif file_item_type:
            #         break
    file_item_type.append([])
    items[0].sublevel = file_item_type
    index_tracker = 0
    initial_comment = ""
    with open(from_file) as loaded_file:
        file_lines = loaded_file.readlines()
        line_counter = 0
        for file_line in file_lines:
            line_counter += 1
            words = file_line.replace('=', ' ').replace(':', ' ').split()
            if file_line.strip() == '':
                continue
            elif file_line.strip()[0] in INI_COMMENTS:
                if not items[-1].is_level_open:
                    initial_comment += ' '.join(file_line.split()) + '\n'
                elif current_level >= 1:
                    items[-1].comment[index_tracker] = f"{LEVEL_INDENT * current_level}{' '.join(file_line.split())}\n"
                    index_tracker += 1
            elif words[0] in file_item_type[current_level]:
                if current_level == 0:
                    items.append(ItemLevel(level_class=words[0]))
                    index_tracker = 0
                    items[-1].is_level_open = True
                    if len(words) >= 2 and words[1][0] not in INI_COMMENTS:
                        items[-1].name = words[1]
                        if len(words) >= 3 and words[2][0] not in INI_COMMENTS:
                            items[-1].tag = words[2]
                            if len(words) > 3 and words[3][0] in INI_COMMENTS:
                                items[-1].comment[index_tracker] = LEVEL_INDENT + file_line[file_line.index(words[3]):]
                                index_tracker += 1
                elif current_level == 1:
                    items[-1].sublevel.append(ItemLevel(level_class=words[0], order_index=index_tracker))
                    index_tracker += 1
                    if len(words) >= 2 and words[1][0] not in INI_COMMENTS:
                        items[-1].sublevel[-1].name = words[1]
                        if len(words) >= 3 and words[2][0] not in INI_COMMENTS:
                            items[-1].sublevel[-1].tag = words[2]
                elif current_level > 1:
                    try:
                        if items[-1].sublevel[-1].is_level_open:
                            items[-1].sublevel[-1].content["all"] += (f"{LEVEL_INDENT * current_level}"
                                                                      f"{' '.join(file_line.split())}\n")
                    except IndexError:
                        items[-1].content[index_tracker] = f"{LEVEL_INDENT}{' '.join(file_line.split())}\n"
                        index_tracker += 1
                current_level += 1
            elif words[0] in INI_ENDS:
                current_level -= 1
                if current_level == 0:
                    items[-1].is_level_open = False
                    items[-1].comment["init"] = initial_comment
                    initial_comment = ""
                    items[-1].order_index = index_tracker
                elif current_level == 1:
                    items[-1].sublevel[-1].is_level_open = False
                elif current_level > 1:
                    try:
                        if items[-1].sublevel[-1].is_level_open:
                            items[-1].sublevel[-1].content['all'] += (f"{LEVEL_INDENT * current_level}"
                                                                      f"{' '.join(file_line.split())}\n")
                    except IndexError:
                        items[-1].content[index_tracker] += f"{LEVEL_INDENT}{' '.join(file_line.split())}\n"
                        index_tracker += 1
            # elif words[0] in INI_PARAMETERS and current_level == 1:
            #     items[-1].parameter[words[0]] = file_line.strip().split('=')[1].strip()
            elif items[-1].is_level_open:
                try:
                    if items[-1].sublevel[-1].is_level_open:
                        items[-1].sublevel[-1].content['all'] += (f"{LEVEL_INDENT * current_level}"
                                                                  f"{' '.join(file_line.split())}\n")
                    else:
                        items[-1].content[index_tracker] = f"{LEVEL_INDENT}{' '.join(file_line.split())}\n"
                        index_tracker += 1
                except IndexError:
                    items[-1].content[index_tracker] = f"{LEVEL_INDENT}{' '.join(file_line.split())}\n"
                    index_tracker += 1
            else:
                print('exception: ' + file_line)
    return items


def print_items(items):
    """ concatenates a string from loaded items like an Object or an ObjectCreationList defined in an INI or STR file"""
    output = ''
    levels_list = []
    splitter = ' '
    for item in items:
        if item.level_class == 'file':
            levels_list = item.sublevel
            if item.name[-len('.str'):] == '.str':
                splitter = ':'
        elif item.level_class in levels_list[0]:
            output += '\n' + item.comment['init'] + item.level_class
            if item.tag != '':
                output += splitter + item.name + splitter + item.tag
            elif item.name != '':
                output += splitter + item.name
            output += '\n'
            for param in item.parameter:
                output += f'{LEVEL_INDENT}{param} = {item.parameter[param]}\n'

            for key in range(item.order_index):
                try:
                    if key in item.content:
                        output += item.content[key]
                    elif key in item.comment:
                        output += item.comment[key]
                    else:
                        for sublevel in item.sublevel:
                            if sublevel.order_index == key:
                                if sublevel.comment['all'] != '':
                                    output += f'\n{LEVEL_INDENT}' + sublevel.comment['all']
                                output += LEVEL_INDENT + sublevel.level_class
                                if sublevel.name != '':
                                    if sublevel.name == 'LifetimeUpdate':
                                        output += ' ' + sublevel.name
                                    else:
                                        output += ' = ' + sublevel.name
                                    if sublevel.tag != '':
                                        output += splitter + sublevel.tag
                                output += '\n'
                                output += sublevel.content['all']
                                output += f'{LEVEL_INDENT}End\n'
                except KeyError:
                    pass
            output += 'End\n'
    return output, levels_list


def comment_out(printed_item):
    """ comments out a few lines in a loaded and printed item"""
    output = ''
    for line in printed_item.split('\n'):
        output += f';;;{line}\n'
    return output


# from tkinter.filedialog import askopenfilename
# print(print_items(load_items(askopenfilename()))[0])
