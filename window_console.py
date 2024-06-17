import os.path
import _tkinter
import tkinter
from tkinter import messagebox
from tkinter.filedialog import askopenfilenames, askdirectory
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Treeview
# from PIL import Image, ImageTk  # installed pillow

from mods_enabler import load_mods, edit_mod, activate_mod, deactivate_mod, reload_mod, create_mod
from file_editor import find_text, replace_text, move_file, duplicates_commenter, load_file, load_directories
from common import INI_COMMENTS, GAME_PATH, WORLDBUILDER_PATH

INI_LEVELS_COLORS = ['green', 'blue', 'violet', 'red', 'orange']
CONTAINER_WIDTH = 150
COLUMN_WIDTH = 11
BUTTON_WIDTH = 10
SCROLLEDTEXT_WIDTH = 150 - 3
TEXT_WIDTH = 150
LIST_WIDTH = 200

# GRAPHICAL_MODE = None
GRAPHICAL_MODE = True

mods = []
current_path = ''
current_levels = []
current_file_content_backup = ''
new_mod_name = ''


class ColumnedListbox(tkinter.ttk.Treeview):
    def __init__(self, master, width, height, show='headings'):  # , **kw
        super().__init__(master=master, height=height, show=show)
        # Treeview.__init__(self, master, **kw)
        # self.show = show
        # self.height = height
        self.width = width * 6
        self.columns_list = ("name", "status", "contains_mods", "description")
        self.build_list()
        self.set_columns_proportions(proportions=(2, 1, 2, 7))

    def build_list(self):
        vertical_scrollbar = tkinter.ttk.Scrollbar(master=self, orient="vertical", command=self.yview)
        # vertical_scrollbar.pack()
        # horizontal_scrollbar = tkinter.ttk.Scrollbar(orient="horizontal", command=self.xview)
        self.configure(yscrollcommand=vertical_scrollbar.set)  # , xscrollcommand=horizontal_scrollbar.set
        self.configure(columns=self.columns_list)
        for column in self.columns_list:
            self.heading(column, text=column)

    def set_columns_proportions(self, proportions):
        total_quotient = sum(proportions)
        for column_index in range(len(proportions)):
            self.column(self.columns_list[column_index], width=int(self.width / total_quotient
                                                                   * proportions[column_index]))


def launch_game():
    os.system(GAME_PATH)


def launch_game_editor():
    os.system(WORLDBUILDER_PATH)


def warning_file_save():
    file_named = text_file_select.get("1.0", tkinter.END).replace('/', '\\').strip('\n\t {}')
    if file_named and current_file_content_backup:
        if text_file_content.get("1.0", tkinter.END).strip() != current_file_content_backup.strip():
            save_file = messagebox.askquestion("Question", "Do you want to save the file?")
            if save_file == 'yes':
                command_save_file()


def clear_window():
    global current_file_content_backup
    warning_file_save()
    current_file_content_backup = ''
    container_directories.grid_remove()
    container_mods.grid_remove()
    container_find.grid_remove()
    container_replace.grid_remove()
    container_folder_select.grid_remove()
    container_file_select.grid_remove()
    container_file_content.grid_remove()
    container_result.grid_remove()
    container_settings.grid_remove()


def set_window_find():
    global current_key_to_command
    current_key_to_command = text_editor_key_to_command.copy()
    clear_window()
    container_find.grid(row=1, column=1)
    container_file_select.grid(row=2, column=1)
    container_result.grid(row=3, column=1)
    button_menu_back.config(command=set_window_file)
    try:
        selection = text_file_content.selection_get()
        text_find.delete("1.0", tkinter.END)
        text_find.insert("1.0", selection)
    except UnboundLocalError:
        pass
    button_run.configure(text="find", command=command_run_find)
    command_run_find()
    text_result.focus()


