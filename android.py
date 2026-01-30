#!/usr/bin/env python3
import subprocess
import time
import sys
import re
from datetime import datetime

LOG = "/tmp/airplane_root.log"
MAX_RETRY = 10
AIRPLANE_ON_WAIT = 15
AIRPLANE_OFF_WAIT = 25


def log(msg):
    with open(LOG, "a") as f:
        f.write("[%s] %s\n" %
                (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg))


def run(cmd):
    return subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )


def fatal(msg):
    log("FATAL: " + msg)
    print("ERROR:", msg)
    sys.exit(1)


# ---------- CHECKS ----------

def check_adb():
    if run(["which", "adb"]).returncode != 0:
        fatal("adb not installed")


def check_device():
    r = run(["adb", "devices"])
    if "device" not in r.stdout.splitlines()[-1]:
        fatal("no android device detected")


def check_root():
    r = run(["adb", "shell", "su", "-c", "id"])
    if "uid=0" not in r.stdout:
        fatal("android not rooted or su denied")


# ---------- NETWORK ----------

def get_android_ip():
    r = run(["adb", "shell", "ip", "route"])
    iface = None

    for line in r.stdout.splitlines():
        if line.startswith("default") and "dev" in line:
            iface = line.split()[line.split().index("dev") + 1]
            break

    if not iface:
        return "N/A"

    r = run(["adb", "shell", "ip", "addr", "show", iface])
    m = re.search(r"inet (\d+\.\d+\.\d+\.\d+)", r.stdout)
    return m.group(1) if m else "N/A"


# ---------- AIRPLANE (ROOT) ----------

def airplane_on():
    log("Airplane ON")
    run(["adb", "shell", "su", "-c",
         "settings put global airplane_mode_on 1"])
    run(["adb", "shell", "su", "-c",
         "am broadcast -a android.intent.action.AIRPLANE_MODE --ez state true"])


def airplane_off():
    log("Airplane OFF")
    run(["adb", "shell", "su", "-c",
         "settings put global airplane_mode_on 0"])
    run(["adb", "shell", "su", "-c",
         "am broadcast -a android.intent.action.AIRPLANE_MODE --ez state false"])


# ---------- MAIN ----------

def main():
    log("===== AIRPLANE ROOT START =====")

    check_adb()
    check_device()
    check_root()

    ip_before = get_android_ip()
    log(f"IP BEFORE: {ip_before}")
    print("IP BEFORE:", ip_before)

    for i in range(1, MAX_RETRY + 1):
        log(f"TRY #{i}")

        airplane_on()
        time.sleep(AIRPLANE_ON_WAIT)

        airplane_off()
        time.sleep(AIRPLANE_OFF_WAIT)

        ip_after = get_android_ip()
        log(f"IP AFTER: {ip_after}")
        print("IP AFTER:", ip_after)

        if ip_after != "N/A" and ip_after != ip_before:
            log("SUCCESS: IP CHANGED")
            print("SUCCESS: IP CHANGED")
            log("DONE\n")
            return

        log("IP NOT CHANGED, retrying...")

    fatal("IP did not change after max retries")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log("UNHANDLED EXCEPTION: " + str(e))
        print("Runtime error, see log:", LOG)
        sys.exit(1)
