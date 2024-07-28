import os
import shutil
import filecmp

# import settings_editor
from constants import MOD_PARAMETERS
from settings_editor import MODS_FOLDER, BACKUP_FOLDER, EXCEPTION_FOLDERS, MOD_TEMPLATE, LOG_PATH  # , load_settings


class Mod:
    """a class storing information about a game mod."""
    def __init__(self, name='default_mod'):
        self.parameter = MOD_PARAMETERS.copy()
        self.parameter['name'] = name

    def edit_mod(self, **key_args):
        edit_mod(mod=self, **key_args)

    def activate_mod(self):
        activate_mod(self)

    def detect_changes(self):
        detect_changes(self)

    def deactivate_mod(self, exceptions=None):
        deactivate_mod(self, exceptions=exceptions)


def load_mods():
    """ loads all mods in the mods folder bypassing folders mentioned as exceptions."""
    # output = ''
    mods = []
    for module in os.listdir(MODS_FOLDER):
        if module not in EXCEPTION_FOLDERS and os.path.isdir(MODS_FOLDER + '/' + module):
            mods.append(Mod(module))
            # output += mods[-1].name + '\n'
            try:
                with open(f'{MODS_FOLDER}/{module}/_mod_parameters.ini') as mod_param_file:
                    # mod_param_content = mod_param_file.readlines()
                    # for line in mod_param_content:
                    line = mod_param_file.readline()
                    for param in mods[-1].parameter:
                        try:
                            if ' = ' in line:
                                mods[-1].parameter[param] = line.split(' = ')[1].strip()
                            # output += '\t' + param + mods[-1].parameter[param] + '\n'
                            else:
                                mods[-1].parameter['comment'] = line.strip()
                            line = mod_param_file.readline()
                        except ValueError:
                            # print("error mods_enabler.load_mods: ValueError")
                            pass
            except FileNotFoundError:
                new_param_content = ''
                with open(f'{MODS_FOLDER}/{module}/_mod_parameters.ini', 'w') as mod_param_file:
                    for param in mods[-1].parameter:
                        if param == 'comment':
                            new_param_content += f'{mods[-1].parameter[param]}\n'
                        else:
                            new_param_content += f'{param} = {mods[-1].parameter[param]}\n'
                    mod_param_file.write(new_param_content)
    # print(output)
    return mods


def edit_mod(mod, **key_args):
    """
     modifies the information about a given mod
    :param mod:
    :param key_args: name, status, children, parent, description
    :return: string log about result
    """
    output = ''
    for edited_param in key_args:
        if edited_param == 'name':
            checked_mods = load_mods()
            if key_args['name'] not in [checked_mod.parameter['name'] for checked_mod in checked_mods]:
                try:
                    os.rename(f"{MODS_FOLDER}/{mod.parameter['name']}", f"{MODS_FOLDER}/{key_args['name']}")
                except PermissionError:
                    output = 'mods_enabler.edit_mod error: could not rename the mod due to PermissionError\n'
                for checked_mod in checked_mods:
                    if (mod.parameter['name'] in checked_mod.parameter['children']
                            and mod.parameter['name'] != checked_mod.parameter['name']):
                        edit_mod(checked_mod, children=checked_mod.parameter['children'].replace(mod.parameter['name'], key_args['name']))
                    if mod.parameter['name'] in checked_mod.parameter['parents'] and mod.parameter['name'] != checked_mod.parameter['name']:
                        edit_mod(checked_mod, parents=checked_mod.parameter['parents'].replace(mod.parameter['name'], key_args['name']))
                output += f"name {mod.parameter['name']} changed to {key_args['name']}\n"
                mod.parameter['name'] = key_args['name']
            else:
                output += 'mods_editor.edit_mod error: name already used\n'
        else:
            if not mod.parameter[edited_param]:
                mod.parameter[edited_param] = '>empty<'
            if key_args[edited_param]:
                output += f'{edited_param} {mod.parameter[edited_param]} changed to {key_args[edited_param]}\n'
            else:
                output += f'{edited_param} {mod.parameter[edited_param]} changed to >empty<\n'
            mod.parameter[edited_param] = key_args[edited_param]
    with open(f"{MODS_FOLDER}/{mod.parameter['name']}/_mod_parameters.ini", 'w') as mod_param_file:
        new_param_content = ''
        for param in mod.parameter:
            new_param_content += f'{param} = {mod.parameter[param]}\n'
        mod_param_file.write(new_param_content)
    try:
        with open(f'{LOG_PATH}/mod_loaded.txt', 'a') as log_file:
            log_file.write(output + '\n')
    except FileNotFoundError:
        with open(f'{LOG_PATH}/mod_loaded.txt', 'w') as log_file:
            log_file.write(output + '\n')
    return output


