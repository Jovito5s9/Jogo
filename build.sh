#!/bin/bash
set -e

APP_NAME="RadioRoots"
ENTRY_POINT="main.py"

echo "🧹 Limpando builds antigos..."
rm -rf build dist "$APP_NAME.spec"

echo "🐍 Ativando ambiente virtual..."
source venv/bin/activate

echo "📦 Buildando ELF com PyInstaller..."
pyinstaller \
  --name "$APP_NAME" \
  --onedir \
  --windowed \
  --clean \
  --icon="assets/geral/logo_RadioRoots.png" \
  --add-data "assets:assets" \
  --add-data "saved:saved" \
  --add-data "content:content" \
  "$ENTRY_POINT"
python "$ENTRY_POINT"

echo "📄 Copiando run.sh..."
cp packaging/run.sh "dist/$APP_NAME/run.sh"
chmod +x "dist/$APP_NAME/run.sh"

echo "copiando o install.sh"
cp packaging/install.sh "dist/$APP_NAME/install.sh"
chmod +x "dist/$APP_NAME/install.sh"

echo "🔐 Ajustando permissões do ELF..."
chmod +x "dist/$APP_NAME/$APP_NAME"

echo "✅ Build final pronto em dist/$APP_NAME/"