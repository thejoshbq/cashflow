#!/bin/bash

# Cashflow Desktop Application Uninstallation Script

set -e

LOCAL_APPS_DIR="$HOME/.local/share/applications"
DESKTOP_FILE="$LOCAL_APPS_DIR/cashflow.desktop"

echo "Uninstalling Cashflow Desktop Application..."

# Remove desktop file
if [ -f "$DESKTOP_FILE" ]; then
    rm "$DESKTOP_FILE"
    echo "Desktop launcher removed."
else
    echo "Desktop launcher not found."
fi

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$LOCAL_APPS_DIR"
fi

echo ""
echo "Uninstallation complete!"
echo "The application has been removed from your applications menu."
echo ""
echo "Note: The application files in $(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "are still present. You can delete them manually if desired."
