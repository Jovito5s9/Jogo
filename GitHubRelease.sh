#!/bin/bash
set -e
APP_NAME="RadioRoots"
ARCH="x86_64"
VERSION="1.0.0"

DIST_DIR="dist/$APP_NAME"
RELEASE_NAME="$APP_NAME-linux-$ARCH-V$VERSION"
ZIP_NAME="$RELEASE_NAME.zip"

./build.sh

if [ ! -d "$DIST_DIR"]; then
    echo "build falhou"
    exit 1
fi

echo "preparanado o release pro GitHub"

cd dist
zip -r "$ZIP_NAME" "$APP_NAME"
cd ..

echo "release linux pro GitHub pronta"
echo "dist/$ZIP_NAME"