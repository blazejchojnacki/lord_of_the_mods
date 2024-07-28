import os.path

from constants import INI_ENDS, INI_COMMENTS, SETTINGS_FILE, SETTINGS_STRUCTURE, SETTINGS_DICT

GAME_PATH = ''
WORLDBUILDER_PATH = ''
LOG_PATH = ''
MODS_FOLDER = ''
BACKUP_FOLDER = ''
EXCEPTION_FOLDERS = []
MOD_TEMPLATE = ''


def check_settings(mode='lines'):
    """
    Checks the parameters of the SETTINGS_FILE against any deviations from the hardcoded form of the settings.ini
    :return: a list of lines being the split SETTINGS_FILE if it is correct or being valueless if incorrect
    """
    settings_dict = {}
    structure_keys = []
    structure_containers = []
    structure_lines = SETTINGS_STRUCTURE.split('\n')
    for structure_line in structure_lines:
        if ' =' in structure_line:
            structure_keys.append(structure_line.strip().split(' =')[0])
        elif (structure_line.strip() != 'Settings' and structure_line.strip() not in INI_ENDS
              and len(structure_line.strip()) > 1):
            if structure_line.strip()[0] not in [_[0] for _ in INI_COMMENTS]:
                structure_containers.append(structure_line.strip())
    try:
        container_open = False
        container_name = ''
        with open(SETTINGS_FILE) as settings_file:
            settings_lines = settings_file.readlines()
        structure_keys_copy = structure_keys.copy()
        for line in settings_lines:
            if ' = ' in line:
                key, value = line.strip().split(' = ')
                if key not in structure_keys:
                    print(f'unrecognized key: {key}')
                    raise FileNotFoundError
                else:
                    try:
                        structure_keys_copy.remove(key)
                    except ValueError:
                        pass
                    if container_open:
                        settings_dict[container_name].append(value)
                    else:
                        settings_dict[key] = value
            elif line.strip() in INI_ENDS:
                container_open = False
            elif line.strip()[0] in [_[0] for _ in INI_COMMENTS]:
                settings_dict['comment'] = line.rstrip()
            elif line.strip() != 'Settings' and line.strip() in structure_containers:
                container_name = line.strip()
                container_open = True
                settings_dict[container_name] = []
            else:
                pass
        for missing_key in structure_keys_copy:
            print(f'missing key: {missing_key}')
    except FileNotFoundError:
        # with open(SETTINGS_FILE, 'w') as settings_file_new:
        #     settings_file_new.write(SETTINGS_STRUCTURE)
        settings_lines = structure_lines
        settings_dict = SETTINGS_DICT
    if mode == 'lines':
        return settings_lines
    else:
        return settings_dict


# print(check_settings())


def read_settings():
    """
    returns a dictionary of settings read from the SETTING_FILE
    :return:
    """
    # settings = {}
    # # with open(SETTINGS_FILE) as settings_file:
    # #     settings_lines = settings_file.readlines()
    # settings_lines = check_settings()
    # container_name = ''
    # container_open = False
    # for line in settings_lines:
    #     if ' = ' in line:
    #         set_key, set_value = line.strip().split(' = ')
    #         if not container_open:
    #             settings[set_key] = set_value
    #         else:
    #             settings[container_name].append(set_value)
    #     elif line.strip() not in INI_ENDS and line.strip() != 'Settings':
    #         container_name = line.strip()
    #         container_open = True
    #         settings[container_name] = []
    #     elif line.strip() in INI_ENDS:
    #         container_open = False
    #     # else:
    #     #     pass
    settings = check_settings(mode='dict')
    return settings


def load_settings():
    """ composes the variables used by the programs functions out of the read settings.

    The sensitivity of the hardcoded values is most probably the biggest weakness of the program."""
    global GAME_PATH, WORLDBUILDER_PATH, MODS_FOLDER, BACKUP_FOLDER, EXCEPTION_FOLDERS, MOD_TEMPLATE, LOG_PATH
    settings = read_settings()
    GAME_PATH = '/'.join((settings['installation_path'], settings['RotWK_folder_name'], settings['game_to_launch']))
    WORLDBUILDER_PATH = '/'.join((settings['installation_path'], settings['editor_to_launch']))
    MODS_FOLDER = '/'.join((settings['installation_path'], settings['mods_folder']))
    BACKUP_FOLDER = '/'.join((settings['installation_path'], settings['backup_folder']))
    EXCEPTION_FOLDERS.clear()
    for folder in settings['mods_folder_exceptions']:
        EXCEPTION_FOLDERS.append(folder)
    for folder in settings['mods_templates']:
        EXCEPTION_FOLDERS.append(folder)
    MOD_TEMPLATE = '/'.join((MODS_FOLDER, settings['mods_templates'][0]))
    LOG_PATH = settings['LotM_log_folder']
    return GAME_PATH, WORLDBUILDER_PATH, MODS_FOLDER, BACKUP_FOLDER, EXCEPTION_FOLDERS, MOD_TEMPLATE, LOG_PATH


load_settings()


def save_settings(dictionary_settings=None, **keyword_settings):
    """
    Saves the values provided (inserted in the application) to the SETTING_FILE.
    Then it checks if the new settings are valid. If not, retrieves the previous settings.
    :param dictionary_settings: settings organized in a dictionary
    :param keyword_settings: settings as key-word arguments-values pairs
    :return: string sentence about success or failure to find the paths provided
    """
    if not keyword_settings and dictionary_settings is not None:
        keyword_settings = dictionary_settings
    settings = read_settings()
    settings_lines = check_settings()
    with open(SETTINGS_FILE.replace('.ini', '_copy.ini'), 'w') as settings_file_copy:
        settings_file_copy.write(''.join(settings_lines))
    settings_new_content = ''
    container_name = ''
    container_open = False
    container_counter = 0
    for line in settings_lines:
        if '=' in line:
            key, value = line.strip().split(' = ')
            if key in keyword_settings and not container_open:
                settings_new_content += line.replace(value, keyword_settings[key])
            elif container_open and container_name in keyword_settings:
                if container_counter + 1 == len(settings[container_name]):
                    for setting_value in keyword_settings[container_name]:
                        settings_new_content += line.replace(value, setting_value)
                container_counter += 1
            else:
                settings_new_content += line
        elif line.strip() in INI_ENDS:
            settings_new_content += line
            container_open = False
        elif line.strip() != 'Settings':
            settings_new_content += line
            container_open = True
            container_name = line.strip()
            container_counter = 0
        else:
            settings_new_content += line
    with open(SETTINGS_FILE, 'w') as settings_file:
        settings_file.write(settings_new_content)
    save_file = True
    check_paths = load_settings()
    for path in check_paths:
        try:
            if not os.path.exists(path) and save_file:
                if not os.path.exists(os.path.abspath(path)):
                    if not os.path.exists(path.split()[0]):
                        save_file = False
        except TypeError:
            for folder in path:
                if not os.path.exists(f'{MODS_FOLDER}/{folder}'):
                    save_file = False
                    break
    if not save_file:
        with open(SETTINGS_FILE.replace('.ini', '_copy.ini'), 'r') as settings_file_copy:
            settings_content = settings_file_copy.read()
            with open(SETTINGS_FILE, 'w') as settings_file:
                settings_file.write(settings_content)
        return 'settings_editor.save_settings error: the provided value seems to be incorrect'
    else:
        return 'settings saved and checked.'


# print(save_settings(mods_templates=['__empty base']))  # , 'yes', 'AotR8-INI_backup'
