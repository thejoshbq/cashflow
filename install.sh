#!/bin/bash

# Cashflow Desktop Application Installation Script

set -e

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DESKTOP_FILE="$APP_DIR/cashflow.desktop"
LOCAL_APPS_DIR="$HOME/.local/share/applications"

echo "Installing Cashflow Desktop Application..."

# Ensure virtual environment exists
if [ ! -d "$APP_DIR/.venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$APP_DIR/.venv"
fi

# Install dependencies
echo "Installing dependencies..."
"$APP_DIR/.venv/bin/pip" install --upgrade pip
"$APP_DIR/.venv/bin/pip" install -r "$APP_DIR/requirements.txt"

# Create local applications directory if it doesn't exist
mkdir -p "$LOCAL_APPS_DIR"

# Copy desktop file to local applications
echo "Installing desktop launcher..."
cp "$DESKTOP_FILE" "$LOCAL_APPS_DIR/cashflow.desktop"
chmod +x "$LOCAL_APPS_DIR/cashflow.desktop"

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$LOCAL_APPS_DIR"
fi

echo ""
echo "Installation complete!"
echo "You can now find 'Cashflow' in your applications menu."
echo ""
echo "Note: If you don't have an icon.png file in $APP_DIR,"
echo "the desktop launcher will use a default icon. You can add"
echo "your own icon.png file to customize the appearance."
