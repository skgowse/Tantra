# Legal Tantra (లీగల్ తంత్ర)

> **"Know the Law. Know Your Rights. Speak with Confidence."**  
> **"చట్టాన్ని తెలుసుకోండి. మీ హక్కులను గుర్తించండి. ఆత్మవిశ్వాసంతో మాట్లాడండి."**

**Legal Tantra** is an AI-powered legal awareness and police assistance platform for ordinary Indian citizens. It helps victims, complainants, and witnesses understand potentially relevant laws under the new Indian criminal codes (BNS, BNSS, BSA 2023), learn their fundamental procedural rights, and prepare a structured, factual incident statement before approaching a police station.

---

## 🌟 Core Features

1. **Conversational AI Incident Assistant ("Understand My Incident")**:
   - Zero-friction start: No mandatory registration, Aadhaar, or phone numbers required.
   - Bilingual support in **English** and **Telugu (తెలుగు)**.
   - Text and speech conversation using the **Web Speech API** (with pre-submission transcript review & editing).
   - Voice playback for AI responses (with play, pause, and mute controls).
2. **Immediate Safety & Emergency Assessment**:
   - Detects ongoing physical danger, active violence, or severe injuries.
   - Prioritizes citizen safety and provides verified emergency numbers:
     - **112**: National Emergency Helpline (Police, Fire, Ambulance)
     - **1091**: Women Helpline (24x7)
     - **1930**: National Cyber Crime Helpline (Golden Hour reporting)
     - **108**: Emergency Medical Ambulance
3. **Emotion-Aware Tone Modulation**:
   - Identifies emotional cues (fear, anxiety, distress, anger, confusion, urgency).
   - Responds in a calm, non-judgmental, supportive tone and keeps follow-up questions short and manageable.
4. **Dynamic AI Follow-Up Questions**:
   - Never asks a fixed list of static questions.
   - Evaluates missing factual elements (dates, locations, identities, specific threats, injury, evidence) and asks 1–2 targeted questions at a time.
5. **Grounded Legal Knowledge Engine (BNS 2023)**:
   - Evaluates provisions strictly against verified statutory references from **India Code**:
     - **Bharatiya Nyaya Sanhita, 2023 (BNS)**: Sec 351 (Criminal Intimidation), Sec 115 (Voluntarily Causing Hurt), Sec 117 (Grievous Hurt), Sec 318 (Cheating/Fraud), Sec 303 (Theft), Sec 78 (Stalking).
     - **Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS)**: Sec 173 (Mandatory FIR recording, Electronic reporting & Free copy to complainant), Zero FIR, Sec 35 (Arrest safeguards).
     - **Bharatiya Sakshya Adhiniyam, 2023 (BSA)**: Sec 61 & 63 (Admissibility of electronic evidence & digital certificates).
     - **Information Technology Act, 2000**: Sec 66D (Cheating by personation).
6. **Police-Station Preparation Assistant**:
   - Generates a formal 7-step factual incident statement.
   - In-place editable textarea for citizen review and correction.
   - Evidence & document checklist (Government ID, preserved WhatsApp chats, medical slips).
   - Key procedural questions to ask the Station House Officer (SHO).
   - One-click copy and clean print / PDF export.
7. **Legal Document Analyzer**:
   - Upload or paste police notices, court summons, or FIR copies.
   - Extracts dates and case reference numbers.
   - Explains complex legal jargon (*Cognizable*, *Zero FIR*, *Bail*, *Charge Sheet*, *Sub Judice*, *Prima Facie*) in plain language.
8. **Legal Knowledge Library**:
   - Searchable, filterable repository of Indian criminal and procedural law.

---

## 🚀 Quick Start (Zero-Dependency Setup)

### 1. Start the Backend (FastAPI + SQLite)
```powershell
cd backend
python -m uvicorn app.main:app --port 8000 --host 127.0.0.1
```
The backend initializes a local SQLite database (`legaltantra.db`) and seeds verified Indian statutes automatically on startup.
- OpenAPI Documentation: **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**
- Health Check: **[http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)**

### 2. Start the Frontend (React + Vite)
```powershell
cd frontend
npm run dev
```
Open your browser at **[http://localhost:3000](http://localhost:3000)**.

---

## 🎯 1-Click Test Scenarios Available on Homepage

You can test the entire workflow with a single click from the home page:
- **Scenario A (Verbal Threat)**: Tests intimidation classification u/s 351 BNS, targeted follow-ups, and FIR rights u/s 173 BNSS.
- **Scenario B (Online Bank Fraud)**: Tests cyber cheating u/s 318 BNS & 66D IT Act, 1930 helpline guidance, and transaction slip checklist.
- **Scenario C (Physical Assault)**: Tests bodily injury checks, medical emergency prompts, and BNS Section 115/117 hurt provisions.
- **Scenario D (Distressed User)**: Tests emotion-cue recognition, calming supportive tone modulation, and bite-sized questions.
- **Scenario E (తెలుగు సంభాషణ - Telugu Input)**: Demonstrates end-to-end conversation, speech synthesis, and legal explanations in Telugu.

---

## ⚖️ Legal & AI Disclaimer

Legal Tantra provides general legal awareness and factual preparation assistance. AI-generated explanations are preliminary and are not a substitute for advice from a qualified legal professional, police inquiry, or court determination.
