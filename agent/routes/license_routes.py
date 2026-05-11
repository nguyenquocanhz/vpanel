"""
VPS Panel - License API Routes
License status endpoint.
"""

from fastapi import APIRouter, Depends
from agent.auth.auth_middleware import get_current_user
from agent.license.validator import get_license_status
from agent.license.hardware_id import get_hardware_summary

router = APIRouter(prefix="/api/license", tags=["License"], dependencies=[Depends(get_current_user)])


@router.get("/status")
async def license_status():
    """Get current license status and information."""
    return get_license_status()


@router.get("/hardware")
async def hardware_info():
    """Get hardware ID for license generation."""
    summary = get_hardware_summary()
    return {
        "hardware_id": summary["hardware_id"],
        "hostname": summary["hostname"],
    }
