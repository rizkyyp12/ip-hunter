#!/usr/bin/env python3
import subprocess
import time
from datetime import datetime

ADB = "/usr/bin/adb"
LOG = "/tmp/android_airplane.log"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG, "a") as f:
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
    # metode lokal (lebih cepat & stabil)
    ip = run([ADB, "shell", "ip route get 8.8.8.8 | awk '{print $7}'"])
    if not ip:
        # fallback IP publik
        ip = run([ADB, "shell", "curl -s ifconfig.me"])
    return ip

def airplane(state: bool):
    val = "1" if state else "0"
    st  = "true" if state else "false"
    run([ADB, "shell", "settings", "put", "global", "airplane_mode_on", val])
    run([
        ADB, "shell", "am", "broadcast",
        "-a", "android.intent.action.AIRPLANE_MODE",
        "--ez", "state", st
    ])

# ================= MAIN =================

log("========================================")
log("        Android ADB Airplane Refresh     ")
log("========================================")

if not adb_ok():
    log("ERROR : Android device tidak terdeteksi")
    exit(1)

ip_before = get_ip()
log(f"IP Sebelum  : {ip_before if ip_before else 'UNKNOWN'}")

log("Mode pesawat ON")
airplane(True)
time.sleep(10)

log("Mode pesawat OFF")
airplane(False)
time.sleep(10)

ip_after = get_ip()
log(f"IP Sesudah  : {ip_after if ip_after else 'UNKNOWN'}")

if ip_before == ip_after:
    log("STATUS      : IP TIDAK BERUBAH")
else:
    log("STATUS      : IP BERUBAH")
