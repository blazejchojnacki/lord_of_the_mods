import os.path
import tkinter
import _tkinter
from tkinter.messagebox import askquestion
from tkinter.simpledialog import askstring
from tkinter.filedialog import askopenfilenames, askdirectory
from tkinter.ttk import Treeview

from constants import INI_COMMENTS
from settings_editor import read_settings, save_settings, GAME_PATH, WORLDBUILDER_PATH
from file_interpreter import convert_string
from file_editor import find_text, replace_text, move_file, duplicates_commenter, load_file, load_directories
from mods_enabler import Mod, load_mods, edit_mod, activate_mod, deactivate_mod, reload_mod, create_mod

INI_LEVELS_COLORS = ['green', 'blue', 'purple', 'red', 'orange']

# GRAPHICAL_MODE = None
GRAPHICAL_MODE = True
GRID = False
# GRID = True

if GRID:
    # CONTAINER_WIDTH = 150
    UNIT_WIDTH = 20
    TEXT_WIDTH = 150
    LIST_WIDTH = 200
else:
    UNIT_WIDTH = 160
    UNIT_HEIGHT = 40
    TEXT_WIDTH = UNIT_WIDTH * 6  # 900
    FULL_WIDTH = int(UNIT_WIDTH*7.5)
    LIST_WIDTH = 160
    

settings = read_settings()
mods = []
default_mod = Mod()
current_path = ''
current_levels = []
current_file_content_backup = ''
new_mod_name = ''


class ColumnedListbox(tkinter.ttk.Treeview):
    """ a tk class based on Treeview to make a list with columns"""
    def __init__(self, master, width, height, show='headings'):  # , **kw
        super().__init__(master=master, height=height, show=show)
        self.width = width * 6
        self.columns_list = ("name", "status", "contains_mods", "description")
        self.build_list()
        self.set_columns_proportions(proportions=(2, 1, 2, 7))

    def build_list(self):
        # vertical_scrollbar = tkinter.ttk.Scrollbar(master=self, orient="vertical", command=self.yview)
        # vertical_scrollbar.pack()
        # self.configure(yscrollcommand=vertical_scrollbar.set)
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


def clear_window():
    """ deletes all the containers of the current feature used """
    global current_file_content_backup
    warning_file_save()
    current_file_content_backup = ''
    if GRID:
        container_directories.grid_remove()
        container_mods.grid_remove()
        container_mod_editor.grid_remove()
        container_find.grid_remove()
        container_replace.grid_remove()
        container_folder_select.grid_remove()
        container_select_file.grid_remove()
        container_file_content.grid_remove()
        # container_result.grid_remove()
        container_settings.grid_remove()
    else:
        container_directories.place_forget()
        container_mods.place_forget()
        container_mod_editor.place_forget()
        container_find.place_forget()
        container_replace.place_forget()
        container_folder_select.place_forget()
        container_select_file.place_forget()
        container_file_content.place_forget()
        container_settings.place_forget()


def set_window_find():
    """ loads the widget containers related to the find_text function """
    global key_to_command_current
    key_to_command_current = key_to_command_text.copy()
    clear_window()
    if GRID:
        container_file_content.grid(row=0, column=1, sticky='w')
        text_file_content.configure(height=15)
        container_find.grid(row=1, column=1, sticky='w')
        container_select_file.grid(row=2, column=1, sticky='w')
        container_command.grid(row=3, column=1, columnspan=10, sticky='w')
        text_result.configure(height=4)
        button_function_find.configure(state='disabled')
        button_function_replace.configure(state='normal')
        button_function_duplicate.configure(state='normal')
    else:
        container_function_selected.place_configure(height=UNIT_HEIGHT*10)
        container_file_content.place(x=0, y=0, width=FULL_WIDTH, height=UNIT_HEIGHT*5)
        text_file_content.place_configure(height=UNIT_HEIGHT*5)
        container_select_file.place(x=0, y=int(UNIT_HEIGHT*5.5), width=FULL_WIDTH, height=UNIT_HEIGHT*2)
        container_find.place(x=0, y=int(UNIT_HEIGHT*7.5), width=FULL_WIDTH, height=UNIT_HEIGHT*1)
        container_command.place_configure(height=UNIT_HEIGHT*5)
        container_command_buttons.place_configure(y=UNIT_HEIGHT*5)
        text_result.place_configure(height=UNIT_HEIGHT*4)
        button_function_find.place_forget()
        button_function_replace.place(x=int(UNIT_WIDTH*6.5), y=0, width=UNIT_WIDTH, height=UNIT_HEIGHT)
        # button_function_duplicate.place(x=int(UNIT_WIDTH*4.5), y=0, width=UNIT_WIDTH, height=UNIT_HEIGHT)
    button_menu_back.config(command=set_window_file)
    try:
        selection = convert_string(text_file_content.selection_get(), direction='display')
        text_find.delete('1.0', 'end')
        text_find.insert('1.0', selection)
    except UnboundLocalError:
        print('set_window_find error: UnboundLocalError')
    except _tkinter.TclError:
        print('set_window_find error: _tkinter.TclError')
    button_run.configure(text="find string", command=command_run_find)
    button_execute.configure(text='clear logs', command=set_log_update)
    command_run_find()
    text_result.focus()


def set_window_replace():
    """ loads the widget containers related to the replace_text function """
    global key_to_command_current
    key_to_command_current = key_to_command_text.copy()
    clear_window()
    if GRID:
        container_file_content.grid(row=0, column=1, sticky='w')
        text_file_content.configure(height=15)
        container_find.grid(row=1, column=1, sticky='w')
        container_replace.grid(row=2, column=1, sticky='w')
        # container_select_file.grid(row=3, column=1, sticky='w')
        container_command.grid(row=3, column=1, columnspan=10, sticky='w')
        text_result.configure(height=4)
        button_function_find.configure(state='normal')
        button_function_replace.configure(state='disabled')
    else:
        container_file_content.place(x=0, y=0, width=FULL_WIDTH, height=UNIT_HEIGHT*5)
        text_file_content.place_configure(height=UNIT_HEIGHT*5)
        container_select_file.place(x=0, y=int(UNIT_HEIGHT*5.5), width=FULL_WIDTH, height=UNIT_HEIGHT*2)
        container_find.place(x=0, y=int(UNIT_HEIGHT*7.5), width=FULL_WIDTH, height=UNIT_HEIGHT*1)
        container_replace.place(x=0, y=int(UNIT_HEIGHT*8.5), width=FULL_WIDTH, height=UNIT_HEIGHT*2)
        container_function_selected.place_configure(height=UNIT_HEIGHT*11)
        container_command.place_configure(height=UNIT_HEIGHT*4)
        container_command_buttons.place_configure(y=UNIT_HEIGHT*4)
        text_result.place_configure(height=UNIT_HEIGHT*3)
        button_function_find.place(x=int(UNIT_WIDTH*5.5), y=0, width=UNIT_WIDTH, height=UNIT_HEIGHT)
        button_function_replace.place_forget()
    try:
        selection = convert_string(text_file_content.selection_get(), direction='display')
        text_find.delete('1.0', 'end')
        text_find.insert('1.0', selection)
    except UnboundLocalError:
        print('set_window_find error: UnboundLocalError')
    except _tkinter.TclError:
        print('set_window_find error: _tkinter.TclError')
    button_menu_back.config(command=set_window_file)
    button_run.configure(text="replace string", command=command_run_replace)
    button_run.focus()
    button_execute.configure(text='clear logs', command=set_log_update)


