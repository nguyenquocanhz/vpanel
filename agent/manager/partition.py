"""
VPS Panel - Partition Manager
Manage disk partitions using parted (non-interactive mode).
"""

import subprocess
import json
from typing import Optional


# Safety: never allow operations on these mount points
PROTECTED_MOUNTPOINTS = ["/", "/boot", "/boot/efi", "/home"]
PROTECTED_DEVICES = []  # Populated at runtime from root device


def _run_cmd(cmd: list, timeout: int = 30) -> dict:
    """Run a shell command and return result."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "stdout": "", "stderr": "Command timed out"}
    except Exception as e:
        return {"success": False, "stdout": "", "stderr": str(e)}


def _get_root_device() -> str:
    """Get the device that holds the root filesystem."""
    result = _run_cmd(["findmnt", "-n", "-o", "SOURCE", "/"])
    if result["success"]:
        return result["stdout"].split("\n")[0].strip()
    return ""


def list_disks() -> list:
    """List all disk devices with partitions (lsblk JSON output)."""
    result = _run_cmd(["lsblk", "-J", "-o", "NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT,MODEL,RO,RM"])
    if result["success"]:
        try:
            data = json.loads(result["stdout"])
            return data.get("blockdevices", [])
        except json.JSONDecodeError:
            pass
    return []


def get_partition_table(device: str) -> dict:
    """Get partition table for a specific device."""
    if not device.startswith("/dev/"):
        return {"success": False, "error": "Invalid device path"}

    result = _run_cmd(["parted", "-s", device, "print", "free", "-j"])
    if result["success"]:
        try:
            return {"success": True, "data": json.loads(result["stdout"])}
        except json.JSONDecodeError:
            # Fallback to text output
            result2 = _run_cmd(["parted", "-s", device, "print", "free"])
            return {"success": True, "data": result2["stdout"]}
    return {"success": False, "error": result["stderr"]}


def create_partition(device: str, start: str, end: str, fs_type: str = "ext4") -> dict:
    """
    Create a new partition on a device.
    Args:
        device: e.g., /dev/sdb
        start: start position, e.g., "1MiB"
        end: end position, e.g., "100%" or "50GiB"
        fs_type: filesystem type (ext4, xfs, btrfs)
    """
    if not _is_safe_device(device):
        return {"success": False, "error": "Cannot modify protected device (root filesystem)"}

    if fs_type not in ["ext4", "xfs", "btrfs", "swap", "fat32", "ntfs"]:
        return {"success": False, "error": f"Unsupported filesystem: {fs_type}"}

    result = _run_cmd([
        "parted", "-s", device,
        "mkpart", "primary", fs_type, start, end
    ])

    if result["success"]:
        return {"success": True, "message": f"Partition created on {device} ({start} - {end}, {fs_type})"}
    return {"success": False, "error": result["stderr"]}


def delete_partition(device: str, partition_number: int) -> dict:
    """Delete a partition by number."""
    if not _is_safe_device(device):
        return {"success": False, "error": "Cannot modify protected device"}

    result = _run_cmd(["parted", "-s", device, "rm", str(partition_number)])
    if result["success"]:
        return {"success": True, "message": f"Partition {partition_number} deleted from {device}"}
    return {"success": False, "error": result["stderr"]}


def format_partition(partition: str, fs_type: str = "ext4") -> dict:
    """
    Format a partition with the specified filesystem.
    Args:
        partition: e.g., /dev/sdb1
        fs_type: ext4, xfs, btrfs, swap
    """
    if not _is_safe_partition(partition):
        return {"success": False, "error": "Cannot format protected partition"}

    mkfs_cmds = {
        "ext4": ["mkfs.ext4", "-F", partition],
        "xfs": ["mkfs.xfs", "-f", partition],
        "btrfs": ["mkfs.btrfs", "-f", partition],
        "swap": ["mkswap", partition],
        "fat32": ["mkfs.vfat", "-F", "32", partition],
        "ntfs": ["mkfs.ntfs", "-f", partition],
    }

    if fs_type not in mkfs_cmds:
        return {"success": False, "error": f"Unsupported filesystem: {fs_type}"}

    result = _run_cmd(mkfs_cmds[fs_type], timeout=120)
    if result["success"]:
        return {"success": True, "message": f"Formatted {partition} as {fs_type}"}
    return {"success": False, "error": result["stderr"]}


def mount_partition(partition: str, mount_point: str) -> dict:
    """Mount a partition to a mount point."""
    if mount_point in PROTECTED_MOUNTPOINTS:
        return {"success": False, "error": f"Cannot mount to protected mountpoint: {mount_point}"}

    # Create mount point if it doesn't exist
    _run_cmd(["mkdir", "-p", mount_point])

    result = _run_cmd(["mount", partition, mount_point])
    if result["success"]:
        return {"success": True, "message": f"Mounted {partition} at {mount_point}"}
    return {"success": False, "error": result["stderr"]}


def unmount_partition(mount_point: str) -> dict:
    """Unmount a partition."""
    if mount_point in PROTECTED_MOUNTPOINTS:
        return {"success": False, "error": f"Cannot unmount protected mountpoint: {mount_point}"}

    result = _run_cmd(["umount", mount_point])
    if result["success"]:
        return {"success": True, "message": f"Unmounted {mount_point}"}
    return {"success": False, "error": result["stderr"]}


def _is_safe_device(device: str) -> bool:
    """Check if a device is safe to modify (not the root device)."""
    root_dev = _get_root_device()
    # Strip partition number to get the base device
    import re
    base_root = re.sub(r'p?\d+$', '', root_dev)
    base_device = re.sub(r'p?\d+$', '', device)
    return base_device != base_root


def _is_safe_partition(partition: str) -> bool:
    """Check if a partition is safe to format."""
    root_dev = _get_root_device()
    if partition == root_dev:
        return False

    # Check if it's mounted on a protected mountpoint
    result = _run_cmd(["findmnt", "-n", "-o", "TARGET", partition])
    if result["success"] and result["stdout"].strip() in PROTECTED_MOUNTPOINTS:
        return False

    return True
