pyinstaller window_console.py ^
 --onefile --windowed ^
 --name lord_of_the_mods ^
 --icon="aesthetic\lotr-icon1.ico" ^
 --add-data="aesthetic\rotwk_button_large_idle.png:img" ^
 --add-data="aesthetic\rotwk_button_small_idle.png:img" ^
 --collect-submodules mods_enabler.py ^
 --collect-submodules file_editor.py ^
 --collect-submodules file_interpreter.py ^
 --collect-submodules constants.py ^
 --collect-submodules settings_editor.py ^
 --distpath=""
REM  --splash="aesthetic\color_palette.png" ^