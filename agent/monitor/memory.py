"""
VPS Panel - Memory Monitor
Collects RAM and swap usage information.
"""

import psutil


def _bytes_to_gb(b: int) -> float:
    """Convert bytes to gigabytes, rounded to 2 decimal places."""
    return round(b / (1024 ** 3), 2)


def get_ram_info() -> dict:
    """Get RAM usage information."""
    mem = psutil.virtual_memory()
    return {
        "total_gb": _bytes_to_gb(mem.total),
        "used_gb": _bytes_to_gb(mem.used),
        "free_gb": _bytes_to_gb(mem.free),
        "available_gb": _bytes_to_gb(mem.available),
        "percent": mem.percent,
        "cached_gb": _bytes_to_gb(getattr(mem, "cached", 0)),
        "buffers_gb": _bytes_to_gb(getattr(mem, "buffers", 0)),
    }


def get_swap_info() -> dict:
    """Get swap memory information."""
    swap = psutil.swap_memory()
    return {
        "total_gb": _bytes_to_gb(swap.total),
        "used_gb": _bytes_to_gb(swap.used),
        "free_gb": _bytes_to_gb(swap.free),
        "percent": swap.percent,
    }


def get_full_memory_data() -> dict:
    """Get comprehensive memory data for dashboard."""
    return {
        "ram": get_ram_info(),
        "swap": get_swap_info(),
    }