# MODS_FOLDER = settings_editor.load_settings()[2]
# print(edit_mod(load_mods()[1], name='renamed_mod', description='yes'))


def activate_mod(mod):
    """
    loads the given mod into the main directory
    :param mod: a Mod class object
    :return: logs about files moved and copied. These are saved into text files, read afterward by the deactivate_mod
    """
    if mod.parameter['active'] == 'yes':
        return "mod active already"
    log_activated = ''
    log_backed_up = ''
    mod_path = f"{MODS_FOLDER}/{mod.parameter['name']}"
    items_list = os.listdir(mod_path)
    folders = []
    files = []
    for item in items_list:
        if os.path.isdir(f'{mod_path}/{item}'):
            folders.append(item)
            for next_item in os.listdir(f'{mod_path}/{item}'):
                items_list.append(f'{item}/{next_item}')
                if os.path.isdir(f'{mod_path}/{item}/{next_item}'):
                    folders.append(f'{item}/{next_item}')
        elif os.path.isfile(f'{mod_path}/{item}'):
            files.append(item)
        else:
            print(f"error mods_enabler.activate_mod(): item {item} is neither file nor folder")
    for folder in folders:
        backed_up_folder = f"{BACKUP_FOLDER}/overwritten_by_{mod.parameter['name']}/{folder}"
        if not os.path.exists(backed_up_folder):
            os.makedirs(backed_up_folder)
            log_backed_up += f'{backed_up_folder}\n'
        activated_folder = f'O:/{folder}'
        if not os.path.exists(activated_folder):
            os.makedirs(activated_folder)
            log_activated += f'{activated_folder}\n'
    for file in files:
        if '_mod_parameter' in file:
            continue
        backed_up_file = f"{BACKUP_FOLDER}/overwritten_by_{mod.parameter['name']}/{file}"
        try:
            shutil.move(f'O:/{file}', backed_up_file)
            log_backed_up += f'{backed_up_file}\n'
        except FileNotFoundError:
            # print(f'error mods_enabler.activate_mod(): FileNotFoundError O:/{file}')
            pass
        except FileExistsError:
            print(f'error mods_enabler.activate_mod(): FileExistsError {backed_up_file}')
        activated_file = f'{mod_path}/{file}'
        shutil.copy(activated_file, f'O:/{file}')
        log_activated += f'O:/{file}\n'
    with open(f"{BACKUP_FOLDER}/overwritten_by_{mod.parameter['name']}/log_backed_up.txt", 'w') as text_backed_up:
        text_backed_up.write(log_backed_up)
    with open(f'{mod_path}/log_activated.txt', 'w') as text_activated:
        text_activated.write(log_activated)
    output = f'backed up:\n{log_backed_up}\nactivated:\n{log_activated}'
    try:
        with open(f'{LOG_PATH}/mod_loaded.txt', 'a') as log_file:
            log_file.write(output + '\n')
    except FileNotFoundError:
        with open(f'{LOG_PATH}/mod_loaded.txt', 'w') as log_file:
            log_file.write(output + '\n')
    return log_backed_up + log_activated


