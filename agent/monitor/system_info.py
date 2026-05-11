"""
VPS Panel - System Info
Collects OS, hostname, uptime, and network information.
"""

import psutil
import platform
import socket
import time
from datetime import datetime, timezone


def get_system_info() -> dict:
    """Get general system information."""
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time

    return {
        "hostname": socket.gethostname(),
        "os": f"{platform.system()} {platform.release()}",
        "os_full": platform.platform(),
        "distro": _get_distro(),
        "kernel": platform.release(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "boot_time": datetime.fromtimestamp(boot_time, tz=timezone.utc).isoformat(),
        "uptime_seconds": int(uptime_seconds),
        "uptime_human": _format_uptime(int(uptime_seconds)),
    }


def _get_distro() -> str:
    """Get Linux distribution name."""
    try:
        with open("/etc/os-release", "r") as f:
            for line in f:
                if line.startswith("PRETTY_NAME="):
                    return line.split("=", 1)[1].strip().strip('"')
    except (IOError, FileNotFoundError):
        pass
    return platform.system()


def _format_uptime(seconds: int) -> str:
    """Format uptime seconds into human-readable string."""
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    parts.append(f"{minutes}m")
    return " ".join(parts)


def get_network_info() -> list:
    """Get network interface information."""
    interfaces = []
    addrs = psutil.net_if_addrs()
    stats = psutil.net_if_stats()

    for iface_name, addr_list in addrs.items():
        iface_info = {
            "name": iface_name,
            "is_up": stats.get(iface_name, None) and stats[iface_name].isup,
            "speed": stats[iface_name].speed if iface_name in stats else 0,
            "addresses": [],
        }

        for addr in addr_list:
            if addr.family.name in ("AF_INET", "AF_INET6"):
                iface_info["addresses"].append({
                    "family": addr.family.name,
                    "address": addr.address,
                    "netmask": addr.netmask,
                })

        if iface_info["addresses"]:
            interfaces.append(iface_info)

    return interfaces


def get_network_io() -> dict:
    """Get network I/O counters."""
    try:
        io = psutil.net_io_counters()
        return {
            "bytes_sent": io.bytes_sent,
            "bytes_recv": io.bytes_recv,
            "packets_sent": io.packets_sent,
            "packets_recv": io.packets_recv,
            "sent_gb": round(io.bytes_sent / (1024**3), 2),
            "recv_gb": round(io.bytes_recv / (1024**3), 2),
        }
    except Exception:
        return {"bytes_sent": 0, "bytes_recv": 0, "packets_sent": 0, "packets_recv": 0, "sent_gb": 0, "recv_gb": 0}


def get_primary_ip() -> str:
    """Get the primary IP address of the server."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"