def set_window_replace():
    global current_key_to_command
    current_key_to_command = text_editor_key_to_command.copy()
    clear_window()
    container_find.grid(row=1, column=1)
    container_replace.grid(row=2, column=1)
    container_file_select.grid(row=3, column=1)
    container_result.grid(row=4, column=1)
    button_menu_back.config(command=set_window_file)
    try:
        selection = text_file_content.selection_get()
        text_find.delete("1.0", tkinter.END)
        text_find.insert("1.0", selection)
    except UnboundLocalError:
        pass
    button_run.configure(text="replace", command=command_run_replace)
    button_run.focus()


def set_window_duplicates():
    global current_key_to_command
    current_key_to_command = text_editor_key_to_command.copy()
    clear_window()
    container_file_select.grid(row=1, column=1)
    container_result.grid(row=5, column=1)
    button_menu_back.configure(command=set_window_file)
    selected_file = f'{label_directory.cget("text")}/{list_directory.selection_get()}'
    text_file_select.delete('1.0', 'end')
    text_file_select.insert('1.0', selected_file)
    button_run.configure(text="remove\nduplicates", command=command_run_duplicate)
    button_run.focus()


def set_window_move():
    global current_key_to_command, current_path
    current_key_to_command = text_editor_key_to_command.copy()
    clear_window()
    container_file_select.grid(row=1, column=1)
    container_folder_select.grid(row=2, column=1)
    container_result.grid(row=5, column=1)
    button_menu_back.configure(command=command_directory_back)
    label_file_select.configure(text='file')
    text_file_select.delete('1.0', 'end')
    current_path = f'{label_directory.cget("text")}/{list_directory.selection_get()}'
    text_file_select.insert('1.0', current_path)
    label_folder.configure(text='to folder')
    button_run.configure(text="move", command=command_run_move)
    button_run.focus()


def set_window_file():
    global current_key_to_command
    clear_window()
    # container_file_select.grid(row=1, column=1)
    container_file_content.grid(row=2, column=1, sticky='w')
    # container_result.grid(row=3, column=1)
    button_menu_back.config(command=command_directory_back)
    current_key_to_command = text_editor_key_to_command
    text_file_content.focus()


def set_window_mods():
    global current_key_to_command
    current_key_to_command = mod_key_to_command.copy()
    clear_window()
    container_mods.grid(row=1, column=1)
    # container_result.grid(row=5, column=1)
    text_result.configure(height=1)
    button_run.configure(text='launch game', command=launch_game)
    button_menu_mods.configure(text='mods')
    button_menu_new.configure(state=tkinter.NORMAL)
    button_menu_back.configure(state=tkinter.DISABLED)
    refresh_mods()
    list_mods_idle.focus_set()
    list_mods_idle.selection_set(list_mods_idle.get_children()[0])
    list_mods_idle.focus(list_mods_idle.get_children()[0])


def set_window_directories():
    global current_key_to_command
    current_key_to_command = browser_key_to_command.copy()
    clear_window()
    container_directories.grid(row=1, column=1)
    # container_result.grid(row=5, column=1)
    open_directory_item()  # command_directory_forward()
    button_menu_back.config(command=command_directory_back)
    button_menu_new.configure(state=tkinter.DISABLED)
    list_directory.focus()


def set_window_settings():
    global current_key_to_command
    current_key_to_command = text_editor_key_to_command.copy()
    clear_window()
    container_settings.grid(row=1, column=1)


def command_select_folder():
    selected_folder = askdirectory()
    text_folder.delete('1.0', tkinter.END)
    text_folder.insert(tkinter.END, selected_folder)


def command_select_file():
    selected_file = askopenfilenames()
    text_file_select.delete('1.0', tkinter.END)
    text_file_select.insert(tkinter.END, selected_file)


def set_text_color(event=None):
    level_colors = INI_LEVELS_COLORS
    text_lines = text_file_content.get("1.0", tkinter.END).split('\n')
    for line in text_lines:
        # for word in line.split(' '):
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
    # pass


def command_load_file():
    global current_levels, current_file_content_backup
    text_file_content.delete("1.0", tkinter.END)
    file_loaded = text_file_select.get("1.0", tkinter.END).replace('/', '\\').strip('\n\t {}')
    try:
        output, current_levels = load_file(full_path=file_loaded)
        current_file_content_backup = output
    except TypeError:
        output = 'cannot open this file type'
    text_file_content.insert(tkinter.END, output)
    set_text_color()


