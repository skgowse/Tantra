#!/bin/bash
# ==============================================================================
# LEGAL TANTRA - LINUX UFW HOST FIREWALL CONFIGURATION
# Enforces network perimeter security and internal service isolation.
# ==============================================================================

set -euo pipefail

if [ "$EUID" -ne 0 ]; then
    echo "Please execute this script as root (sudo ./linux_ufw.sh)."
    exit 1
fi

echo "Configuring UFW host firewall rules for Legal Tantra..."

# Reset default policies: Deny incoming, Allow outgoing
ufw default deny incoming
ufw default allow outgoing

# Allow SSH administration (Customize port if non-standard)
ufw allow 22/tcp comment "SSH Remote Administration"

# Allow Inbound Web Traffic to Nginx Reverse Proxy
ufw allow 80/tcp comment "HTTP (Let's Encrypt / HTTPS Redirection)"
ufw allow 443/tcp comment "HTTPS (Secure Citizen Traffic)"

# Explicitly Deny Direct External Inbound Access to FastAPI Backend (8000)
# (Local loopback 127.0.0.1 traffic is permitted by default in UFW)
ufw deny 8000/tcp comment "Block external access to raw FastAPI backend"

# Enable UFW
ufw --force enable

echo "UFW Firewall configured and enabled successfully."
ufw status verbose