def detect_changes(mod):
    output = ''
    try:
        # with open(f"{BACKUP_FOLDER}/overwritten_by_{mod.parameter['name']}/log_backed_up.txt", 'r') as log_backed_up:
        #     list_backed_up = log_backed_up.readlines()
        with open(f"{MODS_FOLDER}/{mod.parameter['name']}/log_activated.txt", 'r') as log_activated:
            list_activated = log_activated.readlines()
        for file_activated in list_activated:
            if os.path.isfile(file_activated.strip()) and not file_activated.strip().endswith('log_activated.txt'):
                # active_file_path = f"{file_activated.strip().split('/')[0]}/"
                # active_file_path += '/'.join(file_activated.strip().split('/')[3:])
                active_file_path = f"{MODS_FOLDER}/{mod.parameter['name']}/{'/'.join(file_activated.strip().split('/')[1:])}"
                if os.path.isfile(active_file_path):
                    if not filecmp.cmp(file_activated.strip(), active_file_path, shallow=False):
                        output += f'{file_activated.strip()}\n'
            #     else:
            #         pass
            # elif os.path.isdir(file_activated.strip()):
            #     pass
            # else:
            #     pass
    except FileNotFoundError:
        print('mod not activated')
    return output


# MODS_FOLDER, BACKUP_FOLDER = settings_editor.load_settings()[2:4]
# detect_changes(load_mods()[1])


def deactivate_mod(mod, exceptions=None):
    """
    deletes the files copied from a mod directory and restores the files backed up when the mod was loaded
    :param mod: a Mod class object
    :param exceptions: the files to not delete from
    :return: logs about the files
    """
    if mod.parameter['active'].lower() == 'no':
        return "mod is deactivated already"
    try:
        with open(f"{BACKUP_FOLDER}/overwritten_by_{mod.parameter['name']}/log_backed_up.txt", 'r') as log_backed_up:
            list_backed_up = log_backed_up.readlines()
        with open(f"{MODS_FOLDER}/{mod.parameter['name']}/log_activated.txt", 'r') as log_activated:
            list_activated = log_activated.readlines()
    except FileNotFoundError:
        return 'mods_enabler: deactivate_mod error: could not deactivate the mod due to missing log file'
    log_deactivated = ''
    log_backing_up = ''
    for line in list_activated:
        if os.path.isfile(line.strip()):
            deactivated_file = line.strip()  # f'O:/{line.strip()}'
            if os.path.exists(deactivated_file):
                if exceptions:
                    if deactivated_file in exceptions:
                        updated_file = f"{MODS_FOLDER}/{mod.parameter['name']}/{'/'.join(deactivated_file.split('/')[1:])}"
                        if os.path.exists(updated_file):
                            os.remove(updated_file)
                        shutil.move(src=deactivated_file, dst=updated_file)
                    else:
                        os.remove(deactivated_file)
                        log_deactivated += f'{deactivated_file}\n'
                else:
                    os.remove(deactivated_file)
                    log_deactivated += f'{deactivated_file}\n'
        elif os.path.isdir(line.strip()):
            deactivated_folder = line.strip()  # f'O:/{line.strip()}'
            try:
                if not os.listdir(deactivated_folder):
                    os.rmdir(deactivated_folder)
                    log_deactivated += deactivated_folder + '\n'
            except PermissionError:
                log_deactivated += deactivated_folder + ' could not be removed\n'
                print("error mods_enabler.deactivate_mod(): permission denied 1")
            except FileNotFoundError:
                log_deactivated += deactivated_folder + ' could not be found\n'
                print(f"error mods_enabler.deactivate_mod(): FileNotFoundError 1")
        else:
            print(f"error mods_enabler.deactivate_mod(): item {line} is neither file nor folder ")
    for line in list_backed_up:
        if os.path.isdir(line.strip()):
            # backed_up_folder = f'{BACKUP_FOLDER}/overwritten_by_{mod.parameter['name']}/{line.strip()}'
            backed_up_folder = line.strip()
            try:
                if not os.listdir(backed_up_folder):
                    os.rmdir(backed_up_folder)
                    log_backing_up += backed_up_folder + '\n'
            except PermissionError:
                log_backing_up += backed_up_folder + ' could not be removed\n'
                print("error mods_enabler.deactivate_mod(): permission denied 2")
            except FileNotFoundError:
                log_backing_up += backed_up_folder + ' could not be found\n'
                print(f"error mods_enabler.deactivate_mod(): FileNotFoundError 2")
        elif os.path.isfile(line.strip()):
            # backing_up_file = f'{BACKUP_FOLDER}/overwritten_by_{mod.parameter['name']}/{line.strip()}'
            path_parts = line.strip().split('/')
            backing_up_file = path_parts[0] + '/' + '/'.join(path_parts[3:])
            if os.path.exists(backing_up_file):
                shutil.move(line.strip(), backing_up_file)  # f'O:/{line.strip()}'
                log_backing_up += f'{backing_up_file}\n'
        else:
            print(f"error mods_enabler.deactivate_mod(): item {line.strip()} is neither file nor folder ")
    try:
        os.remove(f"{BACKUP_FOLDER}/overwritten_by_{mod.parameter['name']}/log_backed_up.txt")
        os.remove(f"{MODS_FOLDER}/{mod.parameter['name']}/log_activated.txt")
    except FileNotFoundError:
        pass
    output = f'backing up:\n{log_backing_up}\ndeactivated:\n{log_deactivated}'
    try:
        with open(f'{LOG_PATH}/mod_loaded.txt', 'a') as log_file:
            log_file.write(output + '\n')
    except FileNotFoundError:
        with open(f'{LOG_PATH}/mod_loaded.txt', 'w') as log_file:
            log_file.write(output + '\n')
    return log_backing_up + log_deactivated


