"""
VPS Panel - Web Server Manager (Nginx)
Manage Nginx virtual hosts, configs, and sites.
"""

import subprocess
import re
from pathlib import Path
from typing import Optional

NGINX_SITES_AVAILABLE = Path("/etc/nginx/sites-available")
NGINX_SITES_ENABLED = Path("/etc/nginx/sites-enabled")
NGINX_CONF = Path("/etc/nginx/nginx.conf")


def _run_cmd(cmd: list, timeout: int = 10) -> dict:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return {"success": r.returncode == 0, "stdout": r.stdout.strip(), "stderr": r.stderr.strip()}
    except subprocess.TimeoutExpired:
        return {"success": False, "stdout": "", "stderr": "Timeout"}
    except Exception as e:
        return {"success": False, "stdout": "", "stderr": str(e)}


def get_nginx_status() -> dict:
    """Check Nginx install and service status."""
    version = _run_cmd(["nginx", "-v"])
    active = _run_cmd(["systemctl", "is-active", "nginx"])
    enabled = _run_cmd(["systemctl", "is-enabled", "nginx"])
    return {
        "installed": version["success"] or "nginx" in version.get("stderr", ""),
        "version": version["stderr"].split("/")[-1].strip() if version["stderr"] else "unknown",
        "active": active["stdout"] == "active",
        "enabled": enabled["stdout"] == "enabled",
    }


def test_nginx_config() -> dict:
    """Run nginx -t to validate configuration."""
    r = _run_cmd(["nginx", "-t"])
    ok = r["success"] or "syntax is ok" in r.get("stderr", "")
    return {"success": ok, "output": r["stderr"] or r["stdout"]}


def reload_nginx() -> dict:
    """Reload Nginx configuration."""
    test = test_nginx_config()
    if not test["success"]:
        return {"success": False, "error": f"Config test failed: {test['output']}"}
    r = _run_cmd(["systemctl", "reload", "nginx"])
    return {"success": r["success"], "message": "Nginx reloaded" if r["success"] else r["stderr"]}


def restart_nginx() -> dict:
    """Restart Nginx service."""
    r = _run_cmd(["systemctl", "restart", "nginx"])
    return {"success": r["success"], "message": "Nginx restarted" if r["success"] else r["stderr"]}


def list_sites() -> list:
    """List all Nginx virtual host sites."""
    sites = []
    if not NGINX_SITES_AVAILABLE.exists():
        return sites

    for conf_file in sorted(NGINX_SITES_AVAILABLE.iterdir()):
        if conf_file.is_file():
            enabled = (NGINX_SITES_ENABLED / conf_file.name).exists()
            config = conf_file.read_text(errors="replace")

            # Parse basic info from config
            server_names = re.findall(r"server_name\s+([^;]+);", config)
            listens = re.findall(r"listen\s+([^;]+);", config)
            roots = re.findall(r"root\s+([^;]+);", config)

            sites.append({
                "name": conf_file.name,
                "enabled": enabled,
                "server_name": server_names[0].strip() if server_names else "—",
                "listen": listens[0].strip() if listens else "80",
                "root": roots[0].strip() if roots else "—",
                "has_ssl": "443" in config or "ssl" in config.lower(),
                "path": str(conf_file),
            })
    return sites


def get_site_config(site_name: str) -> dict:
    """Read a site's Nginx config."""
    conf_path = NGINX_SITES_AVAILABLE / site_name
    if not conf_path.exists():
        return {"success": False, "error": f"Site not found: {site_name}"}
    try:
        content = conf_path.read_text(errors="replace")
        enabled = (NGINX_SITES_ENABLED / site_name).exists()
        return {"success": True, "name": site_name, "content": content, "enabled": enabled}
    except Exception as e:
        return {"success": False, "error": str(e)}


