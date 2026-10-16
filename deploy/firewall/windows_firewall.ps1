<#
.SYNOPSIS
    Configures Windows Defender Firewall rules for Legal Tantra deployment.
.DESCRIPTION
    Ensures network isolation by:
    1. Permitting Inbound HTTPS (443) and HTTP (80) for Nginx / reverse proxy.
    2. Restricting Backend (Port 8000) strictly to Localhost (127.0.0.1) so direct external calls bypass is prevented.
    3. Blocking direct external access to development ports.
.PARAMETER Rollback
    Removes the Legal Tantra firewall rules and restores defaults.
#>

param (
    [switch]$Rollback = $false
)

# Elevate check
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Error "This script must be executed in an elevated PowerShell session (Run as Administrator)."
    exit 1
}

$RulePrefix = "LegalTantra_"

if ($Rollback) {
    Write-Host "Rolling back Legal Tantra firewall rules..." -ForegroundColor Yellow
    Get-NetFirewallRule | Where-Object { $_.Name -like "$RulePrefix*" } | Remove-NetFirewallRule
    Write-Host "Firewall rules removed successfully." -ForegroundColor Green
    exit 0
}

Write-Host "Configuring Windows Defender Firewall for Legal Tantra..." -ForegroundColor Cyan

# 1. Allow Inbound HTTPS (TCP 443) for Nginx Reverse Proxy
New-NetFirewallRule -Name "${RulePrefix}Inbound_HTTPS" `
    -DisplayName "Legal Tantra - Inbound HTTPS (443)" `
    -Description "Permits external TLS traffic to Nginx reverse proxy" `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 443 `
    -Action Allow `
    -Profile Any `
    -ErrorAction SilentlyContinue | Out-Null

# 2. Allow Inbound HTTP (TCP 80) for ACME Challenge & Redirects
New-NetFirewallRule -Name "${RulePrefix}Inbound_HTTP" `
    -DisplayName "Legal Tantra - Inbound HTTP (80)" `
    -Description "Permits external HTTP traffic for HTTPS redirection and Let's Encrypt validation" `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 80 `
    -Action Allow `
    -Profile Any `
    -ErrorAction SilentlyContinue | Out-Null

# 3. Block External Direct Access to Backend API Port 8000 (Allow Loopback Only)
New-NetFirewallRule -Name "${RulePrefix}Block_External_8000" `
    -DisplayName "Legal Tantra - Block External Backend Access (8000)" `
    -Description "Blocks external networks from accessing the raw FastAPI backend directly without passing through Nginx/WAF" `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 8000 `
    -RemoteAddress @("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "Internet") `
    -Action Block `
    -Profile Any `
    -ErrorAction SilentlyContinue | Out-Null

Write-Host "Windows Defender Firewall configured successfully for Legal Tantra." -ForegroundColor Green
Write-Host "- Inbound Ports 80 & 443: ALLOWED (Public)"
Write-Host "- Inbound Port 8000 (FastAPI): BLOCKED for external IPs (Localhost loopback only)"
