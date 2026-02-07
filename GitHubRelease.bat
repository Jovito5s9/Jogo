@echo off
setlocal

set APP_NAME=RadioRoots
set ARCH=x64
set VERSION=1.1.0

set DIST_DIR=dist\%APP_NAME%
set RELEASE_NAME=%APP_NAME%-windows-%ARCH%-V%VERSION%
set ZIP_NAME=%RELEASE_NAME%.zip

call packaging\build.bat

if not exist "%DIST_DIR%" (
    echo ❌ Build falhou
    exit /b 1
)

echo 📦 Preparando release pro GitHub...

cd dist
powershell Compress-Archive "%APP_NAME%" "%ZIP_NAME%"
cd ..

echo ✅ Release Windows pronta!
echo dist\%ZIP_NAME%
pause