def set_window_duplicates():
    """ loads the widget containers related to the comment_out_duplicates function """
    global key_to_command_current
    key_to_command_current = key_to_command_text.copy()
    clear_window()
    if GRID:
        container_file_content.grid(row=0, column=1, sticky='w')
        text_file_content.configure(height=15)
        container_select_file.grid(row=1, column=1, sticky='w')
        container_command.grid(row=3, column=1, columnspan=10, sticky='w')
        text_result.configure(height=4)
    else:
        container_function_selected.place_configure(height=UNIT_HEIGHT*9)
        container_file_content.place(x=0, y=0, width=FULL_WIDTH, height=UNIT_HEIGHT*5)
        text_file_content.place_configure(height=UNIT_HEIGHT*5)
        container_select_file.place(x=0, y=int(UNIT_HEIGHT*5.5), width=FULL_WIDTH, height=UNIT_HEIGHT*3)
        container_command.place_configure(height=UNIT_HEIGHT*6)
        container_command_buttons.place_configure(y=UNIT_HEIGHT*6)
        text_result.place_configure(height=UNIT_HEIGHT*5)
        button_function_duplicate.place_forget()
    try:
        if os.path.isdir(current_path):
            selected_file = f'{label_directory.cget("text")}/{list_directory.selection_get()}'
        else:
            selected_file = current_path
        text_file_select.delete('1.0', 'end')
        text_file_select.insert('1.0', selected_file)
    except _tkinter.TclError:
        print('set_window_duplicates error: _tkinter.TclError')
    if os.path.isdir(current_path):
        button_menu_back.configure(command=set_window_directories)
    else:
        button_menu_back.configure(command=set_window_file)
    command_file_load()
    button_run.configure(text="remove duplicates", command=command_run_duplicate)
    button_run.focus()
    button_execute.configure(text='clear logs', command=set_log_update)
    set_log_update(f'remove duplicates feature loaded. file: {current_path}')


def set_window_move():
    """ loads the widget containers related to the move file function """
    global key_to_command_current, current_path
    key_to_command_current = key_to_command_text.copy()
    clear_window()
    if GRID:
        container_select_file.grid(row=1, column=1, sticky='w')
        container_folder_select.grid(row=2, column=1, sticky='w')
        container_command.grid(row=3, column=1, columnspan=10, sticky='w')
        text_result.configure(height=4)
    else:
        container_select_file.place(x=0, y=0, width=FULL_WIDTH, height=UNIT_HEIGHT*2)
        container_folder_select.place(x=0, y=UNIT_HEIGHT*2, width=FULL_WIDTH, height=UNIT_HEIGHT*3)
        container_function_selected.place_configure(height=UNIT_HEIGHT*5)
        container_command.place_configure(height=UNIT_HEIGHT*10)
        container_command_buttons.place_configure(y=UNIT_HEIGHT*10)
        text_result.place_configure(height=UNIT_HEIGHT*9)
        button_function_duplicate.place_forget()
    current_path = f'{label_directory.cget("text")}/{list_directory.selection_get()}'
    # if os.path.isdir(current_path):
    button_menu_back.configure(command=command_directory_back)
    label_file_select.configure(text='file')
    text_file_select.delete('1.0', 'end')
    text_file_select.insert('1.0', f'{label_directory.cget("text")}/{list_directory.selection_get()}')
    label_folder_select.configure(text='to folder')
    button_run.configure(text='move the file', command=command_run_move)
    button_run.focus()
    button_execute.configure(text='clear logs', command=set_log_update)
    set_log_update(f'move feature loaded. file: {current_path}')


def set_window_file():
    """ loads the widget containers related to the file editor """
    global key_to_command_current
    clear_window()
    if GRID:
        # container_file_select.grid(row=1, column=1)
        container_file_content.grid(row=2, column=1, sticky='w')
        text_file_content.configure(height=30)
        container_command.grid(row=3, column=1, columnspan=10, sticky='w')
        button_execute.grid(row=1, column=3)
    else:
        container_function_selected.place_configure(height=UNIT_HEIGHT*13)
        container_file_content.place(x=0, y=0, width=FULL_WIDTH, height=UNIT_HEIGHT*13)
        text_file_content.place_configure(height=UNIT_HEIGHT*12)
        button_run.place(x=int(UNIT_WIDTH*2.5), y=0, width=UNIT_WIDTH, height=UNIT_HEIGHT)
        button_function_duplicate.place(x=int(UNIT_WIDTH*4.5), y=0, width=UNIT_WIDTH, height=UNIT_HEIGHT)
        button_function_find.place(x=int(UNIT_WIDTH*5.5), y=0, width=UNIT_WIDTH, height=UNIT_HEIGHT)
        button_function_replace.place(x=int(UNIT_WIDTH*6.5), y=0, width=UNIT_WIDTH, height=UNIT_HEIGHT)
        container_command.place_configure(height=UNIT_HEIGHT*2)
        container_command_buttons.place_configure(y=UNIT_HEIGHT*2)
        text_result.place_configure(height=UNIT_HEIGHT*1)
        button_execute.place(x=int(UNIT_WIDTH*3.5), y=0, width=UNIT_WIDTH, height=UNIT_HEIGHT)
    button_menu_back.config(command=command_directory_back)
    key_to_command_current = key_to_command_text
    text_file_content.focus()
    text_result.configure(height=1)
    set_log_update(f'file editor loaded. file {current_path}')
    button_run.configure(text='save file', command=command_file_save, state='normal')
    button_execute.configure(text='reload file', command=command_file_load)
    button_function_find.configure(state='normal')
    button_function_replace.configure(state='normal')
    button_function_duplicate.configure(state='normal')


def set_window_mods():
    """ loads the widget containers related to the managing of mods """
    global key_to_command_current
    key_to_command_current = key_to_command_mod.copy()
    clear_window()
    if GRID:
        container_mods.grid(row=1, column=1, sticky='w')
        container_command.grid(row=3, column=1, columnspan=10, sticky='w')
        button_execute.grid(row=1, column=3)
        text_result.configure(height=1)
    else:
        container_mods.place(x=0, y=0, width=FULL_WIDTH, height=UNIT_HEIGHT*13)
        button_mod_new.place(x=UNIT_WIDTH*0, y=0, width=UNIT_WIDTH, height=UNIT_HEIGHT)
        button_menu_back.place_forget()
        button_mod_copy.place_forget()
        button_mod_edit.place_forget()
        button_function_find.place_forget()
        button_function_replace.place_forget()
        button_function_duplicate.place_forget()
        container_function_selected.place_configure(height=UNIT_HEIGHT*13)
        container_command.place(x=0, y=UNIT_HEIGHT*15, anchor='sw', width=FULL_WIDTH, height=UNIT_HEIGHT*2)
        container_command_buttons.place_configure(y=UNIT_HEIGHT*2)
        text_result.place_configure(height=UNIT_HEIGHT*1)
        button_execute.place(x=int(UNIT_WIDTH*3.5), y=0, width=UNIT_WIDTH, height=UNIT_HEIGHT)
        button_menu_settings.place(x=int(UNIT_WIDTH*1.5), y=0, width=UNIT_WIDTH, height=UNIT_HEIGHT)
    text_result.configure(state='disabled')
    set_log_update('mod manager window loaded.')
    button_run.configure(text='launch game', command=launch_game)
    button_execute.configure(text='launch Worldbuilder', command=launch_game_editor, state='normal')
    button_menu_settings.configure(text='edit settings', command=set_window_settings, state='normal')
    button_menu_mods.configure(text='refresh mods')
    button_mod_new.configure(state='normal')
    button_menu_back.configure(state='disabled')
    button_mod_copy.config(state='disabled')
    button_mod_edit.config(state='disabled')
    button_function_find.configure(state='disabled')
    button_function_replace.configure(state='disabled')
    button_function_duplicate.configure(state='disabled')
    refresh_mods()
    list_mods_idle.focus_set()
    list_mods_idle.selection_set(list_mods_idle.get_children()[0])
    list_mods_idle.focus(list_mods_idle.get_children()[0])


