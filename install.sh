#!/bin/bash
# ══════════════════════════════════════════════════
# VPS Panel - One-Click Installer
# Supports: Ubuntu 20.04+, Arch Linux
# ══════════════════════════════════════════════════
set -e

RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; YELLOW='\033[1;33m'; NC='\033[0m'
INSTALL_DIR="/opt/vpspanel"
CONFIG_DIR="/etc/vpspanel"
LOG_DIR="/var/log/vpspanel"
SERVICE_NAME="vpspanel"

echo -e "${CYAN}"
echo "  ╔══════════════════════════════════════╗"
echo "  ║     ⚡ VPS Panel Installer v1.0     ║"
echo "  ║     Server Management Dashboard     ║"
echo "  ╚══════════════════════════════════════╝"
echo -e "${NC}"

# Check root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: Please run as root (sudo ./install.sh)${NC}"
    exit 1
fi

# Detect OS
detect_os() {
    if [ -f /etc/arch-release ]; then
        OS="arch"
        PKG_INSTALL="pacman -S --noconfirm"
        PKG_UPDATE="pacman -Syu --noconfirm"
    elif [ -f /etc/lsb-release ] || [ -f /etc/debian_version ]; then
        OS="ubuntu"
        PKG_INSTALL="apt-get install -y"
        PKG_UPDATE="apt-get update -y"
    else
        echo -e "${RED}Unsupported OS. Only Ubuntu/Debian and Arch Linux are supported.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Detected OS: ${OS}${NC}"
}

# Install dependencies
install_deps() {
    echo -e "${CYAN}Installing dependencies...${NC}"
    $PKG_UPDATE
    if [ "$OS" = "arch" ]; then
        $PKG_INSTALL python python-pip python-virtualenv openssl parted lm_sensors
    else
        $PKG_INSTALL python3 python3-pip python3-venv openssl parted lm-sensors
    fi
    echo -e "${GREEN}✓ Dependencies installed${NC}"
}

# Setup directories
setup_dirs() {
    echo -e "${CYAN}Setting up directories...${NC}"
    mkdir -p "$INSTALL_DIR"/{data,certs}
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$LOG_DIR"
    echo -e "${GREEN}✓ Directories created${NC}"
}

# Copy files
copy_files() {
    echo -e "${CYAN}Copying files...${NC}"
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
    cp -r "$SCRIPT_DIR/agent" "$INSTALL_DIR/"
    cp -r "$SCRIPT_DIR/dashboard" "$INSTALL_DIR/"
    echo -e "${GREEN}✓ Files copied to ${INSTALL_DIR}${NC}"
}

# Setup Python venv
setup_venv() {
    echo -e "${CYAN}Setting up Python virtual environment...${NC}"
    python3 -m venv "$INSTALL_DIR/venv"
    "$INSTALL_DIR/venv/bin/pip" install --upgrade pip
    "$INSTALL_DIR/venv/bin/pip" install -r "$INSTALL_DIR/agent/requirements.txt"
    echo -e "${GREEN}✓ Python environment ready${NC}"
}

# Generate self-signed SSL cert
generate_ssl() {
    echo -e "${CYAN}Generating SSL certificate...${NC}"
    openssl req -x509 -newkey rsa:4096 -keyout "$INSTALL_DIR/certs/key.pem" \
        -out "$INSTALL_DIR/certs/cert.pem" -days 365 -nodes \
        -subj "/CN=vpspanel/O=VPSPanel/C=US" 2>/dev/null
    echo -e "${GREEN}✓ SSL certificate generated${NC}"
}

# Setup systemd service
setup_service() {
    echo -e "${CYAN}Setting up systemd service...${NC}"
    cat > /etc/systemd/system/${SERVICE_NAME}.service << EOF
[Unit]
Description=VPS Panel - Server Management Agent
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=${INSTALL_DIR}
Environment="PATH=${INSTALL_DIR}/venv/bin"
Environment="VPSPANEL_DATA_DIR=${INSTALL_DIR}/data"
Environment="VPSPANEL_CONFIG=${CONFIG_DIR}/config.json"
Environment="VPSPANEL_DB_URL=sqlite:///${INSTALL_DIR}/data/vpspanel.db"
ExecStart=${INSTALL_DIR}/venv/bin/uvicorn agent.main:app --host 0.0.0.0 --port 8443 --ssl-keyfile ${INSTALL_DIR}/certs/key.pem --ssl-certfile ${INSTALL_DIR}/certs/cert.pem
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    systemctl daemon-reload
    systemctl enable ${SERVICE_NAME}
    systemctl start ${SERVICE_NAME}
    echo -e "${GREEN}✓ Service installed and started${NC}"
}

# Get server IP
get_ip() {
    IP=$(hostname -I | awk '{print $1}')
    echo "$IP"
}

# Main
main() {
    detect_os
    install_deps
    setup_dirs
    copy_files
    setup_venv
    generate_ssl
    setup_service

    IP=$(get_ip)
    echo ""
    echo -e "${GREEN}══════════════════════════════════════════${NC}"
    echo -e "${GREEN}  ✅ VPS Panel installed successfully!${NC}"
    echo -e "${GREEN}══════════════════════════════════════════${NC}"
    echo ""
    echo -e "  Dashboard: ${CYAN}https://${IP}:8443${NC}"
    echo ""
    echo -e "  ${YELLOW}Default credentials will be shown in logs:${NC}"
    echo -e "  ${CYAN}journalctl -u vpspanel --no-pager | grep -A2 'DEFAULT ADMIN'${NC}"
    echo ""
    echo -e "  Commands:"
    echo -e "    Status:  ${CYAN}systemctl status vpspanel${NC}"
    echo -e "    Logs:    ${CYAN}journalctl -u vpspanel -f${NC}"
    echo -e "    Restart: ${CYAN}systemctl restart vpspanel${NC}"
    echo ""
}

main "$@"
