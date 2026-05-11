"""
VPS Panel - File Manager
Browse, create, edit, upload, download, and delete files on the server.
"""

import os
import shutil
import stat
import mimetypes
from pathlib import Path
from datetime import datetime
from typing import Optional


def _file_info(path: str) -> dict:
    """Get file/directory metadata."""
    try:
        st = os.stat(path)
        p = Path(path)
        return {
            "name": p.name,
            "path": str(p),
            "is_dir": p.is_dir(),
            "is_file": p.is_file(),
            "size": st.st_size,
            "size_human": _human_size(st.st_size),
            "modified": datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "permissions": stat.filemode(st.st_mode),
            "owner_uid": st.st_uid,
            "extension": p.suffix.lower() if p.is_file() else "",
        }
    except (OSError, PermissionError) as e:
        return {"name": Path(path).name, "path": path, "error": str(e)}


def _human_size(size: int) -> str:
    """Convert bytes to human-readable string."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.1f} {unit}" if unit != "B" else f"{size} {unit}"
        size /= 1024
    return f"{size:.1f} PB"


def _is_safe_path(path: str) -> bool:
    """Basic safety check - prevent accessing critical system files."""
    dangerous = ["/proc", "/sys", "/dev", "/boot/efi"]
    resolved = str(Path(path).resolve())
    return not any(resolved.startswith(d) for d in dangerous)


def _is_text_file(path: str) -> bool:
    """Check if file is likely a text file."""
    text_exts = {".txt", ".md", ".py", ".js", ".css", ".html", ".json", ".xml",
                 ".yml", ".yaml", ".toml", ".ini", ".cfg", ".conf", ".sh", ".bash",
                 ".log", ".csv", ".env", ".htaccess", ".php", ".rb", ".go", ".rs",
                 ".java", ".c", ".cpp", ".h", ".sql", ".nginx", ".service", ".timer"}
    ext = Path(path).suffix.lower()
    if ext in text_exts:
        return True
    mime = mimetypes.guess_type(path)[0]
    return mime is not None and mime.startswith("text/")


def list_directory(path: str = "/") -> dict:
    """List contents of a directory."""
    if not _is_safe_path(path):
        return {"success": False, "error": "Access denied to this path"}

    target = Path(path)
    if not target.exists():
        return {"success": False, "error": f"Path not found: {path}"}
    if not target.is_dir():
        return {"success": False, "error": f"Not a directory: {path}"}

    try:
        items = []
        for entry in sorted(target.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower())):
            try:
                items.append(_file_info(str(entry)))
            except (PermissionError, OSError):
                items.append({"name": entry.name, "path": str(entry), "error": "Permission denied"})

        return {
            "success": True,
            "path": str(target.resolve()),
            "parent": str(target.parent.resolve()) if str(target) != "/" else None,
            "items": items,
            "total": len(items),
        }
    except PermissionError:
        return {"success": False, "error": "Permission denied"}


def read_file(path: str) -> dict:
    """Read file contents (text files only, max 1MB)."""
    if not _is_safe_path(path):
        return {"success": False, "error": "Access denied"}

    target = Path(path)
    if not target.exists():
        return {"success": False, "error": "File not found"}
    if not target.is_file():
        return {"success": False, "error": "Not a file"}
    if target.stat().st_size > 1_048_576:
        return {"success": False, "error": "File too large (max 1MB for editing)"}
    if not _is_text_file(path):
        return {"success": False, "error": "Binary file — cannot edit"}

    try:
        content = target.read_text(encoding="utf-8", errors="replace")
        return {"success": True, "path": str(target), "content": content, "size": len(content)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def write_file(path: str, content: str) -> dict:
    """Write content to a file."""
    if not _is_safe_path(path):
        return {"success": False, "error": "Access denied"}

    try:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return {"success": True, "message": f"File saved: {path}", "size": len(content)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_directory(path: str) -> dict:
    """Create a new directory."""
    if not _is_safe_path(path):
        return {"success": False, "error": "Access denied"}

    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return {"success": True, "message": f"Directory created: {path}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def delete_item(path: str) -> dict:
    """Delete a file or directory."""
    if not _is_safe_path(path):
        return {"success": False, "error": "Access denied"}

    critical = ["/", "/etc", "/usr", "/var", "/home", "/root", "/opt", "/bin", "/sbin", "/lib", "/opt/vpspanel"]
    if str(Path(path).resolve()) in critical:
        return {"success": False, "error": "Cannot delete critical system directory"}

    target = Path(path)
    if not target.exists():
        return {"success": False, "error": "Not found"}

    try:
        if target.is_dir():
            shutil.rmtree(str(target))
        else:
            target.unlink()
        return {"success": True, "message": f"Deleted: {path}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def rename_item(old_path: str, new_name: str) -> dict:
    """Rename a file or directory."""
    if not _is_safe_path(old_path):
        return {"success": False, "error": "Access denied"}

    target = Path(old_path)
    if not target.exists():
        return {"success": False, "error": "Not found"}

    new_path = target.parent / new_name
    if new_path.exists():
        return {"success": False, "error": f"Already exists: {new_name}"}

    try:
        target.rename(new_path)
        return {"success": True, "message": f"Renamed to {new_name}", "new_path": str(new_path)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_file_download_path(path: str) -> Optional[str]:
    """Validate and return absolute path for download."""
    if not _is_safe_path(path):
        return None
    target = Path(path)
    if target.exists() and target.is_file():
        return str(target.resolve())
    return None
