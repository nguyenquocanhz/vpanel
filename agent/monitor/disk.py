"""
VPS Panel - Disk Monitor
Collects disk usage, partitions, and I/O statistics.
"""

import psutil
import subprocess
import json


def _bytes_to_gb(b: int) -> float:
    """Convert bytes to gigabytes."""
    return round(b / (1024 ** 3), 2)


def get_disk_usage() -> list:
    """Get disk usage for all mounted partitions."""
    partitions = psutil.disk_partitions(all=False)
    usage_list = []

    for part in partitions:
        try:
            usage = psutil.disk_usage(part.mountpoint)
            usage_list.append({
                "device": part.device,
                "mountpoint": part.mountpoint,
                "fstype": part.fstype,
                "opts": part.opts,
                "total_gb": _bytes_to_gb(usage.total),
                "used_gb": _bytes_to_gb(usage.used),
                "free_gb": _bytes_to_gb(usage.free),
                "percent": usage.percent,
            })
        except (PermissionError, OSError):
            continue

    return usage_list


def get_disk_io() -> dict:
    """Get disk I/O statistics."""
    try:
        io = psutil.disk_io_counters()
        if io:
            return {
                "read_bytes": io.read_bytes,
                "write_bytes": io.write_bytes,
                "read_count": io.read_count,
                "write_count": io.write_count,
                "read_gb": _bytes_to_gb(io.read_bytes),
                "write_gb": _bytes_to_gb(io.write_bytes),
            }
    except Exception:
        pass
    return {"read_bytes": 0, "write_bytes": 0, "read_count": 0, "write_count": 0, "read_gb": 0, "write_gb": 0}


def list_block_devices() -> list:
    """List all block devices using lsblk."""
    try:
        result = subprocess.run(
            ["lsblk", "-J", "-o", "NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT,MODEL,SERIAL"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return data.get("blockdevices", [])
    except (subprocess.SubprocessError, json.JSONDecodeError, FileNotFoundError):
        pass
    return []


def get_full_disk_data() -> dict:
    """Get comprehensive disk data for dashboard."""
    return {
        "usage": get_disk_usage(),
        "io": get_disk_io(),
        "block_devices": list_block_devices(),
    }