def set_window_mod_editor():
    """ loads the widget containers related to the modification of mod parameters """
    global key_to_command_current
    key_to_command_current = key_to_command_text.copy()
    clear_window()
    button_menu_back.configure(state='normal', command=set_window_mods)
    button_menu_settings.configure(state='disabled')
    if GRID:
        container_mod_editor.grid(row=1, column=1, sticky='w')
        container_command.grid(row=3, column=1, columnspan=10, sticky='w')
    else:
        container_mod_editor.place(x=0, y=0, width=FULL_WIDTH, height=UNIT_HEIGHT*11)
        button_menu_back.place(x=0, y=0, width=int(UNIT_WIDTH*0.5), height=UNIT_HEIGHT)
        button_menu_settings.place_forget()
        button_menu_back.place_forget()
        button_execute.place_forget()
    button_run.configure(text='save parameters', command=command_mod_edit)
    button_menu_mods.configure(text='return to mods')
    mod_selected = current_path.split('/')[-1]
    for mod in mods:
        if mod_selected == mod.name:
            level = 0
            for param in default_mod.parameter:
                list_text_mod_editor[level].delete('1.0', 'end')
                list_text_mod_editor[level].insert('end', mod.parameter[param])
                if 'active' in param:
                    list_text_mod_editor[level].configure(state='disabled')
                level += 1


def set_window_directories():
    """ loads the widget containers related to the browsing of mods directories """
    global key_to_command_current
    key_to_command_current = key_to_command_browser.copy()
    clear_window()
    button_mod_new.configure(state='disabled')
    if GRID:
        container_directories.grid(row=1, column=1, sticky='w')
        container_command.grid(row=3, column=1, columnspan=10, sticky='w')
    else:
        button_mod_new.place_forget()
        button_function_find.place_forget()
        button_function_replace.place_forget()
        # button_function_duplicate.place_forget()
        button_menu_settings.place_forget()
        container_function_selected.place_configure(height=UNIT_HEIGHT*13)
        container_directories.place(x=0, y=0, width=FULL_WIDTH, height=UNIT_HEIGHT*12)
        container_command.place_configure(height=UNIT_HEIGHT*2)
        container_command_buttons.place_configure(y=UNIT_HEIGHT*2)
        text_result.place_configure(height=UNIT_HEIGHT)
    set_log_update(f'files browser loaded. mod {current_path}')
    button_run.configure(text='open', command=command_directory_forward)
    button_execute.configure(text='move file', command=set_window_move)
    open_directory_item()
    button_menu_back.config(command=command_directory_back)
    list_directory.focus()


def set_window_settings():
    """ loads the widget containers related to the settings edition """
    global key_to_command_current
    key_to_command_current = key_to_command_text.copy()
    clear_window()
    if GRID:
        container_settings.grid(row=1, column=1, sticky='w')
        container_command.grid(row=3, column=1, columnspan=10, sticky='w')
    else:
        container_settings.place(x=0, y=0, width=FULL_WIDTH, height=UNIT_HEIGHT*11)
    button_menu_settings.configure(text='save settings', command=command_settings_save)
    button_menu_mods.configure(text='return to mods')
    # button_menu_back.configure(command=command_directory_back)


def command_settings_save():
    """ reads the values inserted in the application and orders it to save them to the SETTINGS_FILE """
    counter = 0
    setting_value = []
    new_settings = {}
    for entry_setting in list_entry_settings:
        setting_value.append(entry_setting.get())
    for setting_key in settings:
        if settings[setting_key] != setting_value[counter]:
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
        list_entry_settings[counter].delete('0', 'end')
        if setting_key == 'mods_folder_exceptions' or setting_key == 'mods_templates':
            list_entry_settings[counter].insert('end', ', '.join(settings[setting_key]))
        else:
            list_entry_settings[counter].insert('end', settings[setting_key])
        counter += 1


def command_select_folder():
    """ launches a window for selecting a folder a pastes it into the application """
    selected_folder = askdirectory()
    text_folder_select.delete('1.0', 'end')
    text_folder_select.insert('end', selected_folder)


def command_select_file():
    """ launches a window for selecting a file a pastes it into the application """
    selected_file = askopenfilenames()
    if selected_file:
        text_file_select.delete('1.0', 'end')
        text_file_select.insert('end', selected_file)


def set_text_color(event=None):
    """ provides colors to elements of an edited text file that are defined as its delimiters"""
    level_colors = INI_LEVELS_COLORS
    text_lines = text_file_content.get('1.0', 'end').split('\n')
    for line in text_lines:
        words = line.split()
        for word in words:
            for level in current_levels:
                if len(word.strip()) > 0:
                    if word.strip() in level:
                        index_beg = f'{text_lines.index(line) + 1}.{line.index(word)}'
                        index_end = f'{text_lines.index(line) + 1}.{line.index(word) + len(word)}'
                        text_file_content.tag_add(f"{word}", index_beg, index_end)
                        text_file_content.tag_config(f"{word}",
                                                     foreground=level_colors[current_levels.index(level)])
                    elif word.strip()[0] in INI_COMMENTS:
                        index_beg = f'{text_lines.index(line) + 1}.{line.index(word)}'
                        index_end = f'{text_lines.index(line) + 1}.{len(line)}'
                        text_file_content.tag_add(f"comment", index_beg, index_end)
                        text_file_content.tag_config(f"comment", foreground='grey')


def command_file_load():
    """ loads the file selected into the application and saves its backup """
    global current_levels, current_file_content_backup
    text_file_content.delete('1.0', 'end')
    file_loaded = text_file_select.get('1.0', 'end').replace('/', '\\').strip('\n\t {}')
    try:
        output, current_levels = load_file(full_path=file_loaded)
        current_file_content_backup = output
    except TypeError:
        output = 'cannot open this file type'
    text_file_content.insert('end', output)
    set_text_color()


def command_file_save():
    """ saves the text edited in the application back into its origin file """
    global current_file_content_backup
    content_to_save = text_file_content.get('1.0', 'end')
    file_named = text_file_select.get('1.0', 'end').replace('/', '\\').strip().replace('{', '').replace('}', '')
    with open(file_named, 'w') as file_overwritten:  # .replace('.ini', '_new.ini')
        file_overwritten.write(content_to_save)
    current_file_content_backup = content_to_save


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
    # print(output)
    set_log_update(output)


def command_run_replace():
    """ runs the replace_text function """
    find = convert_string(text_find.get('1.0', 'end').strip(), direction='display')
    replace_with = convert_string(text_replace.get('1.0', 'end').strip(), direction='display')
    in_file = text_file_select.get('1.0', 'end').replace('/', '\\').strip()
    output = replace_text(find, replace_with, in_file)
    # print(output)
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
    file_named = text_folder_select.get('1.0', 'end').replace('/', '\\').strip()
    output = duplicates_commenter(in_file=file_named)
    set_log_update(output)


