#!/bin/sh

echo "===================================="
echo " Uninstalling IP Hunter for OpenWrt"
echo "===================================="

# stop running process (jika ada)
pkill -f modpes.py 2>/dev/null
pkill -f android.py 2>/dev/null

# remove binaries
rm -f /usr/bin/modpes.py
rm -f /usr/bin/android.py

# remove LuCI files
rm -f /usr/lib/lua/luci/controller/ip_hunter.lua
rm -f /usr/lib/lua/luci/view/ip_hunter.htm

# remove temp & state files
rm -f /tmp/ip-hunter.log
rm -f /tmp/ip-hunter.stop

# clear LuCI cache
rm -rf /tmp/luci-*

# restart LuCI services
/etc/init.d/rpcd restart
/etc/init.d/uhttpd restart

echo "===================================="
echo " IP Hunter uninstalled successfully"
echo "===================================="
