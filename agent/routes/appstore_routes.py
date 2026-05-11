"""
VPS Panel - AppStore API Routes
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from agent.auth.auth_middleware import get_current_user
from agent.manager.appstore import (
    list_addons, get_addon, install_addon, uninstall_addon, get_categories
)

router = APIRouter(
    prefix="/api/appstore",
    tags=["AppStore"],
    dependencies=[Depends(get_current_user)]
)


class AddonAction(BaseModel):
    addon_id: str


@router.get("/addons")
async def api_list_addons(category: str = None):
    """List all available addons."""
    return {
        "addons": list_addons(category),
        "categories": get_categories(),
    }


@router.get("/addon/{addon_id}")
async def api_get_addon(addon_id: str):
    """Get details of a specific addon."""
    addon = get_addon(addon_id)
    if not addon:
        raise HTTPException(status_code=404, detail="Addon not found")
    return addon


@router.post("/install")
async def api_install_addon(action: AddonAction):
    """Install an addon."""
    return install_addon(action.addon_id)


@router.post("/uninstall")
async def api_uninstall_addon(action: AddonAction):
    """Uninstall an addon."""
    return uninstall_addon(action.addon_id)


@router.get("/categories")
async def api_get_categories():
    """List all addon categories."""
    return {"categories": get_categories()}
