"""Hotspot management for the captive portal (hostapd + dnsmasq)."""

import subprocess
import time
from pathlib import Path
from typing import IO, Optional

HOTSPOT_SSID = "PiKaraoke-Setup"
HOTSPOT_PASS = "pikaraoke"
PORTAL_IP = "192.168.4.1"
_PORTAL_SUBNET = "192.168.4.1/24"
_IFACE = "wlan0"

# Runtime-generated config files (evaporate on reboot).
_HOSTAPD_CONF = Path("/tmp/pk-hostapd.conf")
_DNSMASQ_CONF = Path("/tmp/pk-dnsmasq.conf")
_HOSTAPD_LOG = Path("/tmp/pk-hostapd.log")
_DNSMASQ_LOG = Path("/tmp/pk-dnsmasq.log")

# Arg names whose following value should be redacted in log output.
_REDACT_AFTER = {"password", "psk", "wifi-sec.psk", "802-11-wireless-security.psk"}

# Module-level handles so teardown_hotspot() can reach the subprocesses.
_hostapd_proc: Optional[subprocess.Popen] = None
_dnsmasq_proc: Optional[subprocess.Popen] = None


# ---------------------------------------------------------------------------
# Logging helpers
# ---------------------------------------------------------------------------

def _log_line(log: Optional[IO[str]], msg: str) -> None:
    if log is None:
        return
    log.write(f"[PORTAL {time.strftime('%H:%M:%S')}] {msg}\n")
    log.flush()


def _safe_args_str(args) -> str:
    """Loggable nmcli arg string with passwords redacted."""
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


# ---------------------------------------------------------------------------
# Command runners
# ---------------------------------------------------------------------------

