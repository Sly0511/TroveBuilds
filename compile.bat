@ECHO OFF
echo Compiling executable file
"C:\Users\raycu\Desktop\Projects\Trove Builds\venv\Scripts\pyinstaller.exe" --noconsole --onefile --add-data="assets;assets" --add-data="data;data" --add-data="locales;locales" main.py>nul
echo "Compilation of executable done successfully
pause