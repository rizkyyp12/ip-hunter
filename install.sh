#!/bin/sh

BASE_URL="https://raw.githubusercontent.com/rizkyyp12/ip-hunter/main/main.py"

echo "Installing IP Hunter for OpenWrt"

# modpes.py
wget -O /usr/bin/modpes.py "$BASE_URL/modpes.py" || exit 1
chmod +x /usr/bin/modpes.py

# LuCI controller
mkdir -p /usr/lib/lua/luci/controller
wget -O /usr/lib/lua/luci/controller/ip_hunter.lua \
"$BASE_URL/luci/controller/ip_hunter.lua" || exit 1

# LuCI view
mkdir -p /usr/lib/lua/luci/view/ip_hunter
wget -O /usr/lib/lua/luci/view/ip_hunter/ip_hunter.htm \
"$BASE_URL/luci/view/ip_hunter.htm" || exit 1

# restart LuCI
rm -rf /tmp/luci-*
/etc/init.d/rpcd restart
/etc/init.d/uhttpd restart

echo "IP Hunter installed successfully"