def save_site_config(site_name: str, content: str) -> dict:
    """Save/update a site's Nginx config."""
    conf_path = NGINX_SITES_AVAILABLE / site_name
    try:
        conf_path.write_text(content)
        test = test_nginx_config()
        if not test["success"]:
            return {"success": False, "error": f"Saved but config invalid: {test['output']}"}
        return {"success": True, "message": f"Config saved: {site_name}. Run reload to apply."}
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_site(domain: str, root_path: str = None, template: str = "static") -> dict:
    """Create a new Nginx virtual host."""
    safe_name = re.sub(r"[^a-zA-Z0-9._-]", "", domain)
    conf_path = NGINX_SITES_AVAILABLE / safe_name
    if conf_path.exists():
        return {"success": False, "error": f"Site already exists: {safe_name}"}

    if not root_path:
        root_path = f"/var/www/{safe_name}"

    # Create web root
    Path(root_path).mkdir(parents=True, exist_ok=True)
    index = Path(root_path) / "index.html"
    if not index.exists():
        index.write_text(f"<h1>Welcome to {domain}</h1><p>VPS Panel managed site.</p>")

    # Generate config from template
    if template == "proxy":
        config = _proxy_template(domain, "http://127.0.0.1:3000")
    elif template == "php":
        config = _php_template(domain, root_path)
    else:
        config = _static_template(domain, root_path)

    try:
        conf_path.write_text(config)
        return {"success": True, "message": f"Site created: {domain}", "config_path": str(conf_path), "root_path": root_path}
    except Exception as e:
        return {"success": False, "error": str(e)}


def enable_site(site_name: str) -> dict:
    """Enable a site by creating symlink in sites-enabled."""
    available = NGINX_SITES_AVAILABLE / site_name
    enabled = NGINX_SITES_ENABLED / site_name

    if not available.exists():
        return {"success": False, "error": "Site not found"}
    if enabled.exists():
        return {"success": False, "error": "Site already enabled"}

    try:
        enabled.symlink_to(available)
        reload_nginx()
        return {"success": True, "message": f"Site {site_name} enabled"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def disable_site(site_name: str) -> dict:
    """Disable a site by removing symlink."""
    enabled = NGINX_SITES_ENABLED / site_name
    if not enabled.exists():
        return {"success": False, "error": "Site not enabled"}

    try:
        enabled.unlink()
        reload_nginx()
        return {"success": True, "message": f"Site {site_name} disabled"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def delete_site(site_name: str) -> dict:
    """Delete a site config."""
    available = NGINX_SITES_AVAILABLE / site_name
    enabled = NGINX_SITES_ENABLED / site_name

    if enabled.exists():
        enabled.unlink()
    if available.exists():
        available.unlink()
        reload_nginx()
        return {"success": True, "message": f"Site {site_name} deleted"}
    return {"success": False, "error": "Site not found"}


# ── Config Templates ──

def _static_template(domain: str, root: str) -> str:
    return f"""server {{
    listen 80;
    listen [::]:80;
    server_name {domain};
    root {root};
    index index.html index.htm;

    location / {{
        try_files $uri $uri/ =404;
    }}

    access_log /var/log/nginx/{domain}.access.log;
    error_log /var/log/nginx/{domain}.error.log;
}}
"""


def _php_template(domain: str, root: str) -> str:
    return f"""server {{
    listen 80;
    listen [::]:80;
    server_name {domain};
    root {root};
    index index.php index.html;

    location / {{
        try_files $uri $uri/ /index.php?$query_string;
    }}

    location ~ \\.php$ {{
        fastcgi_pass unix:/run/php/php-fpm.sock;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $realpath_root$fastcgi_script_name;
        include fastcgi_params;
    }}

    location ~ /\\.ht {{
        deny all;
    }}

    access_log /var/log/nginx/{domain}.access.log;
    error_log /var/log/nginx/{domain}.error.log;
}}
"""


def _proxy_template(domain: str, upstream: str) -> str:
    return f"""server {{
    listen 80;
    listen [::]:80;
    server_name {domain};

    location / {{
        proxy_pass {upstream};
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }}

    access_log /var/log/nginx/{domain}.access.log;
    error_log /var/log/nginx/{domain}.error.log;
}}
"""
