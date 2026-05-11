"""
VPS Panel - WebSocket Routes
Real-time system monitoring via WebSocket.
"""

import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from agent.auth.jwt_handler import decode_access_token
from agent.monitor.cpu import get_cpu_usage
from agent.monitor.memory import get_ram_info
from agent.monitor.disk import get_disk_usage
from agent.monitor.temperature import get_cpu_temperature, get_temp_status
from agent.monitor.system_info import get_network_io, get_system_info
from agent.manager.process import get_process_count

router = APIRouter(tags=["WebSocket"])


class ConnectionManager:
    """Manage active WebSocket connections."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, data: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except Exception:
                disconnected.append(connection)
        for conn in disconnected:
            self.disconnect(conn)


manager = ConnectionManager()

# Store previous network I/O for speed calculation
_prev_net_io = {"bytes_sent": 0, "bytes_recv": 0}


@router.websocket("/ws/monitor")
async def websocket_monitor(websocket: WebSocket, token: str = Query(None)):
    """
    WebSocket endpoint for real-time system monitoring.
    Requires JWT token as query parameter: /ws/monitor?token=<JWT>
    """
    # Authenticate
    if not token:
        await websocket.close(code=4001, reason="Missing authentication token")
        return

    payload = decode_access_token(token)
    if not payload:
        await websocket.close(code=4001, reason="Invalid or expired token")
        return

    await manager.connect(websocket)

    global _prev_net_io

    try:
        while True:
            # Collect metrics
            cpu = get_cpu_usage()
            ram = get_ram_info()
            disks = get_disk_usage()
            cpu_temp = get_cpu_temperature()
            net_io = get_network_io()
            proc = get_process_count()

            # Calculate network speed (bytes/sec)
            net_speed_up = (net_io["bytes_sent"] - _prev_net_io["bytes_sent"]) / 2  # 2s interval
            net_speed_down = (net_io["bytes_recv"] - _prev_net_io["bytes_recv"]) / 2
            _prev_net_io = {"bytes_sent": net_io["bytes_sent"], "bytes_recv": net_io["bytes_recv"]}

            data = {
                "type": "metrics",
                "cpu": {
                    "overall": cpu["overall"],
                    "per_core": cpu["per_core"],
                },
                "ram": {
                    "percent": ram["percent"],
                    "used_gb": ram["used_gb"],
                    "total_gb": ram["total_gb"],
                },
                "disk": [{
                    "mountpoint": d["mountpoint"],
                    "percent": d["percent"],
                    "used_gb": d["used_gb"],
                    "total_gb": d["total_gb"],
                } for d in disks[:5]],  # Top 5 mountpoints
                "temperature": {
                    "cpu": cpu_temp,
                    "status": get_temp_status(cpu_temp),
                },
                "network": {
                    "upload_speed": round(net_speed_up / 1024, 1),    # KB/s
                    "download_speed": round(net_speed_down / 1024, 1),  # KB/s
                },
                "processes": proc,
            }

            await websocket.send_json(data)

            # Wait for next interval (2 seconds)
            try:
                # Also listen for client messages (e.g., ping)
                msg = await asyncio.wait_for(websocket.receive_text(), timeout=2.0)
                if msg == "ping":
                    await websocket.send_json({"type": "pong"})
            except asyncio.TimeoutError:
                pass  # Normal - just means no client message received

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)
