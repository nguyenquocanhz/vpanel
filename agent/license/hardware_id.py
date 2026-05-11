"""
VPS Panel - Hardware ID Generator
Creates a unique fingerprint for the server hardware.
"""

import hashlib
import subprocess
import uuid
import platform


def get_hardware_id() -> str:
    """
    Generate a unique hardware ID by combining:
    - CPU ID from /proc/cpuinfo
    - Motherboard serial from dmidecode
    - Primary MAC address
    Returns a SHA-256 hash string.
    """
    components = []

    # CPU ID
    cpu_id = _get_cpu_id()
    if cpu_id:
        components.append(f"cpu:{cpu_id}")

    # Motherboard serial
    board_serial = _get_board_serial()
    if board_serial:
        components.append(f"board:{board_serial}")

    # Primary MAC address
    mac = _get_mac_address()
    components.append(f"mac:{mac}")

    # Hostname as fallback component
    components.append(f"host:{platform.node()}")

    combined = "|".join(components)
    return hashlib.sha256(combined.encode()).hexdigest()


def _get_cpu_id() -> str:
    """Get CPU model/identifier from /proc/cpuinfo."""
    try:
        with open("/proc/cpuinfo", "r") as f:
            for line in f:
                if line.strip().startswith("model name"):
                    return line.split(":", 1)[1].strip()
    except (IOError, FileNotFoundError):
        pass
    return platform.processor() or ""


def _get_board_serial() -> str:
    """Get motherboard serial number using dmidecode."""
    try:
        result = subprocess.run(
            ["dmidecode", "-s", "baseboard-serial-number"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            serial = result.stdout.strip()
            if serial and serial.lower() not in ["not specified", "to be filled by o.e.m.", "default string", ""]:
                return serial
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    return ""


def _get_mac_address() -> str:
    """Get primary MAC address."""
    mac = uuid.getnode()
    return ':'.join(f'{(mac >> (8 * i)) & 0xff:02x}' for i in reversed(range(6)))


def get_hardware_summary() -> dict:
    """Get hardware ID with component details."""
    return {
        "hardware_id": get_hardware_id(),
        "cpu": _get_cpu_id(),
        "board_serial": _get_board_serial(),
        "mac_address": _get_mac_address(),
        "hostname": platform.node(),
    }
