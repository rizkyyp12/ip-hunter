#!/bin/sh
# =========================================
# IP Hunter Installer for OpenWrt
# Author : YourName
# =========================================

set -e

REPO_BASE="https://raw.githubusercontent.com/USERNAME/ip-hunter-openwrt/main"

echo "========================================="
echo "  Installing IP Hunter for OpenWrt"
echo "========================================="

# --- cek root ---
if [ "$(id -u)" != "0" ]; then
    echo "ERROR: Jalankan sebagai root"
    exit 1
fi

# --- cek python3 ---
if ! command -v python3 >/dev/null; then
    echo "[INFO] Installing python3..."
    opkg update
    opkg install python3
fi

# --- cek adb ---
if ! command -v adb >/dev/null; then
    echo "[INFO] Installing adb..."
    opkg update
    opkg install adb
fi

# --- download python script ---
echo "[INFO] Installing modpes.py"
wget -O /usr/bin/modpes.py "$REPO_BASE/modpes.py"
chmod +x /usr/bin/modpes.py

# --- install LuCI files ---
echo "[INFO] Installing LuCI files"

mkdir -p /usr/lib/lua/luci/controller
mkdir -p /usr/lib/lua/luci/view

wget -O /usr/lib/lua/luci/controller/ip_hunter.lua \
    "$REPO_BASE/luci/controller/ip_hunter.lua"

wget -O /usr/lib/lua/luci/view/ip_hunter.htm \
    "$REPO_BASE/luci/view/ip_hunter.htm"

# --- permission ---
chmod 644 /usr/lib/lua/luci/controller/ip_hunter.lua
chmod 644 /usr/lib/lua/luci/view/ip_hunter.htm

# --- cleanup old data ---
rm -f /tmp/ip_hunter.run
rm -f /tmp/ip_target.conf

echo "========================================="
echo "  IP Hunter Installed Successfully"
echo "========================================="
echo " LuCI Menu : Modem -> IP Hunter"
echo " Reboot LuCI jika menu belum muncul"
echo "========================================="