def _nmcli(*args, check=False, log: Optional[IO[str]] = None):
    """Run sudo nmcli, log command + exit code, raise RuntimeError with stderr on failure."""
    cmd = ["sudo", "nmcli"] + list(args)
    _log_line(log, f"nmcli: {_safe_args_str(args)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=check)
    except subprocess.CalledProcessError as exc:
        error_text = (exc.stderr or "").strip() or (exc.stdout or "").strip()
        _log_line(log, f"nmcli exit={exc.returncode} FAILED — {error_text or '(no output)'}")
        raise RuntimeError(
            f"nmcli {_safe_args_str(args)!r} exited {exc.returncode}"
            + (f"\n{error_text}" if error_text else "")
        ) from exc
    output_text = (result.stderr or "").strip() or (result.stdout or "").strip()
    detail = f" — {output_text}" if (result.returncode != 0 and output_text) else ""
    _log_line(log, f"nmcli exit={result.returncode}{detail}")
    return result


def _syscmd(cmd, *, check=True, log: Optional[IO[str]] = None):
    """Run a system command (ip, iw, …), log it, raise RuntimeError with output on failure."""
    _log_line(log, f"cmd: {' '.join(str(a) for a in cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=check)
    except subprocess.CalledProcessError as exc:
        error_text = (exc.stderr or "").strip() or (exc.stdout or "").strip()
        _log_line(log, f"cmd exit={exc.returncode} FAILED — {error_text or '(no output)'}")
        raise RuntimeError(
            f"Command {' '.join(str(a) for a in cmd)!r} exited {exc.returncode}"
            + (f"\n{error_text}" if error_text else "")
        ) from exc
    output_text = (result.stderr or "").strip() or (result.stdout or "").strip()
    detail = f" — {output_text}" if (result.returncode != 0 and output_text) else ""
    _log_line(log, f"cmd exit={result.returncode}{detail}")
    return result


# ---------------------------------------------------------------------------
# Config generation
# ---------------------------------------------------------------------------

def _write_configs() -> None:
    """Write hostapd and dnsmasq config files to /tmp/."""
    _HOSTAPD_CONF.write_text(
        f"interface={_IFACE}\n"
        "driver=nl80211\n"
        f"ssid={HOTSPOT_SSID}\n"
        "hw_mode=g\n"           # 2.4 GHz b/g/n — broadest device compatibility
        "channel=6\n"
        "ieee80211n=1\n"
        "wmm_enabled=0\n"
        "auth_algs=1\n"
        "ignore_broadcast_ssid=0\n"
        "wpa=2\n"
        f"wpa_passphrase={HOTSPOT_PASS}\n"
        "wpa_key_mgmt=WPA-PSK\n"
        "rsn_pairwise=CCMP\n"
    )
    _DNSMASQ_CONF.write_text(
        f"interface={_IFACE}\n"
        "bind-interfaces\n"
        "dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h\n"
        "dhcp-option=3,192.168.4.1\n"
        # Wildcard DNS redirect — every query resolves to the portal IP.
        # This is standard practice for Pi captive portals (used by RaspAP and
        # the majority of Pi captive-portal guides). Targeted probe-domain
        # lists (Android/iOS/Windows each use different URLs that change without
        # notice) are fragile. Since this hotspot has no upstream internet,
        # hijacking all DNS causes no collateral damage and reliably triggers
        # the OS captive-portal notification on all major platforms.
        "address=/#/192.168.4.1\n"
    )


# ---------------------------------------------------------------------------
# Poll-based readiness checks
# ---------------------------------------------------------------------------

def _wait_for_ap_mode(
    iface: str = _IFACE,
    timeout: float = 10.0,
    interval: float = 0.5,
    log: Optional[IO[str]] = None,
) -> None:
    """Poll `iw dev <iface> info` until the interface reports 'type AP'."""
    _log_line(log, f"_wait_for_ap_mode: polling {iface} for AP mode (timeout={timeout:.0f}s)")
    deadline = time.time() + timeout
    attempt = 0
    while time.time() < deadline:
        attempt += 1
        result = subprocess.run(
            ["iw", "dev", iface, "info"],
            capture_output=True, text=True, check=False,
        )
        if "type AP" in result.stdout:
            _log_line(log, f"_wait_for_ap_mode: poll {attempt} → AP mode confirmed ✓")
            return
        _log_line(log, f"_wait_for_ap_mode: poll {attempt} → not in AP mode yet")
        time.sleep(interval)
    raise RuntimeError(
        f"{iface} did not enter AP mode after {timeout:.0f}s — "
        f"check {_HOSTAPD_LOG} for hostapd diagnostics"
    )


def _wait_for_nm_managed(
    iface: str = _IFACE,
    timeout: float = 15.0,
    interval: float = 0.5,
    log: Optional[IO[str]] = None,
) -> None:
    """Poll `nmcli device` until iface is 'disconnected' (NM owns it, no active connection).

    Replaces the fixed sleep that previously preceded connect_wifi().  NM needs
    a moment after `device set wlan0 managed yes` before it will accept a
    `device wifi connect` command; polling for the disconnected state is both
    faster on average and correctly bounded when NM is slow.
    """
    _log_line(log, f"_wait_for_nm_managed: waiting for NM to reclaim {iface} (timeout={timeout:.0f}s)")
    deadline = time.time() + timeout
    attempt = 0
    while time.time() < deadline:
        attempt += 1
        result = subprocess.run(
            ["nmcli", "-t", "-f", "DEVICE,STATE", "device"],
            capture_output=True, text=True, check=False,
        )
        for line in result.stdout.splitlines():
            if line.startswith(f"{iface}:"):
                state = line.split(":", 1)[1].strip()
                _log_line(log, f"_wait_for_nm_managed: poll {attempt} → {state}")
                if state == "disconnected":
                    return
                break
        time.sleep(interval)
    raise RuntimeError(
        f"Timed out after {timeout:.0f}s waiting for NM to show {iface} as disconnected"
    )


# ---------------------------------------------------------------------------
# Private teardown helpers (also used by create_hotspot's error path)
# ---------------------------------------------------------------------------

def _stop_daemons(log: Optional[IO[str]] = None) -> None:
    """Terminate hostapd and dnsmasq subprocesses if they are running."""
    global _hostapd_proc, _dnsmasq_proc
    for name, proc in [("hostapd", _hostapd_proc), ("dnsmasq", _dnsmasq_proc)]:
        if proc is not None:
            _log_line(log, f"teardown: stopping {name} (pid={proc.pid})")
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                _log_line(log, f"teardown: {name} did not stop cleanly, killing")
                proc.kill()
                proc.wait()
    _hostapd_proc = None
    _dnsmasq_proc = None


def _release_interface(log: Optional[IO[str]] = None) -> None:
    """Flush wlan0's manual IP and return the interface to NetworkManager."""
    _log_line(log, "teardown: flushing wlan0 IP and releasing to NM")
    subprocess.run(["sudo", "ip", "addr", "flush", "dev", _IFACE], capture_output=True)
    subprocess.run(["sudo", "ip", "link", "set", _IFACE, "down"], capture_output=True)
    subprocess.run(
        ["sudo", "nmcli", "device", "set", _IFACE, "managed", "yes"],
        capture_output=True,
    )
    _log_line(log, "teardown: wlan0 returned to NM")


# ---------------------------------------------------------------------------
# Public interface (called by _portal.py — do not change signatures)
# ---------------------------------------------------------------------------

def create_hotspot(log: Optional[IO[str]] = None) -> None:
    """Bring up a 2.4 GHz WPA2 access point on wlan0 using hostapd + dnsmasq.

    Steps
    -----
    1. Write /tmp/ config files for hostapd and dnsmasq.
    2. Tell NM to release wlan0 (managed no).
    3. Assign 192.168.4.1/24 to wlan0 manually via `ip`.
    4. Start dnsmasq (DHCP + wildcard DNS redirect); health-check after 1 s.
    5. Start hostapd (AP mode); health-check after 1 s.
    6. Poll `iw dev wlan0 info` until the interface confirms AP mode.
    On any failure, the error path stops both daemons and returns wlan0 to NM
    before re-raising, so the next attempt starts clean.
    """
    global _hostapd_proc, _dnsmasq_proc

    _log_line(log, "create_hotspot: start")
    _write_configs()

    try:
        # 0. Stop the system dnsmasq service if it is running; it would
        #    otherwise hold port 67 and prevent our own dnsmasq from binding.
        #    check=False so we silently continue if the service is already stopped.
        _syscmd(["sudo", "systemctl", "stop", "dnsmasq"], check=False, log=log)

        # 1. Release wlan0 from NM so hostapd can take exclusive control.
        _log_line(log, "Releasing wlan0 from NetworkManager")
        _syscmd(["sudo", "nmcli", "device", "set", _IFACE, "managed", "no"], log=log)

        # 2. Assign the portal IP manually (NM no longer manages the address).
        _syscmd(["sudo", "ip", "link", "set", _IFACE, "up"], log=log)
        # check=False: harmless if the address is already present from a retry.
        _syscmd(
            ["sudo", "ip", "addr", "add", _PORTAL_SUBNET, "dev", _IFACE],
            check=False, log=log,
        )

        # 3. Start dnsmasq (provides DHCP leases and wildcard DNS redirect).
        _log_line(log, "Starting dnsmasq")
        with open(_DNSMASQ_LOG, "w") as dlog:
            _dnsmasq_proc = subprocess.Popen(
                ["sudo", "dnsmasq", "--no-daemon", f"--conf-file={_DNSMASQ_CONF}"],
                stdout=dlog,
                stderr=subprocess.STDOUT,
            )
        time.sleep(1)
        if _dnsmasq_proc.poll() is not None:
            output = _DNSMASQ_LOG.read_text(errors="replace").strip()
            raise RuntimeError(
                f"dnsmasq exited immediately (returncode={_dnsmasq_proc.returncode})"
                + (f"\n{output}" if output else "")
            )
        _log_line(log, f"dnsmasq running (pid={_dnsmasq_proc.pid})")

        # 4. Start hostapd (switches wlan0 into AP mode).
        _log_line(log, "Starting hostapd")
        with open(_HOSTAPD_LOG, "w") as hlog:
            _hostapd_proc = subprocess.Popen(
                ["sudo", "hostapd", str(_HOSTAPD_CONF)],
                stdout=hlog,
                stderr=subprocess.STDOUT,
            )
        time.sleep(1)
        if _hostapd_proc.poll() is not None:
            output = _HOSTAPD_LOG.read_text(errors="replace").strip()
            raise RuntimeError(
                f"hostapd exited immediately (returncode={_hostapd_proc.returncode})"
                + (f"\n{output}" if output else "")
            )
        _log_line(log, f"hostapd running (pid={_hostapd_proc.pid})")

        # 5. Confirm the driver actually switched to AP mode.
        _wait_for_ap_mode(log=log)

    except Exception:
        # Error path: clean up whatever started before re-raising.
        # Does NOT wait for NM to reclaim wlan0 — run_portal()'s handler
        # calls teardown_hotspot() for the full belt-and-suspenders cleanup.
        _stop_daemons(log=log)
        _release_interface(log=log)
        raise

    _log_line(log, "create_hotspot: done")


def teardown_hotspot(log: Optional[IO[str]] = None) -> None:
    """Stop hostapd and dnsmasq, flush wlan0, and wait for NM to reclaim it.

    Blocks until `nmcli device` shows wlan0 as 'disconnected' so that the
    subsequent connect_wifi() call finds the interface ready.
    """
    _stop_daemons(log=log)
    _release_interface(log=log)
    _wait_for_nm_managed(log=log)
    for f in [_HOSTAPD_CONF, _DNSMASQ_CONF, _HOSTAPD_LOG, _DNSMASQ_LOG]:
        f.unlink(missing_ok=True)


def connect_wifi(ssid: str, password: str, log: Optional[IO[str]] = None) -> bool:
    """Connect wlan0 to the given SSID via NM.  Returns True on success."""
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
