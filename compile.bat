@ECHO OFF
echo Compiling executable file
"C:\Users\raycu\Desktop\Projects\Trove Builds\venv\Scripts\flet.exe" pack --icon="assets/favicon.ico" --add-data="assets;assets" --add-data="data;data" --add-data="locales;locales" --product-name="Trove Calculation Tool" --file-description="Trove Calculation Tool" --product-version="1.0" --file-version="1.0" --company-name="Sly" --copyright="Sly"  main.py>nul
echo "Compilation of executable done successfully
pause