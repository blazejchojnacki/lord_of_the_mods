import os.path
import tkinter
import _tkinter
from tkinter.messagebox import askquestion
from tkinter.simpledialog import askstring
from tkinter.filedialog import askopenfilename, askopenfilenames, askdirectory
from tkinter.ttk import Treeview
from tklinenums import TkLineNumbers

from constants import INI_COMMENTS, LEVEL_INDENT, PROGRAM_NAME, ModuleError, UnderTestWarning  # MOD_PARAMETERS,
from settings_editor import read_settings, save_settings, GAME_PATH, WORLDBUILDER_PATH, MODULES_LIBRARY
from file_editor import convert_string, find_text, replace_text, move_file, duplicates_commenter, load_file, \
    load_directories
from module_control import module_attach, module_reverse, modules_filter, analyse_modules, snapshot_make, \
    snapshot_compare, read_definition, edit_definition, module_detect_changes, module_copy, DEFINITION_DICT

versioned_game = ['BfME2', 'RotWK', 'AotR8']

FONT = ('Lato', 11, 'normal')
BACKGROUND_COLOR = '#2e4a60'
ENTRY_BACKGROUND_COLOR = '#253B4D'
TEXT_COLORS = ['#A8E3F5', '#6BAACE', '#5285AB', '#253B4D']
INI_LEVELS_COLORS = ['#6BAACE', '#7E5FAB', '#AB5A5B', '#AB9061', '#95AB74']

UNIT_WIDTH = 80
UNIT_HEIGHT = 40
TEXT_WIDTH = UNIT_WIDTH * 12
FULL_WIDTH = UNIT_WIDTH * 15
LIST_WIDTH = 160

settings = read_settings()
mods = []
current_path = ''
current_levels = []
current_file_content_backup = ''
current_window = ''
new_mod_name = ''


class ColumnedListbox(tkinter.ttk.Treeview):
    """ a tk class based on Treeview to make a list with columns"""

    def __init__(self, master, width, height, show='headings'):  # , **kw
        super().__init__(master=master, height=height, show=show)
        self.width = width * 6
        self.columns_list = ("name", "progress", "ancestor", "description")
        self.build_list()
        self.set_columns_proportions(proportions=(2, 1, 2, 7))

    def build_list(self):
        self.configure(columns=self.columns_list)
        for column in self.columns_list:
            self.heading(column, text=column)

    def set_columns_proportions(self, proportions):
        total_quotient = sum(proportions)
        for column_index in range(len(proportions)):
            self.column(
                self.columns_list[column_index],
                width=int(self.width / total_quotient * proportions[column_index])
            )
            if column_index == len(proportions) - 1:
                self.column(
                    self.columns_list[column_index],
                    width=int(self.width / total_quotient * proportions[column_index]) - 5
                )


def launch_game():
    """ launches the application provided in the GAME_PATH """
    set_log_update('launching the game - edition halted')
    os.system(GAME_PATH)


def launch_game_editor():
    """ launches the application provided in the WORLDBUILDER_PATH"""
    set_log_update('launching Worldbuilder - edition halted')
    os.system(WORLDBUILDER_PATH)


def warning_file_save():
    """ checks if the edited file have been edited since the previous saving and generates a window if not """
    file_named = text_file_select.get('1.0', 'end').replace('/', '\\').strip('\n\t {}')
    if file_named and current_file_content_backup:
        if text_file_content.get('1.0', 'end').strip() != current_file_content_backup.strip():
            save_file = tkinter.messagebox.askquestion("Question", "Do you want to save the file?")
            if save_file == 'yes':
                command_file_save()


def on_app_close():
    set_log_update('closing application')
    warning_file_save()
    main_window.quit()


def clear_window():
    """ deletes all the containers of the current feature used """
    global current_file_content_backup, current_window
    warning_file_save()
    current_file_content_backup = ''
    current_window = ''
    retrieve(container_browser, container_mods, container_mod_editor, container_find, container_replace,
             container_folder_select, container_select_file, container_file_content, container_settings,
             container_version)


def set_window_controller():
    global current_window
    clear_window()
    container_function_selected.place_configure(height=UNIT_HEIGHT * 13)
    container_command_buttons.place_configure(y=UNIT_HEIGHT * 2)
    position(container_version, container_command)
    retrieve(button_menu_back, button_run)
    current_window = 'version_control'
    set_log_update('version control feature loaded')


def set_window_find():
    """ loads the widget containers related to the find_text function """
    global key_to_command_current, current_window
    key_to_command_current = key_to_command_text.copy()
    clear_window()
    container_function_selected.place_configure(height=UNIT_HEIGHT * 10)
    text_file_content.place_configure(height=UNIT_HEIGHT * 5)
    container_command.place_configure(height=UNIT_HEIGHT * 5)
    container_command_buttons.place_configure(y=UNIT_HEIGHT * 5)
    text_result.place_configure(height=UNIT_HEIGHT * 4)
    position(container_file_content, container_select_file, container_find, button_function_replace)
    container_file_content.place_configure(height=UNIT_HEIGHT * 5)
    container_select_file.place_configure(y=int(UNIT_HEIGHT * 5.5))
    button_menu_back.config(command=set_window_file)
    retrieve(button_function_find)
    try:
        selection = convert_string(text_file_content.selection_get(), direction='display')
        text_find.delete('1.0', 'end')
        text_find.insert('1.0', selection)
    except UnboundLocalError:
        print('set_window_find error: UnboundLocalError')
    except _tkinter.TclError:
        print('set_window_find warning: no text selected')
    button_run.configure(text='find text', command=command_run_find)
    button_execute.configure(text='clear logs', command=set_log_update)
    command_run_find()
    text_result.focus()
    current_window = 'text_find'
    set_log_update('find feature loaded')


def set_window_replace():
    """ loads the widget containers related to the replace_text function """
    global key_to_command_current, current_window
    key_to_command_current = key_to_command_text.copy()
    clear_window()
    text_file_content.place_configure(height=UNIT_HEIGHT * 5)
    container_function_selected.place_configure(height=UNIT_HEIGHT * 11)
    container_command.place_configure(height=UNIT_HEIGHT * 4)
    container_command_buttons.place_configure(y=UNIT_HEIGHT * 4)
    text_result.place_configure(height=UNIT_HEIGHT * 3)
    position(container_file_content, container_select_file, container_find, container_replace,
             button_function_find)
    container_file_content.place_configure(height=UNIT_HEIGHT * 5)
    container_select_file.place_configure(y=int(UNIT_HEIGHT * 5.5))
    retrieve(button_function_replace)
    try:
        selection = convert_string(text_file_content.selection_get(), direction='display')
        text_find.delete('1.0', 'end')
        text_find.insert('1.0', selection)
    except UnboundLocalError:
        print('set_window_find error: UnboundLocalError')
    except _tkinter.TclError:
        print('set_window_find warning: no text selected')
    button_menu_back.config(command=set_window_file)
    button_run.configure(text="replace text", command=command_run_replace)
    button_run.focus()
    button_execute.configure(text='clear logs', command=set_log_update)
    current_window = 'text_replace'
    set_log_update('replace feature loaded')


def set_window_duplicates():
    """ loads the widget containers related to the comment_out_duplicates function """
    global key_to_command_current, current_window
    key_to_command_current = key_to_command_text.copy()
    clear_window()
    container_function_selected.place_configure(height=UNIT_HEIGHT * 9)
    text_file_content.place_configure(height=UNIT_HEIGHT * 5)
    position(container_file_content, container_select_file)
    try:
        if os.path.isdir(current_path):
            selected_file = f"{label_browser.cget('text')}/{listbox_browser.selection_get()}"
        else:
            selected_file = current_path
        text_file_select.delete('1.0', 'end')
        text_file_select.insert('1.0', selected_file)
    except _tkinter.TclError:
        print('set_window_duplicates error: _tkinter.TclError')
    if os.path.isdir(current_path):
        button_menu_back.configure(command=set_window_browser)
    else:
        button_menu_back.configure(command=set_window_file)
    command_file_load()
    button_run.configure(text='remove duplicates', command=command_run_duplicate)
    button_run.focus()
    button_execute.configure(text='clear logs', command=set_log_update)
    current_window = 'duplicates'
    set_log_update(f'remove duplicates feature loaded. file: {current_path}')


