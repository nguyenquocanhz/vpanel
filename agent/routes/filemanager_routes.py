"""
VPS Panel - File Manager API Routes
"""

import os
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
from agent.auth.auth_middleware import get_current_user
from agent.manager.filemanager import (
    list_directory, read_file, write_file, create_directory,
    delete_item, rename_item, get_file_download_path, chmod_item
)

router = APIRouter(
    prefix="/api/files",
    tags=["File Manager"],
    dependencies=[Depends(get_current_user)]
)


class WriteFileRequest(BaseModel):
    path: str
    content: str


class CreateDirRequest(BaseModel):
    path: str


class DeleteRequest(BaseModel):
    path: str


class RenameRequest(BaseModel):
    path: str
    new_name: str


class ChmodRequest(BaseModel):
    path: str
    mode: str


@router.get("/list")
async def api_list_dir(path: str = "/"):
    return list_directory(path)


@router.get("/read")
async def api_read_file(path: str):
    return read_file(path)


@router.post("/write")
async def api_write_file(req: WriteFileRequest):
    return write_file(req.path, req.content)


@router.post("/mkdir")
async def api_create_dir(req: CreateDirRequest):
    return create_directory(req.path)


@router.post("/delete")
async def api_delete(req: DeleteRequest):
    return delete_item(req.path)


@router.post("/rename")
async def api_rename(req: RenameRequest):
    return rename_item(req.path, req.new_name)


@router.get("/download")
async def api_download(path: str):
    file_path = get_file_download_path(path)
    if not file_path:
        return {"success": False, "error": "File not found or access denied"}
    return FileResponse(file_path, filename=os.path.basename(file_path))


@router.post("/upload")
async def api_upload(
    file: UploadFile = File(...),
    directory: str = Query("/tmp")
):
    """Upload a file to the specified directory."""
    from pathlib import Path
    target_dir = Path(directory)
    if not target_dir.exists():
        target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / file.filename
    try:
        with open(target, "wb") as f:
            content = await file.read()
            f.write(content)
        return {"success": True, "message": f"Uploaded: {file.filename}", "path": str(target), "size": len(content)}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/chmod")
async def api_chmod(req: ChmodRequest):
    return chmod_item(req.path, req.mode)

