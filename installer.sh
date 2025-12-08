#!/bin/bash

# TV Garden Installer for Enigma2
# Usage: wget -q --no-check-certificate "https://raw.githubusercontent.com/Belfagor2005/TVGarden/main/installer.sh" -O - | /bin/sh

version='1.0'
changelog='Init Project'

TMPPATH=/tmp/TVGarden-install
FILEPATH=/tmp/TVGarden-main.tar.gz

echo ""
echo "****************************************************"
echo "*          TV Garden Installation Script           *"
echo "****************************************************"
echo ""

# Cleanup function
cleanup() {
    echo "[INFO] Cleaning up temporary files..."
    [ -d "$TMPPATH" ] && rm -rf "$TMPPATH"
    [ -f "$FILEPATH" ] && rm -f "$FILEPATH"
    [ -d "/tmp/TVGarden-main" ] && rm -rf "/tmp/TVGarden-main"
    sync
}

# Trap signals for cleanup
trap cleanup EXIT INT TERM

# Detect OS
detect_os() {
    if [ -f /var/lib/dpkg/status ]; then
        OSTYPE="DreamOS"
        STATUS="/var/lib/dpkg/status"
    elif [ -f /etc/opkg/opkg.conf ] || [ -f /var/lib/opkg/status ]; then
        OSTYPE="OE-Angelic"
        STATUS="/var/lib/opkg/status"
    elif [ -f /etc/opkg/status ]; then
        OSTYPE="OE"
        STATUS="/etc/opkg/status"
    else
        OSTYPE="Unknown"
        STATUS=""
    fi
    echo "[INFO] Detected OS type: $OSTYPE"
}

detect_os

# Check root
if [ $(id -u) -ne 0 ]; then
    echo "[ERROR] This script must be run as root!"
    exit 1
fi

# Clean and prepare
cleanup
mkdir -p "$TMPPATH"

# Check wget
if ! command -v wget >/dev/null 2>&1; then
    echo "[INFO] Installing wget..."
    case "$OSTYPE" in
        "DreamOS")
            apt-get update && apt-get install -y wget || { echo "[ERROR] Failed to install wget"; exit 1; }
            ;;
        "OE"|"OE-Angelic")
            opkg update && opkg install wget || { echo "[ERROR] Failed to install wget"; exit 1; }
            ;;
        *)
            echo "[ERROR] Unsupported OS type. Cannot install wget."
            exit 1
            ;;
    esac
fi

# Detect Python version
if python --version 2>&1 | grep -q '^Python 3\.'; then
    echo "[INFO] Python3 detected"
    PYTHON="PY3"
    Packagesix="python3-six"
    Packagerequests="python3-requests"
else
    echo "[INFO] Python2 detected"
    PYTHON="PY2"
    Packagerequests="python-requests"
    Packagesix="python-six"
fi

# Install package function
install_pkg() {
    local pkg=$1
    echo "[INFO] Checking for $pkg..."
    
    if [ -z "$STATUS" ] || ! grep -qs "Package: $pkg" "$STATUS" 2>/dev/null; then
        echo "[INFO] Installing $pkg..."
        case "$OSTYPE" in
            "DreamOS")
                apt-get update && apt-get install -y "$pkg" || echo "[WARNING] Could not install $pkg, continuing..."
                ;;
            "OE"|"OE-Angelic")
                opkg update && opkg install "$pkg" || echo "[WARNING] Could not install $pkg, continuing..."
                ;;
            *)
                echo "[WARNING] Cannot install $pkg on unknown OS type, continuing..."
                ;;
        esac
    else
        echo "[INFO] $pkg already installed"
    fi
}

# Install required Python packages
echo "[INFO] Installing required packages..."
if [ "$PYTHON" = "PY3" ]; then
    install_pkg "$Packagesix"
fi
install_pkg "$Packagerequests"

# Install multimedia packages for OE
if [ "$OSTYPE" != "DreamOS" ]; then
    echo "[INFO] Installing multimedia packages..."
    for pkg in ffmpeg exteplayer3; do
        install_pkg "$pkg"
    done
fi

# Download TV Garden
echo "[INFO] Downloading TV Garden from GitHub..."
wget --no-check-certificate 'https://github.com/Belfagor2005/TVGarden/archive/refs/heads/main.tar.gz' -O "$FILEPATH"
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to download TVGarden package!"
    exit 1
