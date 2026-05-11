"""
VPS Panel - Process Manager
List and manage system processes.
"""

import psutil


def list_processes(sort_by: str = "cpu", limit: int = 20) -> list:
    """List running processes sorted by CPU or memory usage."""
    processes = []

    for proc in psutil.process_iter(["pid", "name", "username", "cpu_percent", "memory_percent", "status", "create_time"]):
        try:
            info = proc.info
            processes.append({
                "pid": info["pid"],
                "name": info["name"],
                "user": info["username"] or "system",
                "cpu_percent": round(info["cpu_percent"] or 0, 1),
                "memory_percent": round(info["memory_percent"] or 0, 1),
                "status": info["status"],
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    # Sort by specified field
    sort_key = "cpu_percent" if sort_by == "cpu" else "memory_percent"
    processes.sort(key=lambda x: x[sort_key], reverse=True)

    return processes[:limit]


def kill_process(pid: int, signal: int = 15) -> dict:
    """Kill a process by PID. Default signal is SIGTERM (15)."""
    try:
        proc = psutil.Process(pid)
        proc_name = proc.name()

        if signal == 9:
            proc.kill()  # SIGKILL
        else:
            proc.terminate()  # SIGTERM

        return {"success": True, "message": f"Signal {signal} sent to process {proc_name} (PID: {pid})"}
    except psutil.NoSuchProcess:
        return {"success": False, "error": f"Process {pid} not found"}
    except psutil.AccessDenied:
        return {"success": False, "error": f"Access denied to process {pid}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_process_count() -> dict:
    """Get process count statistics."""
    total = 0
    running = 0
    sleeping = 0
    zombie = 0

    for proc in psutil.process_iter(["status"]):
        try:
            total += 1
            status = proc.info["status"]
            if status == psutil.STATUS_RUNNING:
                running += 1
            elif status == psutil.STATUS_SLEEPING:
                sleeping += 1
            elif status == psutil.STATUS_ZOMBIE:
                zombie += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return {
        "total": total,
        "running": running,
        "sleeping": sleeping,
        "zombie": zombie,
    }
