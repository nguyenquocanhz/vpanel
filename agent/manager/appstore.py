"""
VPS Panel - AppStore Addon Manager
Pre-configured application installer for Linux servers.
"""

import subprocess
import json
import time
from pathlib import Path
from typing import Optional

# Addon registry with install/uninstall commands
ADDON_REGISTRY = {
    "nginx": {
        "name": "Nginx",
        "description": "High-performance web server & reverse proxy",
        "icon": "globe",
        "category": "Web Server",
        "tags": ["web", "proxy", "reverse-proxy"],
        "service": "nginx",
        "install": {
            "ubuntu": "apt-get install -y nginx && systemctl enable nginx && systemctl start nginx",
            "arch": "pacman -S --noconfirm nginx && systemctl enable nginx && systemctl start nginx",
        },
        "uninstall": {
            "ubuntu": "systemctl stop nginx; apt-get remove -y nginx nginx-common && apt-get autoremove -y",
            "arch": "systemctl stop nginx; pacman -Rns --noconfirm nginx",
        },
    },
    "docker": {
        "name": "Docker",
        "description": "Container platform for building & running applications",
        "icon": "container",
        "category": "Container",
        "tags": ["container", "devops", "deployment"],
        "service": "docker",
        "install": {
            "ubuntu": "curl -fsSL https://get.docker.com | sh && systemctl enable docker && systemctl start docker",
            "arch": "pacman -S --noconfirm docker && systemctl enable docker && systemctl start docker",
        },
        "uninstall": {
            "ubuntu": "systemctl stop docker; apt-get remove -y docker-ce docker-ce-cli containerd.io && apt-get autoremove -y",
            "arch": "systemctl stop docker; pacman -Rns --noconfirm docker",
        },
    },
    "mysql": {
        "name": "MySQL 8.0",
        "description": "Popular open-source relational database",
        "icon": "database",
        "category": "Database",
        "tags": ["database", "sql", "relational"],
        "service": "mysql",
        "install": {
            "ubuntu": "apt-get install -y mysql-server && systemctl enable mysql && systemctl start mysql",
            "arch": "pacman -S --noconfirm mariadb && mariadb-install-db --user=mysql --basedir=/usr --datadir=/var/lib/mysql && systemctl enable mariadb && systemctl start mariadb",
        },
        "uninstall": {
            "ubuntu": "systemctl stop mysql; apt-get remove -y mysql-server && apt-get autoremove -y",
            "arch": "systemctl stop mariadb; pacman -Rns --noconfirm mariadb",
        },
    },
    "postgresql": {
        "name": "PostgreSQL",
        "description": "Advanced open-source relational database",
        "icon": "database",
        "category": "Database",
        "tags": ["database", "sql", "relational"],
        "service": "postgresql",
        "install": {
            "ubuntu": "apt-get install -y postgresql postgresql-contrib && systemctl enable postgresql && systemctl start postgresql",
            "arch": "pacman -S --noconfirm postgresql && sudo -u postgres initdb --locale=C.UTF-8 --encoding=UTF8 -D /var/lib/postgres/data && systemctl enable postgresql && systemctl start postgresql",
        },
        "uninstall": {
            "ubuntu": "systemctl stop postgresql; apt-get remove -y postgresql postgresql-contrib && apt-get autoremove -y",
            "arch": "systemctl stop postgresql; pacman -Rns --noconfirm postgresql",
        },
    },
    "redis": {
        "name": "Redis",
        "description": "In-memory data store, cache & message broker",
        "icon": "zap",
        "category": "Database",
        "tags": ["cache", "nosql", "memory"],
        "service": "redis",
        "install": {
            "ubuntu": "apt-get install -y redis-server && systemctl enable redis-server && systemctl start redis-server",
            "arch": "pacman -S --noconfirm redis && systemctl enable redis && systemctl start redis",
        },
        "uninstall": {
            "ubuntu": "systemctl stop redis-server; apt-get remove -y redis-server && apt-get autoremove -y",
            "arch": "systemctl stop redis; pacman -Rns --noconfirm redis",
        },
    },
    "mongodb": {
        "name": "MongoDB",
        "description": "NoSQL document database for modern applications",
        "icon": "database",
        "category": "Database",
        "tags": ["database", "nosql", "document"],
        "service": "mongod",
        "install": {
            "ubuntu": "curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | gpg --dearmor -o /usr/share/keyrings/mongodb-server-7.0.gpg && echo 'deb [signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse' > /etc/apt/sources.list.d/mongodb-org-7.0.list && apt-get update && apt-get install -y mongodb-org && systemctl enable mongod && systemctl start mongod",
            "arch": "echo 'Install MongoDB from AUR: yay -S mongodb-bin'",
        },
        "uninstall": {
            "ubuntu": "systemctl stop mongod; apt-get remove -y mongodb-org && apt-get autoremove -y",
            "arch": "systemctl stop mongod; yay -Rns --noconfirm mongodb-bin",
        },
    },
    "nodejs": {
        "name": "Node.js 20 LTS",
        "description": "JavaScript runtime for server-side applications",
        "icon": "hexagon",
        "category": "Runtime",
        "tags": ["runtime", "javascript", "web"],
        "service": None,
        "install": {
            "ubuntu": "curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && apt-get install -y nodejs",
            "arch": "pacman -S --noconfirm nodejs npm",
        },
        "uninstall": {
            "ubuntu": "apt-get remove -y nodejs && apt-get autoremove -y",
            "arch": "pacman -Rns --noconfirm nodejs npm",
        },
    },
    "python3": {
        "name": "Python 3",
        "description": "Popular programming language with pip package manager",
        "icon": "code",
        "category": "Runtime",
        "tags": ["runtime", "python", "scripting"],
        "service": None,
        "install": {
            "ubuntu": "apt-get install -y python3 python3-pip python3-venv",
            "arch": "pacman -S --noconfirm python python-pip",
        },
        "uninstall": {
            "ubuntu": "apt-get remove -y python3-pip python3-venv && apt-get autoremove -y",
            "arch": "pacman -Rns --noconfirm python-pip",
        },
    },
    "certbot": {
        "name": "Certbot (Let's Encrypt)",
        "description": "Free SSL/TLS certificates from Let's Encrypt",
        "icon": "shield",
        "category": "Security",
        "tags": ["ssl", "tls", "certificate", "security"],
        "service": None,
        "install": {
            "ubuntu": "apt-get install -y certbot",
            "arch": "pacman -S --noconfirm certbot",
        },
        "uninstall": {
            "ubuntu": "apt-get remove -y certbot && apt-get autoremove -y",
            "arch": "pacman -Rns --noconfirm certbot",
        },
    },
    "fail2ban": {
        "name": "Fail2Ban",
        "description": "Intrusion prevention & brute-force protection",
        "icon": "shield-alert",
        "category": "Security",
        "tags": ["security", "firewall", "protection"],
        "service": "fail2ban",
        "install": {
            "ubuntu": "apt-get install -y fail2ban && systemctl enable fail2ban && systemctl start fail2ban",
            "arch": "pacman -S --noconfirm fail2ban && systemctl enable fail2ban && systemctl start fail2ban",
        },
        "uninstall": {
            "ubuntu": "systemctl stop fail2ban; apt-get remove -y fail2ban && apt-get autoremove -y",
            "arch": "systemctl stop fail2ban; pacman -Rns --noconfirm fail2ban",
        },
    },
    "ufw": {
        "name": "UFW Firewall",
        "description": "Uncomplicated Firewall — simple iptables frontend",
        "icon": "flame",
        "category": "Security",
        "tags": ["firewall", "security", "network"],
        "service": "ufw",
        "install": {
            "ubuntu": "apt-get install -y ufw && ufw default deny incoming && ufw default allow outgoing && ufw allow ssh && ufw allow 8443/tcp && echo 'y' | ufw enable",
            "arch": "pacman -S --noconfirm ufw && ufw default deny incoming && ufw default allow outgoing && ufw allow ssh && ufw allow 8443/tcp && echo 'y' | ufw enable && systemctl enable ufw",
        },
        "uninstall": {
            "ubuntu": "ufw disable; apt-get remove -y ufw && apt-get autoremove -y",
            "arch": "ufw disable; pacman -Rns --noconfirm ufw",
        },
    },
    "phpmyadmin": {
        "name": "phpMyAdmin",
        "description": "Web-based MySQL/MariaDB administration tool",
        "icon": "layout-dashboard",
        "category": "Tools",
        "tags": ["database", "admin", "web", "mysql"],
        "service": None,
        "install": {
            "ubuntu": "DEBIAN_FRONTEND=noninteractive apt-get install -y phpmyadmin",
            "arch": "pacman -S --noconfirm phpmyadmin",
        },
        "uninstall": {
            "ubuntu": "apt-get remove -y phpmyadmin && apt-get autoremove -y",
            "arch": "pacman -Rns --noconfirm phpmyadmin",
        },
    },
    "portainer": {
        "name": "Portainer CE",
        "description": "Docker container management UI",
        "icon": "ship",
        "category": "Tools",
        "tags": ["docker", "container", "management", "ui"],
        "service": None,
        "install": {
            "ubuntu": "docker volume create portainer_data && docker run -d -p 9443:9443 --name portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce:latest",
            "arch": "docker volume create portainer_data && docker run -d -p 9443:9443 --name portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce:latest",
        },
        "uninstall": {
            "ubuntu": "docker stop portainer; docker rm portainer; docker volume rm portainer_data",
            "arch": "docker stop portainer; docker rm portainer; docker volume rm portainer_data",
        },
    },
}