def command_save_file():
    global current_file_content_backup
    content_to_save = text_file_content.get("1.0", tkinter.END)
    file_named = text_file_select.get("1.0", tkinter.END).replace('/', '\\').strip().replace('{', '').replace('}', '')
    with open(file_named, 'w') as file_overwritten:  # .replace('.ini', '_new.ini')
        file_overwritten.write(content_to_save)
    current_file_content_backup = content_to_save


def command_run_find():
    find = text_find.get("1.0", tkinter.END).strip()
    in_file = text_file_select.get("1.0", tkinter.END).replace('/', '\\').strip()
    output = find_text(find, in_file)
    print(output)
    text_result.insert(tkinter.END, output)


def command_copy_find():
    find = text_find.get("1.0", tkinter.END).strip()
    text_replace.delete("1.0", "end")
    text_replace.insert("1.0", find)


def command_run_replace():
    find = text_find.get("1.0", tkinter.END).strip()
    replace_with = text_replace.get("1.0", tkinter.END).strip()
    in_file = text_folder.get("1.0", tkinter.END).replace('/', '\\').strip()
    output = replace_text(find, replace_with, in_file)
    print(output)
    text_result.insert(tkinter.END, output)


def command_run_move():
    files_named = text_file_select.get("1.0", tkinter.END).replace('/', '\\').strip()
    to_folder = text_folder.get("1.0", tkinter.END).replace('/', '\\').strip()
    output = ''
    for file_named in files_named.split('} {'):
        file_named = file_named.replace('{', '').replace('}', '')
        output += move_file(file_named, to_folder)
        print(output)
    text_result.insert(tkinter.END, output)


def command_run_duplicate():
    file_named = text_folder.get("1.0", tkinter.END).replace('/', '\\').strip()
    output = duplicates_commenter(in_file=file_named)
    text_result.insert(tkinter.END, output)


def selected_mod_idle(event):
    global current_path
    global current_key_to_command
    current_key_to_command['<Return>'] = command_open_mod
    button_mod_deactivate.config(state=tkinter.DISABLED)
    button_mod_activate.config(state=tkinter.NORMAL)
    button_mod_reload.config(state=tkinter.DISABLED)
    button_mod_open.config(state=tkinter.NORMAL)
    try:
        current_path = "O:/_MODULES/" + list_mods_idle.item(list_mods_idle.selection()[0], 'values')[0]
        list_mods_active.selection_remove(list_mods_active.selection()[0])
    except IndexError:
        pass


def selected_mod_active(event):
    global current_path
    global current_key_to_command
    current_key_to_command['<Return>'] = command_open_mod
    button_mod_activate.config(state=tkinter.DISABLED)
    button_mod_deactivate.config(state=tkinter.NORMAL)
    button_mod_reload.config(state=tkinter.NORMAL)
    button_mod_open.config(state=tkinter.NORMAL)
    try:
        current_path = "O:/_MODULES/" + list_mods_active.item(list_mods_active.selection()[0], 'values')[0]
        # list_mods_active.get(list_mods_active.curselection())
        list_mods_idle.selection_remove(list_mods_idle.selection()[0])
    # except _tkinter.TclError:
    #     pass
    except IndexError:
        pass


def refresh_mods():
    global mods
    mods = load_mods()
    list_mods_active.delete(*list_mods_active.get_children())  # (0, tkinter.END)
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
    button_mod_deactivate.config(state=tkinter.DISABLED)
    button_mod_activate.config(state=tkinter.DISABLED)


