#!/bin/sh

BASE_URL="https://raw.githubusercontent.com/rizkyyp12/ip-hunter/main.py"

echo "===================================="
echo " Installing IP Hunter for OpenWrt"
echo "===================================="

# modpes.py
wget -O /usr/bin/modpes.py "$BASE_URL/modpes.py" || exit 1
chmod +x /usr/bin/modpes.py

# android.py
wget -O /usr/bin/android.py "$BASE_URL/android.py" || exit 1
chmod +x /usr/bin/android.py

# LuCI controller
mkdir -p /usr/lib/lua/luci/controller
wget -O /usr/lib/lua/luci/controller/ip_hunter.lua \
"$BASE_URL/luci/controller/ip_hunter.lua" || exit 1

# LuCI view
mkdir -p /usr/lib/lua/luci/view
wget -O /usr/lib/lua/luci/view/ip_hunter.htm \
"$BASE_URL/luci/view/ip_hunter.htm" || exit 1

# restart luci
rm -rf /tmp/luci-*
/etc/init.d/rpcd restart
/etc/init.d/uhttpd restart

echo "===================================="
echo " IP Hunter installed successfully"
echo "===================================="