def set_window_move():
    """ loads the widget containers related to the move file function """
    global key_to_command_current, current_path, current_window
    key_to_command_current = key_to_command_text.copy()
    clear_window()
    container_function_selected.place_configure(height=UNIT_HEIGHT * 5)
    container_command.place_configure(height=UNIT_HEIGHT * 10)
    container_command_buttons.place_configure(y=UNIT_HEIGHT * 10)
    text_result.place_configure(height=UNIT_HEIGHT * 9)
    position(container_select_file, container_folder_select)
    # retrieve(button_function_duplicate)
    current_path = f'{label_browser.cget("text")}/{listbox_browser.selection_get()}'
    button_menu_back.configure(command=command_browser_back)
    label_file_select.configure(text='file')
    text_file_select.delete('1.0', 'end')
    text_file_select.insert('1.0', f'{label_browser.cget("text")}/{listbox_browser.selection_get()}')
    label_folder_select.configure(text='to folder')
    button_run.configure(text='move the file', command=command_run_move)
    button_run.focus()
    button_execute.configure(text='clear logs', command=set_log_update)
    current_window = 'file_move'
    set_log_update(f'move feature loaded. file: {current_path}')


def set_window_file():
    """ loads the widget containers related to the file editor """
    global key_to_command_current, current_window
    clear_window()
    key_to_command_current = key_to_command_text.copy()
    container_function_selected.place_configure(height=UNIT_HEIGHT * 13)
    text_file_content.place_configure(height=UNIT_HEIGHT * 12)
    container_command.place_configure(height=UNIT_HEIGHT * 2)
    container_command_buttons.place_configure(y=UNIT_HEIGHT * 2)
    text_result.place_configure(height=UNIT_HEIGHT * 1)
    button_menu_back.config(command=command_browser_back)
    position(container_file_content, button_run, button_function_find,
             button_function_replace, button_execute)  # , button_function_duplicate
    text_file_content.focus()
    text_result.configure(height=1)
    button_run.configure(text='save file', command=command_file_save, state='normal')
    button_execute.configure(text='reload file', command=command_file_load)
    current_window = 'file_editor'
    set_log_update(f'file editor loaded. file {current_path}')


def set_window_mods():
    """ loads the widget containers related to the managing of mods """
    global key_to_command_current, current_window
    key_to_command_current = key_to_command_mod.copy()
    clear_window()
    container_function_selected.place_configure(height=UNIT_HEIGHT * 13)
    position(container_mods, button_mod_new, container_command, button_execute, button_menu_settings)
    retrieve(button_menu_back, button_mod_copy, button_mod_edit, button_function_find, button_function_replace)
    # ,button_function_duplicate
    refresh_definitions()
    listbox_mods_idle.focus_set()
    try:
        listbox_mods_idle.selection_set(listbox_mods_idle.get_children()[0])
        listbox_mods_idle.focus(listbox_mods_idle.get_children()[0])
    except IndexError:
        pass
    text_result.configure(state='disabled')
    button_run.configure(text='launch game', command=launch_game)
    button_execute.configure(text='launch Worldbuilder', command=launch_game_editor)
    button_menu_settings.configure(text='edit settings', command=set_window_settings)
    button_menu_mods.configure(text='refresh mods')
    button_mod_new.configure(state='normal')
    current_window = 'mods'
    set_log_update('mod manager window loaded.')


def set_window_definition():
    """ loads the widget containers related to the modification of mod parameters """
    global key_to_command_current, current_window
    key_to_command_current = key_to_command_text.copy()
    clear_window()
    position(container_mod_editor, button_menu_back)
    retrieve(button_menu_settings, button_menu_back, button_execute)
    button_menu_back.configure(command=set_window_mods)
    button_run.configure(text='save parameters', command=command_definition_save)
    button_menu_mods.configure(text='return to mods')
    mod_selected = current_path.split('/')[-1]
    for mod in mods:
        if mod_selected == mod['name']:
            level = 0
            for param in DEFINITION_DICT:
                if param == 'comment':
                    continue
                elif param == 'changes':
                    # TODO: reformat the changes into a listbox
                    continue
                list_text_mod_editor[level].configure(state='normal')
                list_text_mod_editor[level].delete('1.0', 'end')
                if mod[param] is bool:
                    list_text_mod_editor[level].insert('end', str(mod[param]))
                else:
                    list_text_mod_editor[level].insert('end', mod[param])
                if 'active' in param or param == 'path':
                    list_text_mod_editor[level].configure(state='disabled')
                level += 1
    set_log_update('mod definition edition feature loaded.')
    current_window = 'mods_editor'


def set_window_browser():
    """ loads the widget containers related to the browsing of mods directories """
    global key_to_command_current, current_window
    key_to_command_current = key_to_command_browser.copy()
    clear_window()
    container_function_selected.place_configure(height=UNIT_HEIGHT * 13)
    container_command.place_configure(height=UNIT_HEIGHT * 2)
    container_command_buttons.place_configure(y=UNIT_HEIGHT * 2)
    text_result.place_configure(height=UNIT_HEIGHT)
    position(container_browser)
    retrieve(button_mod_new, button_function_find, button_function_replace, button_menu_settings)
    button_run.configure(text='open', command=command_browser_forward)
    button_execute.configure(text='move file', command=set_window_move)
    open_browser_item()
    button_menu_back.config(command=command_browser_back)
    listbox_browser.focus()
    current_window = 'browser'
    set_log_update(f'files browser loaded. mod {current_path}')


def set_window_settings():
    """ loads the widget containers related to the settings edition """
    global key_to_command_current, current_window
    key_to_command_current = key_to_command_text.copy()
    clear_window()
    position(container_settings)
    button_menu_settings.configure(text='save settings', command=command_settings_save)
    button_menu_mods.configure(text='return to mods')
    current_window = 'settings'
    set_log_update('settings edition feature loaded')


def command_settings_save():
    """ reads the values inserted in the application and orders it to save them to the SETTINGS_FILE """
    counter = 0
    setting_value = []
    new_settings = {}
    for entry_setting in list_entry_settings:
        setting_value.append(entry_setting.get())
    for setting_key in settings:
        if setting_key == 'comment':
            continue
        if settings[setting_key] != setting_value[counter]:
            # TODO: change those keys
            if setting_key == 'mods_folder_exceptions' or setting_key == 'mods_templates':
                new_settings[setting_key] = setting_value[counter].split(', ')
            else:
                new_settings[setting_key] = setting_value[counter]
        counter += 1
    if new_settings:
        output = save_settings(new_settings)
        set_log_update(output)
    # settings_reload()


def command_settings_reload():
    """ reads the settings from the SETTINGS_FILE and inserts them into the application """
    global settings
    settings = read_settings()
    counter = 0
    for setting_key in settings:
        if setting_key == 'comment':
            continue
        list_entry_settings[counter].delete('0', 'end')
        if setting_key == 'mods_folder_exceptions' or setting_key == 'mods_templates':
            list_entry_settings[counter].insert('end', ', '.join(settings[setting_key]))
        else:
            list_entry_settings[counter].insert('end', settings[setting_key])
        counter += 1
    set_log_update('settings reloaded')


def command_select_folder():
    """ launches a window for selecting a folder and pastes it into the application """
    selected_folder = askdirectory(title=f'{PROGRAM_NAME}: select a folder')
    text_folder_select.delete('1.0', 'end')
    text_folder_select.insert('end', selected_folder)
    set_log_update(f'folder {selected_folder} selected')


def command_select_file():
    """ launches a window for selecting one or more file(s) and pastes it into the application """
    selected_files = askopenfilenames(title=f'{PROGRAM_NAME}: select files')
    if selected_files:
        text_file_select.delete('1.0', 'end')
        text_file_select.insert('end', str(selected_files))
    set_log_update(f'file(s) {selected_files} selected')


