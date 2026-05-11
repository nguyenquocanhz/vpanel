"""
VPS Panel - Power Control
Restart/Shutdown server via systemctl.
"""

import subprocess
import asyncio
from datetime import datetime, timezone


async def restart_server(delay_seconds: int = 5) -> dict:
    """Schedule a server restart with delay."""
    try:
        # Schedule restart with delay
        cmd = ["shutdown", "-r", f"+{max(1, delay_seconds // 60)}",
               f"VPS Panel: Scheduled restart at {datetime.now(timezone.utc).isoformat()}"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            return {"success": True, "message": f"Server will restart in {delay_seconds} seconds"}
        else:
            # Fallback: use systemctl
            result2 = subprocess.run(
                ["systemctl", "reboot"],
                capture_output=True, text=True, timeout=10
            )
            if result2.returncode == 0:
                return {"success": True, "message": "Server is restarting now"}
            return {"success": False, "message": f"Failed to restart: {result2.stderr}"}

    except subprocess.TimeoutExpired:
        return {"success": False, "message": "Restart command timed out"}
    except Exception as e:
        return {"success": False, "message": str(e)}


async def shutdown_server(delay_seconds: int = 5) -> dict:
    """Schedule a server shutdown with delay."""
    try:
        cmd = ["shutdown", "-h", f"+{max(1, delay_seconds // 60)}",
               f"VPS Panel: Scheduled shutdown at {datetime.now(timezone.utc).isoformat()}"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            return {"success": True, "message": f"Server will shutdown in {delay_seconds} seconds"}
        else:
            result2 = subprocess.run(
                ["systemctl", "poweroff"],
                capture_output=True, text=True, timeout=10
            )
            if result2.returncode == 0:
                return {"success": True, "message": "Server is shutting down now"}
            return {"success": False, "message": f"Failed to shutdown: {result2.stderr}"}

    except subprocess.TimeoutExpired:
        return {"success": False, "message": "Shutdown command timed out"}
    except Exception as e:
        return {"success": False, "message": str(e)}


async def cancel_shutdown() -> dict:
    """Cancel a pending shutdown/restart."""
    try:
        result = subprocess.run(["shutdown", "-c"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return {"success": True, "message": "Scheduled shutdown cancelled"}
        return {"success": False, "message": f"Failed to cancel: {result.stderr}"}
    except Exception as e:
        return {"success": False, "message": str(e)}