def selected_mod_idle(event):
    """ on select of a value in the non-active mods, activates and deactivates the appropriate buttons"""
    global current_path
    global key_to_command_current
    try:
        current_path = "O:/_MODULES/" + list_mods_idle.item(list_mods_idle.selection()[0], 'values')[0]
        list_mods_active.selection_remove(list_mods_active.selection()[0])
        # selection_remove is a selection event steeling focus to the other list
        list_mods_idle.selection_set(list_mods_idle.selection()[0])
    except IndexError:
        pass
    key_to_command_current['<Return>'] = command_mod_open
    button_mod_deactivate.config(state='disabled')
    button_mod_activate.config(state='normal')
    button_mod_reload.config(state='disabled')
    button_mod_open.config(state='normal')
    button_mod_copy.config(state='normal')
    button_mod_edit.config(state='normal')
    if not GRID:
        button_mod_deactivate.place_forget()
        button_mod_activate.place(x=UNIT_WIDTH*1, y=0, width=UNIT_WIDTH, height=UNIT_HEIGHT)
        button_mod_reload.place_forget()
        button_mod_open.place(x=UNIT_WIDTH*4, y=0, width=UNIT_WIDTH, height=UNIT_HEIGHT)
        button_mod_copy.place(x=UNIT_WIDTH*5, y=0, width=UNIT_WIDTH, height=UNIT_HEIGHT)
        button_mod_edit.place(x=UNIT_WIDTH*6, y=0, width=UNIT_WIDTH, height=UNIT_HEIGHT)
    # list_mods_idle.selection_get()[0].focus()
    list_mods_idle.focus()


def selected_mod_active(event):
    """ on select of a value in the active mods, activates and deactivates the appropriate buttons"""
    global current_path
    global key_to_command_current
    try:
        current_path = "O:/_MODULES/" + list_mods_active.item(list_mods_active.selection()[0], 'values')[0]
        list_mods_idle.selection_remove(list_mods_idle.selection()[0])
        # selection_remove is a selection event steeling focus to the other list
        list_mods_active.selection_set(list_mods_active.selection()[0])
    except IndexError:
        pass
    key_to_command_current['<Return>'] = command_mod_open
    button_mod_activate.config(state='disabled')
    button_mod_deactivate.config(state='normal')
    button_mod_reload.config(state='normal')
    button_mod_open.config(state='normal')
    button_mod_copy.config(state='normal')
    button_mod_edit.config(state='normal')
    if not GRID:
        button_mod_activate.place_forget()
        button_mod_deactivate.place(x=UNIT_WIDTH*2, y=0, width=UNIT_WIDTH, height=UNIT_HEIGHT)
        button_mod_reload.place(x=UNIT_WIDTH*3, y=0, width=UNIT_WIDTH, height=UNIT_HEIGHT)
        button_mod_open.place(x=UNIT_WIDTH*4, y=0, width=UNIT_WIDTH, height=UNIT_HEIGHT)
        button_mod_copy.place(x=UNIT_WIDTH*5, y=0, width=UNIT_WIDTH, height=UNIT_HEIGHT)
        button_mod_edit.place(x=UNIT_WIDTH*6, y=0, width=UNIT_WIDTH, height=UNIT_HEIGHT)


def refresh_mods():
    """ refreshes the lists of active and non-active mods """
    global mods
    mods = load_mods()
    list_mods_active.delete(*list_mods_active.get_children())  # (0, 'end')
    list_active_index = 0
    list_mods_idle.delete(*list_mods_idle.get_children())
    list_idle_index = 0
    for mod in mods:
        if mod.is_active.lower() == 'yes' or mod.parameter['is active: '].lower() == 'yes':
            list_mods_active.insert(parent='', index=list_active_index, values=(mod.name, mod.status, mod.contains_mod,
                                                                                mod.description))
            list_active_index += 1
        elif mod.is_active.lower() == 'no' or mod.parameter['is active: '].lower() == 'no':
            list_mods_idle.insert(parent='', index=list_idle_index, values=(mod.name, mod.parameter['status: '],
                                                                            mod.parameter['contains mod(s): '],
                                                                            mod.parameter['description: ']))
            list_idle_index += 1
    button_mod_deactivate.config(state='disabled')
    button_mod_activate.config(state='disabled')
    if not GRID:
        button_mod_deactivate.place_forget()
        button_mod_activate.place_forget()


def command_new_mod():
    """ initiates the creation of a new mod """
    global new_mod_name
    first_run = True
    while new_mod_name in [mod.name for mod in mods] or first_run:
        message = 'provide a name unique to the new mod'
        if first_run:
            message = 'provide the new mod name'
        new_mod_name = tkinter.simpledialog.askstring(title='new mod name', prompt=message)
        first_run = False
        # ISSUE: askstring window loses focus on second run
    if new_mod_name:
        print(create_mod(new_mod_name))
        refresh_mods()
    else:
        set_log_update('command_new_mod error: a correct unique name was not provided')
    new_mod_name = ''


def command_copy_mod():
    """ initiates the copy of the selected mod """
    mod_selected = current_path
    name = mod_selected.split('/')[-1] + '_copy'
    print(create_mod(name, mod_selected))
    refresh_mods()


def command_mod_edit():
    """ edits the current mod parameters"""
    mod_selected = current_path.split('/')[-1]
    for mod in mods:
        if mod_selected == mod.name:
            level = 0
            for param in default_mod.parameter:
                value = list_text_mod_editor[level].get('1.0', 'end').strip()
                if value:
                    default_mod.parameter[param] = value
                else:
                    default_mod.parameter[param] = None
                level += 1
            default_mod.internalise()
            edit_mod(
                mod,
                mod_name=default_mod.name,
                mod_status=default_mod.status,
                mod_contains_mod=default_mod.contains_mod,
                mod_contained_in=default_mod.contained_in,
                mod_description=default_mod.description
            )


def command_activate_mod():
    """ initiates the activation of the selected mod """
    global mods
    try:
        mod_selected = list_mods_idle.item(list_mods_idle.focus(), 'values')[0]
        for mod in mods:
            if mod.name == mod_selected:
                activate_mod(mod)
                edit_mod(mod, mod_is_active='yes')
                return refresh_mods()
        print("error command_activate_mod: mod not found")
    except _tkinter.TclError:
        print("error command_activate_mod: TclError")


def command_deactivate_mod():
    """ initiates the deactivation of the selected mod """
    global mods
    try:
        mod_selected = list_mods_active.item(list_mods_active.focus(), 'values')[0]
        for mod in mods:
            if mod.name == mod_selected:
                deactivate_mod(mod)
                edit_mod(mod, mod_is_active='no')
                refresh_mods()
                return
        print("error command_deactivate_mod: mod not found")
    except _tkinter.TclError:
        print("error command_deactivate_mod: TclError")


def command_reload_mod():
    """ initiates the reloading of a mod """
    global mods
    try:
        mod_selected = list_mods_active.item(list_mods_active.focus(), 'values')[0]
        for mod in mods:
            if mod.name == mod_selected:
                reload_mod(mod)
                refresh_mods()
                return
        print("error command_deactivate_mod: mod not found")
    except _tkinter.TclError:
        print("error command_reload_mod: TclError")


def command_mod_open(event=None):
    """ at this point could be cannibalized by set_window_directories"""
    button_menu_mods.configure(text="return to mods")
    set_window_directories()


