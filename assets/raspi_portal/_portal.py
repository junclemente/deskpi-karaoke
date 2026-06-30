"""Captive-portal orchestrator: hotspot → HTTP form → connect → reboot."""

import subprocess
import time
import traceback
from pathlib import Path

from ._hotspot import (
    HOTSPOT_PASS,
    HOTSPOT_SSID,
    PORTAL_IP,
    connect_wifi,
    create_hotspot,
    teardown_hotspot,
)
from ._server import run_server, stop_server

_PORT = 80
_LOGFILE = Path.home() / "pikaraoke_output.log"


def _plog(log, msg: str) -> None:
    """Write a timestamped line to the log file AND print it to stdout."""
    line = f"[PORTAL {time.strftime('%H:%M:%S')}] {msg}"
    print(line)
    log.write(line + "\n")
    log.flush()


def _allow_unprivileged_port_80():
    """Lower the kernel's unprivileged port floor to 80 for this boot session.

    Port 80 normally requires CAP_NET_BIND_SERVICE.  Setting this sysctl to 80
    lets any process bind it without elevated privileges.  The change reverts
    on the reboot we issue at the end of the portal flow anyway.
    """
    subprocess.run(
        ["sudo", "sysctl", "-w", "net.ipv4.ip_unprivileged_port_start=80"],
        capture_output=True,
        check=False,
    )


def _show(msg: str, duration: int = 30):
    """Best-effort Tkinter info popup (pikaraoke_ui lives in the same directory
    as autostart_pikaraoke.py, one level above this package)."""
    try:
        from pikaraoke_ui import show_info  # type: ignore[import]
        show_info(msg, duration=duration)
    except Exception:
        print(f"[PORTAL] {msg}")


def run_portal():
    """Replace the 'no internet' error path with a self-service WiFi setup portal.

    Flow
    ----
    1. Allow binding to port 80 (sysctl, reverts on reboot).
    2. Create a WPA2 hotspot named HOTSPOT_SSID via nmcli.
    3. Show a Tkinter popup telling the user what to do.
    4. Start an HTTP server at PORTAL_IP:80 and wait for the form submission.
    5. Serve a confirmation page, then tear down the hotspot.
    6. Connect wlan0 to the user's home WiFi via nmcli.
    7. Reboot after 10 seconds.
    """
    with open(_LOGFILE, "a") as log:
        _plog(log, "===== portal session start =====")
        _allow_unprivileged_port_80()

        _plog(log, "Entering create_hotspot()")
        try:
            create_hotspot(log=log)
        except Exception as exc:
            _plog(log, f"create_hotspot() FAILED: {exc}")
            log.write(traceback.format_exc())
            log.flush()
            # Belt-and-suspenders: ensure the profile is gone even if
            # create_hotspot()'s own cleanup didn't fully run.
            teardown_hotspot(log=log)
            try:
                from pikaraoke_ui import show_error  # type: ignore[import]
                show_error(
                    f"❌ No internet found and hotspot setup failed.\n{exc}\n"
                    "Please connect manually and restart."
                )
            except Exception:
                pass
            return

        _plog(log, f"Hotspot up — HTTP server starting on http://{PORTAL_IP}:{_PORT}")

        _show(
            f"📡 No internet detected.\n\n"
            f"1. Connect your phone/laptop to:\n"
            f"   WiFi: {HOTSPOT_SSID}\n"
            f"   Password: {HOTSPOT_PASS}\n\n"
            f"2. Open a browser and go to:\n"
            f"   http://{PORTAL_IP}\n\n"
            f"3. Enter your home WiFi details.",
            duration=300,  # stays up for 5 min; dismissed automatically once done
        )

        server, result_queue = run_server(PORTAL_IP, _PORT)

        # Block until the user submits the form
        _plog(log, "Waiting for WiFi credentials from portal form…")
        ssid, password = result_queue.get()
        _plog(log, f"Credentials received for SSID: '{ssid}'")

        # Give the browser a moment to fully receive the confirmation page before
        # the hotspot disappears
        time.sleep(2)
        stop_server(server)

        _plog(log, "Tearing down hotspot…")
        teardown_hotspot(log=log)

        _plog(log, f"Connecting to '{ssid}'…")
        ok = connect_wifi(ssid, password, log=log)
        if not ok:
            _plog(log, f"WARNING: connect_wifi failed for '{ssid}' — rebooting anyway")

        _plog(log, "Rebooting in 10 seconds…")
        time.sleep(10)
        subprocess.run(["sudo", "reboot"], check=False)
