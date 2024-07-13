import os
import shutil

from constants import MODS_FOLDER, BACKUP_FOLDER, EXCEPTION_FOLDERS, MOD_TEMPLATE, LOG_PATH


class Mod:
    """ a class storing information about a game mod."""
    def __init__(self, name='default_mod'):
        self.name = name
        self.status = ''
        self.is_active = ''
        self.contains_mod = ''
        self.contained_in = ''
        self.description = ''
        self.parameter = {
            "name: ": name,
            "is active: ": 'no',
            "status: ": '',
            "contains mod(s): ": '',
            "is contained in mod(s): ": '',
            "description: ": ''
        }

    def internalise(self):
        self.name = self.parameter["name: "]
        self.status = self.parameter["status: "]
        self.is_active = self.parameter["is active: "]
        self.contains_mod = self.parameter["contains mod(s): "]
        self.contained_in = self.parameter["is contained in mod(s): "]
        self.description = self.parameter["description: "]


def load_mods():
    """ loads all mods in the mods folder bypassing folders mentioned as exceptions."""
    # output = ''
    mods = []
    for module in os.listdir(MODS_FOLDER):
        if module not in EXCEPTION_FOLDERS and os.path.isdir(MODS_FOLDER + '/' + module):
            mods.append(Mod(module))
            # output += mods[-1].name + '\n'
            if os.path.isfile(MODS_FOLDER + '/' + module + '/_mod_parameters.txt'):
                with open(MODS_FOLDER + '/' + module + '/_mod_parameters.txt') as mod_param_file:
                    mod_param_content = mod_param_file.readlines()
                    for line in mod_param_content:
                        for param in mods[-1].parameter:
                            try:
                                mods[-1].parameter[param] = line[line.index(param) + len(param):-1]
                                # output += '\t' + param + mods[-1].parameter[param] + '\n'
                            except ValueError:
                                # print("error mods_enabler.load_mods: ValueError")
                                pass
                mods[-1].internalise()
            else:
                new_param_content = ''
                with open(MODS_FOLDER + '/' + module + '/_mod_parameters.txt', 'w') as mod_param_file:
                    for param in mods[-1].parameter:
                        new_param_content += param + mods[-1].parameter[param] + '\n'
                    mod_param_file.write(new_param_content)
    # print(output)
    return mods


def edit_mod(mod, mod_name=None, mod_status=None, mod_is_active=None, mod_contains_mod=None, mod_contained_in=None,
             mod_description=None):
    """ modify the information about a given mod"""
    output = ''
    if mod_name is not None:
        checked_mods = load_mods()
        if mod_name not in [checked_mod.name for checked_mod in checked_mods]:
            mod.parameter["name: "] = mod_name
            os.rename(f'{MODS_FOLDER}/{mod.name}', f'{MODS_FOLDER}/{mod_name}')
            for checked_mod in checked_mods:
                if mod.name in checked_mod.contains_mod and mod.name != checked_mod.name:
                    edit_mod(checked_mod, mod_contains_mod=checked_mod.contains_mod.replace(mod.name, mod_name))
                if mod.name in checked_mod.contained_in and mod.name != checked_mod.name:
                    edit_mod(checked_mod, mod_contained_in=checked_mod.contained_in.replace(mod.name, mod_name))
            output += f'name {mod.name} changed to {mod_name}\n'
        else:
            print('mods_editor.edit_mod error: name already used')
    if mod_status is not None:
        mod.parameter["status: "] = mod_status
        output += f'status {mod.status} changed to {mod_status}\n'
    if mod_is_active is not None:
        mod.parameter["is active: "] = mod_is_active
        output += f'is_active {mod.is_active} changed to {mod_is_active}\n'
    if mod_contains_mod is not None:
        mod.parameter["contains mod(s): "] = mod_contains_mod
        output += f'contains_mod {mod.contains_mod} changed to {mod_contains_mod}\n'
    if mod_contained_in is not None:
        mod.parameter["is contained in mod(s): "] = mod_contained_in
        output += f'contained_in {mod.contained_in} changed to {mod_contained_in}\n'
    if mod_description is not None:
        mod.parameter["description: "] = mod_description
        output += f'description {mod.description} changed to {mod_description}\n'
    mod.internalise()
    with open(f'{MODS_FOLDER}/{mod.name}/_mod_parameters.txt', 'w') as mod_param_file:
        new_param_content = ''
        for param in mod.parameter:
            new_param_content += param + mod.parameter[param] + '\n'
        mod_param_file.write(new_param_content)
    # return mod
    try:
        with open(f'{LOG_PATH}/mod_loaded.txt', 'a') as log_file:
            log_file.write(output + '\n')
    except FileNotFoundError:
        with open(f'{LOG_PATH}/mod_loaded.txt', 'w') as log_file:
            log_file.write(output + '\n')
    return output