def command_directory_back():
    """ triggered on browsing back to a previous directory """
    global current_path, key_to_command_current
    if len(current_path) > len("O:/_MODULES"):
        current_path = current_path[:current_path.rfind('/')]
        if main_window.focus_get() == list_directory:
            open_directory_item()
        else:
            set_window_directories()
    if len(current_path) <= len("O:/_MODULES"):
        # print(f'permission denied to escape {current_path}')
        button_menu_back.configure(state='disabled')
        if not GRID:
            button_menu_back.place_forget()
        key_to_command_current['<BackSpace>'] = set_window_mods
    # current_key_to_command['<Return>'] = command_directory_forward
    key_to_command_current = key_to_command_browser.copy()


def on_select_list_directory(event=None):
    """ triggered on selection of an item in the directory to enable or disable buttons """
    global current_path
    # yes = list_directory.selection_get()
    if 'file editor loaded' not in text_result.get('1.0', 'end'):
        try:
            if list_directory.selection_get()[-4] == '.' or list_directory.selection_get()[-5] == '.':
                button_run.configure(text='open file')
                button_execute.configure(state='normal')  # button_function_move
                button_function_duplicate.configure(state='normal')
                if not GRID:
                    button_execute.place(x=int(UNIT_WIDTH*3.5), y=0, width=UNIT_WIDTH, height=UNIT_HEIGHT)
                    button_function_duplicate.place(x=int(UNIT_WIDTH*4.5), y=0, width=UNIT_WIDTH, height=UNIT_HEIGHT)
            else:
                button_run.configure(text='open folder')
                button_execute.configure(state='disabled')
                button_function_duplicate.configure(state='disabled')
                if not GRID:
                    button_execute.place_forget()
                    button_function_duplicate.place_forget()
        except IndexError:
            # print(current_path)
            button_run.configure(text='open folder')
            button_execute.configure(state='disabled')
            button_function_duplicate.configure(state='disabled')
            if not GRID:
                button_execute.place_forget()
                button_function_duplicate.place_forget()


def on_double_click_list_directory(event):
    """ triggered by a double click of an item in the directory """
    command_directory_forward()


def command_directory_forward():
    """ gets the selected item in the directory and opens it """
    global current_path
    try:
        item_selected = list_directory.get(list_directory.curselection())
        current_path += '/' + item_selected
    except _tkinter.TclError:
        print("error: open_directory_item 1")
    open_directory_item()


def open_directory_item():  # event=None
    """ opens the selected item in the directory whether it is a folder or a file """
    if os.path.isdir(current_path):
        list_directory.delete(0, 'end')
        output_folders, output_files = load_directories(current_path)
        item_index = 0
        for output_folder in output_folders:
            list_directory.insert(item_index, output_folder)
            list_directory.itemconfig(item_index, foreground=INI_LEVELS_COLORS[1])
            item_index += 1
        for output_file in output_files:
            list_directory.insert(item_index, output_file)
            list_directory.itemconfig(item_index,
                                      foreground=INI_LEVELS_COLORS[2] if output_file[-len('.ini'):] == '.ini' else
                                      INI_LEVELS_COLORS[3])
            item_index += 1
        # list_directory.focus()
        list_directory.activate(0)
        # list_directory.selection_set(0)
        if not output_folders:
            button_run.configure(text='open file')
            button_execute.configure(state='normal')  # button_function_move
            button_function_duplicate.configure(state='normal')
            if not GRID:
                button_execute.place(x=int(UNIT_WIDTH*3.5), y=0, width=UNIT_WIDTH, height=UNIT_HEIGHT)
                button_function_duplicate.place(x=int(UNIT_WIDTH*4.5), y=0, width=UNIT_WIDTH, height=UNIT_HEIGHT)
        else:
            button_run.configure(text='open folder')
            button_execute.configure(state='disabled')
            if not GRID:
                button_execute.place_forget()
                button_function_duplicate.place_forget()
        list_directory.select_set(0)
    elif os.path.isfile(current_path):
        text_file_select.delete('1.0', 'end')
        text_file_select.insert('end', current_path)
        set_window_file()
        command_file_load()
        list_directory.selection_clear(list_directory.curselection())
        button_execute.configure(state='normal')
        if not GRID:
            button_execute.place(x=int(UNIT_WIDTH*3.5), y=0, width=UNIT_WIDTH, height=UNIT_HEIGHT)
    label_directory.configure(text=current_path)
    button_menu_back.configure(state='normal')
    if not GRID:
        button_menu_back.place(x=0, y=0, width=int(UNIT_WIDTH*0.5), height=UNIT_HEIGHT)


def use_selected_text(event=None):
    """ bound to key presses to trigger the appropriate function """
    try:
        # selection = convert_string(text_file_content.selection_get(), direction='display')
        if event.keysym == 'f':
            # text_find.delete('1.0', 'end')
            # text_find.insert('1.0', selection)
            set_window_find()
        elif event.keysym == 'r':
            # text_find.delete('1.0', 'end')
            # text_find.insert('1.0', selection)
            set_window_replace()
        else:
            pass
    except UnboundLocalError:
        print("error use_selected_text: selection seems empty")


def focus_on_next_item():
    """ bound to arrow pressing to change between the lists of active and non-active mods """
    if main_window.focus_get() == list_mods_idle:
        list_mods_idle.selection_remove(list_mods_idle.selection())
        list_mods_active.focus_set()
        # mod_selected = ''
        if list_mods_active.focus():
            mod_selected = list_mods_active.focus()
        elif list_mods_active.selection():
            mod_selected = list_mods_active.selection()
        else:
            mod_selected = list_mods_active.get_children()[0]
        list_mods_active.selection_set(mod_selected)
    elif main_window.focus_get() == list_mods_active:
        list_mods_active.selection_remove(list_mods_active.selection())
        list_mods_idle.focus_set()
        list_mods_idle.selection_set(list_mods_idle.focus())
        if list_mods_idle.focus():
            mod_selected = list_mods_idle.focus()
        elif list_mods_idle.selection():
            mod_selected = list_mods_idle.selection()
        else:
            mod_selected = list_mods_idle.get_children()[0]
        list_mods_idle.selection_set(mod_selected)
    elif main_window.focus_get() == list_directory:
        # try:
        list_length = len(list_directory.get('0', 'end'))
        selected_item_index = list_directory.get('0', 'end').index(list_directory.selection_get())
        list_directory.selection_set((selected_item_index + 1) % list_length)
        # except _tkinter.TclError:
        #     print("error")
    else:
        print(main_window.focus_get())


def set_log_update(line=''):
    """ unlocks the result field and inserts the output of a function """
    text_result.configure(state='normal')
    text_result.delete('1.0', 'end')
    text_result.insert('end', line)
    text_result.configure(state='disabled')


# def set_command_update(line=''):
#     """ unlocks the command field and inserts the output of a function """
#     entry_command.configure(state='normal')
#     entry_command.delete(0, 'end')
#     entry_command.insert('end', line)
#     entry_command.configure(state='disabled')


def press_key_in_current_mode(event=None):
    """ attributes the key presses to the currently allowed functions """
    if f'<{event.keysym}>' in key_to_command_current:
        key_to_command_current[f'<{event.keysym}>']()
    else:
        # print(f'<{event.keysym}>')
        pass


key_to_command_mod = {
    '<Return>': command_directory_forward,
    '<Right>': focus_on_next_item,
    '<Left>': focus_on_next_item,
}
key_to_command_browser = {
    '<Return>': command_directory_forward,
    '<BackSpace>': command_directory_back,
    '<Escape>': set_window_mods,
    # '<Down>': focus_on_next_item,
    # '<Up>': focus_on_next_item
}
key_to_command_text = {
    '<Escape>': command_directory_back
}
key_to_command_current = {
    '<Return>': set_window_mods,
}


