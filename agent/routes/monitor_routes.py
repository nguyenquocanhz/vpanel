"""
VPS Panel - Monitor API Routes (Optimized with async)
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, Depends
from agent.auth.auth_middleware import get_current_user
from agent.monitor.cpu import get_full_cpu_data
from agent.monitor.memory import get_full_memory_data
from agent.monitor.disk import get_full_disk_data
from agent.monitor.temperature import get_full_temperature_data
from agent.monitor.system_info import get_system_info, get_network_info, get_network_io, get_primary_ip
from agent.manager.process import list_processes, get_process_count

router = APIRouter(prefix="/api/monitor", tags=["Monitoring"], dependencies=[Depends(get_current_user)])

# Thread pool for blocking psutil calls
_executor = ThreadPoolExecutor(max_workers=4)


async def _run_in_thread(func, *args):
    """Run blocking function in thread pool."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, func, *args)


@router.get("/overview")
async def get_overview():
    """Get complete system overview - all metrics in PARALLEL."""
    cpu, memory, disk, temp, sys_info, net_io, proc_count = await asyncio.gather(
        _run_in_thread(get_full_cpu_data),
        _run_in_thread(get_full_memory_data),
        _run_in_thread(get_full_disk_data),
        _run_in_thread(get_full_temperature_data),
        _run_in_thread(get_system_info),
        _run_in_thread(get_network_io),
        _run_in_thread(get_process_count),
    )

    return {
        "system": sys_info,
        "cpu": cpu,
        "memory": memory,
        "disk": disk,
        "temperature": temp,
        "network": {
            "io": net_io,
            "primary_ip": get_primary_ip(),
        },
        "processes": proc_count,
    }


@router.get("/cpu")
async def get_cpu():
    return await _run_in_thread(get_full_cpu_data)


@router.get("/memory")
async def get_memory():
    return await _run_in_thread(get_full_memory_data)


@router.get("/disk")
async def get_disk():
    return await _run_in_thread(get_full_disk_data)


@router.get("/temperature")
async def get_temperature():
    return await _run_in_thread(get_full_temperature_data)


@router.get("/system")
async def get_system():
    return await _run_in_thread(get_system_info)


@router.get("/network")
async def get_network():
    return {
        "interfaces": await _run_in_thread(get_network_info),
        "io": await _run_in_thread(get_network_io),
        "primary_ip": get_primary_ip(),
    }


@router.get("/processes")
async def get_processes(sort: str = "cpu", limit: int = 20):
    procs, summary = await asyncio.gather(
        _run_in_thread(list_processes, sort, limit),
        _run_in_thread(get_process_count),
    )
    return {"processes": procs, "summary": summary}
