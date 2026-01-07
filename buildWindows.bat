@echo off
setlocal

set APP_NAME=RadioRoots
set ENTRY_POINT=main.py

echo 🧹 Limpando builds antigos...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist %APP_NAME%.spec del %APP_NAME%.spec

echo 🐍 Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo 📦 Buildando EXE com PyInstaller...
pyinstaller ^
  --name "%APP_NAME%" ^
  --onedir ^
  --windowed ^
  --clean ^
  --icon="assets\geral\logo_RadioRoots.ico" ^
  --add-data "assets;assets" ^
  --add-data "saved;saved" ^
  "%ENTRY_POINT%"

echo 📄 Copiando run.bat...
copy packaging\run.bat dist\%APP_NAME%\run.bat >nul

echo 📄 Copiando install.bat...
copy packaging\install.bat dist\%APP_NAME%\install.bat >nul

echo 🔐 Permissões OK (Windows não precisa chmod)

echo ✅ Build final pronto em dist\%APP_NAME%
pause