main_window = tkinter.Tk()
main_window.iconbitmap('aesthetic/lotr-icon1.ico')
main_window.title("Lord of the mods")
# main_window.minsize(width=1300, height=400)
# main_window.maxsize(width=1600, height=900)
main_window.geometry('1250x650')
# main_window.attributes("-alpha", 0.6)
main_window.configure(padx=10, pady=10)

main_window.bind_all('<Control-Key-f>', use_selected_text)
main_window.bind_all('<Control-Key-r>', use_selected_text)
main_window.bind('<Key>', press_key_in_current_mode)

container_command = tkinter.Frame(master=main_window)
container_command_buttons = tkinter.Frame(master=container_command)
button_run = tkinter.Button(master=container_command_buttons, height=1)
button_execute = tkinter.Button(master=container_command_buttons, height=1, text='clear logs', command=set_log_update)
text_result = tkinter.Text(master=container_command, height=1, state='disabled', padx=10, pady=10)  # Scrolled

# container_menu = tkinter.Frame(master=main_window)  # , width=CONTAINER_WIDTH
# container_menu.grid(row=1, column=1, sticky='w')
button_menu_mods = tkinter.Button(master=container_command_buttons, text="mods", command=set_window_mods)
button_menu_back = tkinter.Button(master=container_command_buttons, text="back", state='disabled')
button_menu_settings = tkinter.Button(master=container_command_buttons, text='edit settings',
                                      command=set_window_settings)

# container_file_buttons = tkinter.Frame(master=container_file_content)
# container_file_buttons.grid(row=1, column=1, sticky='w')
# button_file_load = tkinter.Button(master=container_file_buttons, text="reload", command=command_file_load)
# button_file_load.grid(row=1, column=1)
# button_file_save = tkinter.Button(master=container_file_buttons, text="save", command=command_file_save)
# button_file_save.grid(row=1, column=2)
button_function_duplicate = tkinter.Button(master=container_command_buttons, text="remove duplicates",
                                           command=set_window_duplicates)
button_function_find = tkinter.Button(master=container_command_buttons, text="find string",
                                      command=set_window_find)
button_function_replace = tkinter.Button(master=container_command_buttons, text="replace string",
                                         command=set_window_replace)

container_function_selected = tkinter.Frame(master=main_window)  # , width=CONTAINER_WIDTH

container_file_content = tkinter.Frame(master=container_function_selected)
text_file_content = tkinter.Text(master=container_file_content, width=TEXT_WIDTH, height=30)  # Scrolled
text_file_content.bind('<KeyPress>', set_text_color)

container_settings = tkinter.Frame(master=container_function_selected)
list_labels_settings = []
list_entry_settings = []
row_counter = 0
for setting in settings:
    list_labels_settings.append(tkinter.Label(master=container_settings, text=setting))
    list_entry_settings.append(tkinter.Entry(master=container_settings))
command_settings_reload()
# button_settings_save = tkinter.Button(master=container_settings, text='save', command=command_settings_save)
# button_settings_save.grid(row=row_counter, column=1)

container_mods = tkinter.Frame(master=container_function_selected)
label_mods_idle = tkinter.Label(master=container_mods, text="available mods:", width=UNIT_WIDTH)
list_mods_idle = ColumnedListbox(master=container_mods, width=LIST_WIDTH, height=10)
list_mods_idle.bind('<<TreeviewSelect>>', selected_mod_idle)
list_mods_idle.bind('<Double-1>', command_mod_open)
container_mod_buttons = tkinter.Frame(master=container_mods, pady=7)
button_mod_activate = tkinter.Button(master=container_mod_buttons, text="activate mod", command=command_activate_mod)
button_mod_deactivate = tkinter.Button(master=container_mod_buttons, text="deactivate mod",
                                       command=command_deactivate_mod)
button_mod_reload = tkinter.Button(master=container_mod_buttons, text="reload mod", command=command_reload_mod)
button_mod_reload.config(state='disabled')
button_mod_open = tkinter.Button(master=container_mod_buttons, text="open mod", command=command_mod_open,
                                 state='disabled')
button_mod_copy = tkinter.Button(master=container_mod_buttons, text="copy mod", command=command_copy_mod,
                                 state='disabled')
button_mod_new = tkinter.Button(master=container_mod_buttons, text="new mod", command=command_new_mod)
button_mod_edit = tkinter.Button(master=container_mod_buttons, text="edit mod data", command=set_window_mod_editor,
                                 state='disabled')

label_mods_active = tkinter.Label(master=container_mods, text="active mods:", width=UNIT_WIDTH)
list_mods_active = ColumnedListbox(master=container_mods, width=LIST_WIDTH, height=10)
list_mods_active.bind('<<TreeviewSelect>>', selected_mod_active)
list_mods_active.bind('<Double-1>', command_mod_open)

container_mod_editor = tkinter.Frame(master=container_function_selected)
list_labels_mod_editor = []
list_text_mod_editor = []
for key in default_mod.parameter:
    list_labels_mod_editor.append(tkinter.Label(master=container_mod_editor, text=key))
    list_text_mod_editor.append(tkinter.Text(master=container_mod_editor, height=2))
# button_save_mod = tkinter.Button(master=container_mod_editor, text='save', command=command_edit_mod)
# button_save_mod.grid(row=level_counter, column=1)

container_directories = tkinter.Frame(master=container_function_selected)
label_directory = tkinter.Label(master=container_directories)
# button_function_move = tkinter.Button(master=container_directories, text='move file', state='disabled',
#                                       command=set_window_move)
# button_function_move.grid(row=2, column=1)
list_directory = tkinter.Listbox(master=container_directories, width=LIST_WIDTH, height=20)
list_directory.bind('<<ListboxSelect>>', on_select_list_directory)
list_directory.bind('<Double-1>', on_double_click_list_directory)

container_select_file = tkinter.Frame(master=container_function_selected)
label_file_select = tkinter.Label(master=container_select_file, text="in file:")
button_file_select = tkinter.Button(master=container_select_file, text="select another file",
                                    command=command_select_file)
text_file_select = tkinter.Text(master=container_select_file, width=TEXT_WIDTH, height=3)  # Scrolled

container_folder_select = tkinter.Frame(master=container_function_selected)
label_folder_select = tkinter.Label(master=container_folder_select, text="in folder:")
button_folder_select = tkinter.Button(master=container_folder_select, text="select folder",
                                      command=command_select_folder)
text_folder_select = tkinter.Text(master=container_folder_select, height=3)  # Scrolled

container_find = tkinter.Frame(master=container_function_selected)
label_find = tkinter.Label(master=container_find, text="find string:")
text_find = tkinter.Text(master=container_find, height=3)  # Scrolled

container_replace = tkinter.Frame(master=container_function_selected)
button_replace_copy = tkinter.Button(master=container_replace, text="copy string", command=command_copy_find)
label_replace = tkinter.Label(master=container_replace, text="replace with string:")
text_replace = tkinter.Text(master=container_replace, height=3)  # Scrolled

# container_command = tkinter.Frame(master=main_window)
# container_command.grid(row=3, column=1, sticky='w')
# entry_command = tkinter.Entry(master=container_command, state='disabled')
# entry_command.grid(row=1, column=1)

