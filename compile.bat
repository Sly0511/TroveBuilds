@ECHO OFF
echo Compiling executable file
pyinstaller --noconsole --onefile --add-data="assets;assets" --add-data="data;data" --add-data="locales;locales" main.py>nul
echo "Compilation of executable done successfully
pause