def command_new_mod():
    global new_mod_name
    first_run = True

    def command_confirm_name(event=None):
        global new_mod_name
        new_mod_name = provide_name_text.get()
        window_provide_name.quit()
        window_provide_name.destroy()

    while new_mod_name in [mod.name for mod in mods] or first_run:
        window_provide_name = tkinter.Tk()
        provide_name_label = tkinter.Label(master=window_provide_name, width=100, text="Please provide a name:")
        provide_name_label.grid(row=1, column=1)
        if not first_run:
            provide_name_label.configure(text="Please provide a new name that is not used already")
        provide_name_text = tkinter.Entry(master=window_provide_name, width=100)
        provide_name_text.grid(row=2, column=1)
        window_provide_name.bind('<Return>', command_confirm_name)
        provide_name_button = tkinter.Button(master=window_provide_name, width=BUTTON_WIDTH, text="confirm",
                                             command=command_confirm_name)
        provide_name_button.grid(row=3, column=1)
        window_provide_name.mainloop()
        first_run = False
    if new_mod_name:
        print(create_mod(new_mod_name))
        refresh_mods()
        new_mod_name = ''
    else:
        print("error command_new_mod")


def command_activate_mod():
    global mods
    try:
        mod_selected = list_mods_idle.item(list_mods_idle.focus(), 'values')[0]
        for mod in mods:
            if mod.name == mod_selected:
                activate_mod(mod)  # TODO: save these logs
                edit_mod(mod, mod_is_active='yes')
                return refresh_mods()
        print("error command_activate_mod: mod not found")
    except _tkinter.TclError:
        print("error command_activate_mod: TclError")


def command_deactivate_mod():
    global mods
    try:
        mod_selected = list_mods_active.item(list_mods_active.focus(), 'values')[0]
        # list_mods_active.get(list_mods_active.curselection())
        for mod in mods:
            if mod.name == mod_selected:
                deactivate_mod(mod)  # TODO: save these logs
                edit_mod(mod, mod_is_active='no')
                refresh_mods()
                return
        print("error command_deactivate_mod: mod not found")
    except _tkinter.TclError:
        print("error command_deactivate_mod: TclError")


def command_reload_mod():
    global mods
    try:
        mod_selected = list_mods_active.item(list_mods_active.focus(), 'values')[0]
        for mod in mods:
            if mod.name == mod_selected:
                reload_mod(mod)  # TODO: save these logs
                refresh_mods()
                return
        print("error command_deactivate_mod: mod not found")
    except _tkinter.TclError:
        print("error command_reload_mod: TclError")


def command_open_mod(event=None):
    # global current_key_to_command
    button_menu_mods.configure(text="return to mods")
    set_window_directories()
    # current_key_to_command['<Return>'] = command_directory_forward


def command_directory_back():
    global current_path
    global current_key_to_command
    if len(current_path) > len("O:/_MODULES"):
        current_path = current_path[:current_path.rfind('/')]
        if main_window.focus_get() == list_directory:
            open_directory_item()
        else:
            set_window_directories()
    if len(current_path) <= len("O:/_MODULES"):
        # print(f'permission denied to escape {current_path}')
        button_menu_back.configure(state=tkinter.DISABLED)
        current_key_to_command['<BackSpace>'] = set_window_mods
    # current_key_to_command['<Return>'] = command_directory_forward
    current_key_to_command = browser_key_to_command.copy()


def on_select_list_directory(event=None):
    global current_path
    # print(event)
    if string_select_mode.get() == 'browsing':
        command_directory_forward()
        # open_directory_item()  # event=event
    elif string_select_mode.get() == 'selection':
        # open_directory_item()
        pass


def command_directory_forward():
    global current_path
    try:
        item_selected = list_directory.get(list_directory.curselection())
        current_path += '/' + item_selected
    except _tkinter.TclError:
        print("error: open_directory_item 1")
    open_directory_item()


def open_directory_item():  # event=None
    if os.path.isdir(current_path):
        list_directory.delete(0, tkinter.END)
        output_folders, output_files = load_directories(current_path)
        item_index = 0
        for output_folder in output_folders:
            list_directory.insert(item_index, output_folder)
            list_directory.itemconfig(item_index, foreground=INI_LEVELS_COLORS[1])
            item_index += 1
        for output_file in output_files:
            list_directory.insert(item_index, output_file)
            list_directory.itemconfig(item_index,
                                      foreground=INI_LEVELS_COLORS[2] if output_file[-len('.ini'):] == '.ini' else INI_LEVELS_COLORS[3])
            item_index += 1
        list_directory.selection_set(0)
        list_directory.activate(0)
    elif os.path.isfile(current_path):
        text_file_select.delete("1.0", tkinter.END)
        text_file_select.insert(tkinter.END, current_path)
        set_window_file()
        command_load_file()
    label_directory.configure(text=current_path)
    button_menu_back.configure(state=tkinter.NORMAL)