def set_text_color(event=None):
    """ provides colors to elements of an edited text file that are defined as its delimiters"""
    if event:
        pass
    level_colors = INI_LEVELS_COLORS
    text_lines = text_file_content.get('1.0', 'end').split('\n')
    for line in text_lines:
        words = line.split()
        for word in words:
            for level in current_levels:
                if len(word.strip()) > 0:
                    if word.strip() in level:
                        index_beg = f'{text_lines.index(line) + 1}.{line.index(word)}'
                        index_end = f'{text_lines.index(line) + 1}.end'
                        text_file_content.tag_add(f"{word}", index_beg, index_end)
                        text_file_content.tag_config(f"{word}",
                                                     foreground=level_colors[current_levels.index(level)])
                    elif word.strip()[0] in INI_COMMENTS:
                        index_beg = f'{text_lines.index(line) + 1}.{line.index(word)}'
                        index_end = f'{text_lines.index(line) + 1}.end'
                        text_file_content.tag_add('comment', index_beg, index_end)
                        text_file_content.tag_config('comment', foreground='grey')
                        text_file_content.tag_raise('comment')


def command_text_comment():
    """   """
    text_to_comment = ''
    try:
        text_to_comment += text_file_content.get('insert linestart', 'sel.last lineend')
    except _tkinter.TclError:
        text_to_comment += text_file_content.get('insert linestart', 'insert lineend')
        text_file_content.tag_add('sel', 'insert linestart', 'insert lineend')
    lines_to_comment = text_to_comment.split('\n')
    text_commented = ''
    for line in lines_to_comment:
        for level in range(6):
            if line.startswith(LEVEL_INDENT * (6 - level)):
                text_commented += f'{LEVEL_INDENT * (6 - level)}; {line.strip()}\n'
                break
    text_file_content.replace('sel.first linestart', 'sel.last lineend + 1 chars', text_commented)
    set_text_color()
    set_log_update('selected text has been commented out')


def command_text_uncomment():
    """   """
    text_to_comment = ''
    try:
        text_to_comment += text_file_content.get('insert linestart', 'sel.last lineend')
    except _tkinter.TclError:
        text_file_content.tag_add('sel', 'insert linestart', 'insert lineend')
        text_to_comment += text_file_content.get('insert linestart', 'insert lineend')
    lines_to_comment = text_to_comment.split('\n')
    text_commented = ''
    for line in lines_to_comment:
        for level in range(6):
            if line.startswith(LEVEL_INDENT * (6 - level)):
                text_commented += f"{LEVEL_INDENT * (6 - level)}{line.strip()[len('; '):]}\n"
                break
    text_file_content.replace('sel.first linestart', 'sel.last lineend + 1 chars', text_commented)
    set_text_color()
    set_log_update('selected text has been uncommented')


def command_file_load():
    """ loads the file selected into the application and saves its backup """
    global current_levels, current_file_content_backup
    text_file_content.delete('1.0', 'end')
    file_loaded = text_file_select.get('1.0', 'end').replace('/', '\\').strip('\n\t {}')
    try:
        current_file_content_backup, current_levels = load_file(full_path=file_loaded)
    except TypeError:
        set_log_update('cannot open this file type')
    text_file_content.insert('end', current_file_content_backup)
    set_text_color()
    set_log_update(f'file {file_loaded} loaded successfully')


def command_file_save():
    """ saves the text edited in the application back into its origin file """
    global current_file_content_backup
    content_to_save = text_file_content.get('1.0', 'end')
    file_named = text_file_select.get('1.0', 'end').replace('/', '\\').strip().replace('{', '').replace('}', '')
    with open(file_named, 'w') as file_overwritten:
        file_overwritten.write(content_to_save)
    set_log_update(f'file {file_named} saved')


def command_copy_find():
    """ copies the string to find into the field of the string to replace it with"""
    find = text_find.get('1.0', 'end').strip()
    text_replace.delete('1.0', "end")
    text_replace.insert('1.0', find)


def command_run_find():
    """ runs the find_text function """
    find = convert_string(text_find.get('1.0', 'end').strip(), direction='display')
    in_file = text_file_select.get('1.0', 'end').replace('/', '\\').strip()
    output = find_text(find, in_file)
    set_log_update(output)


def command_run_replace():
    """ runs the replace_text function """
    find = convert_string(text_find.get('1.0', 'end').strip(), direction='display')
    replace_with = convert_string(text_replace.get('1.0', 'end').strip(), direction='display')
    in_file = text_file_select.get('1.0', 'end').replace('/', '\\').strip()
    output = replace_text(find, replace_with, in_file)
    set_log_update(output)
    text_file_content.delete('1.0', 'end')
    text_file_content.insert('end', load_file(in_file)[0])
    set_text_color()


def command_run_move():
    """ runs the move_file function """
    files_named = text_file_select.get('1.0', 'end').replace('/', '\\').strip()
    to_folder = text_folder_select.get('1.0', 'end').replace('/', '\\').strip()
    output = ''
    for file_named in files_named.split('} {'):
        file_named = file_named.replace('{', '').replace('}', '')
        output += move_file(file_named, to_folder)
        print(output)
    set_log_update(output)


def command_run_duplicate():
    """ runs the duplicates_commenter function """
    file_named = text_file_select.get('1.0', 'end').replace('/', '\\').strip()
    output = duplicates_commenter(in_file=file_named)
    set_log_update(output)


def command_definition_save():
    """ edits the current mod parameters"""
    output = 'mod data edition failed'
    mod_selected = current_path.split('/')[-1]
    for mod in mods:
        if mod_selected == mod['name']:
            edited_parameters = {}
            expected_definition = mod
            level = 0
            for param in DEFINITION_DICT:
                if param == 'comment':
                    continue
                elif param == 'changes':
                    # TODO: reformat the changes
                    continue
                value = list_text_mod_editor[level].get('1.0', 'end').strip()
                if value != mod[param]:
                    edited_parameters[param] = value
                    expected_definition[param] = value
                level += 1
            new_definition = edit_definition(mod, **edited_parameters)
            if new_definition == expected_definition:
                output = 'new definition saved'
            break
    set_log_update(output)


def selected_mod_idle(event):
    """ on select of a value in the non-active mods, activates and deactivates the appropriate buttons"""
    global current_path, key_to_command_current
    if event:
        pass
    try:
        current_path = f"{MODULES_LIBRARY}/{listbox_mods_idle.item(listbox_mods_idle.selection()[0], 'values')[0]}"
        listbox_mods_active.selection_remove(listbox_mods_active.selection()[0])
        # selection_remove is a selection event steeling focus to the other list
        listbox_mods_idle.selection_set(listbox_mods_idle.selection()[0])
    except IndexError:
        pass
    key_to_command_current['<Return>'] = command_mod_open
    position(button_mod_activate, button_mod_open, button_mod_copy, button_mod_edit)
    retrieve(button_mod_deactivate, button_mod_reload)
    listbox_mods_idle.focus()


def selected_mod_active(event):
    """ on select of a value in the active mods, activates and deactivates the appropriate buttons"""
    global current_path, key_to_command_current
    if event:
        pass
    try:
        current_path = f"{MODULES_LIBRARY}/{listbox_mods_active.item(listbox_mods_active.selection()[0], 'values')[0]}"
        listbox_mods_idle.selection_remove(listbox_mods_idle.selection()[0])
        # selection_remove is a selection event steeling focus to the other list
        listbox_mods_active.selection_set(listbox_mods_active.selection()[0])
    except IndexError:
        pass
    key_to_command_current['<Return>'] = command_mod_open
    position(button_mod_deactivate, button_mod_reload, button_mod_open, button_mod_copy, button_mod_edit)
    retrieve(button_mod_activate)


def refresh_definitions():
    """ refreshes the lists of active and non-active mods """
    # TODO: sort modules in order of activation / by heir / ancestor
    global mods
    set_log_update('refreshing definitions...')
    mods = modules_filter('all', 'definitions')
    # mods.clear()
    # all_modules = modules_filter(strict=False)
    # for module_name in all_modules:
    #     mods.append(read_definition(module_path=f'{MODULES_LIBRARY}/{module_name}').copy())
    listbox_mods_active.delete(*listbox_mods_active.get_children())
    list_active_index = 0
    listbox_mods_idle.delete(*listbox_mods_idle.get_children())
    list_idle_index = 0
    for mod in mods:
        if mod['active'] is True:
            listbox_mods_active.insert(parent='', index=list_active_index, values=(
                mod['name'], mod['progress'], mod['ancestor'], mod['description']
            ))
            list_active_index += 1
        elif mod['active'] is False:
            listbox_mods_idle.insert(parent='', index=list_idle_index, values=(
                mod['name'], mod['progress'],
                mod['ancestor'], mod['description']
            ))
            list_idle_index += 1
        else:
            # TODO: definition error
            pass
    retrieve(button_mod_deactivate, button_mod_activate)
    set_log_update('module definitions refreshed')