def _detect_os() -> str:
    """Detect the operating system."""
    try:
        with open("/etc/os-release") as f:
            content = f.read().lower()
        if "arch" in content:
            return "arch"
        return "ubuntu"  # Default for Debian/Ubuntu family
    except Exception:
        return "ubuntu"


def _check_service_status(service_name: Optional[str]) -> str:
    """Check if a systemd service is running."""
    if not service_name:
        return "no-service"
    try:
        result = subprocess.run(
            ["systemctl", "is-active", service_name],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip()
    except Exception:
        return "unknown"


def _check_installed(addon_id: str) -> bool:
    """Check if an addon appears to be installed."""
    addon = ADDON_REGISTRY.get(addon_id)
    if not addon:
        return False
    # Check by service
    if addon.get("service"):
        status = _check_service_status(addon["service"])
        return status in ("active", "inactive", "failed")
    # Check by command existence
    check_cmds = {
        "nodejs": "node", "python3": "python3",
        "certbot": "certbot", "phpmyadmin": "phpmyadmin",
    }
    cmd = check_cmds.get(addon_id, addon_id)
    try:
        result = subprocess.run(["which", cmd], capture_output=True, timeout=3)
        return result.returncode == 0
    except Exception:
        return False


def list_addons(category: Optional[str] = None) -> list:
    """List all available addons with their install status."""
    os_type = _detect_os()
    addons = []
    for addon_id, addon in ADDON_REGISTRY.items():
        if category and addon["category"].lower() != category.lower():
            continue
        installed = _check_installed(addon_id)
        service_status = _check_service_status(addon.get("service")) if addon.get("service") else None
        addons.append({
            "id": addon_id,
            "name": addon["name"],
            "description": addon["description"],
            "icon": addon["icon"],
            "category": addon["category"],
            "tags": addon["tags"],
            "installed": installed,
            "service_status": service_status,
            "has_service": addon.get("service") is not None,
            "supported": os_type in addon.get("install", {}),
        })
    return addons


def get_addon(addon_id: str) -> Optional[dict]:
    """Get details of a specific addon."""
    addon = ADDON_REGISTRY.get(addon_id)
    if not addon:
        return None
    installed = _check_installed(addon_id)
    service_status = _check_service_status(addon.get("service")) if addon.get("service") else None
    return {
        "id": addon_id,
        **addon,
        "installed": installed,
        "service_status": service_status,
        "os": _detect_os(),
    }


def install_addon(addon_id: str) -> dict:
    """Install an addon."""
    addon = ADDON_REGISTRY.get(addon_id)
    if not addon:
        return {"success": False, "error": f"Unknown addon: {addon_id}"}

    os_type = _detect_os()
    cmd = addon["install"].get(os_type)
    if not cmd:
        return {"success": False, "error": f"Not supported on {os_type}"}

    if _check_installed(addon_id):
        return {"success": False, "error": f"{addon['name']} is already installed"}

    try:
        result = subprocess.run(
            ["bash", "-c", cmd],
            capture_output=True, text=True, timeout=300
        )
        if result.returncode == 0:
            return {
                "success": True,
                "message": f"{addon['name']} installed successfully",
                "output": result.stdout[-500:] if result.stdout else "",
            }
        return {
            "success": False,
            "error": f"Installation failed (exit code {result.returncode})",
            "output": result.stderr[-500:] if result.stderr else "",
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Installation timed out (5 min limit)"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def uninstall_addon(addon_id: str) -> dict:
    """Uninstall an addon."""
    addon = ADDON_REGISTRY.get(addon_id)
    if not addon:
        return {"success": False, "error": f"Unknown addon: {addon_id}"}

    os_type = _detect_os()
    cmd = addon["uninstall"].get(os_type)
    if not cmd:
        return {"success": False, "error": f"Not supported on {os_type}"}

    try:
        result = subprocess.run(
            ["bash", "-c", cmd],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode == 0:
            return {"success": True, "message": f"{addon['name']} uninstalled successfully"}
        return {"success": False, "error": result.stderr[-500:] if result.stderr else "Uninstall failed"}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Uninstall timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_categories() -> list:
    """Get all addon categories with counts."""
    cats = {}
    for addon in ADDON_REGISTRY.values():
        cat = addon["category"]
        cats[cat] = cats.get(cat, 0) + 1
    return [{"name": k, "count": v} for k, v in sorted(cats.items())]