fi

echo "[INFO] Extracting package..."
tar -xzf "$FILEPATH" -C "$TMPPATH"
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to extract TVGarden package!"
    exit 1
fi

# Determine plugin path
if [ -d /usr/lib64 ]; then
    PLUGINPATH="/usr/lib64/enigma2/python/Plugins/Extensions/TVGarden"
else
    PLUGINPATH="/usr/lib/enigma2/python/Plugins/Extensions/TVGarden"
fi

echo "[INFO] Plugin will be installed to: $PLUGINPATH"

# Remove old installation if exists
if [ -d "$PLUGINPATH" ]; then
    echo "[INFO] Removing old installation..."
    rm -rf "$PLUGINPATH"
fi

# Install plugin
echo "[INFO] Installing plugin files..."
mkdir -p "$PLUGINPATH"

# Find source directory
SRCPATH=""
if [ -d "$TMPPATH/TVGarden-main/TVGarden" ]; then
    SRCPATH="$TMPPATH/TVGarden-main/TVGarden"
elif [ -d "$TMPPATH/TVGarden-main" ]; then
    SRCPATH="$TMPPATH/TVGarden-main"
elif [ -d "$TMPPATH/TVGarden-main/usr/lib/enigma2/python/Plugins/Extensions/TVGarden" ]; then
    SRCPATH="$TMPPATH/TVGarden-main/usr/lib/enigma2/python/Plugins/Extensions/TVGarden"
fi

if [ -n "$SRCPATH" ] && [ -d "$SRCPATH" ]; then
    cp -r "$SRCPATH"/* "$PLUGINPATH/" 2>/dev/null
    echo "[INFO] Copied plugin files successfully"
else
    echo "[ERROR] Could not find plugin files in extracted archive!"
    echo "[DEBUG] Looking in: $TMPPATH"
    find "$TMPPATH" -type f -name "*.py" | head -5
    exit 1
fi

# Set permissions
echo "[INFO] Setting permissions..."
chmod -R 755 "$PLUGINPATH"
find "$PLUGINPATH" -name "*.sh" -exec chmod 755 {} \;
find "$PLUGINPATH" -name "*.py" -exec chmod 644 {} \;

sync

# Verify installation
echo "[INFO] Verifying installation..."
if [ -f "$PLUGINPATH/plugin.py" ] && [ -f "$PLUGINPATH/__init__.py" ]; then
    echo "[SUCCESS] TV Garden installed successfully!"
    echo "[INFO] Plugin path: $PLUGINPATH"
else
    echo "[ERROR] Installation verification failed!"
    echo "[DEBUG] Files in plugin directory:"
    ls -la "$PLUGINPATH/" 2>/dev/null | head -10
    exit 1
fi

# Display system info
echo ""
echo "****************************************************"
echo "*           Installation Complete!                 *"
echo "****************************************************"
echo ""

BOX_NAME=$(cat /etc/hostname 2>/dev/null || echo "Unknown")
IMAGE_NAME=$(grep '^distro=' /etc/image-version 2>/dev/null | cut -d= -f2 || echo "Unknown")
IMAGE_VERSION=$(grep '^version=' /etc/image-version 2>/dev/null | cut -d= -f2 || echo "Unknown")
PYTHON_VERSION=$(python --version 2>&1 || echo "Unknown")

cat <<EOF
Debug Information:
-----------------
Box Model:     $BOX_NAME
OS Type:       $OSTYPE
Python:        $PYTHON_VERSION
Image:         $IMAGE_NAME $IMAGE_VERSION
Plugin Version: $version
Install Path:  $PLUGINPATH
EOF

echo ""
echo "[INFO] Restarting Enigma2 in 5 seconds..."
echo "[INFO] You can find TV Garden in the plugins menu"
echo ""

sleep 5

# Restart Enigma2
if command -v systemctl >/dev/null 2>&1; then
    systemctl restart enigma2
elif command -v init >/dev/null 2>&1; then
    init 4 && sleep 2 && init 3
elif command -v killall >/dev/null 2>&1; then
    killall -9 enigma2
else
    echo "[WARNING] Could not restart Enigma2 automatically"
    echo "[INFO] Please restart your receiver manually"
fi

exit 0