# Legal Tantra (లీగల్ తంత్ర)

> **"Know the Law. Know Your Rights. Speak with Confidence."**  
> **"చట్టాన్ని తెలుసుకోండి. మీ హక్కులను గుర్తించండి. ఆత్మవిశ్వాసంతో మాట్లాడండి."**

**Legal Tantra** is an AI-assisted legal awareness and incident preparation platform for ordinary Indian citizens. It helps victims, complainants, and citizens understand potentially relevant laws under the new Indian legal codes (**BNS 2023**, **BNSS 2023**, **BSA 2023**, **Consumer Protection Act 2019**, **PWDVA 2005**, **Specific Relief Act 1963**), learn their procedural rights, and prepare an editable, strictly factual incident summary before approaching the appropriate authority.

---

## 🌟 Key Architecture & Capabilities

1. **Safety-First Intake & Triage**:
   - Detects active danger, weapons, physical injury, and domestic emergencies.
   - Immediately surfaces verified helplines without delaying for AI processing:
     - **112**: National Emergency Helpline (Police, Fire, Ambulance)
     - **1091 / 181**: Women Helpline (24x7)
     - **1930**: National Cyber Crime Helpline (Golden Hour reporting)
     - **108**: Emergency Medical Ambulance
     - **1098**: Childline

2. **Multi-Jurisdiction Classification**:
   - Does **not** force every issue into a criminal police complaint.
   - Categorizes incidents into:
     - **Criminal Offences** (Assault, Threat, Theft, Stalking u/s BNS 2023)
     - **Cyber & Financial Scams** (1930 Helpline & IT Act 2000)
     - **Domestic Violence** (Protection Officer & Magistrate u/s PWDVA 2005)
     - **Civil & Property Disputes** (Civil Court & SDM u/s Specific Relief Act)
     - **Consumer Grievances** (District Consumer Commission u/s CPA 2019)
     - **Employment Disputes** (Labour Commissioner u/s Payment of Wages Act)
     - **Uncertain / Mixed Matters** (Neutral clarification questions)

3. **Strictly Non-Fabricated Factual Summaries**:
   - Adheres strictly to factual integrity rules:
     - Never invents dates, times, locations, witnesses, or injuries.
     - Never inserts assumed assertions (e.g. no assumed "lack of provocation").
     - Customizes target venue by jurisdiction (Police Station, Consumer Commission, Civil Court, Labour Authority).
     - Marks unstated details explicitly as *"Not provided"*.
     - Generates in-place editable statement for citizen review before export.

4. **Hybrid AI Architecture with Offline Fallback**:
   - Works 100% offline out-of-the-box using the deterministic legal engine.
   - Pluggable Gemini (`GEMINI_API_KEY`) and OpenAI (`OPENAI_API_KEY`) integrations with request timeouts and automatic fallback.

5. **Bilingual Support (English & తెలుగు)**:
   - Complete interface, follow-up questions, legal summaries, and speech recognition/synthesis in English and Telugu.

---

## 🚀 Local Setup Instructions (Windows)

### Prerequisites
- **Python 3.10+**
- **Node.js v18+ & npm**

### 1. Start the Backend (FastAPI + SQLite)
```powershell
# Navigate to backend directory
cd backend

# Run the backend server
python -m uvicorn app.main:app --port 8000 --host 127.0.0.1
```
- OpenAPI Documentation: **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**
- Health Check: **[http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)**