def command_mod_new():
    """ initiates the creation of a new mod """
    global new_mod_name
    first_run = True
    while new_mod_name in [mod['name'] for mod in mods] or first_run:
        message = 'provide a name unique to the new mod'
        if first_run:
            message = 'provide the new mod name'
        new_mod_name = tkinter.simpledialog.askstring(title='new mod name', prompt=message)
        first_run = False
        # ISSUE: askstring window loses focus on second run
    if new_mod_name:
        set_log_update(module_copy(new_mod_name))
        refresh_definitions()
    else:
        set_log_update('command_new_mod error: a correct unique name was not provided')
    new_mod_name = ''


def command_mod_copy():
    """ initiates the copy of the selected mod """
    mod_selected = current_path
    name = mod_selected.split('/')[-1] + '_copy'
    set_log_update(module_copy(name, mod_selected))
    refresh_definitions()


def command_mod_activate():
    # TODO: if the module overrides another, ask if save it as ancestor / heir
    """ initiates the activation of the selected mod """
    global mods
    try:
        mod_selected = listbox_mods_idle.item(listbox_mods_idle.focus(), 'values')[0]
        set_log_update(f"loading mod {mod_selected} ...")
        for mod in mods:
            if mod['name'] == mod_selected:
                if mod['class'] == 'Version':
                    module_attach(mod['path'])  # , transfer='move'
                elif mod['class'] == 'Module':
                    module_attach(mod['path'])
                edit_definition(mod, active=True)
                set_log_update(f"mod {mod_selected} loaded")
                return refresh_definitions()
        set_log_update(f"command_module_attach error: mod {mod_selected} not found")
    except _tkinter.TclError:
        set_log_update("command_module_attach warning: TclError")
    except ModuleError as err:
        set_log_update(err.message)
    except UnderTestWarning as err:
        set_log_update(err.message)


def command_mod_deactivate():
    """ initiates the deactivation of the selected mod """
    global mods
    try:
        mod_selected = listbox_mods_active.item(listbox_mods_active.focus(), 'values')[0]
        set_log_update(f"unloading mod {mod_selected} ...")
        for mod in mods:
            if mod['name'] == mod_selected:
                changes = module_detect_changes(module_directory=mod['path'])
                if changes:
                    keep_changes = tkinter.messagebox.askyesnocancel(
                        title=f'{PROGRAM_NAME}: deactivate mod - question:',
                        message='Files have been changed since the mod activation. Do you wish to save them in the mod?'
                                f'\n{changes}'
                    )
                    if keep_changes is True:
                        # mod.deactivate_mod(exceptions=changes)
                        # TODO: differentiate between changed and unchanged files
                        pass
                    elif keep_changes is False:
                        if mod['class'] == 'Version':
                            module_reverse(mod_name=mod['name'], transfer='move')
                        elif mod['class'] == 'Module':
                            module_reverse(mod_name=mod['name'], transfer='delete')
                    elif keep_changes is None:
                        set_log_update(f"module {mod['name']} deactivation cancelled")
                        return
                else:
                    if mod['class'] == 'Version':
                        module_reverse(mod_name=mod['name'], transfer='move')
                    elif mod['class'] == 'Module':
                        module_reverse(mod_name=mod['name'], transfer='delete')
                edit_definition(mod, active=False)
                refresh_definitions()
                set_log_update(f"module {mod['name']} deactivated")
                return
        set_log_update(f"error command_module_reverse: mod {mod_selected} not found")
    except _tkinter.TclError:
        set_log_update("error command_module_reverse: TclError")
    except ModuleError as err:
        set_log_update(err.message)
    except UnderTestWarning as err:
        set_log_update(err.message)


def command_mod_reload():
    """ initiates the reloading of a mod """
    global mods
    try:
        mod_selected = listbox_mods_active.item(listbox_mods_active.focus(), 'values')[0]
        for mod in mods:
            if mod['name'] == mod_selected:
                mod.reload()
                refresh_definitions()
                return
        set_log_update(f"error command_module_reload: mod {mod_selected} not found")
    except _tkinter.TclError:
        set_log_update("error command_module_reload: TclError")


def command_mod_open(event=None):
    """ """
    global current_path
    if event:
        pass
    if os.path.isdir(f'{current_path}/AotR8/aotr/data/ini/object'):
        current_path += '/AotR8/aotr/data/ini/object'
    else:
        for game_name in versioned_game:
            if os.path.isdir(f'{current_path}/{game_name}/data/ini/object'):
                current_path = f'{current_path}/{game_name}/data/ini/object'
                break
            elif os.path.isdir(f'{current_path}/{game_name}'):
                current_path = f'{current_path}/{game_name}'
    # elif os.path.isdir(f'{current_path}/BfME2/data/ini/object'):
    #     current_path += '/BfME2/data/ini/object'
    # elif os.path.isdir(f'{current_path}/RotWK/data/ini/object'):
    #     current_path += '/BfME2-RotWK/data/ini/object'
    button_menu_mods.configure(text='return to mods')
    set_window_browser()


def command_browser_back():
    """ triggered on browsing back to a previous directory """
    global current_path, key_to_command_current
    set_log_update('browsing directory backwards')
    if current_window == 'text_find' or current_window == 'text_replace':
        set_window_file()
    if len(current_path) > len(MODULES_LIBRARY):
        current_path = current_path[:current_path.rfind('/')]
        if main_window.focus_get() == listbox_browser:
            open_browser_item()
        else:
            set_window_browser()
    if len(current_path) <= len(MODULES_LIBRARY):
        retrieve(button_menu_back)
        # button_menu_back.configure(state='disabled')
        # button_menu_back.place_forget()
        key_to_command_current['<BackSpace>'] = set_window_mods
    key_to_command_current = key_to_command_browser.copy()


def on_select_browser_item(event=None):
    """ triggered on selection of an item in the directory to enable or disable buttons """
    # global current_path
    if event:
        pass
    # if 'file editor loaded' not in text_result.get('1.0', 'end'):
    if current_window != 'file_editor':
        try:
            if os.path.isfile(f'{current_path}/{listbox_browser.selection_get()}'):
                button_run.configure(text='open file')
                position(button_execute)  # , button_function_duplicate
                # button_execute.configure(state='normal')  # button_function_move
                # button_function_duplicate.configure(state='normal')
                # button_execute.place(x=UNIT_WIDTH * 7, y=0, width=UNIT_WIDTH * 2, height=UNIT_HEIGHT)
                # button_function_duplicate.place(x=UNIT_WIDTH * 9, y=0, width=UNIT_WIDTH * 2, height=UNIT_HEIGHT)
            else:
                button_run.configure(text='open folder')
                retrieve(button_execute, button_function_duplicate)
                # button_execute.configure(state='disabled')
                # button_function_duplicate.configure(state='disabled')
                # button_execute.place_forget()
                # button_function_duplicate.place_forget()
        except IndexError:
            # print(current_path)
            button_run.configure(text='open folder')
            retrieve(button_execute, button_function_duplicate)
            # button_execute.configure(state='disabled')
            # button_function_duplicate.configure(state='disabled')
            # button_execute.place_forget()
            # button_function_duplicate.place_forget()


def command_browser_forward(event=None):
    """ gets the selected item in the directory and opens it """
    global current_path
    if event:
        pass
    set_log_update('browsing forward')
    try:
        item_selected = listbox_browser.get(listbox_browser.curselection())
        current_path += f'/{item_selected}'
    except _tkinter.TclError:
        print('error: open_directory_item _tkinter.TclError')
    open_browser_item()