containers = [
    # container_menu,
    container_function_selected,
    container_settings,
    container_mods,
    container_mod_buttons,
    container_mod_editor,
    container_directories,
    container_file_content,
    # container_file_buttons,
    container_select_file,
    container_folder_select,
    container_find,
    container_replace,
    container_command,
    container_command_buttons
]
small_buttons = [
    button_menu_back,
]
large_buttons = [
    button_menu_settings,
    # button_settings_save,
    button_mod_activate,
    button_mod_deactivate,
    button_mod_reload,
    button_mod_open,
    button_mod_new,
    button_mod_copy,
    button_mod_edit,
    # button_function_move,
    button_replace_copy,
    # button_file_load,
    # button_file_save,
    button_menu_mods,
    button_file_select,
    button_folder_select,
    button_function_duplicate,
    button_function_find,
    button_function_replace,
    button_run,
    button_execute
]
radio_buttons = [
]
labels = [
    label_mods_idle,
    label_mods_active,
    label_directory,
    label_file_select,
    label_find,
    label_replace,
    label_folder_select
]
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
    text_folder_select,
    # entry_command
]
entries = []
for setting_entry in list_entry_settings:
    entries.append(setting_entry)
for parameter_entry in list_text_mod_editor:
    entries.append(parameter_entry)

if GRID:
    for button in large_buttons:
        button.configure(width=UNIT_WIDTH, justify='left')
    for label in labels:
        label.configure(width=UNIT_WIDTH, padx=5, pady=5)
    label_directory.configure(width=TEXT_WIDTH)
    for text in texts:
        text.configure(width=TEXT_WIDTH)
    for entry in entries:
        entry.configure(width=TEXT_WIDTH)
    # entry_command.configure(width=TEXT_WIDTH + 2 * UNIT_WIDTH)
    for container in containers:
        container.configure(padx=5, pady=5)
else:
    for button in large_buttons:
        button.place_configure(width=UNIT_WIDTH, height=UNIT_HEIGHT)
    for label in labels:
        label.place_configure(width=UNIT_WIDTH, height=UNIT_HEIGHT)
    label_directory.place_configure(width=TEXT_WIDTH)
    for text in texts:
        text.place_configure(width=TEXT_WIDTH)
    for entry in entries:
        entry.place_configure(width=TEXT_WIDTH)
    # for container in containers:
        # container.place_configure(width=2000, height=800)

if GRID:
    container_command_buttons.grid(row=1, column=1, sticky='w')
    button_run.grid(row=1, column=2)
    button_execute.grid(row=1, column=3)
    text_result.grid(row=2, column=1, columnspan=10)
    button_menu_mods.grid(row=1, column=4)
    button_menu_back.grid(row=1, column=1)
    button_menu_settings.grid(row=1, column=10)
    button_function_duplicate.grid(row=1, column=5)
    button_function_find.grid(row=1, column=6)
    button_function_replace.grid(row=1, column=7)
    container_function_selected.grid(row=2, column=1, sticky='w')
    text_file_content.grid(row=2, column=1, columnspan=6)
    container_settings.grid(row=1, column=1, sticky='w')
    label_mods_idle.grid(row=1, column=1)
    list_mods_idle.grid(row=1, column=2)
    container_mod_buttons.grid(row=2, column=2, sticky='w')
    button_mod_activate.grid(row=2, column=1)
    button_mod_deactivate.grid(row=2, column=2)
    button_mod_reload.grid(row=2, column=3)
    button_mod_open.grid(row=2, column=4)
    button_mod_copy.grid(row=2, column=5)
    button_mod_new.grid(row=2, column=6)
    button_mod_edit.grid(row=2, column=7)
    label_mods_active.grid(row=3, column=1)
    list_mods_active.grid(row=3, column=2)
    label_directory.grid(row=1, column=1, columnspan=2)
    list_directory.grid(row=2, column=1)
    label_file_select.grid(row=1, column=1)
    button_file_select.grid(row=2, column=1)
    text_file_select.grid(row=1, rowspan=2, column=2)
    label_folder_select.grid(row=1, column=1)
    button_folder_select.grid(row=2, column=1)
    text_folder_select.grid(row=1, rowspan=2, column=2)
    label_find.grid(row=1, column=1)
    text_find.grid(row=1, column=2)
    button_replace_copy.grid(row=1, column=1)
    label_replace.grid(row=2, column=1)
    text_replace.grid(row=1, column=2, rowspan=2)
    row_counter = 0
    for setting in settings:
        list_labels_settings[-1].grid(row=row_counter, column=1)
        list_entry_settings[-1].grid(row=row_counter, column=2)
        row_counter += 1
    level_counter = 1
    for key in default_mod.parameter:
        list_labels_mod_editor[-1].grid(row=level_counter, column=1)
        list_text_mod_editor[-1].grid(row=level_counter, column=2)
        if 'description' in key:
            list_text_mod_editor[-1].configure(height=8)
        level_counter += 1
else:
    container_function_selected.place(x=0, y=0, width=FULL_WIDTH, height=UNIT_HEIGHT*13)
    text_file_content.place(x=int(UNIT_WIDTH*0.5), y=0, width=TEXT_WIDTH, height=UNIT_HEIGHT*12)
    label_mods_idle.place(x=0, y=int(UNIT_HEIGHT*2.5), width=UNIT_WIDTH, height=UNIT_HEIGHT)
    list_mods_idle.place(x=UNIT_WIDTH, y=0, width=TEXT_WIDTH, height=UNIT_HEIGHT*5)
    container_mod_buttons.place(x=UNIT_WIDTH*0, y=UNIT_HEIGHT*5+5, width=FULL_WIDTH, height=UNIT_HEIGHT+10)
    button_mod_new.place(x=UNIT_WIDTH*0, y=0)
    button_mod_activate.place(x=UNIT_WIDTH*1, y=0)
    # button_mod_deactivate.place(x=UNIT_WIDTH*2, y=0)
    # button_mod_reload.place(x=UNIT_WIDTH*3, y=0)
    # button_mod_open.place(x=UNIT_WIDTH*4, y=0)
    # button_mod_copy.place(x=UNIT_WIDTH*5, y=0)
    # button_mod_edit.place(x=UNIT_WIDTH*6, y=0)
    label_mods_active.place(x=0, y=int(UNIT_HEIGHT*9), width=UNIT_WIDTH, height=UNIT_HEIGHT)
    list_mods_active.place(x=UNIT_WIDTH, y=int(UNIT_HEIGHT*6.5), width=TEXT_WIDTH, height=UNIT_HEIGHT*5)
    label_directory.place(x=0, y=0, width=TEXT_WIDTH, height=UNIT_HEIGHT)
    list_directory.place(x=int(UNIT_WIDTH*0.5), y=UNIT_HEIGHT, width=TEXT_WIDTH, height=UNIT_HEIGHT*10)
    label_file_select.place(x=0, y=0)
    button_file_select.place(x=0, y=UNIT_HEIGHT)
    text_file_select.place(x=UNIT_WIDTH, y=UNIT_HEIGHT*0, width=TEXT_WIDTH, height=UNIT_HEIGHT*2)
    label_folder_select.place(x=0, y=0)
    button_folder_select.place(x=0, y=UNIT_HEIGHT)
    text_folder_select.place(x=UNIT_WIDTH, y=0, width=TEXT_WIDTH, height=UNIT_HEIGHT*2)
    label_find.place(x=0, y=0, width=UNIT_WIDTH, height=UNIT_HEIGHT)
    text_find.place(x=UNIT_WIDTH, y=0, width=TEXT_WIDTH, height=UNIT_HEIGHT)
    # container_replace.place(x=0, y=UNIT_HEIGHT*3, width=TEXT_WIDTH, height=UNIT_HEIGHT*2)
    button_replace_copy.place(x=0, y=0)
    label_replace.place(x=0, y=UNIT_HEIGHT)
    text_replace.place(x=UNIT_WIDTH, y=0, width=TEXT_WIDTH, height=UNIT_HEIGHT*2)
    text_result.place(x=0, y=0, width=FULL_WIDTH, height=UNIT_HEIGHT)
    container_command_buttons.place(x=0, y=UNIT_HEIGHT*2, anchor='sw', width=FULL_WIDTH, height=UNIT_HEIGHT)
    button_menu_back.place(x=0, y=0)
    button_menu_mods.place(x=int(UNIT_WIDTH*0.5), y=0)
    button_menu_settings.place(x=int(UNIT_WIDTH*1.5), y=0)
    button_run.place(x=int(UNIT_WIDTH*2.5), y=0)
    button_execute.place(x=int(UNIT_WIDTH*3.5), y=0)
    button_function_duplicate.place(x=int(UNIT_WIDTH*4.5), y=0)
    button_function_find.place(x=int(UNIT_WIDTH*5.5), y=0)
    button_function_replace.place(x=int(UNIT_WIDTH*6.5), y=0)
    for index in range(len(settings)):
        list_labels_settings[index].place(x=0, y=UNIT_HEIGHT*index, width=UNIT_WIDTH, height=UNIT_HEIGHT)
        list_entry_settings[index].place(x=UNIT_WIDTH+10, y=UNIT_HEIGHT*index, width=TEXT_WIDTH, height=UNIT_HEIGHT)
    for index in range(len(default_mod.parameter)):
        list_labels_mod_editor[index].place(x=0, y=UNIT_HEIGHT*index, width=UNIT_WIDTH, height=UNIT_HEIGHT)
        list_text_mod_editor[index].place(x=UNIT_WIDTH+10, y=UNIT_HEIGHT*index, width=TEXT_WIDTH, height=UNIT_HEIGHT)
    list_text_mod_editor[-1].place_configure(height=UNIT_HEIGHT*4)

