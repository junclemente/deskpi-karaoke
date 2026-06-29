"""nmcli helpers for the captive-portal hotspot."""

import subprocess
import time

HOTSPOT_CON_NAME = "pikaraoke-portal"
HOTSPOT_SSID = "PiKaraoke-Setup"
HOTSPOT_PASS = "pikaraoke"
PORTAL_IP = "192.168.4.1"
_PORTAL_SUBNET = "192.168.4.1/24"
_IFACE = "wlan0"


def _nmcli(*args, check=False, capture=True):
    return subprocess.run(
        ["sudo", "nmcli"] + list(args),
        capture_output=capture,
        text=True,
        check=check,
    )


def create_hotspot():
    """Create and activate a WPA2 access point at PORTAL_IP via NetworkManager."""
    # Remove any leftover connection from a previous interrupted run
    _nmcli("connection", "delete", HOTSPOT_CON_NAME)

    _nmcli(
        "connection", "add",
        "type", "wifi",
        "ifname", _IFACE,
        "con-name", HOTSPOT_CON_NAME,
        "ssid", HOTSPOT_SSID,
        "802-11-wireless.mode", "ap",
        "802-11-wireless-security.key-mgmt", "wpa-psk",
        "802-11-wireless-security.psk", HOTSPOT_PASS,
        "ipv4.method", "shared",
        "ipv4.addresses", _PORTAL_SUBNET,
        "ipv6.method", "disabled",
        check=True,
    )
    _nmcli("connection", "up", HOTSPOT_CON_NAME, check=True)
    # Give NM and dnsmasq time to come up before we bind the socket
    time.sleep(3)


def teardown_hotspot():
    """Remove the hotspot connection profile and release wlan0."""
    _nmcli("connection", "delete", HOTSPOT_CON_NAME)
    time.sleep(2)


def connect_wifi(ssid: str, password: str) -> bool:
    """Connect wlan0 to the given SSID.  Returns True on success."""
    # Trigger a fresh scan so NM can see the target network
    _nmcli("device", "wifi", "rescan", "ifname", _IFACE)
    time.sleep(3)

    result = _nmcli(
        "device", "wifi", "connect", ssid,
        "password", password,
        "ifname", _IFACE,
    )
    if result.returncode == 0:
        print(f"[PORTAL] Connected to '{ssid}'")
        return True
    print(f"[PORTAL] nmcli connect failed: {result.stderr.strip()}")
    return False
