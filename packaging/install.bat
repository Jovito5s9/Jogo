@echo off
setlocal

set APP_NAME=RadioRoots
set APP_ID=RadioRoots
set INSTALL_DIR=%LOCALAPPDATA%\Programs\%APP_NAME%
set START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs
set DESKTOP=%USERPROFILE%\Desktop
set ICON=%INSTALL_DIR%\assets\geral\logo_RadioRoots.ico

echo 📦 Instalando %APP_NAME%...

mkdir "%INSTALL_DIR%" >nul 2>&1

xcopy * "%INSTALL_DIR%\" /E /I /Y >nul

echo 🔗 Criando atalho no Menu Iniciar...
powershell -command ^
"$s=(New-Object -COM WScript.Shell).CreateShortcut('%START_MENU%\%APP_NAME%.lnk'); ^
$s.TargetPath='%INSTALL_DIR%\run.bat'; ^
$s.IconLocation='%ICON%,0'; ^
$s.Save()"

echo 🔗 Criando atalho na Área de Trabalho...
powershell -command ^
"$s=(New-Object -COM WScript.Shell).CreateShortcut('%DESKTOP%\%APP_NAME%.lnk'); ^
$s.TargetPath='%INSTALL_DIR%\run.bat'; ^
$s.IconLocation='%ICON%'; ^
$s.Save()"

echo ✅ %APP_NAME% instalado com sucesso!
echo 🎮 Procure por "%APP_NAME%" no Menu Iniciar
pause