if GRAPHICAL_MODE:

    FONT = ('Lato', 11, 'normal')
    SMALL_BUTTON_WIDTH = 80
    LARGE_BUTTON_WIDTH = 160
    BACKGROUND_COLOR = '#2e4a60'
    ENTRY_BACKGROUND_COLOR = '#253B4D'
    TEXT_COLORS = ['#A8E3F5', '#6BAACE', '#5285AB', '#253B4D']
    INI_LEVELS_COLORS = ['#6BAACE', '#7E5FAB', '#AB5A5B', '#AB9061', '#95AB74']

    main_window.configure(background=BACKGROUND_COLOR)

    """https://stackoverflow.com/questions/67444141/how-to-change-the-title-bar-in-tkinter"""
    from ctypes import windll, byref, sizeof, c_int
    main_window.update()
    HWND = windll.user32.GetParent(main_window.winfo_id())
    # This attribute is for Windows 11
    DWMWA_CAPTION_COLOR = 35
    COLOR_1 = 0x004d3b25  # color should be in hex order: 0x00bbggrr
    windll.dwmapi.DwmSetWindowAttribute(HWND, DWMWA_CAPTION_COLOR, byref(c_int(COLOR_1)), sizeof(c_int))

    image_button_small_idle = tkinter.PhotoImage(file=r'aesthetic\rotwk_button_small_idle.png')
    # image_button_small_hover = tkinter.PhotoImage(file=r'aesthetic\rotwk_button_small_hover.png')
    # image_button_small_pressed = tkinter.PhotoImage(file=r'aesthetic\rotwk_button_small_pressed.png')
    image_button_large_idle = tkinter.PhotoImage(file=r'aesthetic\rotwk_button_large_idle.png')
    # image_button_large_hover = tkinter.PhotoImage(file=r'aesthetic\rotwk_button_large_hover.png')
    # image_button_large_pressed = tkinter.PhotoImage(file=r'aesthetic\rotwk_button_large_pressed.png')

    for container in containers:
        container.configure(background=BACKGROUND_COLOR)
    for button in small_buttons:
        button.configure(image=image_button_small_idle, compound='center', foreground=TEXT_COLORS[0], font=FONT,
                         border=0, width=SMALL_BUTTON_WIDTH, height=40, background=BACKGROUND_COLOR,
                         activebackground=BACKGROUND_COLOR)
    for button in large_buttons:
        button.configure(image=image_button_large_idle, compound='center', foreground=TEXT_COLORS[0], font=FONT,
                         border=0, background=BACKGROUND_COLOR, width=LARGE_BUTTON_WIDTH, height=40,
                         activebackground=BACKGROUND_COLOR, disabledforeground=TEXT_COLORS[2])
    # for button in radio_buttons:
    #     button.configure(image=image_button_large_idle, compound='center', foreground=TEXT_COLORS[0], font=FONT,
    #                      border=0, width=LARGE_BUTTON_WIDTH, height=40, background=BACKGROUND_COLOR,
    #                      selectimage=image_button_large_hover, tristateimage=image_button_large_pressed,
    #                      activebackground=BACKGROUND_COLOR, activeforeground=TEXT_COLORS[0],
    #                      disabledforeground=TEXT_COLORS[2])
    for label in labels:
        label.configure(background=BACKGROUND_COLOR, foreground=TEXT_COLORS[0], font=FONT,
                        width=int(LARGE_BUTTON_WIDTH / 10))
    label_directory.configure(width=LARGE_BUTTON_WIDTH, height=2)
    for text in texts:
        text.configure(background=ENTRY_BACKGROUND_COLOR, foreground=TEXT_COLORS[0], font=FONT,
                       selectbackground=TEXT_COLORS[0], selectforeground=TEXT_COLORS[-1])
    for entry in entries:
        entry.configure(background=ENTRY_BACKGROUND_COLOR, foreground=TEXT_COLORS[0], font=FONT,
                        selectbackground=TEXT_COLORS[0], selectforeground=TEXT_COLORS[-1],
                        )  # disabledbackground=BACKGROUND_COLOR, disabledforeground=TEXT_COLORS[0])
    text_result.configure(foreground=TEXT_COLORS[1])
    # text_file_content.configure(height=35)
    list_directory.configure(background=ENTRY_BACKGROUND_COLOR, foreground=TEXT_COLORS[0], font=FONT,
                             width=LARGE_BUTTON_WIDTH, selectbackground=TEXT_COLORS[0],
                             selectforeground=TEXT_COLORS[-1])

    current_style = tkinter.ttk.Style(master=main_window)
    current_style.theme_use('clam')
    tkinter.ttk.Style().configure('.', width=LARGE_BUTTON_WIDTH, font=FONT,
                                  foreground=TEXT_COLORS[0], background=ENTRY_BACKGROUND_COLOR)
    tkinter.ttk.Style().configure('Treeview', background=ENTRY_BACKGROUND_COLOR,
                                  selectbackground=TEXT_COLORS[0], selectforeground=TEXT_COLORS[-1],
                                  fieldbackground=ENTRY_BACKGROUND_COLOR, fieldbw=0)
    tkinter.ttk.Style().configure('Treeview.Heading', borderwidth=0,
                                  overbackground=TEXT_COLORS[0], overforeground=TEXT_COLORS[-1])

set_window_mods()
main_window.mainloop()