def open_browser_item():  # event=None
    """ opens the selected item in the directory whether it is a folder or a file """
    if os.path.isdir(current_path):
        listbox_browser.delete(0, 'end')
        output_folders, output_files = load_directories(current_path)
        item_index = 0
        for output_folder in output_folders:
            listbox_browser.insert(item_index, output_folder)
            listbox_browser.itemconfig(item_index, foreground=INI_LEVELS_COLORS[1])
            item_index += 1
        for output_file in output_files:
            listbox_browser.insert(item_index, output_file)
            listbox_browser.itemconfig(
                item_index,
                foreground=INI_LEVELS_COLORS[2] if output_file[-len('.ini'):] == '.ini' else INI_LEVELS_COLORS[3]
            )
            item_index += 1
        listbox_browser.activate(0)
        if not output_folders:
            button_run.configure(text='open file')
            position(button_execute)  # , button_function_duplicate
            # button_execute.configure(state='normal')
            # button_function_duplicate.configure(state='normal')
            # button_execute.place(x=UNIT_WIDTH * 7, y=0, width=UNIT_WIDTH * 2, height=UNIT_HEIGHT)
            # button_function_duplicate.place(x=UNIT_WIDTH * 9, y=0, width=UNIT_WIDTH * 2, height=UNIT_HEIGHT)
        else:
            button_run.configure(text='open folder')
            retrieve(button_execute, button_function_duplicate)
            # button_execute.configure(state='disabled')
            # button_execute.place_forget()
            # button_function_duplicate.place_forget()
        listbox_browser.select_set(0)
    elif os.path.isfile(current_path):
        text_file_select.delete('1.0', 'end')
        text_file_select.insert('end', current_path)
        set_window_file()
        command_file_load()
        listbox_browser.selection_clear(listbox_browser.curselection())
        position(button_execute)
        # button_execute.configure(state='normal')
        # button_execute.place(x=UNIT_WIDTH * 7, y=0, width=UNIT_WIDTH * 2, height=UNIT_HEIGHT)
    label_browser.configure(text=current_path)
    position(button_menu_back)
    # button_menu_back.configure(state='normal')
    # button_menu_back.place(x=0, y=0, width=UNIT_WIDTH * 1, height=UNIT_HEIGHT)
    set_log_update('opened selected item')


def focus_on_next_item():
    """ bound to arrow pressing to change between the lists of active and non-active mods """
    if main_window.focus_get() == listbox_mods_idle:
        listbox_mods_idle.selection_remove(listbox_mods_idle.selection())
        listbox_mods_active.focus_set()
        if listbox_mods_active.focus():
            mod_selected = listbox_mods_active.focus()
        elif listbox_mods_active.selection():
            mod_selected = listbox_mods_active.selection()
        elif len(listbox_mods_active.get_children()) > 0:
            mod_selected = listbox_mods_active.get_children()[0]
        else:
            return
        listbox_mods_active.selection_set(mod_selected)
    elif main_window.focus_get() == listbox_mods_active:
        listbox_mods_active.selection_remove(listbox_mods_active.selection())
        listbox_mods_idle.focus_set()
        listbox_mods_idle.selection_set(listbox_mods_idle.focus())
        if listbox_mods_idle.focus():
            mod_selected = listbox_mods_idle.focus()
        elif listbox_mods_idle.selection():
            mod_selected = listbox_mods_idle.selection()
        elif listbox_mods_idle.get_children():
            mod_selected = listbox_mods_idle.get_children()[0]
        else:
            return
        listbox_mods_idle.selection_set(mod_selected)
    elif main_window.focus_get() == listbox_browser:
        # try:
        list_length = len(listbox_browser.get('0', 'end'))
        selected_item_index = listbox_browser.get('0', 'end').index(listbox_browser.selection_get())
        listbox_browser.selection_set((selected_item_index + 1) % list_length)
    else:
        print(main_window.focus_get())


def set_log_update(line=''):
    """ unlocks the result field and inserts the output of a function """
    text_result.configure(state='normal')
    text_result.delete('1.0', 'end')
    text_result.insert('end', line)
    text_result.configure(state='disabled')


def use_selected_text(event=None):
    """ bound to key presses to trigger the appropriate function """
    try:
        if event.keysym == 'f':
            set_window_find()
        elif event.keysym == 'r':
            set_window_replace()
        elif event.keysym == 'slash':
            command_text_comment()
        elif event.keysym == 'backslash':
            command_text_uncomment()
        else:
            print(event.keysym)
    except UnboundLocalError:
        print("error use_selected_text: selection seems empty")


def press_key_in_current_mode(event=None):
    """ attributes the key presses to the currently allowed functions """
    if f'<{event.keysym}>' in key_to_command_current:
        key_to_command_current[f'<{event.keysym}>']()
    else:
        # print(f'<{event.keysym}>')
        pass


def settings_select_new_directory(index_funct):
    list_entry_settings[index_funct].delete(0, 'end')
    added = askdirectory(title=f'{PROGRAM_NAME}: select a new directory')
    if '/' == added[-1]:
        added = added[:-1]
    elif '/' in added:
        added = added.split('/')[-1]
    # else:
    #     pass
    list_entry_settings[index_funct].insert('end', added)


def settings_select_new_file(index_funct):
    list_entry_settings[index_funct].delete(0, 'end')
    added = askopenfilename(title=f'{PROGRAM_NAME}: select a new file').split('/')[-1]
    list_entry_settings[index_funct].insert('end', added)


def settings_select_add_directory(index_funct):
    present = list_entry_settings[index_funct].get()
    if not present:
        added = f"{askdirectory(title=f'{PROGRAM_NAME}: select a new directory').split('/')[-1]}"
    else:
        added = f", {askdirectory(title=f'{PROGRAM_NAME}: select a new directory').split('/')[-1]}"
    list_entry_settings[index_funct].insert('end', added)


def command_snapshot_make():
    set_log_update('generating snapshot - please wait')
    result_path = snapshot_make()
    set_log_update(f'snapshot generated. path: {result_path}')


def command_snapshot_compare():
    set_log_update('generating snapshot comparison - please wait')
    result_path = snapshot_compare(return_type='path')
    set_log_update(f'snapshot comparison generated. path: {result_path}')


version_list_deployed = False
popping_list_placeholder = None


def version_deploy_list(index_funct):
    global version_list_deployed, popping_list_placeholder

    def version_list_follow(event=None):
        if event:
            pass
        main_window.update()
        popping_list_offset_x = UNIT_WIDTH * 5 + 20  # the padding you need.
        popping_list_offset_y = UNIT_HEIGHT * (int(index_funct / 3) * 2 + 2)
        try:
            if popping_list_placeholder:
                popping_list.geometry(
                    f"+{main_window.winfo_x() + popping_list_offset_x}+{main_window.winfo_y() + popping_list_offset_y}"
                )
        except _tkinter.TclError:
            print('version selection aborted: window closed')

    def version_select_directory(event):
        global version_list_deployed, popping_list_placeholder
        if event:
            pass
        try:
            selected_version = version_listbox.selection_get()
            version_controller[index_funct - 1].configure(text=selected_version)
            # popping_list.quit()
            popping_list.destroy()
            version_list_deployed = False
        except _tkinter.TclError:
            print('version_select_directory error: TclError')

    def version_selection_cancel(event=None):
        global version_list_deployed, popping_list_placeholder
        if event:
            pass
        try:
            popping_list_placeholder.destroy()
            version_list_deployed = False
        except NameError:
            pass

    if not version_list_deployed:
        game_name = version_controller[index_funct - 2].cget('text')
        version_list = modules_filter(game_name)
        popping_list = tkinter.Toplevel(master=main_window)
        popping_list_placeholder = popping_list
        popping_list.overrideredirect(True)
        popping_list.attributes('-topmost', True)
        version_listbox = tkinter.Listbox(master=popping_list)
        version_listbox.pack()
        version_list_deployed = True
        version_dict = analyse_modules(version_list)
        for version_name in version_list:
            version_listbox.insert('end', version_name)
            version_listbox.itemconfig('end', foreground='grey' if version_dict[version_name] else 'green')
            # version_index = version_listbox.index('end')
            # if version_dict[version_name]:

        version_listbox.bind('<<ListboxSelect>>', version_select_directory)
        main_window.bind('<Configure>', version_list_follow)
        version_list_follow()
    else:
        version_selection_cancel()