### 2. Start the Frontend (React + Vite)
```powershell
# In a new terminal, navigate to frontend directory
cd frontend

# Install dependencies (if not already installed)
npm install

# Start Vite development server
npm run dev
```
- Web Application: **[http://localhost:3000](http://localhost:3000)**

---

## 🧪 Automated Testing Suite

The repository includes a comprehensive test suite covering API contracts, RAG hallucination guards, and representative Scenarios A through J:

```powershell
cd backend
python -m pytest
```

### Verified Scenarios:
| Scenario | Description | Verified Behavior |
| :--- | :--- | :--- |
| **Scenario A** | Threatening Message | Classified u/s 351 BNS 2023 with FIR rights u/s 173 BNSS |
| **Scenario B** | Online Banking Scam | Extracts amount lost, routes to 1930 Cyber helpline & IT Act 66D |
| **Scenario C** | Property Boundary Dispute | Identified as Civil matter; targets Civil Court / SDM without forcing police FIR |
| **Scenario D** | Incomplete Description | System asks targeted 1-by-1 follow-up questions without overwhelming user |
| **Scenario E** | Injury & Immediate Threat | Priority 112 / 108 emergency advisory triggered |
| **Scenario F** | Changing Earlier Answer | System accepts corrected date/timeline without contradictory assertions |
| **Scenario G** | Telugu Input | End-to-end conversation, fact extraction, and response in Telugu |
| **Scenario H** | AI Provider Failure | Seamless fallback to deterministic provider without crash |
| **Scenario I** | Unverified / Fake Law | Hallucination guard identifies nonexistent act as Unverified / Low Confidence |
| **Scenario J** | Missing Facts in Summary | Unstated fields marked *"Not provided"*; no fabricated claims |

---

## 🛡️ Application Security & DevSecOps Architecture

Legal Tantra implements enterprise-grade DevSecOps controls to protect citizen privacy and platform availability:

1. **Web Application Firewall (WAF) & Reverse Proxy**:
   - Production Nginx reverse proxy configuration (`deploy/nginx/nginx.conf`) with TLS 1.2/1.3, HSTS, and rate-limiting zones.
   - Cloudflare WAF integration rules (`deploy/waf/cloudflare_rules.json` and `deploy/waf/CLOUDFLARE_WAF_GUIDE.md`) with explicit charset allowance for Telugu (Indic) Unicode scripts (`\u0C00-\u0C7F`).
2. **Network Isolation**:
   - Windows Defender Firewall script (`deploy/firewall/windows_firewall.ps1`) and Linux UFW script (`deploy/firewall/linux_ufw.sh`) isolate the raw FastAPI backend (port 8000) to localhost loopback (`127.0.0.1`), preventing direct external access.
3. **Application Layer Defenses**:
   - **OWASP Security Headers**: Enforces `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection`, strict `Referrer-Policy`, and CSP.
   - **Sliding-Window Rate Limiting**: Built-in `InMemoryRateLimiter` restricts AI endpoints (`/api/chat/message`, `/api/document/analyze`) to prevent volumetric quota exhaustion.
   - **Request Size Caps**: 1 MB limit for standard JSON payloads and 10 MB cap for document uploads (returning HTTP 413).
   - **Prompt Injection Defense**: Deterministic filtering in `app/security/sanitization.py` strips adversarial override patterns (`"ignore previous instructions"`, `"jailbreak"`, `"reveal system prompt"`).
   - **Privacy & PII Masking**: Real-time redaction of Aadhaar, phone numbers, PAN cards, and emails prior to logging, compliant with India's Digital Personal Data Protection Act (DPDP Act 2023).

### Running Security Tests
```powershell
cd backend
python -m pytest tests/test_security.py
```

---

## 🎭 3-Minute Demonstration Script

1. **Safety Triage**: Type *"Someone is following me right now with a weapon near the market!"*  
   *Notice*: Immediate 112 / 108 Emergency banner triggers with verified numbers.
2. **Civil vs Criminal Awareness**: Type *"My builder refused to hand over flat keys and cancelled my flat booking after I paid 5 lakhs."*  
   *Notice*: System recognizes a Consumer / Civil grievance and suggests the District Consumer Commission rather than forcing a police FIR.
3. **Telugu Language Processing**: Switch language to **తెలుగు** and type:  
   *"నిన్న సాయంత్రం కాలేజీ దగ్గర ఒక వ్యక్తి నన్ను చంపేస్తానని బెదిరించాడు."*  
   *Notice*: System responds with supportive Telugu guidance and identifies BNS 351 criminal intimidation.
4. **Factual Summary Review**: Click **View Legal Analysis & Rights**, then **Draft Incident Statement**.  
   *Notice*: Factual statement is neutral, marks missing elements cleanly, contains no fabricated statements, and provides an editable text area with print controls.

---

## ⚖️ Legal & AI Disclaimer

Legal Tantra is an educational and factual preparation aid for citizens. It does not provide certified legal representation, legal advice, or substitute for consultation with a licensed advocate, police officer, or judicial magistrate.
