"""
VPS Panel - Main Application Entry Point
FastAPI server for Linux server management.
"""

import os
import secrets
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from agent.config import settings, BASE_DIR
from agent.database import init_db, SessionLocal, User
from agent.auth.password import hash_password
from agent.utils import logger

# Import routers
from agent.routes.auth_routes import router as auth_router
from agent.routes.monitor_routes import router as monitor_router
from agent.routes.manager_routes import router as manager_router
from agent.routes.websocket_routes import router as websocket_router
from agent.routes.license_routes import router as license_router
from agent.routes.appstore_routes import router as appstore_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # ── Startup ──
    logger.info("=" * 50)
    logger.info("  VPS Panel v1.0.0 - Starting Up")
    logger.info("=" * 50)

    # Initialize database
    init_db()
    logger.info("✓ Database initialized")

    # Create default admin user if none exists
    _ensure_admin_user()

    # License check (warning only, don't block)
    try:
        from agent.license.validator import validate_license
        license_info = validate_license()
        logger.info(f"✓ License valid: {license_info.customer} (expires: {license_info.expires_at})")
    except Exception as e:
        logger.warning(f"⚠ License: {e}")
        logger.warning("⚠ Running in unlicensed mode. Some features may be restricted.")

    logger.info(f"✓ Server ready on port {settings['server']['port']}")
    logger.info("=" * 50)

    yield

    # ── Shutdown ──
    logger.info("VPS Panel shutting down...")


def _ensure_admin_user():
    """Create default admin user if no users exist."""
    db = SessionLocal()
    try:
        user_count = db.query(User).count()
        if user_count == 0:
            default_password = secrets.token_urlsafe(12)
            admin = User(
                username="admin",
                password_hash=hash_password(default_password),
                role="admin",
            )
            db.add(admin)
            db.commit()
            logger.info("=" * 50)
            logger.info("  DEFAULT ADMIN ACCOUNT CREATED")
            logger.info(f"  Username: admin")
            logger.info(f"  Password: {default_password}")
            logger.info("  ⚠ CHANGE THIS PASSWORD IMMEDIATELY!")
            logger.info("=" * 50)
    finally:
        db.close()


# ──────────────────────────────────────────────────
#  Create FastAPI Application
# ──────────────────────────────────────────────────

app = FastAPI(
    title="VPS Panel",
    description="Linux Server Management Dashboard",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth_router)
app.include_router(monitor_router)
app.include_router(manager_router)
app.include_router(websocket_router)
app.include_router(license_router)
app.include_router(appstore_router)

# ──────────────────────────────────────────────────
#  Static Files & Frontend Serving
# ──────────────────────────────────────────────────

DASHBOARD_DIR = BASE_DIR / "dashboard"

# Mount static assets
if (DASHBOARD_DIR / "css").exists():
    app.mount("/css", StaticFiles(directory=str(DASHBOARD_DIR / "css")), name="css")
if (DASHBOARD_DIR / "js").exists():
    app.mount("/js", StaticFiles(directory=str(DASHBOARD_DIR / "js")), name="js")
if (DASHBOARD_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(DASHBOARD_DIR / "assets")), name="assets")


@app.get("/", include_in_schema=False)
async def serve_login():
    """Serve the login page."""
    index_path = DASHBOARD_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return JSONResponse({"message": "VPS Panel API", "docs": "/api/docs"})


@app.get("/dashboard", include_in_schema=False)
async def serve_dashboard():
    """Serve the main dashboard page."""
    dash_path = DASHBOARD_DIR / "dashboard.html"
    if dash_path.exists():
        return FileResponse(str(dash_path))
    return JSONResponse({"error": "Dashboard not found"}, status_code=404)


@app.get("/partitions", include_in_schema=False)
async def serve_partitions():
    """Serve the partition manager page."""
    part_path = DASHBOARD_DIR / "partitions.html"
    if part_path.exists():
        return FileResponse(str(part_path))
    return JSONResponse({"error": "Partition manager not found"}, status_code=404)


@app.get("/services", include_in_schema=False)
async def serve_services():
    """Serve the service manager page."""
    svc_path = DASHBOARD_DIR / "services.html"
    if svc_path.exists():
        return FileResponse(str(svc_path))
    return JSONResponse({"error": "Service manager not found"}, status_code=404)


@app.get("/appstore", include_in_schema=False)
async def serve_appstore():
    """Serve the AppStore page."""
    store_path = DASHBOARD_DIR / "appstore.html"
    if store_path.exists():
        return FileResponse(str(store_path))
    return JSONResponse({"error": "AppStore not found"}, status_code=404)


# ──────────────────────────────────────────────────
#  Error Handlers
# ──────────────────────────────────────────────────

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(status_code=404, content={"error": "Not found"})


@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    logger.error(f"Internal error: {exc}")
    return JSONResponse(status_code=500, content={"error": "Internal server error"})


# ──────────────────────────────────────────────────
#  Direct Execution
# ──────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "agent.main:app",
        host=settings["server"]["host"],
        port=settings["server"]["port"],
        reload=False,
        log_level="info",
    )
