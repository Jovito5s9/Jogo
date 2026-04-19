@echo off
setlocal

set APP_NAME=RadioRoots
set ENTRY_POINT=main.py

echo Limpando builds antigos...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist %APP_NAME%.spec del %APP_NAME%.spec

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo Buildando EXE (ONEFILE)...
pyinstaller ^
  --name "%APP_NAME%" ^
  --onefile ^
  --windowed ^
  --clean ^
  --icon="assets\geral\logo_RadioRoots.ico" ^
  --add-data "assets;assets" ^
  --add-data "saved;saved" ^
  --add-data "content;content" ^
  "%ENTRY_POINT%"

echo.
echo Build final pronto em:
echo dist\%APP_NAME%.exe
echo.

pause