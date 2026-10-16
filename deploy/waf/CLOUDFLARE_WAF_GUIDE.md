# Web Application Firewall (WAF) Implementation Guide

## 1. WAF Architecture Overview

Legal Tantra employs defense-in-depth across the web layer:

```
Citizen Browser / Mobile Client
        │  HTTPS (TLS 1.3)
        ▼
Cloudflare Edge / Managed WAF
  ├─ OWASP Core Ruleset (CRS) Scoring
  ├─ Cloudflare Managed Threat Intelligence
  ├─ Volumetric AI Endpoint Rate Limiting
  └─ Indic UTF-8 Script Normalization
        │  Authenticated Origin Pull (mTLS / Cloudflare Tunnel)
        ▼
Nginx Reverse Proxy
  ├─ Local Rate Limiting Zones (General: 60r/m, AI: 15r/m)
  ├─ Request Body Limits (1MB JSON, 10MB Doc Upload)
  └─ OWASP Security Response Headers
        │  Loopback only (127.0.0.1:8000)
        ▼
FastAPI Application Backend
  ├─ In-Memory Sliding-Window Limiter
  ├─ Prompt Injection Detection & Neutralization
  ├─ XSS & HTML Input Sanitization
  └─ Zero-PII Log Masking
```

---

## 2. Managed Rulesets & Configuration

### A. Cloudflare Managed Ruleset
* **Status**: Enabled
* **Action**: Block high-confidence attacks (CVE exploits, command injections, Apache/Nginx vulnerabilities).
* **Sensitivity**: Default / High.

### B. Cloudflare OWASP Core Ruleset (CRS)
* **Paranoia Level**: Level 1 (Recommended for production to prevent false positives on natural language complaints).
* **Anomaly Score Threshold**: 40 (Score-based evaluation).
* **Action on Threshold Exceeded**: Managed Challenge or Block.

---

## 3. Handling Telugu (Indic) Script False Positives

### The Challenge
Standard WAF anomaly detection rules (such as OWASP CRS rule `920270` - *Invalid Character in Request Body*) often flag multibyte UTF-8 non-ASCII characters as suspicious binary payloads. Because Legal Tantra supports bilingual intake in Telugu (`\u0C00` to `\u0C7F`), overly aggressive rules could block legitimate citizens reporting crimes in their native language.

### Remediation Protocol
1. **Content-Type Enforcement**: Ensure the client always sends `Content-Type: application/json; charset=utf-8`.
2. **Rule Exception**: In Cloudflare WAF, create an exception for paths matching `/api/chat/*` and `/api/incident/*` to bypass CRS Rule `920270` (Restricted Characters) while maintaining SQLi and RCE checks active.
3. **Paranoia Level Control**: Keep CRS at **Paranoia Level 1** on public intake routes. Do not enable Level 3 or 4 on natural language endpoints without character set whitelisting.

---

## 4. Rate Limiting Rules

| Endpoint | Purpose | Rate Limit | Action |
| :--- | :--- | :--- | :--- |
| `/api/chat/message` | Incident conversation & follow-up questions | 20 req / minute per IP | 429 Too Many Requests |
| `/api/document/analyze` | OCR & document parsing | 5 req / minute per IP | 429 Too Many Requests |
| `/api/incident/analyze` | AI statutory matching & legal synthesis | 20 req / minute per IP | 429 Too Many Requests |
| `/api/legal/search` | Legal knowledge library queries | 60 req / minute per IP | 429 Too Many Requests |

---

## 5. False Positive Review Workflow

1. Navigate to **Cloudflare Dashboard** -> **Security** -> **Events**.
2. Filter events by `Action: Block` or `Action: Managed Challenge`.
3. Check the `Ray ID`, `Rule ID`, and `Matched Pattern`.
4. If a legitimate citizen incident description triggered a false positive:
   - Identify whether it was flagged by a specific CRS Rule ID (e.g. `942100` SQLi false positive on word combinations or `920270` multibyte characters).
   - Add an override exception in **WAF** -> **Custom Rules** -> **Skip Rule** for that specific Rule ID when `http.request.uri.path matches "^/api/chat/"`.
   - Never globally disable WAF protection.
