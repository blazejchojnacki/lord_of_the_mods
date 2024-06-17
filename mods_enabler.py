import os
import shutil

from common import MODS_FOLDER, BACKUP_FOLDER, EXCEPTION_FOLDERS, MOD_TEMPLATE


class Mod:
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
    output = ''
    mods = []
    for module in os.listdir(MODS_FOLDER):
        if module not in EXCEPTION_FOLDERS and os.path.isdir(MODS_FOLDER + '/' + module):
            mods.append(Mod(module))
            output += mods[-1].name + '\n'
            if os.path.isfile(MODS_FOLDER + '/' + module + '/_mod_parameters.txt'):
                with open(MODS_FOLDER + '/' + module + '/_mod_parameters.txt') as mod_param_file:
                    mod_param_content = mod_param_file.readlines()
                    for line in mod_param_content:
                        for param in mods[-1].parameter:
                            try:
                                mods[-1].parameter[param] = line[line.index(param) + len(param):-1]
                                output += '\t' + param + mods[-1].parameter[param] + '\n'
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
    # print(output)  TODO: log this output
    return mods


def edit_mod(mod, mod_name=None, mod_status=None, mod_is_active=None, mod_contains_mod=None, mod_contained_in=None,
             mod_description=None):
    log_output = ''
    if mod_name is not None:
        log_output += mod.name + " changed to "
        mod.name = mod_name
        mod.parameter["name: "] = mod_name
        log_output += mod.name + '\n'
    if mod_status is not None:
        log_output += mod.status + " changed to "
        mod.status = mod_status
        mod.parameter["status: "] = mod_status
        log_output += mod.status + '\n'
    if mod_is_active is not None:
        log_output += mod.is_active + " changed to "
        mod.is_active = mod_is_active
        mod.parameter["is active: "] = mod_is_active
        log_output += mod.is_active + '\n'
    if mod_contains_mod is not None:
        log_output += mod.contains_mod + " changed to "
        mod.contains_mod = mod_contains_mod
        mod.parameter["contains mod(s): "] = mod_contains_mod
        log_output += mod.contains_mod + '\n'
    if mod_contained_in is not None:
        log_output += mod.contained_in + " changed to "
        mod.contained_in = mod_contained_in
        mod.parameter["is contained in mod(s): "] = mod_contained_in
        log_output += mod.contained_in + '\n'
    if mod_description is not None:
        log_output += mod.description + " changed to "
        mod.description = mod_description
        mod.parameter["description: "] = mod_description
        log_output += mod.description + '\n'
    with open(MODS_FOLDER + '/' + mod.name + '/_mod_parameters.txt', 'w') as mod_param_file:
        new_param_content = ''
        for param in mod.parameter:
            new_param_content += param + mod.parameter[param] + '\n'
        mod_param_file.write(new_param_content)
    # return mod
    return log_output


def activate_mod(mod):  # TODO: save the logs for later file deactivation
    if mod.is_active == 'yes':
        return "mod is active already"
    # mods = load_mods()
    log_activated = 'activated:\n'
    log_backed_up = 'backed up:\n'
    mod_path = MODS_FOLDER + '/' + mod.name
    items_list = os.listdir(mod_path)
    folders = []
    files = []
    for item in items_list:
        if os.path.isdir(f'{mod_path}/{item}'):
            folders.append(item)  # mod_path + '/' +
            for next_item in os.listdir(f'{mod_path}/{item}'):
                items_list.append(f'{item}/{next_item}')
                if os.path.isdir(f'{mod_path}/{item}/{next_item}'):
                    folders.append(f'{item}/{next_item}')  # mod_path + '/' +
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
            # print(activated_folder + " - non-existent")
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
    # print(log_backed_up)
    # print(log_activated)
    return log_backed_up + log_activated


def deactivate_mod(mod):  # TODO: base the removal on logs from activate_mod
    if mod.is_active.lower() == 'no':
        return "mod is deactivated already"
    log_deactivated = 'deactivated:\n'
    log_backing_up = 'backing up:\n'
    mod_path = f'{MODS_FOLDER}/{mod.name}'
    items_list = os.listdir(mod_path)
    folders = []
    files = []
    for item in items_list:
        if os.path.isdir(f'{mod_path}/{item}'):
            folders.append(item)  # mod_path + '/' +
            for next_item in os.listdir(f'{mod_path}/{item}'):
                items_list.append(f'{item}/{next_item}')
                if os.path.isdir(f'{mod_path}/{item}/{next_item}'):
                    folders.append(f'{item}/{next_item}')  # mod_path + '/' +
        elif os.path.isfile(f'{mod_path}/{item}'):
            files.append(item)
        else:
            print(f"error mods_enabler.deactivate_mod(): item {item} is neither file nor folder ")
    for file in files:
        deactivated_file = f'O:/{file}'
        if os.path.exists(deactivated_file):
            os.remove(deactivated_file)
            log_deactivated += f'{deactivated_file}\n'
        backing_up_file = f'{BACKUP_FOLDER}/overwritten_by_{mod.name}/{file}'
        if os.path.exists(backing_up_file):
            shutil.move(backing_up_file, deactivated_file)
            log_backing_up += f'{backing_up_file}\n'
    for folder in folders:
        deactivated_folder = f'O:/{folder}'
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
        backed_up_folder = f'{BACKUP_FOLDER}/overwritten_by_{mod.name}/{folder}'
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
    # print(log_backing_up)
    # print(log_deactivated)
    return log_backing_up + log_deactivated


def reload_mod(mod):
    output = ''
    output += deactivate_mod(mod)
    output += activate_mod(mod)
    return output


def create_mod(named, from_template=MOD_TEMPLATE):
    mods = load_mods()
    if named in [mod.name for mod in mods]:
        return "mod already created"
    else:
        log_copied = ''
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
                log_copied += folder + '\n'
        for file in files:
            copied_file = f'{from_template}/{file}'
            try:
                shutil.copy(copied_file, f'O:/_MODULES/{named}/{file}')
                log_copied += f'O:/_MODULES/{named}/{file}\n'
            except FileNotFoundError:
                print("error mods_enabler.create_mod(): permission denied")
            except FileExistsError:
                print(f"error mods_enabler.create_mod(): FileNotFoundError")
        return log_copied

