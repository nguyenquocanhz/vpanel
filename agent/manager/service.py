"""
VPS Panel - Systemd Service Manager (Optimized)
Cached service listing to reduce systemctl calls.
"""

import subprocess
import time

# Cache services list for 10 seconds
_services_cache = {"data": [], "timestamp": 0, "ttl": 10}


def _run_systemctl(args: list, timeout: int = 10) -> dict:
    """Run a systemctl command."""
    try:
        result = subprocess.run(
            ["systemctl"] + args,
            capture_output=True, text=True, timeout=timeout
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "stdout": "", "stderr": "Command timed out"}
    except Exception as e:
        return {"success": False, "stdout": "", "stderr": str(e)}


def list_services(filter_type: str = "service", use_cache: bool = True) -> list:
    """List systemd services with caching."""
    now = time.time()
    if use_cache and _services_cache["data"] and (now - _services_cache["timestamp"]) < _services_cache["ttl"]:
        return _services_cache["data"]

    # Only list loaded services (much faster than --all)
    result = _run_systemctl([
        "list-units", f"--type={filter_type}",
        "--no-pager", "--no-legend", "--plain"
    ])

    services = []
    if result["success"] and result["stdout"]:
        for line in result["stdout"].split("\n"):
            parts = line.split(None, 4)
            if len(parts) >= 4:
                services.append({
                    "name": parts[0],
                    "load": parts[1],
                    "active": parts[2],
                    "sub": parts[3],
                    "description": parts[4] if len(parts) > 4 else "",
                })

    _services_cache["data"] = services
    _services_cache["timestamp"] = now
    return services


def get_service_status(service_name: str) -> dict:
    """Get detailed status of a specific service."""
    is_active = _run_systemctl(["is-active", service_name])
    is_enabled = _run_systemctl(["is-enabled", service_name])

    return {
        "name": service_name,
        "active": is_active["stdout"] if is_active["success"] else "inactive",
        "enabled": is_enabled["stdout"] if is_enabled["success"] else "unknown",
    }


def start_service(service_name: str) -> dict:
    _services_cache["data"] = []  # Invalidate cache
    result = _run_systemctl(["start", service_name])
    if result["success"]:
        return {"success": True, "message": f"Service {service_name} started"}
    return {"success": False, "error": result["stderr"]}


def stop_service(service_name: str) -> dict:
    if service_name in ["vpspanel.service", "vpspanel"]:
        return {"success": False, "error": "Cannot stop VPS Panel from itself"}
    _services_cache["data"] = []
    result = _run_systemctl(["stop", service_name])
    if result["success"]:
        return {"success": True, "message": f"Service {service_name} stopped"}
    return {"success": False, "error": result["stderr"]}


def restart_service(service_name: str) -> dict:
    _services_cache["data"] = []
    result = _run_systemctl(["restart", service_name])
    if result["success"]:
        return {"success": True, "message": f"Service {service_name} restarted"}
    return {"success": False, "error": result["stderr"]}


def enable_service(service_name: str) -> dict:
    result = _run_systemctl(["enable", service_name])
    if result["success"]:
        return {"success": True, "message": f"Service {service_name} enabled"}
    return {"success": False, "error": result["stderr"]}


def disable_service(service_name: str) -> dict:
    result = _run_systemctl(["disable", service_name])
    if result["success"]:
        return {"success": True, "message": f"Service {service_name} disabled"}
    return {"success": False, "error": result["stderr"]}
