"""
VPS Panel - Auth API Routes
Login, logout, and password management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from agent.database import get_db, User, AuditLog
from agent.auth.password import hash_password, verify_password
from agent.auth.jwt_handler import create_access_token, create_refresh_token
from agent.auth.auth_middleware import get_current_user, check_account_locked
from agent.config import settings

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    username: str
    password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, req: Request, db: Session = Depends(get_db)):
    """Authenticate user and return JWT tokens."""
    user = db.query(User).filter(User.username == request.username).first()

    client_ip = req.client.host if req.client else "unknown"

    if not user:
        # Log failed attempt
        db.add(AuditLog(user=request.username, action="login_failed", details="User not found", ip_address=client_ip, success=False))
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Check if account is locked
    if check_account_locked(user):
        remaining = int((user.locked_until - datetime.now(timezone.utc)).total_seconds())
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Account locked. Try again in {remaining} seconds"
        )

    # Verify password
    if not verify_password(request.password, user.password_hash):
        user.login_attempts += 1

        # Lock account after max attempts
        max_attempts = settings["auth"]["max_login_attempts"]
        lockout_minutes = settings["auth"]["lockout_minutes"]

        if user.login_attempts >= max_attempts:
            user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=lockout_minutes)
            user.login_attempts = 0

        db.add(AuditLog(user=request.username, action="login_failed", details=f"Wrong password (attempt {user.login_attempts})", ip_address=client_ip, success=False))
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Success - reset login attempts
    user.login_attempts = 0
    user.locked_until = None
    user.last_login = datetime.now(timezone.utc)
    db.add(AuditLog(user=request.username, action="login_success", ip_address=client_ip, success=True))
    db.commit()

    # Generate tokens
    token_data = {"sub": user.username, "role": user.role}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings["auth"]["access_token_expire_minutes"] * 60,
    )


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change the current user's password."""
    if not verify_password(request.current_password, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")

    if len(request.new_password) < 8:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at least 8 characters")

    current_user.password_hash = hash_password(request.new_password)
    current_user.updated_at = datetime.now(timezone.utc)
    db.add(AuditLog(user=current_user.username, action="password_changed", success=True))
    db.commit()

    return {"message": "Password changed successfully"}


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return {
        "username": current_user.username,
        "role": current_user.role,
        "last_login": current_user.last_login.isoformat() if current_user.last_login else None,
    }
