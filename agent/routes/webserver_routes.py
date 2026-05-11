"""
VPS Panel - Web Server Manager API Routes
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from agent.auth.auth_middleware import get_current_user
from agent.manager.webserver import (
    get_nginx_status, test_nginx_config, reload_nginx, restart_nginx,
    list_sites, get_site_config, save_site_config, create_site,
    enable_site, disable_site, delete_site
)

router = APIRouter(
    prefix="/api/webserver",
    tags=["Web Server"],
    dependencies=[Depends(get_current_user)]
)


class SiteConfig(BaseModel):
    site_name: str
    content: str


class CreateSiteRequest(BaseModel):
    domain: str
    root_path: Optional[str] = None
    template: str = "static"  # static, php, proxy


class SiteAction(BaseModel):
    site_name: str


@router.get("/status")
async def api_nginx_status():
    return get_nginx_status()


@router.get("/test")
async def api_test_config():
    return test_nginx_config()


@router.post("/reload")
async def api_reload():
    return reload_nginx()


@router.post("/restart")
async def api_restart():
    return restart_nginx()


@router.get("/sites")
async def api_list_sites():
    return {"sites": list_sites()}


@router.get("/site/{site_name}")
async def api_get_site(site_name: str):
    return get_site_config(site_name)


@router.post("/site/save")
async def api_save_site(req: SiteConfig):
    return save_site_config(req.site_name, req.content)


@router.post("/site/create")
async def api_create_site(req: CreateSiteRequest):
    return create_site(req.domain, req.root_path, req.template)


@router.post("/site/enable")
async def api_enable_site(req: SiteAction):
    return enable_site(req.site_name)


@router.post("/site/disable")
async def api_disable_site(req: SiteAction):
    return disable_site(req.site_name)


@router.post("/site/delete")
async def api_delete_site(req: SiteAction):
    return delete_site(req.site_name)