def use_selected_text(event=None):
    try:
        selection = text_file_content.selection_get()
        if event.keysym == 'f':
            text_find.delete("1.0", tkinter.END)
            text_find.insert("1.0", selection)
            set_window_find()
        elif event.keysym == 'r':
            text_find.delete("1.0", tkinter.END)
            text_find.insert("1.0", selection)
            set_window_replace()
        else:
            pass
    except UnboundLocalError:
        print("error use_selected_text: selection seems empty")


def focus_on_next_item():
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
        # if list_mods_active.focus():
        #     list_mods_active.selection_remove(list_mods_active.focus())
        # else:
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


mod_key_to_command = {
    '<Return>': command_directory_forward,
    '<Right>': focus_on_next_item,
    '<Left>': focus_on_next_item,
}
browser_key_to_command = {
    '<Return>': command_directory_forward,
    '<BackSpace>': command_directory_back,
    '<Escape>': set_window_mods,
    # '<Down>': focus_on_next_item,
    # '<Up>': focus_on_next_item
}
text_editor_key_to_command = {
    '<Escape>': command_directory_back
}
current_key_to_command = {
    '<Return>': set_window_mods,
}


def press_key_in_current_mode(event=None):
    if f'<{event.keysym}>' in current_key_to_command:
        current_key_to_command[f'<{event.keysym}>']()
    else:
        # print(f'{event.keysym} not bound')
        print(f'<{event.keysym}>')
        pass


main_window = tkinter.Tk()
main_window.title("Lord of the mods")
# main_window.minsize(width=1300, height=400)
# main_window.maxsize(width=1600, height=900)
main_window.geometry('1400x700')
main_window.configure(padx=10, pady=10)

main_window.bind_all('<Control-Key-f>', use_selected_text)
main_window.bind_all('<Control-Key-r>', use_selected_text)
main_window.bind('<Key>', press_key_in_current_mode)

container_menu = tkinter.Frame(master=main_window, width=CONTAINER_WIDTH, padx=10)
container_menu.grid(row=1, column=1, sticky='w')
button_menu_mods = tkinter.Button(master=container_menu, text="mods", width=BUTTON_WIDTH * 2, command=set_window_mods)
button_menu_mods.grid(row=1, column=1)
button_menu_new = tkinter.Button(master=container_menu, text="new", width=BUTTON_WIDTH, command=command_new_mod,
                                 state=tkinter.DISABLED)
button_menu_new.grid(row=1, column=2)
button_menu_back = tkinter.Button(master=container_menu, text="back", width=BUTTON_WIDTH, state=tkinter.DISABLED)
button_menu_back.grid(row=1, column=3)

container_radio_browsing_mode = tkinter.Frame(master=container_menu, width=50, padx=10)
container_radio_browsing_mode.grid(row=1, column=4, sticky='w')
string_select_mode = tkinter.StringVar()
button_menu_select_mode = tkinter.Radiobutton(master=container_radio_browsing_mode, text="selection",
                                              width=BUTTON_WIDTH, justify='left',
                                              value='selection', variable=string_select_mode)
button_menu_select_mode.grid(row=0, column=4)
button_menu_browse_mode = tkinter.Radiobutton(master=container_radio_browsing_mode, text="quick browsing",
                                              width=BUTTON_WIDTH, justify='left',
                                              value='browsing', variable=string_select_mode)
button_menu_browse_mode.grid(row=1, column=4)
string_select_mode.set('selection')

button_menu_settings = tkinter.Button(master=container_menu, text='settings', width=BUTTON_WIDTH,
                                      command=set_window_settings)