key_to_command_mod = {
    '<Return>': command_browser_forward,
    '<Right>': focus_on_next_item,
    '<Left>': focus_on_next_item,
}
key_to_command_browser = {
    '<Return>': command_browser_forward,
    '<BackSpace>': command_browser_back,
    '<Escape>': set_window_mods,
}
key_to_command_text = {
    '<Escape>': command_browser_back
}
key_to_command_current = {
    '<Return>': set_window_mods,
}

main_window = tkinter.Tk()
main_window.iconbitmap('aesthetic/lotr-icon1.ico')
main_window.title('Lord of the mods')
main_window.minsize(width=1100, height=400)
main_window.maxsize(width=1600, height=900)
main_window.geometry('1250x650')
# main_window.attributes("-alpha", 0.6)
main_window.configure(padx=10, pady=10, background=BACKGROUND_COLOR)
main_window.bind('<Key>', press_key_in_current_mode)
main_window.bind_all('<Control-Key-f>', use_selected_text)
main_window.bind_all('<Control-Key-r>', use_selected_text)
if True:  #
    """https://stackoverflow.com/questions/67444141/how-to-change-the-title-bar-in-tkinter"""
    from ctypes import windll, byref, sizeof, c_int

    main_window.update()
    HWND = windll.user32.GetParent(main_window.winfo_id())
    # This attribute is for Windows 11
    DWMWA_CAPTION_COLOR = 35
    COLOR_1 = 0x004d3b25  # color should be in hex order: 0x00bbggrr
    windll.dwmapi.DwmSetWindowAttribute(HWND, DWMWA_CAPTION_COLOR, byref(c_int(COLOR_1)), sizeof(c_int))

container_command = tkinter.Frame(master=main_window)
container_command_buttons = tkinter.Frame(master=container_command)
button_run = tkinter.Button(master=container_command_buttons)
button_execute = tkinter.Button(master=container_command_buttons, text='clear logs', command=set_log_update)
text_result = tkinter.Text(master=container_command, state='disabled')
button_menu_mods = tkinter.Button(master=container_command_buttons, text='mods', command=set_window_mods)
button_menu_back = tkinter.Button(master=container_command_buttons, text='back')  # , state='disabled'
button_menu_settings = tkinter.Button(master=container_command_buttons, text='edit settings',
                                      command=set_window_settings)

button_function_duplicate = tkinter.Button(master=container_command_buttons, text='remove duplicates',
                                           command=set_window_duplicates)
button_function_find = tkinter.Button(master=container_command_buttons, text='find text',
                                      command=set_window_find)
button_function_replace = tkinter.Button(master=container_command_buttons, text='replace text',
                                         command=set_window_replace)

container_function_selected = tkinter.Frame(master=main_window)

container_version = tkinter.Frame(master=container_function_selected)
container_version_tools = tkinter.Frame(master=container_version)
button_snapshot_make = tkinter.Button(master=container_version_tools, text='make snapshot',
                                      command=command_snapshot_make)
button_snapshot_compare = tkinter.Button(master=container_version_tools, text='compare snapshots',
                                         command=command_snapshot_compare)
version_controller = []
for game_index in range(len(versioned_game)):
    current_version = ''
    versions_dict = analyse_modules(game=versioned_game[game_index])
    for version_key in versions_dict:
        if versions_dict[version_key]:  # and version_key == versioned_game
            current_version = version_key
    # index = versioned_game.index(game)
    version_controller.append(tkinter.Label(master=container_version, text=versioned_game[game_index]))
    version_controller[-1].place(x=UNIT_WIDTH * 3, y=UNIT_HEIGHT * 2 * game_index, width=UNIT_WIDTH * 2,
                                 height=UNIT_HEIGHT)
    version_controller.append(tkinter.Label(master=container_version, text=current_version))
    version_controller[-1].place(x=UNIT_WIDTH * 5, y=UNIT_HEIGHT * 2 * game_index, width=UNIT_WIDTH * 2,
                                 height=UNIT_HEIGHT)
    version_controller.append(tkinter.Button(master=container_version, text='select'))
    version_controller[-1].place(x=UNIT_WIDTH * 7, y=UNIT_HEIGHT * 2 * game_index, width=UNIT_WIDTH * 2,
                                 height=UNIT_HEIGHT)
version_controller[2].configure(command=lambda: version_deploy_list(2))
version_controller[5].configure(command=lambda: version_deploy_list(5))
version_controller[8].configure(command=lambda: version_deploy_list(8))

container_file_content = tkinter.Frame(master=container_function_selected)
text_file_content = tkinter.Text(master=container_file_content, width=TEXT_WIDTH, height=30, undo=True)
numeration = TkLineNumbers(container_file_content, text_file_content, justify='right')
# text_file_content.bind('<KeyPress>', set_text_color)
main_window.event_delete('<<SelectAll>>', '<Control-Key-/>')
text_file_content.bind('<Control-Key-/>', use_selected_text)
text_file_content.bind('<Control-Key-\>', use_selected_text)
text_file_content.bind('<<Modified>>', lambda event: main_window.after_idle(numeration.redraw), add=True)
text_file_content.bind('<<Modified>>', lambda event: main_window.after_idle(set_text_color), add=True)

container_settings = tkinter.Frame(master=container_function_selected)
list_labels_settings = []
list_entry_settings = []
list_buttons_settings = []
for setting in settings:
    if setting == 'comment':
        continue
    list_labels_settings.append(tkinter.Label(master=container_settings, text=setting))
    list_entry_settings.append(tkinter.Entry(master=container_settings))
    list_buttons_settings.append(tkinter.Button(master=container_settings, text='select'))
command_settings_reload()

list_buttons_settings[0].configure(command=lambda: settings_select_new_directory(0))
list_buttons_settings[1].configure(command=lambda: settings_select_new_directory(1))
list_buttons_settings[2].configure(command=lambda: settings_select_new_directory(2))
list_buttons_settings[3].configure(command=lambda: settings_select_new_file(3))
list_buttons_settings[4].configure(command=lambda: settings_select_new_file(4))
list_buttons_settings[5].configure(command=lambda: settings_select_new_directory(5))
list_buttons_settings[6].configure(command=lambda: settings_select_new_directory(6))
list_buttons_settings[7].configure(command=lambda: settings_select_add_directory(7))
list_buttons_settings[8].configure(command=lambda: settings_select_new_directory(8))
list_buttons_settings[9].configure(command=lambda: settings_select_new_directory(9))

container_mods = tkinter.Frame(master=container_function_selected)
label_mods_idle = tkinter.Label(master=container_mods, text='available mods:')  # , width=UNIT_WIDTH * 2
listbox_mods_idle = ColumnedListbox(master=container_mods, width=LIST_WIDTH, height=10)
listbox_mods_idle.bind('<<TreeviewSelect>>', selected_mod_idle)
# TODO: prevent to open game directory when no mod is selected
listbox_mods_idle.bind('<Double-1>', command_mod_open)
container_mod_buttons = tkinter.Frame(master=container_mods, pady=7)
button_mod_activate = tkinter.Button(master=container_mod_buttons, text='activate mod', command=command_mod_activate)
button_mod_deactivate = tkinter.Button(master=container_mod_buttons, text='deactivate mod',
                                       command=command_mod_deactivate)
button_mod_reload = tkinter.Button(master=container_mod_buttons, text='reload mod', command=command_mod_reload)
button_mod_open = tkinter.Button(master=container_mod_buttons, text='open mod', command=command_mod_open)
button_mod_copy = tkinter.Button(master=container_mod_buttons, text='copy mod', command=command_mod_copy)
button_mod_new = tkinter.Button(master=container_mod_buttons, text='new mod', command=command_mod_new)
button_mod_edit = tkinter.Button(master=container_mod_buttons, text='edit mod data', command=set_window_definition)

