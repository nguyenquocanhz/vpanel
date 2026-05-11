"""
VPS Panel - CPU Monitor (Optimized - non-blocking)
"""

import psutil
import platform

# Pre-cache static info
_cpu_info_cache = None
_cpu_percent_history = 0.0
_per_core_history = []


def _init_cpu():
    """Initialize CPU percent tracking (call once at startup)."""
    psutil.cpu_percent(interval=None)
    psutil.cpu_percent(interval=None, percpu=True)


# Initialize on import
_init_cpu()


def get_cpu_usage() -> dict:
    """Get current CPU usage - NON-BLOCKING (uses cached delta)."""
    global _cpu_percent_history, _per_core_history
    _cpu_percent_history = psutil.cpu_percent(interval=None)
    _per_core_history = psutil.cpu_percent(interval=None, percpu=True)
    return {
        "overall": _cpu_percent_history,
        "per_core": _per_core_history,
    }


def get_cpu_info() -> dict:
    """Get CPU hardware info (cached after first call)."""
    global _cpu_info_cache
    if _cpu_info_cache:
        return _cpu_info_cache

    freq = psutil.cpu_freq()
    _cpu_info_cache = {
        "physical_cores": psutil.cpu_count(logical=False) or 0,
        "logical_cores": psutil.cpu_count(logical=True) or 0,
        "architecture": platform.machine(),
        "processor": platform.processor() or "Unknown",
        "frequency": {
            "current": round(freq.current, 2) if freq else 0,
            "min": round(freq.min, 2) if freq else 0,
            "max": round(freq.max, 2) if freq else 0,
        } if freq else {"current": 0, "min": 0, "max": 0},
    }
    return _cpu_info_cache


def get_cpu_times() -> dict:
    """Get CPU time distribution - NON-BLOCKING."""
    times = psutil.cpu_times_percent(interval=None)
    return {
        "user": round(times.user, 1),
        "system": round(times.system, 1),
        "idle": round(times.idle, 1),
        "iowait": round(getattr(times, "iowait", 0), 1),
    }


def get_load_average() -> dict:
    """Get system load average."""
    try:
        load = psutil.getloadavg()
        cores = psutil.cpu_count() or 1
        return {
            "load_1m": round(load[0], 2),
            "load_5m": round(load[1], 2),
            "load_15m": round(load[2], 2),
            "cores": cores,
            "load_percent_1m": round((load[0] / cores) * 100, 1),
        }
    except (OSError, AttributeError):
        return {"load_1m": 0, "load_5m": 0, "load_15m": 0, "cores": 1, "load_percent_1m": 0}


def get_full_cpu_data() -> dict:
    """Get comprehensive CPU data for dashboard."""
    return {
        "usage": get_cpu_usage(),
        "info": get_cpu_info(),
        "times": get_cpu_times(),
        "load": get_load_average(),
    }