def activate_mod(mod):
    """
    loads the given mod into the main directory
    :param mod: a Mod class object
    :return: logs about files moved and copied. These are saved into text files, read afterward by the deactivate_mod
    """
    if mod.is_active == 'yes':
        return "mod is active already"
    log_activated = ''
    log_backed_up = ''
    mod_path = f'{MODS_FOLDER}/{mod.name}'
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
        backed_up_folder = f'{BACKUP_FOLDER}/overwritten_by_{mod.name}/{folder}'
        if not os.path.exists(backed_up_folder):
            os.makedirs(backed_up_folder)
            log_backed_up += f'{backed_up_folder}\n'
        activated_folder = f'O:/{folder}'
        if not os.path.exists(activated_folder):
            os.makedirs(activated_folder)
            log_activated += f'{activated_folder}\n'
    for file in files:
        backed_up_file = f'{BACKUP_FOLDER}/overwritten_by_{mod.name}/{file}'
        try:
            shutil.move(f'O:/{file}', backed_up_file)
            log_backed_up += f'{backed_up_file}\n'
        except FileNotFoundError:
            print('error mods_enabler.activate_mod(): FileNotFoundError')
        except FileExistsError:
            print('error mods_enabler.activate_mod(): FileExistsError')
        activated_file = f'{mod_path}/{file}'
        shutil.copy(activated_file, f'O:/{file}')
        log_activated += f'{activated_file}\n'
    with open(f'{BACKUP_FOLDER}/overwritten_by_{mod.name}/log_backed_up.txt', 'w') as text_backed_up:
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


# TODO: function to check if the files have been modified before deactivating the mod


def deactivate_mod(mod):
    """

    :param mod: a Mod class object
    :return: logs about the files
    """
    if mod.is_active.lower() == 'no':
        return "mod is deactivated already"
    with open(f'{BACKUP_FOLDER}/overwritten_by_{mod.name}/log_backed_up.txt', 'r') as log_backed_up:
        list_backed_up = log_backed_up.readlines()
    with open(f'{MODS_FOLDER}/{mod.name}/log_activated.txt', 'r') as log_activated:
        list_activated = log_activated.readlines()
    log_deactivated = ''
    log_backing_up = ''
    for line in list_activated:
        if os.path.isfile(line.strip()):
            deactivated_file = line.strip()  # f'O:/{line.strip()}'
            if os.path.exists(deactivated_file):
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
            # backed_up_folder = f'{BACKUP_FOLDER}/overwritten_by_{mod.name}/{line.strip()}'
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
            # backing_up_file = f'{BACKUP_FOLDER}/overwritten_by_{mod.name}/{line.strip()}'
            backing_up_file = line.strip()
            if os.path.exists(backing_up_file):
                shutil.move(backing_up_file, line.strip())  # f'O:/{line.strip()}'
                log_backing_up += f'{backing_up_file}\n'
        else:
            print(f"error mods_enabler.deactivate_mod(): item {line.strip()} is neither file nor folder ")
    os.remove(f'{BACKUP_FOLDER}/overwritten_by_{mod.name}/log_backed_up.txt')
    os.remove(f'{MODS_FOLDER}/{mod.name}/log_activated.txt')
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
    if named in [mod.name for mod in mods]:
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
