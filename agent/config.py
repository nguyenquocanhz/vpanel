"""
VPS Panel - Configuration Management
Loads configuration from /etc/vpspanel/config.json or defaults.
"""

import os
import json
import secrets
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
AGENT_DIR = BASE_DIR / "agent"
DASHBOARD_DIR = BASE_DIR / "dashboard"
DATA_DIR = Path(os.getenv("VPSPANEL_DATA_DIR", "/opt/vpspanel/data"))
CONFIG_PATH = Path(os.getenv("VPSPANEL_CONFIG", "/etc/vpspanel/config.json"))

# Default configuration
DEFAULT_CONFIG = {
    "server": {
        "host": "0.0.0.0",
        "port": 8443,
        "ssl_keyfile": "/opt/vpspanel/certs/key.pem",
        "ssl_certfile": "/opt/vpspanel/certs/cert.pem",
    },
    "auth": {
        "jwt_secret": secrets.token_hex(32),
        "jwt_algorithm": "HS256",
        "access_token_expire_minutes": 1440,  # 24 hours
        "max_login_attempts": 5,
        "lockout_minutes": 5,
    },
    "database": {
        "url": f"sqlite:///{DATA_DIR / 'vpspanel.db'}",
    },
    "monitoring": {
        "interval_seconds": 2,
        "history_retention_hours": 24,
        "temperature_warning": 70,
        "temperature_critical": 85,
    },
    "license": {
        "license_file": "/opt/vpspanel/license.lic",
    },
    "logging": {
        "level": "INFO",
        "file": "/var/log/vpspanel/agent.log",
    },
}


def load_config() -> dict:
    """Load configuration from file, merging with defaults."""
    config = DEFAULT_CONFIG.copy()

    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r") as f:
                user_config = json.load(f)
            # Deep merge user config into defaults
            _deep_merge(config, user_config)
        except (json.JSONDecodeError, IOError) as e:
            print(f"[WARNING] Failed to load config from {CONFIG_PATH}: {e}")
            print("[WARNING] Using default configuration.")

    return config


def _deep_merge(base: dict, override: dict) -> dict:
    """Deep merge override dict into base dict."""
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value
    return base


def save_config(config: dict):
    """Save configuration to file."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)


# Load config on import
settings = load_config()
