"""
VPS Panel - Database Connection & Models
SQLAlchemy ORM with SQLite backend.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
import os

DATABASE_URL = os.getenv("VPSPANEL_DB_URL", "sqlite:///./data/vpspanel.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ──────────────────────────────────────────────────
#  Models
# ──────────────────────────────────────────────────

class User(Base):
    """Admin user account."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="admin")  # admin | viewer
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class MetricSnapshot(Base):
    """Historical metric snapshots for charts."""
    __tablename__ = "metric_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    cpu_percent = Column(Float, default=0.0)
    ram_percent = Column(Float, default=0.0)
    ram_used_gb = Column(Float, default=0.0)
    disk_percent = Column(Float, default=0.0)
    disk_used_gb = Column(Float, default=0.0)
    temperature = Column(Float, nullable=True)
    net_sent_mbps = Column(Float, default=0.0)
    net_recv_mbps = Column(Float, default=0.0)


class AuditLog(Base):
    """Audit log for security-critical actions."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    user = Column(String(50), nullable=False)
    action = Column(String(100), nullable=False)
    details = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    success = Column(Boolean, default=True)


class LicenseInfo(Base):
    """Cached license information."""
    __tablename__ = "license_info"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer = Column(String(255), nullable=True)
    hardware_id = Column(String(64), nullable=True)
    issued_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    features = Column(Text, nullable=True)  # JSON array
    is_valid = Column(Boolean, default=False)
    last_check = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# ──────────────────────────────────────────────────
#  Database Initialization
# ──────────────────────────────────────────────────

def init_db():
    """Create all tables if they don't exist."""
    # Ensure data directory exists
    db_path = DATABASE_URL.replace("sqlite:///", "")
    os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else ".", exist_ok=True)
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency injection for FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
