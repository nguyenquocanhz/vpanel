# ⚡ VPS Panel

**Professional Linux Server Management Dashboard**

A secure, high-performance server management panel with real-time monitoring, remote administration, and one-click application deployment — built with FastAPI and a premium Glassmorphism UI.

![Python](https://img.shields.io/badge/python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square&logo=fastapi&logoColor=white)
![License](https://img.shields.io/badge/license-Proprietary-ef4444?style=flat-square)
![Platform](https://img.shields.io/badge/platform-Linux-FCC624?style=flat-square&logo=linux&logoColor=black)

---

## 📋 Table of Contents

- [Features](#-features)
- [Screenshots](#-screenshots)
- [Architecture](#-architecture)
- [Quick Install](#-quick-install)
- [Configuration](#-configuration)
- [AppStore Addons](#-appstore-addons)
- [License System](#-license-system)
- [API Reference](#-api-reference)
- [Security](#-security)
- [Tech Stack](#-tech-stack)
- [Development](#-development)
- [Troubleshooting](#-troubleshooting)

---

## ✨ Features

### 📊 Real-time Monitoring
- **CPU** — Usage per-core, frequency, load average (non-blocking, zero-delay)
- **Memory** — Total, Used, Free, Cached, Swap with live progress bars
- **Disk** — Usage per mountpoint, I/O throughput, partition list
- **Temperature** — Hardware sensors + sysfs thermal zone fallback
- **Network** — Upload/Download speed, interface list, primary IP
- **Charts** — Live CPU/RAM history and Network I/O (Chart.js, 60-point rolling)

### 🔧 Server Management
- **Power Control** — Remote Restart / Shutdown with confirmation dialog
- **Partition Manager** — Create, delete, format, mount/unmount (parted backend)
- **Service Manager** — List, Start, Stop, Restart systemd services with search
- **Process Monitor** — Top processes sorted by CPU/Memory with kill support

### 📦 AppStore (One-Click Install)
- **14 pre-configured addons** across 6 categories
- Auto-detect OS (Ubuntu/Arch) and run appropriate install commands
- Real-time install log output in modal
- Status tracking with service health indicators

### 🔐 Security
- **JWT Authentication** — Stateless tokens with bcrypt password hashing
- **RSA-4096 License** — Digitally signed license files bound to hardware
- **Hardware Fingerprint** — CPU ID + Board Serial + MAC address binding
- **Rate Limiting** — Brute-force protection on login endpoint
- **HTTPS** — Self-signed SSL certificate generated on install

### 🎨 Premium UI
- **Morphe UI** — Custom Glassmorphism design system
- **Lucide Icons** — Crisp SVG icons throughout (no emoji)
- **Dark Theme** — Deep navy/indigo palette with cyan/purple accents
- **Responsive** — Mobile-friendly sidebar with hamburger menu
- **Animations** — Smooth fade-in, glow effects, and micro-interactions
- **Shared Sidebar** — Single JS component across all pages

---

## 🏗️ Architecture

```
VPSPanel/
├── agent/                          # Python FastAPI Backend
│   ├── main.py                     # App entry + lifespan + static serving
│   ├── config.py                   # JSON config with deep merge
│   ├── auth/
│   │   ├── jwt_handler.py          # JWT create/decode (python-jose)
│   │   ├── password.py             # bcrypt hash/verify (direct, no passlib)
│   │   └── auth_middleware.py      # FastAPI dependency for route protection
│   ├── database/
│   │   └── __init__.py             # SQLAlchemy models (User, Metric, Audit)
│   ├── license/
│   │   ├── validator.py            # RSA signature + hardware ID verification
│   │   ├── hardware_id.py          # CPU/Board/MAC fingerprint generator
│   │   └── public_key.pem          # Embedded public key
│   ├── monitor/
│   │   ├── cpu.py                  # Non-blocking CPU metrics (interval=None)
│   │   ├── memory.py               # RAM + Swap stats
│   │   ├── disk.py                 # Disk usage + I/O + block devices
│   │   ├── temperature.py          # Sensors + sysfs fallback
│   │   └── system_info.py          # Hostname, uptime, network, OS info
│   ├── manager/
│   │   ├── power.py                # systemctl reboot/shutdown
│   │   ├── partition.py            # parted wrapper with root protection
│   │   ├── service.py              # systemd service CRUD (10s cache)
│   │   ├── process.py              # Process list/kill
│   │   └── appstore.py             # Addon registry + install/uninstall
│   ├── routes/
│   │   ├── auth_routes.py          # POST /api/auth/login, GET /me
│   │   ├── monitor_routes.py       # GET /api/monitor/* (async parallel)
│   │   ├── manager_routes.py       # POST /api/manager/*
│   │   ├── websocket_routes.py     # WS /ws/monitor (2s interval)
│   │   ├── license_routes.py       # GET /api/license/*
│   │   └── appstore_routes.py      # GET/POST /api/appstore/*
│   ├── utils/
│   │   └── __init__.py             # Logger setup
│   └── requirements.txt
│
├── dashboard/                      # Frontend (Vanilla HTML/CSS/JS)
│   ├── index.html                  # Login page
│   ├── dashboard.html              # Main overview dashboard
│   ├── partitions.html             # Disk & partition manager
│   ├── services.html               # Systemd service manager
│   ├── appstore.html               # One-click app installer
│   ├── css/
│   │   ├── morphe.css              # Glassmorphism design system
│   │   ├── login.css               # Login page styles
│   │   └── dashboard.css           # Dashboard layout + components
│   └── js/
│       ├── auth.js                 # Token management + apiFetch wrapper
│       ├── sidebar.js              # Shared sidebar (Lucide SVG icons)
│       ├── websocket.js            # WS client with auto-reconnect
│       ├── charts.js               # Chart.js setup (CPU/RAM + Network)
│       ├── monitor.js              # Metric card + disk/process rendering
│       └── app.js                  # Toast, power modal, init logic
│
├── tools/                          # Developer-only utilities
│   ├── generate_keys.py            # RSA-4096 keypair generator
│   └── license_generator.py        # Signed license file creator
│
├── install.sh                      # One-click installer (Ubuntu + Arch)
├── uninstall.sh                    # Clean removal script
└── README.md
```

---

## 🚀 Quick Install

### Requirements
- Linux server (Ubuntu 20.04+ or Arch Linux)
- Python 3.10+
- Root access

### One-Line Install

```bash
git clone https://github.com/yourname/VPSPanel.git
cd VPSPanel
sudo bash install.sh
```

The installer will:
1. Detect your OS (Ubuntu/Arch)
2. Install system dependencies (Python, OpenSSL, parted, lm-sensors)
3. Create Python virtualenv at `/opt/vpspanel/venv`
4. Generate self-signed SSL certificate
5. Configure & start systemd service
6. Create default admin account

### Access Dashboard

```
🌐 https://YOUR_SERVER_IP:8443
```

> ⚠️ Browser will show SSL warning (self-signed cert) → Click **Advanced** → **Proceed**

### Get Admin Password

```bash
journalctl -u vpspanel --no-pager | grep -A3 'DEFAULT ADMIN'
```

### Service Commands

```bash
systemctl status vpspanel      # Check status
systemctl restart vpspanel     # Restart
systemctl stop vpspanel        # Stop
journalctl -u vpspanel -f      # Live logs
```

---

## ⚙️ Configuration

Config file: `/etc/vpspanel/config.json`

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8443,
    "workers": 1
  },
  "security": {
    "jwt_secret": "auto-generated-on-first-run",
    "jwt_expire_hours": 24,
    "rate_limit_attempts": 5,
    "rate_limit_window": 300
  },
  "monitoring": {
    "websocket_interval": 2,
    "history_retention_hours": 24
  }
}
```

---

## 📦 AppStore Addons

One-click installation of popular server software:

| Category | Addons | Description |
|----------|--------|-------------|
| 🌐 Web Server | **Nginx** | High-performance web server & reverse proxy |
| 📦 Container | **Docker** | Container platform for applications |
| 🗄️ Database | **MySQL**, **PostgreSQL**, **Redis**, **MongoDB** | SQL & NoSQL databases |
| ⚡ Runtime | **Node.js 20**, **Python 3** | Application runtimes |
| 🛡️ Security | **Certbot**, **Fail2Ban**, **UFW** | SSL certs, intrusion prevention, firewall |
| 🛠️ Tools | **phpMyAdmin**, **Portainer CE** | Web-based admin tools |

Each addon:
- Auto-detects OS and runs the correct package manager
- Enables & starts the associated systemd service
- Shows real-time install log in the UI
- Tracks installed/running status

---

## 🔑 License System

### How It Works

```
Developer Machine                     Customer Server
─────────────────                     ───────────────
1. generate_keys.py
   → private_key.pem (SECRET)
   → public_key.pem ──────────────→  Embedded in agent

2. Customer gets hardware_id
   ←──── GET /api/license/hardware

3. license_generator.py
   --customer "Company"
   --hardware-id "SHA256..."
   → license.lic ─────────────────→  /opt/vpspanel/license.lic

                                      4. Agent validates on startup:
                                         ✓ RSA signature intact?
                                         ✓ Hardware ID matches?
                                         ✓ Not expired?
```

### Generate Keys (Once)

```bash
cd tools
python generate_keys.py
```

### Create License

```bash
# Get hardware ID from target server
curl -k https://SERVER:8443/api/license/hardware \
  -H "Authorization: Bearer TOKEN"

# Generate license
python license_generator.py \
  -c "Customer Name" \
  -hw "HARDWARE_ID_HERE" \
  -d 365 \
  -o license.lic
```

### Install License

```bash
scp license.lic root@server:/opt/vpspanel/license.lic
systemctl restart vpspanel
```

---

## 📡 API Reference

Base URL: `https://SERVER:8443`

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/login` | Login → JWT tokens |
| `GET` | `/api/auth/me` | Current user info |

### Monitoring

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/monitor/overview` | All metrics (parallel) |
| `GET` | `/api/monitor/cpu` | CPU usage + info |
| `GET` | `/api/monitor/memory` | RAM + Swap |
| `GET` | `/api/monitor/disk` | Disk usage + partitions |
| `GET` | `/api/monitor/temperature` | Hardware temperatures |
| `GET` | `/api/monitor/network` | Network interfaces + I/O |
| `GET` | `/api/monitor/processes` | Process list |
| `WS` | `/ws/monitor?token=JWT` | Real-time metrics stream |

### Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/manager/power/restart` | Restart server |
| `POST` | `/api/manager/power/shutdown` | Shutdown server |
| `GET` | `/api/manager/services` | List systemd services |
| `POST` | `/api/manager/service/{name}/{action}` | Start/Stop/Restart |
| `GET` | `/api/manager/partitions` | List disks & partitions |
| `POST` | `/api/manager/partition/create` | Create partition |

### AppStore

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/appstore/addons` | List all addons + status |
| `GET` | `/api/appstore/addon/{id}` | Addon details |
| `POST` | `/api/appstore/install` | Install addon |
| `POST` | `/api/appstore/uninstall` | Uninstall addon |

### Interactive Docs

- Swagger UI: `https://SERVER:8443/api/docs`
- ReDoc: `https://SERVER:8443/api/redoc`

---

## 🔐 Security

### Protection Layers

| Layer | Mechanism |
|-------|-----------|
| **Transport** | HTTPS with TLS (self-signed or custom cert) |
| **Auth** | JWT tokens (24h expiry) + bcrypt password hashing |
| **License** | RSA-4096 digital signatures |
| **Hardware Binding** | CPU ID + Board Serial + MAC fingerprint |
| **Rate Limiting** | 5 login attempts per 5 minutes |
| **Partition Safety** | Root `/` partition is protected from modification |
| **Service Safety** | Cannot stop VPS Panel from itself |

### Production Recommendations

```bash
# 1. Change default admin password immediately after install

# 2. Use real SSL certificate
sudo certbot certonly --standalone -d your-domain.com
# Update systemd ExecStart with real cert paths

# 3. Restrict firewall
sudo ufw allow 8443/tcp
sudo ufw enable

# 4. Apply Pyarmor obfuscation for distribution
pip install pyarmor
pyarmor gen --recursive agent/
```

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Backend | Python 3.10+ / FastAPI | REST API + WebSocket |
| Server | Uvicorn | ASGI server with SSL |
| Database | SQLite / SQLAlchemy | User auth + audit logs |
| Monitoring | psutil | System metrics collection |
| Auth | python-jose + bcrypt | JWT tokens + password hashing |
| License | cryptography (RSA-4096) | Digital signature verification |
| Frontend | HTML5 / Vanilla CSS / JS | No build step needed |
| Charts | Chart.js 4.x | Live metric visualization |
| Icons | Lucide (inline SVG) | Crisp, consistent iconography |
| UI Theme | Morphe UI (custom) | Glassmorphism dark design system |

---

## 💻 Development

### Local Development (Windows/Mac)

```bash
# Install dependencies
cd agent
pip install -r requirements.txt

# Run in dev mode (monitoring won't work on non-Linux)
python -m uvicorn agent.main:app --reload --port 8443
```

### Run Tests

```bash
pip install pytest
python -m pytest agent/tests/ -v
```

### Project Structure Notes

- **Non-blocking CPU**: Uses `psutil.cpu_percent(interval=None)` — zero delay
- **Parallel Overview**: `asyncio.gather()` runs all monitors concurrently
- **Service Cache**: 10-second TTL to reduce `systemctl` calls
- **Shared Sidebar**: Single `sidebar.js` renders nav across all pages
- **Direct bcrypt**: No passlib wrapper — avoids bcrypt 4.1+ incompatibility

---

## 🔧 Troubleshooting

### Service won't start

```bash
journalctl -u vpspanel -n 50 --no-pager
```

### Port 8443 not accessible

```bash
# Check listening
ss -tlnp | grep 8443

# Open firewall
sudo ufw allow 8443/tcp
```

### Reset admin password

```bash
sudo rm -f /opt/vpspanel/data/vpspanel.db
sudo systemctl restart vpspanel
journalctl -u vpspanel --no-pager | grep -A3 'DEFAULT ADMIN'
```

### bcrypt / passlib error

This project uses **bcrypt directly** (not via passlib) to avoid compatibility issues with bcrypt >= 4.1. If you see passlib errors, ensure `agent/auth/password.py` imports `bcrypt` directly.

---

## 📄 License

Proprietary Software. All rights reserved.

Redistribution and use require a valid license key issued by the developer.

---

## 👤 Author

**NQA Tech** — Server Management Solutions

---

<p align="center">
  <b>⚡ VPS Panel v1.0.0</b><br>
  Built with FastAPI • Morphe UI • Lucide Icons
</p>
