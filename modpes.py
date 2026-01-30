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
DELAY = 8


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

def get_ip():
    ip = run([ADB, "shell", "ip route get 8.8.8.8 | awk '{print $7}'"])
    if not ip:
        ip = run([ADB, "shell", "curl -s ifconfig.me"])
    return ip

def toggle_data():
    run([ADB, "shell", "svc", "data", "disable"])
    time.sleep(DELAY)
    run([ADB, "shell", "svc", "data", "enable"])
    time.sleep(DELAY)

def save_ip(ip):
    if not ip:
        return
    try:
        with open(IP_LIST, "r") as f:
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
log("        Android IP Hunter Started        ")
log("========================================")

# cek flag RUN
if not os.path.exists(RUN_FLAG):
    log("STOP : RUN flag tidak ditemukan")
    exit(0)

if not adb_ok():
    log("ERROR : ADB device tidak terdeteksi")
    exit(1)

target = load_target()
if not target:
    log("ERROR : Target IP belum diset")
    exit(1)

for attempt in range(1, MAX_RETRY + 1):

    # cek STOP setiap loop
    if not os.path.exists(RUN_FLAG):
        log("STOP : Dihentikan manual oleh user")
        break

    ip = get_ip()
    log(f"TRY {attempt} - IP : {ip if ip else 'UNKNOWN'}")

    if ip and re.match(target, ip):
        log("STATUS : IP SESUAI TARGET ✅")
        save_ip(ip)
        break

    log("IP tidak sesuai, refresh koneksi")
    toggle_data()
else:
    log("GAGAL : Target IP tidak didapat")

# cleanup
if os.path.exists(RUN_FLAG):
    os.remove(RUN_FLAG)

log("IP Hunter selesai")