label_mods_active = tkinter.Label(master=container_mods, text='active mods:', width=UNIT_WIDTH * 2)
listbox_mods_active = ColumnedListbox(master=container_mods, width=LIST_WIDTH, height=10)
listbox_mods_active.bind('<<TreeviewSelect>>', selected_mod_active)
listbox_mods_active.bind('<Double-1>', command_mod_open)

container_mod_editor = tkinter.Frame(master=container_function_selected)
list_labels_mod_editor = []
list_text_mod_editor = []
for key in DEFINITION_DICT:
    if key == 'comment' or key == 'changes':
        continue
    list_labels_mod_editor.append(tkinter.Label(master=container_mod_editor, text=key))
    list_text_mod_editor.append(tkinter.Text(master=container_mod_editor, height=2))

container_browser = tkinter.Frame(master=container_function_selected)
label_browser = tkinter.Label(master=container_browser)
listbox_browser = tkinter.Listbox(master=container_browser, width=LIST_WIDTH, height=20)
listbox_browser.bind('<<ListboxSelect>>', on_select_browser_item)
listbox_browser.bind('<Double-1>', command_browser_forward)

container_select_file = tkinter.Frame(master=container_function_selected)
label_file_select = tkinter.Label(master=container_select_file, text='in file(s):')
button_file_select = tkinter.Button(master=container_select_file, text='select a file',
                                    command=command_select_file)
text_file_select = tkinter.Text(master=container_select_file, width=TEXT_WIDTH, height=3)

container_folder_select = tkinter.Frame(master=container_function_selected)
label_folder_select = tkinter.Label(master=container_folder_select, text='in folder(s):')
button_folder_select = tkinter.Button(master=container_folder_select, text='select a folder',
                                      command=command_select_folder)
text_folder_select = tkinter.Text(master=container_folder_select, height=3)

container_find = tkinter.Frame(master=container_function_selected)
label_find = tkinter.Label(master=container_find, text='find text:')
text_find = tkinter.Text(master=container_find, height=3)

container_replace = tkinter.Frame(master=container_function_selected)
button_replace_copy = tkinter.Button(master=container_replace, text='copy text', command=command_copy_find)
label_replace = tkinter.Label(master=container_replace, text='replace with text:')
text_replace = tkinter.Text(master=container_replace, height=3)

containers = [
    container_function_selected,
    container_settings,
    container_mods,
    container_mod_buttons,
    container_mod_editor,
    container_browser,
    container_file_content,
    container_select_file,
    container_folder_select,
    container_find,
    container_replace,
    container_command,
    container_command_buttons,
    container_version,
    container_version_tools
]
small_buttons = [
    button_menu_back,
]
for button_settings in list_buttons_settings:
    small_buttons.append(button_settings)
large_buttons = [
    button_menu_settings,
    button_mod_activate,
    button_mod_deactivate,
    button_mod_reload,
    button_mod_open,
    button_mod_new,
    button_mod_copy,
    button_mod_edit,
    button_replace_copy,
    button_menu_mods,
    button_file_select,
    button_folder_select,

    button_function_find,
    button_function_replace,
    button_run,
    button_execute,
    button_snapshot_make,
    button_snapshot_compare
]  # button_function_duplicate,
for game_index in range(len(versioned_game)):
    large_buttons.append(version_controller[2 + game_index * 3])
labels = [
    label_mods_idle,
    label_mods_active,
    label_browser,
    label_file_select,
    label_find,
    label_replace,
    label_folder_select
]
for game_index in range(len(versioned_game)):
    labels.append(version_controller[0 + game_index * 3])
    labels.append(version_controller[1 + game_index * 3])
for setting_label in list_labels_settings:
    labels.append(setting_label)
for parameter_label in list_labels_mod_editor:
    labels.append(parameter_label)
texts = [
    text_result,
    text_find,
    text_replace,
    text_file_content,
    text_file_select,
    text_folder_select
]
entries = []
for setting_entry in list_entry_settings:
    entries.append(setting_entry)
for parameter_entry in list_text_mod_editor:
    entries.append(parameter_entry)

for button in small_buttons:
    button.place_configure(width=UNIT_WIDTH, height=UNIT_HEIGHT)
for button in large_buttons:
    button.place_configure(width=UNIT_WIDTH * 2, height=UNIT_HEIGHT)
for label in labels:
    label.place_configure(width=UNIT_WIDTH * 2, height=UNIT_HEIGHT)
label_browser.place_configure(width=TEXT_WIDTH)
for text in texts:
    text.place_configure(width=TEXT_WIDTH)
for entry in entries:
    entry.place_configure(width=TEXT_WIDTH)


def argument(**key_args):
    return key_args


# def position_settings():
for index in range(len(settings) - 1):
    list_labels_settings[index].place(x=0, y=UNIT_HEIGHT * index, width=UNIT_WIDTH * 2, height=UNIT_HEIGHT)
    list_entry_settings[index].place(x=UNIT_WIDTH * 2 + 10, y=UNIT_HEIGHT * index, width=TEXT_WIDTH - UNIT_WIDTH,
                                     height=UNIT_HEIGHT)
    list_buttons_settings[index].place(x=TEXT_WIDTH + UNIT_WIDTH + 10, y=UNIT_HEIGHT * index,
                                       width=UNIT_WIDTH, height=UNIT_HEIGHT)

# def position_definition():
for index in range(len(DEFINITION_DICT) - 2):
    list_labels_mod_editor[index].place(x=0, y=UNIT_HEIGHT * index, width=UNIT_WIDTH * 2, height=UNIT_HEIGHT)
    list_text_mod_editor[index].place(x=UNIT_WIDTH * 2 + 10, y=UNIT_HEIGHT * index, width=TEXT_WIDTH,
                                      height=UNIT_HEIGHT)
list_text_mod_editor[-1].place_configure(height=UNIT_HEIGHT * 4)