button_menu_settings.grid(row=1, column=10)

container_function_selected = tkinter.Frame(master=main_window, width=CONTAINER_WIDTH)
container_function_selected.grid(row=2, column=1, sticky='w')

# TODO: edit settings like game paths
container_settings = tkinter.Frame(master=container_function_selected)
container_settings.grid(row=1, column=1)
label_settings_main_path = tkinter.Label(master=container_settings, text='game path', width=COLUMN_WIDTH)
label_settings_main_path.grid(row=1, column=1)
text_settings_main_path = tkinter.Entry(master=container_settings, width=TEXT_WIDTH)
text_settings_main_path.insert('end', GAME_PATH)
text_settings_main_path.grid(row=1, column=2)
label_settings_editor_path = tkinter.Label(master=container_settings, text='editor path', width=COLUMN_WIDTH)
label_settings_editor_path.grid(row=2, column=1)
text_settings_editor_path = tkinter.Entry(master=container_settings, width=TEXT_WIDTH)
text_settings_editor_path.insert('end', WORLDBUILDER_PATH)
text_settings_editor_path.grid(row=2, column=2)

container_mods = tkinter.Frame(master=container_function_selected)
label_mods_idle = tkinter.Label(master=container_mods, text="available mods:", width=COLUMN_WIDTH)
label_mods_idle.grid(row=1, column=1)
list_mods_idle = ColumnedListbox(master=container_mods, width=LIST_WIDTH, height=10)
list_mods_idle.bind('<<TreeviewSelect>>', selected_mod_idle)
list_mods_idle.grid(row=1, column=2)
container_mod_buttons = tkinter.Frame(master=container_mods)
container_mod_buttons.grid(row=2, column=2, sticky='w')
button_mod_activate = tkinter.Button(master=container_mod_buttons, text="activate", command=command_activate_mod)
button_mod_activate.grid(row=2, column=1)
button_mod_deactivate = tkinter.Button(master=container_mod_buttons, text="deactivate", command=command_deactivate_mod)
button_mod_deactivate.grid(row=2, column=2)
button_mod_reload = tkinter.Button(master=container_mod_buttons, text="reload", command=command_reload_mod)
button_mod_reload.config(state=tkinter.DISABLED)
button_mod_reload.grid(row=2, column=3)
button_mod_open = tkinter.Button(master=container_mod_buttons, text="open", command=command_open_mod,
                                 state=tkinter.DISABLED)
button_mod_open.grid(row=2, column=4)
# TODO: button mod copy
# TODO: edit mod parameters
label_mods_active = tkinter.Label(master=container_mods, text="active mods:", width=COLUMN_WIDTH)
label_mods_active.grid(row=3, column=1)
list_mods_active = ColumnedListbox(master=container_mods, width=LIST_WIDTH, height=10)
list_mods_active.bind('<<TreeviewSelect>>', selected_mod_active)
list_mods_active.grid(row=3, column=2)

container_directories = tkinter.Frame(master=container_function_selected)
label_directory = tkinter.Label(master=container_directories, width=TEXT_WIDTH)
label_directory.grid(row=1, column=1, columnspan=2)
button_function_move = tkinter.Button(master=container_directories, text="move", width=BUTTON_WIDTH,
                                      command=set_window_move)
button_function_move.grid(row=2, column=1)
list_directory = tkinter.Listbox(master=container_directories, width=LIST_WIDTH, height=20)
list_directory.bind('<<ListboxSelect>>', on_select_list_directory)
list_directory.grid(row=2, column=2, rowspan=10)

container_file_content = tkinter.Frame(master=container_function_selected)
button_file_load = tkinter.Button(master=container_file_content, text="load", width=BUTTON_WIDTH,
                                  command=command_load_file)
button_file_load.grid(row=1, column=1)
button_file_save = tkinter.Button(master=container_file_content, text="save", width=BUTTON_WIDTH,
                                  command=command_save_file)
