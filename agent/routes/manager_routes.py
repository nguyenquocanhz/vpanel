"""
VPS Panel - Manager API Routes
Server management endpoints (power, partitions, services).
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from agent.auth.auth_middleware import require_admin, get_current_user
from agent.database import get_db, AuditLog, User
from sqlalchemy.orm import Session
from agent.manager import power, partition, service, process

router = APIRouter(prefix="/api/manager", tags=["Management"], dependencies=[Depends(require_admin)])


# ──────────────────────────────────────────────────
#  Power Control
# ──────────────────────────────────────────────────

class PowerActionRequest(BaseModel):
    confirm: bool = False
    delay_seconds: int = 60


@router.post("/power/restart")
async def api_restart(
    request: PowerActionRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Restart the server. Requires confirm=true."""
    if not request.confirm:
        raise HTTPException(status_code=400, detail="Set confirm=true to proceed with restart")

    db.add(AuditLog(user=current_user.username, action="server_restart", details=f"Delay: {request.delay_seconds}s"))
    db.commit()

    result = await power.restart_server(request.delay_seconds)
    return result


@router.post("/power/shutdown")
async def api_shutdown(
    request: PowerActionRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Shutdown the server. Requires confirm=true."""
    if not request.confirm:
        raise HTTPException(status_code=400, detail="Set confirm=true to proceed with shutdown")

    db.add(AuditLog(user=current_user.username, action="server_shutdown", details=f"Delay: {request.delay_seconds}s"))
    db.commit()

    result = await power.shutdown_server(request.delay_seconds)
    return result


@router.post("/power/cancel")
async def api_cancel_shutdown():
    """Cancel a pending shutdown/restart."""
    return await power.cancel_shutdown()


# ──────────────────────────────────────────────────
#  Partition Management
# ──────────────────────────────────────────────────

class CreatePartitionRequest(BaseModel):
    device: str
    start: str = "1MiB"
    end: str = "100%"
    fs_type: str = "ext4"


class FormatPartitionRequest(BaseModel):
    partition: str
    fs_type: str = "ext4"
    confirm: bool = False


class MountRequest(BaseModel):
    partition: str
    mount_point: str


@router.get("/partitions")
async def api_list_disks():
    """List all disks and partitions."""
    return {
        "disks": partition.list_disks(),
    }


@router.get("/partitions/{device_name}")
async def api_get_partition_table(device_name: str):
    """Get partition table for a specific device."""
    device = f"/dev/{device_name}"
    return partition.get_partition_table(device)


@router.post("/partition/create")
async def api_create_partition(
    request: CreatePartitionRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new partition."""
    db.add(AuditLog(
        user=current_user.username, action="partition_create",
        details=f"{request.device} {request.start}-{request.end} {request.fs_type}"
    ))
    db.commit()
    return partition.create_partition(request.device, request.start, request.end, request.fs_type)


@router.post("/partition/delete")
async def api_delete_partition(
    device: str, partition_number: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a partition by number."""
    db.add(AuditLog(user=current_user.username, action="partition_delete", details=f"{device} #{partition_number}"))
    db.commit()
    return partition.delete_partition(device, partition_number)


@router.post("/partition/format")
async def api_format_partition(
    request: FormatPartitionRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Format a partition. Requires confirm=true."""
    if not request.confirm:
        raise HTTPException(status_code=400, detail="Set confirm=true to proceed with format (DESTRUCTIVE)")

    db.add(AuditLog(
        user=current_user.username, action="partition_format",
        details=f"{request.partition} → {request.fs_type}"
    ))
    db.commit()
    return partition.format_partition(request.partition, request.fs_type)


@router.post("/partition/mount")
async def api_mount(request: MountRequest):
    """Mount a partition."""
    return partition.mount_partition(request.partition, request.mount_point)


@router.post("/partition/unmount")
async def api_unmount(mount_point: str):
    """Unmount a partition."""
    return partition.unmount_partition(mount_point)


# ──────────────────────────────────────────────────
#  Service Management
# ──────────────────────────────────────────────────

@router.get("/services")
async def api_list_services():
    """List all systemd services."""
    return {"services": service.list_services()}


@router.get("/service/{service_name}")
async def api_service_status(service_name: str):
    """Get status of a specific service."""
    return service.get_service_status(service_name)


@router.post("/service/{service_name}/{action}")
async def api_service_action(
    service_name: str, action: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Start, stop, or restart a service."""
    actions = {
        "start": service.start_service,
        "stop": service.stop_service,
        "restart": service.restart_service,
        "enable": service.enable_service,
        "disable": service.disable_service,
    }

    if action not in actions:
        raise HTTPException(status_code=400, detail=f"Invalid action. Use: {', '.join(actions.keys())}")

    db.add(AuditLog(user=current_user.username, action=f"service_{action}", details=service_name))
    db.commit()

    return actions[action](service_name)


# ──────────────────────────────────────────────────
#  Process Management
# ──────────────────────────────────────────────────

@router.post("/process/{pid}/kill")
async def api_kill_process(
    pid: int, signal: int = 15,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Kill a process by PID."""
    db.add(AuditLog(user=current_user.username, action="process_kill", details=f"PID {pid}, signal {signal}"))
    db.commit()
    return process.kill_process(pid, signal)
