#!/bin/bash
set -e

APP_NAME="RadioRoots"
APP_ID="RadioRoots"
INSTALL_DIR="$HOME/.local/opt/$APP_NAME"
DESKTOP_FILE="$HOME/.local/share/applications/$APP_ID.desktop"
ICON_PATH="$INSTALL_DIR/_internal/assets/geral/logo_RadioRoots.png"

echo "📦 Instalando $APP_NAME..."

# Cria diretórios
mkdir -p "$INSTALL_DIR"
mkdir -p "$HOME/.local/share/applications"

# Copia arquivos do jogo
cp -r ./* "$INSTALL_DIR"

# Garante permissões
chmod +x "$INSTALL_DIR/RadioRoots"
chmod +x "$INSTALL_DIR/run.sh"

# Cria arquivo .desktop
cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Name=$APP_NAME
Comment=Jogo feito em Python e Kivy
Exec=$INSTALL_DIR/run.sh
Icon=$ICON_PATH
Terminal=false
Type=Application
Categories=Game;
EOF

chmod +x "$DESKTOP_FILE"

echo "✅ $APP_NAME instalado com sucesso!"
echo "🎮 Procure por '$APP_NAME' no menu do sistema."