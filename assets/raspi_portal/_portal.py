"""Captive-portal orchestrator: hotspot → HTTP form → connect → reboot."""

import subprocess
import sys
import time

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
    _allow_unprivileged_port_80()

    print("[PORTAL] Creating hotspot…")
    try:
        create_hotspot()
    except Exception as exc:
        print(f"[PORTAL] Failed to create hotspot: {exc}", file=sys.stderr)
        try:
            from pikaraoke_ui import show_error  # type: ignore[import]
            show_error(
                f"❌ No internet found and hotspot setup failed.\n{exc}\n"
                "Please connect manually and restart."
            )
        except Exception:
            pass
        return

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

    print(f"[PORTAL] HTTP server starting on http://{PORTAL_IP}:{_PORT}")
    server, result_queue = run_server(PORTAL_IP, _PORT)

    # Block until the user submits the form
    ssid, password = result_queue.get()
    print(f"[PORTAL] Credentials received for SSID: '{ssid}'")

    # Give the browser a moment to fully receive the confirmation page before
    # the hotspot disappears
    time.sleep(2)
    stop_server(server)

    print("[PORTAL] Tearing down hotspot…")
    teardown_hotspot()

    print(f"[PORTAL] Connecting to '{ssid}'…")
    connect_wifi(ssid, password)

    print("[PORTAL] Rebooting in 10 seconds…")
    time.sleep(10)
    subprocess.run(["sudo", "reboot"], check=False)
