"""nmcli helpers for the captive-portal hotspot."""

import subprocess
import time
from typing import IO, Optional

HOTSPOT_CON_NAME = "pikaraoke-portal"
HOTSPOT_SSID = "PiKaraoke-Setup"
HOTSPOT_PASS = "pikaraoke"
PORTAL_IP = "192.168.4.1"
_PORTAL_SUBNET = "192.168.4.1/24"
_IFACE = "wlan0"

# Arg names whose following value should be redacted in log output.
_REDACT_AFTER = {"password", "psk", "wifi-sec.psk", "802-11-wireless-security.psk"}


def _log_line(log: Optional[IO[str]], msg: str) -> None:
    if log is None:
        return
    log.write(f"[PORTAL {time.strftime('%H:%M:%S')}] {msg}\n")
    log.flush()


def _safe_args_str(args) -> str:
    """Return a loggable representation of nmcli args with passwords redacted."""
    parts = []
    redact_next = False
    for arg in args:
        if redact_next:
            parts.append("***")
            redact_next = False
        else:
            parts.append(str(arg))
            if arg in _REDACT_AFTER:
                redact_next = True
    return " ".join(parts)


def _nmcli(*args, check=False, capture=True, log: Optional[IO[str]] = None):
    cmd = ["sudo", "nmcli"] + list(args)
    _log_line(log, f"nmcli: {_safe_args_str(args)}")
    try:
        result = subprocess.run(cmd, capture_output=capture, text=True, check=check)
    except subprocess.CalledProcessError as exc:
        detail = f" stderr: {exc.stderr.strip()}" if exc.stderr and exc.stderr.strip() else ""
        _log_line(log, f"nmcli exit={exc.returncode} FAILED{detail}")
        raise
    detail = ""
    if result.returncode != 0 and hasattr(result, "stderr") and result.stderr and result.stderr.strip():
        detail = f" stderr: {result.stderr.strip()}"
    _log_line(log, f"nmcli exit={result.returncode}{detail}")
    return result


def _wait_for_ip(
    ip: str = PORTAL_IP,
    iface: str = _IFACE,
    timeout: float = 5.0,
    interval: float = 0.5,
    log: Optional[IO[str]] = None,
):
    """Poll until ip is assigned to iface, raising RuntimeError on timeout.

    nmcli reports a connection as 'up' before the kernel has finished
    assigning the address, so binding a socket immediately after
    'nmcli connection up' can fail with EADDRNOTAVAIL (Errno 99).
    """
    _log_line(log, f"_wait_for_ip: polling {iface} for {ip} (timeout={timeout:.0f}s, interval={interval}s)")
    deadline = time.time() + timeout
    attempt = 0
    while time.time() < deadline:
        attempt += 1
        result = subprocess.run(
            ["ip", "addr", "show", iface],
            capture_output=True,
            text=True,
            check=False,
        )
        found = ip in result.stdout
        _log_line(log, f"_wait_for_ip: poll {attempt} → {'found ✓' if found else 'not found'}")
        if found:
            return
        time.sleep(interval)
    msg = f"Timed out after {timeout:.0f} s waiting for {ip} on {iface}. NetworkManager reported the hotspot as up but the IP was never assigned."
    _log_line(log, f"_wait_for_ip: TIMEOUT — {msg}")
    raise RuntimeError(msg)


def create_hotspot(log: Optional[IO[str]] = None):
    """Create and activate a WPA2 access point at PORTAL_IP via NetworkManager."""
    _log_line(log, "create_hotspot: start")
    # Remove any leftover connection from a previous interrupted run
    _nmcli("connection", "delete", HOTSPOT_CON_NAME, log=log)

    try:
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
            log=log,
        )
        _nmcli("connection", "up", HOTSPOT_CON_NAME, check=True, log=log)
        _wait_for_ip(log=log)
    except Exception:
        # Remove the profile we may have just created so the next attempt
        # starts clean instead of hitting a name/interface conflict.
        _nmcli("connection", "delete", HOTSPOT_CON_NAME, log=log)
        raise

    _log_line(log, "create_hotspot: done")


def teardown_hotspot(log: Optional[IO[str]] = None):
    """Remove the hotspot connection profile and release wlan0."""
    _nmcli("connection", "delete", HOTSPOT_CON_NAME, log=log)
    time.sleep(2)


def connect_wifi(ssid: str, password: str, log: Optional[IO[str]] = None) -> bool:
    """Connect wlan0 to the given SSID.  Returns True on success."""
    # Trigger a fresh scan so NM can see the target network
    _nmcli("device", "wifi", "rescan", "ifname", _IFACE, log=log)
    time.sleep(3)

    result = _nmcli(
        "device", "wifi", "connect", ssid,
        "password", password,
        "ifname", _IFACE,
        log=log,
    )
    if result.returncode == 0:
        _log_line(log, f"connect_wifi: connected to '{ssid}'")
        return True
    _log_line(log, f"connect_wifi: FAILED for '{ssid}'")
    return False
