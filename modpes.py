#!/usr/bin/env python3
import subprocess
import time
import re
import os
from datetime import datetime

ADB = "/usr/bin/adb"

LOG_FILE    = "/tmp/android_airplane.log"
IP_LIST     = "/tmp/ip_hunter.list"
TARGET_FILE = "/tmp/ip_target.conf"
RUN_FLAG    = "/tmp/ip_hunter.run"

MAX_RETRY = 50
AIRPLANE_ON_DELAY  = 15
AIRPLANE_OFF_DELAY = 25


# ================= UTIL =================

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] {msg}\n")

def run(cmd):
    try:
        return subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode().strip()
    except subprocess.CalledProcessError:
        return ""

def adb_ok():
    out = run([ADB, "devices"])
    return any(line.endswith("\tdevice") for line in out.splitlines())

def root_ok():
    out = run([ADB, "shell", "su", "-c", "id"])
    return "uid=0" in out


# ================= IP =================

def get_ip():
    """
    Ambil IP dari interface default route Android
    """
    route = run([ADB, "shell", "ip", "route"])
    iface = None

    for line in route.splitlines():
        if line.startswith("default") and "dev" in line:
            iface = line.split()[line.split().index("dev") + 1]
            break

    if not iface:
        return ""

    addr = run([ADB, "shell", "ip", "addr", "show", iface])
    m = re.search(r"inet (\d+\.\d+\.\d+\.\d+)", addr)
    return m.group(1) if m else ""


# ================= AIRPLANE (ROOT) =================

def airplane_on():
    log("Airplane ON")
    run([ADB, "shell", "su", "-c",
         "settings put global airplane_mode_on 1"])
    run([ADB, "shell", "su", "-c",
         "am broadcast -a android.intent.action.AIRPLANE_MODE --ez state true"])

def airplane_off():
    log("Airplane OFF")
    run([ADB, "shell", "su", "-c",
         "settings put global airplane_mode_on 0"])
    run([ADB, "shell", "su", "-c",
         "am broadcast -a android.intent.action.AIRPLANE_MODE --ez state false"])


def refresh_ip():
    airplane_on()
    time.sleep(AIRPLANE_ON_DELAY)
    airplane_off()
    time.sleep(AIRPLANE_OFF_DELAY)


# ================= TARGET =================

def save_ip(ip):
    if not ip:
        return
    try:
        with open(IP_LIST) as f:
            if ip in f.read():
                return
    except FileNotFoundError:
        pass

    with open(IP_LIST, "a") as f:
        f.write(ip + "\n")

def load_target():
    try:
        with open(TARGET_FILE) as f:
            t = f.read().strip()
            if not t:
                return None
            return r"^" + re.escape(t)
    except:
        return None


# ================= MAIN =================

log("========================================")
log("      Android ROOT IP Hunter Start      ")
log("========================================")

if not os.path.exists(RUN_FLAG):
    log("STOP : RUN flag tidak ditemukan")
    exit(0)

if not adb_ok():
    log("ERROR : ADB device tidak terdeteksi")
    exit(1)

if not root_ok():
    log("ERROR : Android belum ROOT / su ditolak")
    exit(1)

target = load_target()
if not target:
    log("ERROR : Target IP belum diset")
    exit(1)

ip_before = get_ip()
log(f"IP AWAL : {ip_before if ip_before else 'UNKNOWN'}")

for attempt in range(1, MAX_RETRY + 1):

    if not os.path.exists(RUN_FLAG):
        log("STOP : Dihentikan manual oleh user")
        break

    ip = get_ip()
    log(f"TRY {attempt} - IP : {ip if ip else 'UNKNOWN'}")

    if ip and re.match(target, ip):
        log("STATUS : IP SESUAI TARGET ✅")
        save_ip(ip)
        break

    log("IP tidak sesuai, refresh via AIRPLANE ROOT")
    refresh_ip()
else:
    log("GAGAL : Target IP tidak didapat")

if os.path.exists(RUN_FLAG):
    os.remove(RUN_FLAG)

log("IP Hunter selesai")