dict_position = {
    container_function_selected: argument(x=0, y=0, width=FULL_WIDTH, height=UNIT_HEIGHT * 13),

    label_mods_idle: argument(x=0, y=int(UNIT_HEIGHT * 2.5), width=UNIT_WIDTH * 2, height=UNIT_HEIGHT),
    listbox_mods_idle: argument(x=UNIT_WIDTH * 2, y=0, width=TEXT_WIDTH, height=UNIT_HEIGHT * 5),
    container_mod_buttons: argument(x=UNIT_WIDTH * 0, y=UNIT_HEIGHT * 5 + 5, width=FULL_WIDTH, height=UNIT_HEIGHT + 10),
    button_mod_new: argument(x=UNIT_WIDTH * 0, y=0),
    button_mod_activate: argument(x=UNIT_WIDTH * 2, y=0),
    label_mods_active: argument(x=0, y=int(UNIT_HEIGHT * 9), width=UNIT_WIDTH * 2, height=UNIT_HEIGHT),
    listbox_mods_active: argument(x=UNIT_WIDTH * 2, y=int(UNIT_HEIGHT * 6.5), width=TEXT_WIDTH, height=UNIT_HEIGHT * 5),

    label_browser: argument(x=0, y=0, width=TEXT_WIDTH, height=UNIT_HEIGHT),
    listbox_browser: argument(x=UNIT_WIDTH * 1, y=UNIT_HEIGHT, width=TEXT_WIDTH, height=UNIT_HEIGHT * 10),

    label_file_select: argument(x=0, y=0),
    button_file_select: argument(x=0, y=UNIT_HEIGHT),
    text_file_select: argument(x=UNIT_WIDTH * 2, y=UNIT_HEIGHT * 0, width=TEXT_WIDTH, height=UNIT_HEIGHT * 2),
    label_folder_select: argument(x=0, y=0),
    button_folder_select: argument(x=0, y=UNIT_HEIGHT),
    text_folder_select: argument(x=UNIT_WIDTH * 2, y=0, width=TEXT_WIDTH, height=UNIT_HEIGHT * 2),

    text_file_content: argument(x=UNIT_WIDTH * 1, y=0, width=TEXT_WIDTH, height=UNIT_HEIGHT * 12),
    numeration: argument(x=0, y=0, width=UNIT_WIDTH - 1, height=UNIT_HEIGHT * 12),
    label_find: argument(x=0, y=0, width=UNIT_WIDTH * 2, height=UNIT_HEIGHT),
    text_find: argument(x=UNIT_WIDTH * 2, y=0, width=TEXT_WIDTH, height=UNIT_HEIGHT),
    button_replace_copy: argument(x=0, y=0),
    label_replace: argument(x=0, y=UNIT_HEIGHT),
    text_replace: argument(x=UNIT_WIDTH * 2, y=0, width=TEXT_WIDTH, height=UNIT_HEIGHT * 2),
    # container_command:
    text_result: argument(x=0, y=0, width=FULL_WIDTH, height=UNIT_HEIGHT),
    container_command_buttons: argument(x=0, y=UNIT_HEIGHT * 2, anchor='sw', width=FULL_WIDTH, height=UNIT_HEIGHT),
    button_menu_back: argument(x=0, y=0),
    button_menu_mods: argument(x=UNIT_WIDTH * 1, y=0),
    button_menu_settings: argument(x=UNIT_WIDTH * 3, y=0),
    button_run: argument(x=UNIT_WIDTH * 5, y=0),
    button_execute: argument(x=UNIT_WIDTH * 7, y=0),
    button_function_duplicate: argument(x=UNIT_WIDTH * 9, y=0),
    button_function_find: argument(x=UNIT_WIDTH * 11, y=0),
    button_function_replace: argument(x=UNIT_WIDTH * 13, y=0),

    container_version_tools: argument(x=0, y=0, width=UNIT_WIDTH * 3, height=UNIT_HEIGHT * 5),
    button_snapshot_make: argument(x=0, y=0),
    button_snapshot_compare: argument(x=0, y=UNIT_HEIGHT * 2),

    # non-default
    container_mods: argument(x=0, y=0, width=FULL_WIDTH, height=UNIT_HEIGHT * 13),  # configure(bg='blue'),
    button_mod_open: argument(x=UNIT_WIDTH * 8, y=0, width=UNIT_WIDTH * 2, height=UNIT_HEIGHT),
    button_mod_copy: argument(x=UNIT_WIDTH * 10, y=0, width=UNIT_WIDTH * 2, height=UNIT_HEIGHT),
    button_mod_edit: argument(x=UNIT_WIDTH * 12, y=0, width=UNIT_WIDTH * 2, height=UNIT_HEIGHT),
    button_mod_deactivate: argument(x=UNIT_WIDTH * 4, y=0, width=UNIT_WIDTH * 2, height=UNIT_HEIGHT),
    button_mod_reload: argument(x=UNIT_WIDTH * 6, y=0, width=UNIT_WIDTH * 2, height=UNIT_HEIGHT),

    container_command: argument(x=0, y=UNIT_HEIGHT * 15, anchor='sw', width=FULL_WIDTH, height=UNIT_HEIGHT * 2),
    container_settings: argument(x=0, y=0, width=FULL_WIDTH, height=UNIT_HEIGHT * 11),
    container_mod_editor: argument(x=0, y=0, width=FULL_WIDTH, height=UNIT_HEIGHT * 11),
    container_browser: argument(x=0, y=0, width=FULL_WIDTH, height=UNIT_HEIGHT * 12),
    container_select_file: argument(x=0, y=0, width=FULL_WIDTH, height=UNIT_HEIGHT * 2),
    container_folder_select: argument(x=0, y=UNIT_HEIGHT * 2, width=FULL_WIDTH, height=UNIT_HEIGHT * 3),
    container_file_content: argument(x=0, y=0, width=FULL_WIDTH, height=UNIT_HEIGHT * 13),
    container_find: argument(x=0, y=int(UNIT_HEIGHT * 7.5), width=FULL_WIDTH, height=UNIT_HEIGHT * 1),
    container_replace: argument(x=0, y=int(UNIT_HEIGHT * 8.5), width=FULL_WIDTH, height=UNIT_HEIGHT * 2),
    container_version: argument(x=0, y=0, width=FULL_WIDTH, height=UNIT_HEIGHT * 10),
}


# 024-08_06
def position(*elements):
    for element in elements:
        try:
            element.place(dict_position[element])
        except AttributeError as err:  # KeyError or
            print(f'element {element} not predefined\n{err}')


position(
    container_function_selected, text_result,
    container_command_buttons, button_menu_back, button_menu_mods, button_menu_settings, button_run,
    button_execute, button_function_find, button_function_replace,
    container_mod_buttons, button_mod_new, button_mod_activate,
    text_file_content, numeration, label_browser, listbox_browser,
    label_mods_idle, listbox_mods_idle, label_mods_active, listbox_mods_active,
    label_file_select, button_file_select, text_file_select,
    label_folder_select, button_folder_select, text_folder_select,
    label_find, text_find, button_replace_copy, label_replace, text_replace,
    container_version_tools, button_snapshot_make, button_snapshot_compare
)  # , button_function_duplicate


def retrieve(*elements):
    for element in elements:
        try:
            # element.configure(state='disabled')
            element.place_forget()
        except NameError:
            pass


image_button_small_idle = tkinter.PhotoImage(file=r'aesthetic\rotwk_button_small_idle.png')
image_button_small_hover = tkinter.PhotoImage(file=r'aesthetic\rotwk_button_small_hover.png')
# image_button_small_pressed = tkinter.PhotoImage(file=r'aesthetic\rotwk_button_small_pressed.png')
image_button_large_idle = tkinter.PhotoImage(file=r'aesthetic\rotwk_button_large_idle.png')
image_button_large_hover = tkinter.PhotoImage(file=r'aesthetic\rotwk_button_large_hover.png')
# image_button_large_pressed = tkinter.PhotoImage(file=r'aesthetic\rotwk_button_large_pressed.png')

for container in containers:
    container.configure(background=BACKGROUND_COLOR)
for button in small_buttons:
    button.configure(image=image_button_small_idle, compound='center', foreground=TEXT_COLORS[0], font=FONT, border=0,
                     background=BACKGROUND_COLOR, activebackground=BACKGROUND_COLOR)
# , width=UNIT_WIDTH, height=40
for button in large_buttons:
    button.configure(image=image_button_large_idle, compound='center', foreground=TEXT_COLORS[0], font=FONT, border=0,
                     background=BACKGROUND_COLOR, activebackground=BACKGROUND_COLOR, disabledforeground=TEXT_COLORS[2])
for label in labels:
    label.configure(background=BACKGROUND_COLOR, foreground=TEXT_COLORS[0], font=FONT)
# label_browser.configure(width=UNIT_WIDTH * 2, height=2)
for text in texts:
    text.configure(foreground=TEXT_COLORS[0], font=FONT, selectforeground=TEXT_COLORS[-1],
                   background=ENTRY_BACKGROUND_COLOR, selectbackground=TEXT_COLORS[0])
for entry in entries:
    entry.configure(foreground=TEXT_COLORS[0], font=FONT, selectforeground=TEXT_COLORS[-1],
                    background=ENTRY_BACKGROUND_COLOR, selectbackground=TEXT_COLORS[0])
text_result.configure(foreground=TEXT_COLORS[1])
listbox_browser.configure(background=ENTRY_BACKGROUND_COLOR, foreground=TEXT_COLORS[0], font=FONT,
                          selectbackground=TEXT_COLORS[0], selectforeground=TEXT_COLORS[-1])
# width=UNIT_WIDTH * 2,
current_style = tkinter.ttk.Style(master=main_window)
current_style.theme_use('clam')
tkinter.ttk.Style().configure('.', width=UNIT_WIDTH * 2, font=FONT,
                              foreground=TEXT_COLORS[0], background=ENTRY_BACKGROUND_COLOR)
tkinter.ttk.Style().configure('Treeview', background=ENTRY_BACKGROUND_COLOR,
                              selectbackground=TEXT_COLORS[0], selectforeground=TEXT_COLORS[-1],
                              fieldbackground=ENTRY_BACKGROUND_COLOR, fieldbw=0)
tkinter.ttk.Style().configure('Treeview.Heading', borderwidth=0,
                              overbackground=TEXT_COLORS[0], overforeground=TEXT_COLORS[-1])

# set_window_mods()
set_window_controller()
main_window.protocol("WM_DELETE_WINDOW", on_app_close)
main_window.mainloop()