button_file_save.grid(row=1, column=2)
button_function_duplicate = tkinter.Button(master=container_file_content, text="remove duplicates",
                                           width=BUTTON_WIDTH * 2, command=set_window_duplicates)
button_function_duplicate.grid(row=1, column=3)
button_function_find = tkinter.Button(master=container_file_content, text="find phrase", width=BUTTON_WIDTH,
                                      command=set_window_find)
button_function_find.grid(row=1, column=4)
button_function_replace = tkinter.Button(master=container_file_content, text="replace phrase", width=BUTTON_WIDTH,
                                         command=set_window_replace)
button_function_replace.grid(row=1, column=5)
text_file_content = ScrolledText(master=container_file_content, width=TEXT_WIDTH, height=40)
text_file_content.grid(row=2, column=1, columnspan=6)
text_file_content.bind('<KeyPress>', set_text_color)

container_file_select = tkinter.Frame(master=container_function_selected)
label_file_select = tkinter.Label(master=container_file_select, text="in file:", width=COLUMN_WIDTH)
label_file_select.grid(row=1, column=1)
button_file_select = tkinter.Button(master=container_file_select, text="select another file", width=BUTTON_WIDTH * 2,
                                    command=command_select_file)
button_file_select.grid(row=2, column=1)
text_file_select = ScrolledText(master=container_file_select, width=TEXT_WIDTH, height=3)
text_file_select.grid(row=1, rowspan=2, column=2)

container_folder_select = tkinter.Frame(master=container_function_selected)
label_folder = tkinter.Label(master=container_folder_select, text="in folder:", width=COLUMN_WIDTH)
label_folder.grid(row=1, column=1)
button_folder = tkinter.Button(master=container_folder_select, text="select folder", width=BUTTON_WIDTH,
                               command=command_select_folder)
button_folder.grid(row=2, column=1)
text_folder = ScrolledText(master=container_folder_select, width=TEXT_WIDTH, height=3)
text_folder.grid(row=1, rowspan=2, column=2)

container_find = tkinter.Frame(master=container_function_selected)
label_find = tkinter.Label(master=container_find, text="find:", width=COLUMN_WIDTH)
label_find.grid(row=1, column=1)
text_find = ScrolledText(master=container_find, width=TEXT_WIDTH, height=3)
text_find.grid(row=1, column=2)

container_replace = tkinter.Frame(master=container_function_selected)
button_replace_copy = tkinter.Button(master=container_replace, text="copy", command=command_copy_find)
button_replace_copy.grid(row=1, column=1)
label_replace = tkinter.Label(master=container_replace, text="replace with:", width=COLUMN_WIDTH)
label_replace.grid(row=2, column=1)
text_replace = ScrolledText(master=container_replace, width=TEXT_WIDTH, height=3)
text_replace.grid(row=2, column=2)

# TODO: use this container as overall log output or make another for it
container_result = tkinter.Frame(master=container_function_selected)
button_run = tkinter.Button(master=container_result, width=BUTTON_WIDTH, height=2)
button_run.grid(row=1, column=1)
text_result = ScrolledText(master=container_result, width=SCROLLEDTEXT_WIDTH, height=10)
text_result.grid(row=1, column=2)

