#!/bin/bash
# VPS Panel - Uninstaller
set -e
RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; NC='\033[0m'

if [ "$EUID" -ne 0 ]; then echo -e "${RED}Please run as root${NC}"; exit 1; fi

echo -e "${RED}⚠ This will remove VPS Panel completely.${NC}"
read -p "Are you sure? (y/N): " confirm
if [ "$confirm" != "y" ]; then echo "Cancelled."; exit 0; fi

echo -e "${CYAN}Stopping service...${NC}"
systemctl stop vpspanel 2>/dev/null || true
systemctl disable vpspanel 2>/dev/null || true
rm -f /etc/systemd/system/vpspanel.service
systemctl daemon-reload

echo -e "${CYAN}Removing files...${NC}"
rm -rf /opt/vpspanel
rm -rf /etc/vpspanel
rm -rf /var/log/vpspanel

echo -e "${GREEN}✅ VPS Panel removed successfully.${NC}"