def reload_mod(mod):
    output = ''
    output += deactivate_mod(mod)
    output += activate_mod(mod)
    try:
        with open(f'{LOG_PATH}/mod_loaded.txt', 'a') as log_file:
            log_file.write(output + '\n')
    except FileNotFoundError:
        with open(f'{LOG_PATH}/mod_loaded.txt', 'w') as log_file:
            log_file.write(output + '\n')
    return output


def create_mod(named, from_template=MOD_TEMPLATE):
    """
    copies a template mod and gives it the given name
    :param named: string name of the mod to create
    :param from_template: path of the mod used as a template
    :return: logs about the files that have been created
    """
    mods = load_mods()
    if named in [mod.parameter['name'] for mod in mods]:
        return "mod already created"
    else:
        output = ''
        folders = []
        files = []
        items_list = os.listdir(from_template)
        for item in items_list:
            if os.path.isdir(f'{from_template}/{item}'):
                folders.append(f'O:/_MODULES/{named}/{item}')
                for next_item in os.listdir(f'{from_template}/{item}'):
                    items_list.append(f'{item}/{next_item}')
                    if os.path.isdir(f'{from_template}/{item}/{next_item}'):
                        folders.append(f'O:/_MODULES/{named}/{item}/{next_item}')
            elif os.path.isfile(f'{from_template}/{item}'):
                files.append(item)
            else:
                print(f"error mods_enabler.create_mod(): item {item} is neither file nor folder ")
        for folder in folders:
            if not os.path.exists(folder):
                os.makedirs(folder)
                output += folder + '\n'
        for file in files:
            copied_file = f'{from_template}/{file}'
            try:
                shutil.copy(copied_file, f'O:/_MODULES/{named}/{file}')
                output += f'O:/_MODULES/{named}/{file}\n'
            except FileNotFoundError:
                print('mods_enabler.create_mod() error: permission denied')
            except FileExistsError:
                print(f'mods_enabler.create_mod() error: FileNotFoundError')
            if file == '_mod_parameters.txt':
                with open(f'O:/_MODULES/{named}/{file}', 'r') as read_file:
                    read_lines = read_file.readlines()
                    new_content = ''
                for line in read_lines:
                    if 'name: ' in line:
                        new_content += f'name: {named}\n'
                    else:
                        new_content += line
                with open(f'O:/_MODULES/{named}/{file}', 'w') as overwritten_file:
                    overwritten_file.write(new_content)
        try:
            with open(f'{LOG_PATH}/mod_loaded.txt', 'a') as log_file:
                log_file.write(output + '\n')
        except FileNotFoundError:
            with open(f'{LOG_PATH}/mod_loaded.txt', 'w') as log_file:
                log_file.write(output + '\n')
        return output