if GRAPHICAL_MODE:

    FONT = ('Lato', 11, 'normal')
    SMALL_BUTTON_WIDTH = 80
    LARGE_BUTTON_WIDTH = 160
    BACKGROUND_COLOR = '#2e4a60'
    ENTRY_BACKGROUND_COLOR = '#253B4D'
    TEXT_COLORS = ['#A8E3F5', '#6BAACE', '#5285AB', '#253B4D']
    INI_LEVELS_COLORS = ['#6BAACE', '#9E68AB', '#AB5A5B', '#AB9061', '#95AB74']

    # main_window.configure(background='blue')
    main_window.configure(background=BACKGROUND_COLOR)

    image_button_small_idle = tkinter.PhotoImage(file=r'aesthetic\rotwk_button_small_idle.png')
    # image_button_small_idle = ImageTk.PhotoImage(Image.open(r'aesthetic\rotwk_button_small_idle.png'))
    image_button_small_hover = tkinter.PhotoImage(file=r'aesthetic\rotwk_button_small_hover.png')
    image_button_small_pressed = tkinter.PhotoImage(file=r'aesthetic\rotwk_button_small_pressed.png')
    image_button_large_idle = tkinter.PhotoImage(file=r'aesthetic\rotwk_button_large_idle.png')
    image_button_large_hover = tkinter.PhotoImage(file=r'aesthetic\rotwk_button_large_hover.png')
    image_button_large_pressed = tkinter.PhotoImage(file=r'aesthetic\rotwk_button_large_pressed.png')

    containers = [
        container_menu,
        container_function_selected,
        container_settings,
        container_mods,
        container_mod_buttons,
        container_radio_browsing_mode,
        container_directories,
        container_file_content,
        container_file_select,
        container_folder_select,
        container_find,
        container_replace,
        container_result
    ]
    small_buttons = [
        button_menu_new,
        button_menu_back,
        button_menu_settings,
        button_mod_activate,
        button_mod_deactivate,
        button_mod_reload,
        button_mod_open,
        button_function_move,
        button_replace_copy,
        button_file_load,
        button_file_save
    ]
    large_buttons = [
        button_menu_mods,
        button_file_select,
        button_folder,
        button_function_duplicate,
        button_function_find,
        button_function_replace,
        button_run
    ]
    radio_buttons = [
        button_menu_select_mode,
        button_menu_browse_mode
    ]
    labels = [
        label_settings_main_path,
        label_settings_editor_path,
        label_mods_idle,
        label_mods_active,
        label_directory,
        label_file_select,
        label_find,
        label_replace,
        label_folder
    ]
    entries = [
        text_settings_main_path,
        text_settings_editor_path,
        text_result,
        text_find,
        text_replace,
        text_file_content,
        text_file_select,
        text_folder
    ]

    for container in containers:
        container.configure(background=BACKGROUND_COLOR)
    for button in small_buttons:
        button.configure(image=image_button_small_idle, compound='center', foreground=TEXT_COLORS[0], font=FONT, border=0,
                         width=SMALL_BUTTON_WIDTH, height=40, background=BACKGROUND_COLOR,
                         activebackground=BACKGROUND_COLOR)
    for button in large_buttons:
        button.configure(image=image_button_large_idle, compound='center', foreground=TEXT_COLORS[0], font=FONT, border=0,
                         width=LARGE_BUTTON_WIDTH, height=40, background=BACKGROUND_COLOR,
                         activebackground=BACKGROUND_COLOR)
    for button in radio_buttons:
        button.configure(image=image_button_large_idle, compound='center', foreground=TEXT_COLORS[0], font=FONT,
                         border=0, width=LARGE_BUTTON_WIDTH, height=40, background=BACKGROUND_COLOR,
                         selectimage=image_button_large_hover, tristateimage=image_button_large_pressed,
                         activebackground=BACKGROUND_COLOR, activeforeground=TEXT_COLORS[0],
                         disabledforeground=TEXT_COLORS[2])
    for label in labels:
        label.configure(background=BACKGROUND_COLOR, foreground=TEXT_COLORS[0], font=FONT,
                        width=int(LARGE_BUTTON_WIDTH/10))
    label_directory.configure(width=LARGE_BUTTON_WIDTH, height=2)
    for entry in entries:
        entry.configure(background=ENTRY_BACKGROUND_COLOR, foreground=TEXT_COLORS[0], font=FONT,
                        selectbackground=TEXT_COLORS[0], selectforeground=TEXT_COLORS[-1])
    text_file_content.configure(height=35)
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

    # Treeview frame not changeable:
    # https://tcl.tk/man/tcl8.6/TkCmd/ttk_treeview.htm#M82

    # text_file_content.vbar.configure(bg=ENTRY_BACKGROUND_COLOR)
    # scrollbar not changeable:
    # https://stackoverflow.com/questions/6965260/how-ro-change-a-tkinter-scrolledtext-widgets-scrollbar-color

main_window.mainloop()
