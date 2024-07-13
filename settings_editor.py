import os.path

INI_ENDS = ['End', 'END', 'EndScript']
SETTINGS_FILE = 'LotM_settings.ini'

GAME_PATH = ''
WORLDBUILDER_PATH = ''
LOG_PATH = ''
MODS_FOLDER = ''
BACKUP_FOLDER = ''
EXCEPTION_FOLDERS = []
MOD_TEMPLATE = ''


def read_settings():
    """ returns a dictionary of settings read from the SETTING_FILE"""
    settings = {}
    with open(SETTINGS_FILE) as settings_file:
        settings_lines = settings_file.readlines()
    container_name = ''
    container_open = False
    for line in settings_lines:
        if '=' in line:
            set_key, set_value = line.strip().split(' = ')
            if not container_open:
                settings[set_key] = set_value
            else:
                settings[container_name].append(set_value)
        elif line.strip() not in INI_ENDS and line.strip() != 'Settings':
            container_name = line.strip()
            container_open = True
            settings[container_name] = []
        elif line.strip() in INI_ENDS:
            container_open = False
        # else:
        #     pass
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


def save_settings(dictionary_settings=None, **keyword_settings):
    """
    reads values inserted in the application and saves them to the SETTING_FILE.
    Then it checks if the new settings are valid. If not retrieves the previous settings.
    :param dictionary_settings:
    :param keyword_settings:
    :return: string sentence about success or failure to find the paths provided
    """
    if not keyword_settings and dictionary_settings is not None:
        keyword_settings = dictionary_settings
    settings = read_settings()
    with open(SETTINGS_FILE, 'r') as settings_file:
        settings_lines = settings_file.readlines()
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
