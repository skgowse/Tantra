import React, { useState, useEffect, useRef } from 'react'
import {
  Scale, Shield, FileText, AlertTriangle, Activity, CheckCircle2,
  FolderOpen, Settings, Search, Users, BookOpen,
  Volume2, VolumeX, Mic, Download, Plus, Clock, Lock, RefreshCw, Send, Trash2, Eye,
  ArrowRight, ShieldCheck, Printer, HelpCircle, PhoneCall, ExternalLink, Globe,
  MessageSquare, Sparkles, CheckSquare, Square, Edit3, Copy, AlertOctagon, Info,
  Menu, X, ChevronRight, Layers, Check, ArrowUpRight, Home
} from 'lucide-react'

const API_BASE = (import.meta as any).env?.VITE_API_BASE || 'http://localhost:8000/api'

// Bilingual Dictionary
const I18N = {
  en: {
    brandTagline: "Know the Law. Know Your Rights. Speak with Confidence.",
    emergencyBtn: "🚨 Emergency: 112",
    navHome: "Home",
    navChat: "Incident Assistant",
    navAnalysis: "Legal Analysis",
    navPolice: "Police Statement",
    navLibrary: "Legal Library",
    navDoc: "Document Analyzer",
    navAbout: "About & Privacy",
    heroTitle: "Before You Visit the Police Station, Know Your Rights.",
    heroSubtitle: "Describe what happened in your own words. Understand potentially relevant laws, learn about your rights, and prepare to explain your incident clearly.",
    ctaStart: "Start Incident Assistant",
    ctaRights: "Explore Legal Library",
    step1Title: "1. Tell Us What Happened",
    step1Desc: "Type or speak naturally in plain English or Telugu. No legal jargon required.",
    step2Title: "2. Understand Your Position",
    step2Desc: "Our AI retrieves verified provisions under the Bharatiya Nyaya Sanhita (BNS) and explains your rights.",
    step3Title: "3. Prepare With Confidence",
    step3Desc: "Get an organized 7-step factual incident statement and an evidence checklist ready for the police.",
    chatHeading: "Tell Us What Happened",
    chatSub: "You don't need to know legal terminology. Explain what happened in your own words. Our AI assistant will help you understand potentially relevant laws, your rights, and how to prepare before approaching the police.",
    chatPlaceholder: "Describe what happened. For example, someone threatened me outside college, or I lost money in an online bank fraud...",
    sendBtn: "Send",
    micReviewTitle: "Review Recognized Speech",
    micReviewDesc: "You can edit any transcription errors before submitting to the AI.",
    micSubmit: "Submit Statement",
    micCancel: "Cancel",
    factsTitle: "Extracted Incident Facts",
    clearChat: "Clear Session",
    viewAnalysisBtn: "View Legal Analysis & Rights →",
    disclaimer: "Legal Tantra provides preliminary legal awareness and factual preparation. AI is not a substitute for a qualified lawyer or court determination."
  },
  te: {
    brandTagline: "చట్టాన్ని తెలుసుకోండి. మీ హక్కులను గుర్తించండి. ఆత్మవిశ్వాసంతో మాట్లాడండి.",
    emergencyBtn: "🚨 అత్యవసర నంబర్: 112",
    navHome: "హోమ్",
    navChat: "సమస్య నమోదు",
    navAnalysis: "చట్టపరమైన విశ్లేషణ",
    navPolice: "పోలీస్ స్టేషన్ సన్నద్ధత",
    navLibrary: "చట్టాల నిఘంటువు",
    navDoc: "పత్రాల విశ్లేషణ",
    navAbout: "గోప్యత & వివరాలు",
    heroTitle: "పోలీస్ స్టేషన్‌కు వెళ్లే ముందు, మీ హక్కులను తెలుసుకోండి.",
    heroSubtitle: "ఏమి జరిగిందో మీ స్వంత మాటలలో వివరించండి. వర్తించే చట్టాలు, మీ హక్కులు తెలుసుకుని, పోలీసులకు వివరంగా చెప్పడానికి సిద్ధం కండి.",
    ctaStart: "సమస్య నమోదు ప్రారంభించండి",
    ctaRights: "హక్కులను తెలుసుకోండి",
    step1Title: "1. ఏమి జరిగిందో చెప్పండి",
    step1Desc: "సాధారణ తెలుగు లేదా ఇంగ్లీషులో టైప్ చేయండి లేదా మాట్లాడండి. చట్టపరమైన పదాలు అవసరం లేదు.",
    step2Title: "2. చట్టపరమైన అంశాలను గ్రహించండి",
    step2Desc: "భారతీయ న్యాయ సంహిత (BNS) చట్టాల ఆధారంగా మీ పరిస్థితిని మరియు మీ హక్కులను AI వివరిస్తుంది.",
    step3Title: "3. ఆత్మవిశ్వాసంతో సిద్ధమవ్వండి",
    step3Desc: "పోలీస్ స్టేషన్ కొరకు 7-దశల అధికారిక ప్రకటన మరియు ఆధారాల జాబితాను సిద్ధం చేసుకోండి.",
    chatHeading: "ఏమి జరిగిందో మాకు చెప్పండి",
    chatSub: "చట్టపరమైన పదాలు అవసరం లేదు. మీ సాధారణ మాటల్లో చెప్పండి. వర్తించే చట్టాలు, హక్కులు మరియు పోలీస్ స్టేషన్‌కు ఎలా సిద్ధమవ్వాలో మా AI సహాయం చేస్తుంది.",
    chatPlaceholder: "ఉదాహరణకు: నన్ను ఒకరు బెదిరించారు, లేదా ఆన్‌లైన్‌లో బ్యాంక్ మోసం జరిగింది...",
    sendBtn: "పంపు",
    micReviewTitle: "వాయిస్ రికగ్నిషన్ సమీక్ష",
    micReviewDesc: "AIకి పంపే ముందు మాటలను సరిచూసుకోండి లేదా సవరించండి.",
    micSubmit: "సమర్పించు",
    micCancel: "రద్దు",
    factsTitle: "నమోదైన వివరాలు",
    clearChat: "సెషన్ తొలగించు",
    viewAnalysisBtn: "విశ్లేషణ మరియు హక్కులను చూడండి →",
    disclaimer: "లీగల్ తంత్ర చట్టపరమైన అవగాహన మరియు సన్నద్ధత కొరకు మాత్రమే. ఇది న్యాయవాది లేదా కోర్టు నిర్ణయానికి ప్రత్యామ్నాయం కాదు."
  }
}

export default function App() {
  const [lang, setLang] = useState<'en' | 'te'>('en')
  const [activeTab, setActiveTab] = useState<'home' | 'chat' | 'analysis' | 'police' | 'library' | 'doc' | 'about'>('home')
  const [sidebarOpen, setSidebarOpen] = useState(false)
  
  // Chat state
  const [sessionId, setSessionId] = useState<string>(() => 'session-' + Date.now())
  const [messages, setMessages] = useState<Array<{ role: string; content: string }>>([
    {
      role: 'assistant',
      content: lang === 'te' 
        ? "నమస్కారం! నేను లీగల్ తంత్ర AI సహాయకుడిని. ఏమి జరిగిందో మీ సాధారణ మాటల్లో చెప్పండి (ఉదా: బెదిరింపు, శారీరక దాడి, ఆన్‌లైన్ మోసం)."
        : "Hello! I am your Legal Tantra assistant. Please describe what happened in your own words. You don't need to know any legal terms."
    }
  ])
  const [inputVal, setInputVal] = useState('')
  const [isAiLoading, setIsAiLoading] = useState(false)
  const [extractedFacts, setExtractedFacts] = useState<any>({
    incident_type: null,
    date_time: null,
    location: null,
    people_involved: null,
    threat_injury_or_loss: null,
    evidence_available: null
  })
  const [isClarified, setIsClarified] = useState(false)
  const [safetyAlert, setSafetyAlert] = useState<any | null>(null)
  const [emotionCue, setEmotionCue] = useState<string>('neutral')
  
  // Voice input
  const [isListening, setIsListening] = useState(false)
  const [transcriptCandidate, setTranscriptCandidate] = useState('')
  const [showTranscriptModal, setShowTranscriptModal] = useState(false)
  const [voicePlaybackEnabled, setVoicePlaybackEnabled] = useState(true)
  const recognitionRef = useRef<any>(null)
  
  // Analysis & Police statement
  const [analysisData, setAnalysisData] = useState<any | null>(null)
  const [policeStatement, setPoliceStatement] = useState<string>('')
  const [checklist, setChecklist] = useState<Array<{ item: string; checked: boolean }>>([])
  
  // Legal Library
  const [libraryProvisions, setLibraryProvisions] = useState<any[]>([])
  const [librarySearch, setLibrarySearch] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('All')

  // Document Analyzer
  const [docText, setDocText] = useState('')
  const [docAnalysis, setDocAnalysis] = useState<any | null>(null)
  const [isDocLoading, setIsDocLoading] = useState(false)

  // Emergency Modal
  const [showEmergencyModal, setShowEmergencyModal] = useState(false)
  const [copySuccess, setCopySuccess] = useState(false)

  const t = I18N[lang]

  // Count extracted facts for dynamic menu badge
  const factCount = Object.values(extractedFacts).filter(v => v !== null && v !== '').length

  // Update initial greeting when language toggles
  useEffect(() => {
    if (messages.length === 1 && messages[0].role === 'assistant') {
      setMessages([{
        role: 'assistant',
        content: lang === 'te' 
          ? "నమస్కారం! నేను లీగల్ తంత్ర AI సహాయకుడిని. ఏమి జరిగిందో మీ సాధారణ మాటల్లో చెప్పండి (ఉదా: బెదిరింపు, శారీరక దాడి, ఆన్‌లైన్ మోసం)."
          : "Hello! I am your Legal Tantra assistant. Please describe what happened in your own words. You don't need to know any legal terms."
      }])
    }
  }, [lang])

  // Fetch Legal Library provisions on mount
  useEffect(() => {
    fetch(`${API_BASE}/legal/library`)
      .then(res => res.json())
      .then(data => {
        if (data.provisions && data.provisions.length > 0) {
          setLibraryProvisions(data.provisions)
        }
      })
      .catch(() => {
        setLibraryProvisions([
          { act: "Bharatiya Nyaya Sanhita, 2023", section_number: "351", title: "Criminal Intimidation", category: "Threat", plain_explanation: "Intentional threats to cause injury to person, reputation or property to cause alarm.", source_url: "https://indiacode.nic.in" },
          { act: "Bharatiya Nyaya Sanhita, 2023", section_number: "115", title: "Voluntarily Causing Hurt", category: "Assault", plain_explanation: "Causing bodily pain or injury intentionally.", source_url: "https://indiacode.nic.in" },
          { act: "Bharatiya Nyaya Sanhita, 2023", section_number: "318", title: "Cheating", category: "Fraud", plain_explanation: "Dishonestly inducing delivery of money or property through deception.", source_url: "https://indiacode.nic.in" },
          { act: "Bharatiya Nagarik Suraksha Sanhita, 2023", section_number: "173", title: "FIR Registration & Zero FIR", category: "Rights_Procedure", plain_explanation: "Mandatory recording of cognizable offence and right to a free signed FIR copy.", source_url: "https://indiacode.nic.in" }
        ])
      })
  }, [])

  // Text to Speech
  const speakText = (text: string) => {
    if (!voicePlaybackEnabled || !('speechSynthesis' in window)) return
    window.speechSynthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(text.slice(0, 300))
    utterance.lang = lang === 'te' ? 'te-IN' : 'en-IN'
    utterance.rate = 0.95
    window.speechSynthesis.speak(utterance)
  }

  const stopSpeaking = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel()
    }
  }

  // Speech Recognition
  const toggleSpeechRecognition = () => {
    if (isListening) {
      if (recognitionRef.current) recognitionRef.current.stop()
      setIsListening(false)
      return
    }

    const SpeechRec = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    if (!SpeechRec) {
      alert("Speech recognition is not supported in this browser. Please use Chrome or Edge.")
      return
    }

    const rec = new SpeechRec()
    rec.continuous = false
    rec.interimResults = false
    rec.lang = lang === 'te' ? 'te-IN' : 'en-IN'

    rec.onstart = () => {
      setIsListening(true)
    }

    rec.onresult = (event: any) => {
      const text = event.results[0][0].transcript
      setTranscriptCandidate(text)
      setShowTranscriptModal(true)
      setIsListening(false)
    }

    rec.onerror = () => {
      setIsListening(false)
    }

    rec.onend = () => {
      setIsListening(false)
    }

    recognitionRef.current = rec
    rec.start()
  }

  // Send Chat Message
  const sendMessage = async (overrideText?: string) => {
    const textToSend = overrideText || inputVal
    if (!textToSend.trim() || isAiLoading) return

    const newMsgs = [...messages, { role: 'user', content: textToSend }]
    setMessages(newMsgs)
    setInputVal('')
    setIsAiLoading(true)

    try {
      const res = await fetch(`${API_BASE}/chat/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          message: textToSend,
          language: lang
        })
      })

      if (res.ok) {
        const data = await res.json()
        setMessages(prev => [...prev, { role: 'assistant', content: data.reply }])
        setExtractedFacts(data.extracted_facts)
        setIsClarified(data.is_clarified)
        setEmotionCue(data.emotion_cue || 'neutral')

        if (data.safety_alert) {
          setSafetyAlert(data.safety_details)
        }

        speakText(data.reply)
      } else {
        throw new Error("Server error")
      }
    } catch {
      // Offline fallback
      setTimeout(() => {
        let reply = ""
        const lower = textToSend.toLowerCase()
        let detected = "Threat"

        if (lower.includes("threat") || lower.includes("harm") || lower.includes("బెదిరించారు")) {
          detected = "Threat"
          reply = lang === 'te'
            ? "నేను వింటున్నాను. దయచేసి చెప్పండి, ఈ సంఘటన ఎప్పుడు మరియు ఎక్కడ జరిగింది? నిందితుడు ఏదైనా ఆయుధం చూపించాడా?"
            : "I hear you, and we will take this step-by-step. Approximately what date and location did this threat take place? Did the individual show any weapon?"
        } else if (lower.includes("fraud") || lower.includes("money") || lower.includes("upi") || lower.includes("మోసం")) {
          detected = "Fraud"
          reply = lang === 'te'
            ? "ఆర్థిక మోసం గురించి నమోదు చేసుకున్నాను. లావాదేవీ ఏ తేదీన జరిగింది? మీరు లావాదేవీ ఐడీ లేదా రసీదులను భద్రపరిచారా?"
            : "I have noted the financial fraud. On what date did this transaction occur? Do you have the UPI reference or transaction ID preserved?"
        } else {
          reply = lang === 'te'
            ? "వివరాలు అర్థమయ్యాయి. ఎవరైనా గాయపడ్డారా లేదా ఎంత నష్టం జరిగింది? ఆధారాలు ఏమైనా ఉన్నాయా?"
            : "Thank you for describing this. Was there any physical injury or specific loss? Do you have messages or witnesses?"
        }

        const updatedFacts = {
          ...extractedFacts,
          incident_type: detected,
          date_time: "Recent occurrence reported",
          location: "Location specified in statement"
        }

        setMessages(prev => [...prev, { role: 'assistant', content: reply }])
        setExtractedFacts(updatedFacts)
        setIsClarified(true)
        speakText(reply)
      }, 700)
    } finally {
      setIsAiLoading(false)
    }
  }

  // Clear Chat
  const clearChat = async () => {
    try {
      await fetch(`${API_BASE}/chat/reset`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
      })
    } catch {}

    const newId = 'session-' + Date.now()
    setSessionId(newId)
    setExtractedFacts({ incident_type: null, date_time: null, location: null, people_involved: null, threat_injury_or_loss: null, evidence_available: null })
    setIsClarified(false)
    setSafetyAlert(null)
    setAnalysisData(null)
    setPoliceStatement('')
    setMessages([{
      role: 'assistant',
      content: lang === 'te' 
        ? "నమస్కారం! నేను లీగల్ తంత్ర AI సహాయకుడిని. ఏమి జరిగిందో మీ సాధారణ మాటల్లో చెప్పండి."
        : "Hello! I am your Legal Tantra assistant. Please describe what happened in your own words."
    }])
  }

  // Load 1-Click Scenario
  const loadScenario = (scenarioKey: string) => {
    setActiveTab('chat')
    clearChat()

    let text = ""
    if (scenarioKey === 'threat') {
      text = "Someone threatened me outside my college yesterday and said he would physically hurt me if I complained."
    } else if (scenarioKey === 'fraud') {
      text = "I lost Rs 25,000 yesterday in an online bank scam where an unknown caller pretended to be from SBI."
    } else if (scenarioKey === 'assault') {
      text = "Two people attacked me physically near the metro station and I have bruises on my arm."
    } else if (scenarioKey === 'distressed') {
      text = "I'm terrified and crying. My landlord is constantly threatening to throw my family out and ruin our reputation."
    } else if (scenarioKey === 'telugu') {
      setLang('te')
      text = "నిన్న సాయంత్రం కాలేజీ బయట ఒక వ్యక్తి నన్ను చంపేస్తానని తీవ్రంగా బెదిరించాడు. నాకు చాలా భయంగా ఉంది."
    }

    setTimeout(() => {
      sendMessage(text)
    }, 200)
  }

  // Fetch Incident Analysis
  const loadAnalysis = async () => {
    setActiveTab('analysis')
    try {
      const res = await fetch(`${API_BASE}/incident/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          facts: extractedFacts,
          language: lang
        })
      })
      if (res.ok) {
        const data = await res.json()
        setAnalysisData(data)
      } else {
        throw new Error()
      }
    } catch {
      setAnalysisData({
        incident_category: extractedFacts.incident_type || "Threat / Assault",
        facts_summary: extractedFacts,
        provisions: [
          { act: "Bharatiya Nyaya Sanhita, 2023", section_number: "351", title: "Criminal Intimidation", plain_explanation: "Punishes intentional threats to cause injury to person, reputation or property.", source_url: "https://indiacode.nic.in" },
          { act: "Bharatiya Nagarik Suraksha Sanhita, 2023", section_number: "173", title: "Information in Cognizable Cases (FIR Registration & Copy)", plain_explanation: "Mandatory registration of FIR with immediate free signed copy provided to the complainant.", source_url: "https://indiacode.nic.in" }
        ],
        rights_guide: [
          { right_title: "Right to Free Copy of FIR (Sec 173 BNSS)", explanation: "The police station must provide a signed physical copy of the FIR immediately without charging any fee." },
          { right_title: "Zero FIR", explanation: "If an incident occurred outside their geographical limits, police must still record a 'Zero FIR' and transfer it." }
        ],
        evidence_checklist: [
          { item: "Exact timeline of date, time, and locations", essential: true },
          { item: "Screenshots of threatening messages or phone call logs", essential: true },
          { item: "Medical prescription or injury marks documentation (if physical assault)", essential: true }
        ],
        is_simulated_ai: true
      })
    }
  }

  // Load Police Statement
  const loadPoliceStatement = async () => {
    setActiveTab('police')
    try {
      const res = await fetch(`${API_BASE}/incident/summary`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          facts: extractedFacts,
          language: lang
        })
      })
      if (res.ok) {
        const data = await res.json()
        setPoliceStatement(data.statement_text)
        setChecklist(data.evidence_checklist.map((c: any) => ({ item: c.item, checked: true })))
      } else {
        throw new Error()
      }
    } catch {
      const mockStatement = `================================================================================
                    FACTUAL INCIDENT STATEMENT FOR POLICE STATION
================================================================================
(Prepared with Legal Tantra - Preliminary citizen factual aid)

1. PURPOSE OF APPROACHING THE POLICE:
I am approaching the police station to report an incident of ${extractedFacts.incident_type || "Threat / Intimidation"} and request prompt inquiry and registration of First Information Report (FIR) under relevant sections of the Bharatiya Nyaya Sanhita (BNS), 2023.

2. DATE, TIME AND LOCATION:
- Approximate Date & Time: ${extractedFacts.date_time || "Recent occurrence reported"}
- Location of Incident: ${extractedFacts.location || "Location as specified in citizen statement"}

3. PERSONS INVOLVED:
${extractedFacts.people_involved || "Individual named in report"}

4. CHRONOLOGICAL SUMMARY OF EVENTS:
On the date and time mentioned above, the complainant reports the following events involving ${extractedFacts.incident_type || "the reported situation"}:
- Narrative as reported by complainant: ${extractedFacts.alleged_actions || "Details stated during consultation"}

5. REPORTED INJURIES, HARM OR FINANCIAL LOSS:
${extractedFacts.threat_injury_or_loss || extractedFacts.injuries_or_loss || "None reported or not provided"}

6. EVIDENCE AND WITNESSES (AS CITED):
- Available Records / Digital Evidence: ${extractedFacts.evidence_available || extractedFacts.evidence_mentioned || "Not specified at this time"}

7. ASSISTANCE SOUGHT:
The complainant respectfully requests the competent authority to:
(a) Receive and formally acknowledge receipt of this factual summary.
(b) Review the stated facts in accordance with applicable legal procedure.
(c) Issue an official acknowledgment or reference code for tracking.

--------------------------------------------------------------------------------
Signature of Complainant / Citizen: ____________________
Full Name: ____________________
Date: ____________________
`
      setPoliceStatement(mockStatement)
      setChecklist([
        { item: "Physical printed copy of this statement", checked: true },
        { item: "Government ID Proof (Aadhaar / Voter ID)", checked: true },
        { item: "Phone with preserved chats / call recordings", checked: true },
        { item: "Medical prescription or injury report (if applicable)", checked: false }
      ])
    }
  }

  // Document Analyzer
  const handleDocAnalyze = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!docText.trim()) return
    setIsDocLoading(true)

    try {
      const formData = new FormData()
      formData.append("raw_text", docText)

      const res = await fetch(`${API_BASE}/document/analyze`, {
        method: 'POST',
        body: formData
      })
      if (res.ok) {
        const data = await res.json()
        setDocAnalysis(data)
      } else {
        throw new Error()
      }
    } catch {
      setDocAnalysis({
        filename: "Pasted Legal Notice Excerpt",
        summary: "This document contains formal notice references with instructions to appear or reply within a stipulated period.",
        dates_found: ["15-10-2026", "22-10-2026"],
        case_references: ["Notice No. 442/2026", "FIR No. 128/2026"],
        explained_terms: [
          { term: "COGNIZABLE", plain_meaning: "A serious offence where police can investigate without a Magistrate's warrant." },
          { term: "FIR", plain_meaning: "First Information Report—the formal document registering a crime with the police." }
        ],
        recommended_questions: [
          "What is the statutory response deadline mentioned in this document?",
          "Does this require personal appearance or written reply through an advocate?"
        ]
      })
    } finally {
      setIsDocLoading(false)
    }
  }

  // Copy to Clipboard
  const copyStatementToClipboard = () => {
    navigator.clipboard.writeText(policeStatement)
    setCopySuccess(true)
    setTimeout(() => setCopySuccess(false), 3000)
  }

  return (
    <div className="lt-app-layout">
      {/* Mobile Drawer Backdrop */}
      {sidebarOpen && (
        <div className="lt-sidebar-backdrop" onClick={() => setSidebarOpen(false)} />
      )}

      {/* ================= SIDE MENU BAR (SIDEBAR) ================= */}
      <aside className={`lt-sidebar ${sidebarOpen ? 'open' : ''} no-print`}>
        {/* Brand / Logo */}
        <div className="lt-sidebar-header">
          <div className="lt-sidebar-brand" onClick={() => { setActiveTab('home'); setSidebarOpen(false); }}>
            <div className="lt-brand-icon">
              <Scale size={24} color="var(--lt-teal)" />
            </div>
            <div className="lt-sidebar-brand-text">
              <span className="lt-brand-title">LEGAL TANTRA</span>
              <span className="lt-sidebar-sub">LEGAL AID SYSTEM</span>
            </div>
          </div>
          <button 
            className="lt-sidebar-close" 
            onClick={() => setSidebarOpen(false)}
            aria-label="Close Sidebar"
          >
            <X size={18} />
          </button>
        </div>

        {/* Sidebar Nav Items */}
        <div className="lt-sidebar-content">
          <div className="lt-sidebar-group">
            <span className="lt-sidebar-group-title">MAIN WORKFLOW</span>

            <div 
              className={`lt-sidebar-item ${activeTab === 'home' ? 'active' : ''}`}
              onClick={() => { setActiveTab('home'); setSidebarOpen(false); }}
            >
              <Home size={18} />
              <span>{t.navHome}</span>
            </div>

            <div 
              className={`lt-sidebar-item ${activeTab === 'chat' ? 'active' : ''}`}
              onClick={() => { setActiveTab('chat'); setSidebarOpen(false); }}
            >
              <MessageSquare size={18} />
              <span>{t.navChat}</span>
              {factCount > 0 && <span className="lt-sidebar-badge">{factCount} Facts</span>}
            </div>

            <div 
              className={`lt-sidebar-item ${activeTab === 'analysis' ? 'active' : ''}`}
              onClick={() => { loadAnalysis(); setSidebarOpen(false); }}
            >
              <Shield size={18} />
              <span>{t.navAnalysis}</span>
              {analysisData && <span className="lt-sidebar-badge">✓ Ready</span>}
            </div>

            <div 
              className={`lt-sidebar-item ${activeTab === 'police' ? 'active' : ''}`}
              onClick={() => { loadPoliceStatement(); setSidebarOpen(false); }}
            >
              <FileText size={18} />
              <span>{t.navPolice}</span>
              {policeStatement && <span className="lt-sidebar-badge">Drafted</span>}
            </div>
          </div>

          <div className="lt-sidebar-group">
            <span className="lt-sidebar-group-title">RESOURCES & TOOLS</span>

            <div 
              className={`lt-sidebar-item ${activeTab === 'library' ? 'active' : ''}`}
              onClick={() => { setActiveTab('library'); setSidebarOpen(false); }}
            >
              <BookOpen size={18} />
              <span>{t.navLibrary}</span>
            </div>

            <div 
              className={`lt-sidebar-item ${activeTab === 'doc' ? 'active' : ''}`}
              onClick={() => { setActiveTab('doc'); setSidebarOpen(false); }}
            >
              <Search size={18} />
              <span>{t.navDoc}</span>
            </div>

            <div 
              className={`lt-sidebar-item ${activeTab === 'about' ? 'active' : ''}`}
              onClick={() => { setActiveTab('about'); setSidebarOpen(false); }}
            >
              <HelpCircle size={18} />
              <span>{t.navAbout}</span>
            </div>
          </div>

          {/* Active Incident Summary Card in Sidebar */}
          {factCount > 0 && (
            <div className="lt-sidebar-card">
              <div className="lt-sidebar-card-header">
                <span className="lt-sidebar-card-label">ACTIVE INCIDENT</span>
                <span className="lt-sidebar-card-pill">{factCount}/5 Facts</span>
              </div>
              <div className="lt-sidebar-card-title">
                {extractedFacts.incident_type || "Incident in progress"}
              </div>
              <div className="lt-sidebar-card-meta">
                {extractedFacts.date_time && <div>📅 {extractedFacts.date_time}</div>}
                {extractedFacts.location && <div>📍 {extractedFacts.location}</div>}
              </div>
            </div>
          )}
        </div>

        {/* Sidebar Footer */}
        <div className="lt-sidebar-footer">
          {/* Language Switcher */}
          <div className="lt-sidebar-lang">
            <Globe size={14} color="var(--lt-teal)" />
            <span style={{ fontSize: '0.78rem' }}>Language:</span>
            <select 
              value={lang} 
              onChange={e => setLang(e.target.value as 'en' | 'te')}
              className="lt-sidebar-lang-select"
            >
              <option value="en" style={{ background: '#050B18', color: '#fff' }}>English</option>
              <option value="te" style={{ background: '#050B18', color: '#fff' }}>తెలుగు</option>
            </select>
          </div>

          {/* Emergency SOS Button */}
          <button 
            className="btn btn-danger lt-sidebar-emergency"
            onClick={() => setShowEmergencyModal(true)}
          >
            <PhoneCall size={14} />
            <span>{t.emergencyBtn}</span>
          </button>

          {/* Statutory Verification Pill */}
          <div className="lt-sidebar-verify-pill">
            <span className="lt-status-dot"></span>
            <span>BNS, BNSS, BSA 2023 Verified</span>
          </div>
        </div>
      </aside>

      {/* ================= MAIN CONTENT WRAPPER ================= */}
      <div className="lt-main-wrapper">
        {/* Clean Topbar with breadcrumb context and quick actions */}
        <header className="lt-topbar no-print">
          <div className="lt-topbar-inner">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
              <button 
                className="lt-mobile-toggle" 
                onClick={() => setSidebarOpen(true)}
                aria-label="Open Navigation Menu"
              >
                <Menu size={20} />
              </button>

              <div className="lt-topbar-title-wrap">
                <span className="lt-topbar-crumb">LEGAL TANTRA</span>
                <ChevronRight size={14} color="var(--lt-border-light)" />
                <span className="lt-topbar-active">
                  {activeTab === 'home' && t.navHome}
                  {activeTab === 'chat' && t.navChat}
                  {activeTab === 'analysis' && t.navAnalysis}
                  {activeTab === 'police' && t.navPolice}
                  {activeTab === 'library' && t.navLibrary}
                  {activeTab === 'doc' && t.navDoc}
                  {activeTab === 'about' && t.navAbout}
                </span>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <div className="lt-topbar-badge">
                <span className="lt-status-dot"></span>
                <span>BNS 2023 Live</span>
              </div>

              <div className="lt-topbar-lang">
                <Globe size={14} color="var(--lt-teal)" />
                <select 
                  value={lang} 
                  onChange={e => setLang(e.target.value as 'en' | 'te')}
                  className="lt-topbar-lang-select"
                >
                  <option value="en" style={{ background: '#050B18', color: '#fff' }}>EN</option>
                  <option value="te" style={{ background: '#050B18', color: '#fff' }}>తెలుగు</option>
                </select>
              </div>

              <button 
                className="btn btn-danger" 
                style={{ padding: '0.4rem 0.85rem', fontSize: '0.8rem', borderRadius: '18px' }} 
                onClick={() => setShowEmergencyModal(true)}
              >
                <PhoneCall size={13} /> {t.emergencyBtn}
              </button>
            </div>
          </div>
        </header>

      {/* ================= DYNAMIC WORKFLOW STEP PROGRESS BAR ================= */}
      <div className="lt-step-bar no-print">
        <div className="lt-step-bar-inner">
          <div className="lt-steps-indicator">
            <span 
              className={`lt-step-pill ${activeTab === 'chat' ? 'current' : (factCount > 0 ? 'completed' : '')}`}
              onClick={() => setActiveTab('chat')}
            >
              {factCount > 0 ? <Check size={12} /> : <span>1</span>}
              <span>1. Describe Incident</span>
            </span>

            <ChevronRight size={14} color="var(--lt-border-light)" />

            <span 
              className={`lt-step-pill ${activeTab === 'chat' && isClarified ? 'completed' : (activeTab === 'chat' ? 'current' : '')}`}
              onClick={() => setActiveTab('chat')}
            >
              {isClarified ? <Check size={12} /> : <span>2</span>}
              <span>2. AI Clarification & Facts ({factCount}/5)</span>
            </span>

            <ChevronRight size={14} color="var(--lt-border-light)" />

            <span 
              className={`lt-step-pill ${activeTab === 'analysis' ? 'current' : (analysisData ? 'completed' : '')}`}
              onClick={loadAnalysis}
            >
              {analysisData ? <Check size={12} /> : <span>3</span>}
              <span>3. BNS Statutory Analysis</span>
            </span>

            <ChevronRight size={14} color="var(--lt-border-light)" />

            <span 
              className={`lt-step-pill ${activeTab === 'police' ? 'current' : (policeStatement ? 'completed' : '')}`}
              onClick={loadPoliceStatement}
            >
              {policeStatement ? <Check size={12} /> : <span>4</span>}
              <span>4. Police Station Statement</span>
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', fontSize: '0.78rem', color: 'var(--lt-text-muted)' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--lt-success)' }}></span>
            <span>Grounded in India Code (BNS 2023)</span>
          </div>
        </div>
      </div>

      {/* ================= MAIN CONTAINER ================= */}
      <main className="lt-container">
        {/* Active Emergency Alert if danger detected */}
        {safetyAlert && (
          <div className="emergency-banner">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <AlertOctagon size={24} color="var(--lt-danger)" />
              <div>
                <strong style={{ display: 'block', fontSize: '0.95rem' }}>Immediate Safety Advisory:</strong>
                <span style={{ fontSize: '0.85rem' }}>{safetyAlert.safety_message}</span>
              </div>
            </div>
            <button className="btn btn-danger" onClick={() => setShowEmergencyModal(true)}>
              View Emergency Numbers (112)
            </button>
          </div>
        )}

        {/* ----------------- PAGE 1: HOME ----------------- */}
        {activeTab === 'home' && (
          <div>
            <div className="hero-box">
              <span className="badge badge-teal" style={{ marginBottom: '1.25rem' }}>
                <Sparkles size={12} style={{ display: 'inline', marginRight: '5px' }} />
                Grounded in Bharatiya Nyaya Sanhita (BNS), 2023
              </span>
              <h1 className="hero-title">{t.heroTitle}</h1>
              <p className="hero-subtitle">{t.heroSubtitle}</p>
              
              <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', flexWrap: 'wrap' }}>
                <button className="btn btn-teal" style={{ padding: '0.85rem 1.85rem', fontSize: '0.95rem' }} onClick={() => setActiveTab('chat')}>
                  <MessageSquare size={18} /> {t.ctaStart}
                </button>
                <button className="btn btn-outline" style={{ padding: '0.85rem 1.85rem', fontSize: '0.95rem' }} onClick={() => setActiveTab('library')}>
                  <BookOpen size={18} /> {t.ctaRights}
                </button>
              </div>
            </div>

            {/* 3 Step Workflow */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem', marginTop: '1.5rem' }}>
              <div className="card">
                <div style={{ width: '42px', height: '42px', borderRadius: '10px', backgroundColor: 'var(--lt-teal-subtle)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.1rem' }}>
                  <Mic size={22} color="var(--lt-teal)" />
                </div>
                <h3 style={{ fontSize: '1.18rem', marginBottom: '0.5rem' }}>{t.step1Title}</h3>
                <p style={{ color: 'var(--lt-text-muted)', fontSize: '0.88rem' }}>{t.step1Desc}</p>
              </div>

              <div className="card">
                <div style={{ width: '42px', height: '42px', borderRadius: '10px', backgroundColor: 'var(--lt-teal-subtle)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.1rem' }}>
                  <Scale size={22} color="var(--lt-teal)" />
                </div>
                <h3 style={{ fontSize: '1.18rem', marginBottom: '0.5rem' }}>{t.step2Title}</h3>
                <p style={{ color: 'var(--lt-text-muted)', fontSize: '0.88rem' }}>{t.step2Desc}</p>
              </div>

              <div className="card">
                <div style={{ width: '42px', height: '42px', borderRadius: '10px', backgroundColor: 'var(--lt-teal-subtle)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.1rem' }}>
                  <FileText size={22} color="var(--lt-teal)" />
                </div>
                <h3 style={{ fontSize: '1.18rem', marginBottom: '0.5rem' }}>{t.step3Title}</h3>
                <p style={{ color: 'var(--lt-text-muted)', fontSize: '0.88rem' }}>{t.step3Desc}</p>
              </div>
            </div>

            {/* Test Scenarios Demonstration Section */}
            <div style={{ marginTop: '3.5rem', background: 'var(--lt-bg-surface)', border: '1px solid var(--lt-border)', borderRadius: 'var(--radius-lg)', padding: '2rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
                <div>
                  <h3 style={{ fontSize: '1.25rem', marginBottom: '0.25rem' }}>🎯 1-Click Interactive Test Scenarios</h3>
                  <p style={{ color: 'var(--lt-text-muted)', fontSize: '0.85rem' }}>Select a fictional incident to test the conversational workflow, follow-up questions, and legal retrieval instantly:</p>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(230px, 1fr))', gap: '1rem' }}>
                <button className="btn btn-outline" style={{ textAlign: 'left', display: 'flex', flexDirection: 'column', alignItems: 'flex-start', padding: '1rem', width: '100%' }} onClick={() => loadScenario('threat')}>
                  <strong style={{ color: 'var(--lt-teal)' }}>Scenario A: Verbal Threat</strong>
                  <span style={{ fontSize: '0.78rem', color: 'var(--lt-text-muted)' }}>Threatened outside college with physical harm</span>
                </button>

                <button className="btn btn-outline" style={{ textAlign: 'left', display: 'flex', flexDirection: 'column', alignItems: 'flex-start', padding: '1rem', width: '100%' }} onClick={() => loadScenario('fraud')}>
                  <strong style={{ color: 'var(--lt-teal)' }}>Scenario B: Online Bank Fraud</strong>
                  <span style={{ fontSize: '0.78rem', color: 'var(--lt-text-muted)' }}>Lost money in fake banking phone scam</span>
                </button>

                <button className="btn btn-outline" style={{ textAlign: 'left', display: 'flex', flexDirection: 'column', alignItems: 'flex-start', padding: '1rem', width: '100%' }} onClick={() => loadScenario('assault')}>
                  <strong style={{ color: 'var(--lt-teal)' }}>Scenario C: Physical Assault</strong>
                  <span style={{ fontSize: '0.78rem', color: 'var(--lt-text-muted)' }}>Physical attack with injury & emergency prompt</span>
                </button>

                <button className="btn btn-outline" style={{ textAlign: 'left', display: 'flex', flexDirection: 'column', alignItems: 'flex-start', padding: '1rem', width: '100%' }} onClick={() => loadScenario('distressed')}>
                  <strong style={{ color: 'var(--lt-teal)' }}>Scenario D: Distressed / Fear</strong>
                  <span style={{ fontSize: '0.78rem', color: 'var(--lt-text-muted)' }}>Empathetic & calming tone modulation</span>
                </button>

                <button className="btn btn-outline" style={{ textAlign: 'left', display: 'flex', flexDirection: 'column', alignItems: 'flex-start', padding: '1rem', width: '100%' }} onClick={() => loadScenario('telugu')}>
                  <strong style={{ color: 'var(--lt-teal)' }}>Scenario E: తెలుగు (Telugu Input)</strong>
                  <span style={{ fontSize: '0.78rem', color: 'var(--lt-text-muted)' }}>తెలుగులో సంభాషణ మరియు చట్టాల విశ్లేషణ</span>
                </button>
              </div>
            </div>
          </div>
        )}

        {/* ----------------- PAGE 2: AI INCIDENT ASSISTANT ----------------- */}
        {activeTab === 'chat' && (
          <div>
            <div style={{ marginBottom: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
                <div>
                  <h1 style={{ fontSize: '1.9rem', marginBottom: '0.35rem' }}>{t.chatHeading}</h1>
                  <p style={{ color: 'var(--lt-text-muted)', fontSize: '0.92rem', maxWidth: '780px' }}>{t.chatSub}</p>
                </div>
                <div style={{ display: 'flex', gap: '0.65rem', alignItems: 'center' }}>
                  <button className="btn btn-outline" onClick={clearChat} title="Reset session">
                    <Trash2 size={15} /> {t.clearChat}
                  </button>
                  <button 
                    className="btn btn-outline" 
                    onClick={() => {
                      setVoicePlaybackEnabled(!voicePlaybackEnabled)
                      if (voicePlaybackEnabled) stopSpeaking()
                    }}
                    title={voicePlaybackEnabled ? "Mute Voice Readout" : "Enable Voice Readout"}
                  >
                    {voicePlaybackEnabled ? <Volume2 size={16} color="var(--lt-teal)" /> : <VolumeX size={16} />}
                  </button>
                </div>
              </div>

              {/* Emotion Indicator */}
              {emotionCue !== 'neutral' && (
                <div style={{ marginTop: '0.75rem', display: 'inline-flex', alignItems: 'center', gap: '0.5rem', background: 'var(--lt-teal-subtle)', padding: '0.3rem 0.85rem', borderRadius: '20px', border: '1px solid var(--lt-teal)' }}>
                  <Sparkles size={14} color="var(--lt-teal)" />
                  <span style={{ fontSize: '0.78rem', color: 'var(--lt-teal)' }}>
                    Emotion Cue: <strong>{emotionCue.toUpperCase()}</strong> (Empathetic & supportive tone active)
                  </span>
                </div>
              )}
            </div>

            {/* Chat Layout with Fluid Resolution Flex */}
            <div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap', width: '100%' }}>
              {/* Left Column: Chat Window */}
              <div style={{ flex: '1 1 540px', minWidth: 0, width: '100%' }}>
                <div className="chat-window">
                  <div className="chat-messages">
                    {messages.map((m, idx) => (
                      <div key={idx} className={`message-bubble ${m.role === 'user' ? 'msg-user' : 'msg-ai'}`}>
                        {m.content}
                      </div>
                    ))}
                    {isAiLoading && (
                      <div className="message-bubble msg-ai" style={{ fontStyle: 'italic', color: 'var(--lt-text-muted)' }}>
                        AI is analyzing facts and retrieving verified Indian statutes...
                      </div>
                    )}
                  </div>

                  {/* Input bar with Text + Mic */}
                  <div className="chat-input-bar">
                    <input
                      type="text"
                      className="chat-input"
                      placeholder={t.chatPlaceholder}
                      value={inputVal}
                      onChange={e => setInputVal(e.target.value)}
                      onKeyDown={e => e.key === 'Enter' && sendMessage()}
                      disabled={isAiLoading}
                    />

                    {/* Microphone button */}
                    <button 
                      className={`btn btn-outline ${isListening ? 'mic-btn-active' : ''}`}
                      onClick={toggleSpeechRecognition}
                      title={isListening ? "Listening... Click to stop" : "Speak your incident"}
                      style={{ borderRadius: '50%', width: '42px', height: '42px', padding: 0, flexShrink: 0 }}
                    >
                      <Mic size={18} />
                    </button>

                    <button 
                      className="btn btn-teal" 
                      onClick={() => sendMessage()}
                      disabled={isAiLoading || !inputVal.trim()}
                      style={{ flexShrink: 0 }}
                    >
                      <Send size={15} /> {t.sendBtn}
                    </button>
                  </div>
                </div>

                <div style={{ marginTop: '0.75rem', fontSize: '0.78rem', color: 'var(--lt-text-muted)' }}>
                  💡 <em>{t.disclaimer}</em>
                </div>
              </div>

              {/* Right Column: Live Extracted Facts Drawer */}
              <div style={{ flex: '1 1 320px', minWidth: 0, width: '100%' }}>
                <div className="card" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.15rem' }}>
                    <h3 style={{ fontSize: '1.15rem' }}>{t.factsTitle}</h3>
                    <span className="badge badge-teal">
                      {extractedFacts.incident_type || "Awaiting Info"}
                    </span>
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', flex: 1 }}>
                    <div style={{ background: 'var(--lt-bg-deep)', padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--lt-border)' }}>
                      <span style={{ fontSize: '0.72rem', color: 'var(--lt-text-muted)', display: 'block' }}>Incident Type:</span>
                      <strong style={{ fontSize: '0.88rem' }}>{extractedFacts.incident_type || "Not yet identified"}</strong>
                    </div>

                    <div style={{ background: 'var(--lt-bg-deep)', padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--lt-border)' }}>
                      <span style={{ fontSize: '0.72rem', color: 'var(--lt-text-muted)', display: 'block' }}>Date & Approximate Time:</span>
                      <strong style={{ fontSize: '0.88rem' }}>{extractedFacts.date_time || "Pending clarification"}</strong>
                    </div>

                    <div style={{ background: 'var(--lt-bg-deep)', padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--lt-border)' }}>
                      <span style={{ fontSize: '0.72rem', color: 'var(--lt-text-muted)', display: 'block' }}>Location:</span>
                      <strong style={{ fontSize: '0.88rem' }}>{extractedFacts.location || "Pending clarification"}</strong>
                    </div>

                    <div style={{ background: 'var(--lt-bg-deep)', padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--lt-border)' }}>
                      <span style={{ fontSize: '0.72rem', color: 'var(--lt-text-muted)', display: 'block' }}>Persons / Suspects:</span>
                      <strong style={{ fontSize: '0.88rem' }}>{extractedFacts.people_involved || "Not specified"}</strong>
                    </div>

                    <div style={{ background: 'var(--lt-bg-deep)', padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--lt-border)' }}>
                      <span style={{ fontSize: '0.72rem', color: 'var(--lt-text-muted)', display: 'block' }}>Threats / Injuries / Loss:</span>
                      <strong style={{ fontSize: '0.88rem' }}>{extractedFacts.threat_injury_or_loss || "None recorded"}</strong>
                    </div>
                  </div>

                  {/* Ready for Analysis CTA */}
                  <div style={{ marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid var(--lt-border)' }}>
                    <button 
                      className="btn btn-teal" 
                      style={{ width: '100%' }} 
                      onClick={loadAnalysis}
                    >
                      {t.viewAnalysisBtn}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ----------------- PAGE 3: INCIDENT ANALYSIS ----------------- */}
        {activeTab === 'analysis' && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
              <div>
                <h1 style={{ fontSize: '1.9rem', marginBottom: '0.25rem' }}>Your Incident Analysis</h1>
                <p style={{ color: 'var(--lt-text-muted)', fontSize: '0.92rem' }}>
                  Preliminary factual assessment and statutory grounding under verified Indian criminal law.
                </p>
              </div>

              <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                <button className="btn btn-outline" onClick={() => setActiveTab('chat')}>
                  ← Back to Assistant
                </button>
                <button className="btn btn-teal" onClick={loadPoliceStatement}>
                  Prepare Police Statement →
                </button>
              </div>
            </div>

            {/* A. Preliminary Incident Summary */}
            <div className="card" style={{ marginBottom: '1.5rem', borderLeft: '4px solid var(--lt-teal)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                <h3 style={{ fontSize: '1.15rem' }}>A. Incident Summary (Preliminary Account)</h3>
                <span className="badge badge-warning">Citizen's Preliminary Report</span>
              </div>
              <p style={{ fontSize: '0.9rem', color: '#E2E8F0' }}>
                This summary reflects the statements provided by the user during the interactive AI interview. It has not been independently verified by police inquiry or judicial process.
              </p>
              <div style={{ background: 'var(--lt-bg-deep)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--lt-border)', marginTop: '0.75rem' }}>
                <p style={{ margin: 0, fontSize: '0.88rem', lineHeight: '1.7' }}>
                  <strong>Reported Category:</strong> {analysisData?.incident_category || extractedFacts.incident_type || "Threat / Intimidation"}<br />
                  <strong>Date & Time:</strong> {extractedFacts.date_time || "Recent"}<br />
                  <strong>Location:</strong> {extractedFacts.location || "Location as specified"}<br />
                  <strong>Reported Impact:</strong> {extractedFacts.threat_injury_or_loss || "Specific words or actions creating apprehension"}
                </p>
              </div>
            </div>

            {/* B. Potentially Relevant Laws */}
            <div className="card" style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ fontSize: '1.15rem', marginBottom: '0.5rem' }}>B. Potentially Relevant Legal Provisions (BNS 2023)</h3>
              <p style={{ color: 'var(--lt-text-muted)', fontSize: '0.85rem', marginBottom: '1.25rem' }}>
                Retrieved from the authoritative <strong>India Code</strong> database. These provisions are preliminary pointers based on the reported facts.
              </p>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {(analysisData?.provisions || []).map((p: any, idx: number) => (
                  <div key={idx} style={{ background: 'var(--lt-bg-deep)', border: '1px solid var(--lt-border)', borderRadius: '8px', padding: '1.25rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem', flexWrap: 'wrap', gap: '0.5rem' }}>
                      <div>
                        <strong style={{ fontSize: '1.02rem', color: 'var(--lt-teal)' }}>
                          {p.act} — Section {p.section_number}
                        </strong>
                        <div style={{ fontSize: '0.9rem', fontWeight: 600, color: '#FFFFFF' }}>{p.title}</div>
                      </div>
                      <a href={p.source_url} target="_blank" rel="noreferrer" className="btn btn-outline" style={{ padding: '0.3rem 0.65rem', fontSize: '0.72rem' }}>
                        View on India Code <ExternalLink size={12} />
                      </a>
                    </div>

                    <p style={{ fontSize: '0.88rem', color: '#E2E8F0', marginBottom: '0.5rem' }}>
                      <strong>Simple Explanation:</strong> {p.plain_explanation}
                    </p>

                    {p.conditions_exceptions && (
                      <p style={{ fontSize: '0.78rem', color: 'var(--lt-text-muted)', margin: 0, fontStyle: 'italic' }}>
                        ⚠️ Conditions & Limitations: {p.conditions_exceptions}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* C. Know Your Rights */}
            <div className="card" style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ fontSize: '1.15rem', marginBottom: '0.5rem' }}>C. Know Your Rights as a Complainant (BNSS 2023)</h3>
              <p style={{ color: 'var(--lt-text-muted)', fontSize: '0.85rem', marginBottom: '1.25rem' }}>
                Essential procedural rights protecting ordinary citizens when approaching the police station.
              </p>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
                {(analysisData?.rights_guide || []).map((r: any, idx: number) => (
                  <div key={idx} style={{ background: 'var(--lt-bg-deep)', border: '1px solid var(--lt-border)', borderRadius: '8px', padding: '1rem' }}>
                    <strong style={{ color: 'var(--lt-teal)', display: 'block', fontSize: '0.92rem', marginBottom: '0.35rem' }}>
                      {r.right_title}
                    </strong>
                    <p style={{ fontSize: '0.85rem', color: '#CBD5E1', margin: 0 }}>
                      {r.explanation}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* D. Evidence to Prepare */}
            <div className="card">
              <h3 style={{ fontSize: '1.15rem', marginBottom: '0.5rem' }}>D. Information & Evidence to Prepare</h3>
              <p style={{ color: 'var(--lt-text-muted)', fontSize: '0.85rem', marginBottom: '1rem' }}>
                Organizing these items beforehand will significantly strengthen the clarity of your police complaint:
              </p>

              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
                {(analysisData?.evidence_checklist || []).map((ev: any, idx: number) => (
                  <li key={idx} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.88rem' }}>
                    <CheckCircle2 size={16} color="var(--lt-teal)" style={{ flexShrink: 0 }} />
                    <span>{ev.item} {ev.essential && <span className="badge badge-warning" style={{ fontSize: '0.65rem', marginLeft: '6px' }}>Recommended</span>}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* ----------------- PAGE 4: POLICE PREPARATION ----------------- */}
        {activeTab === 'police' && (
          <div>
            <div className="no-print" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
              <div>
                <h1 style={{ fontSize: '1.9rem', marginBottom: '0.25rem' }}>Prepare Before Visiting the Police Station</h1>
                <p style={{ color: 'var(--lt-text-muted)', fontSize: '0.92rem' }}>
                  Review and edit your 7-step factual statement. Print or save it to present clearly to the Station House Officer (SHO).
                </p>
              </div>

              <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                <button className="btn btn-outline" onClick={() => setActiveTab('analysis')}>
                  ← Back to Analysis
                </button>
                <button className="btn btn-outline" onClick={copyStatementToClipboard}>
                  <Copy size={15} /> {copySuccess ? "Copied!" : "Copy Statement"}
                </button>
                <button className="btn btn-teal" onClick={() => window.print()}>
                  <Printer size={15} /> Print / Save PDF
                </button>
              </div>
            </div>

            {/* 7-Step Structure Explanation */}
            <div className="card no-print" style={{ marginBottom: '1.5rem', background: 'var(--lt-teal-subtle)', border: '1px solid var(--lt-teal)' }}>
              <h3 style={{ fontSize: '1rem', color: 'var(--lt-teal)', marginBottom: '0.4rem' }}>
                📋 The 7-Step Structure of a Clear Police Complaint
              </h3>
              <p style={{ fontSize: '0.83rem', color: '#CBD5E1', margin: 0 }}>
                1. Purpose of visit • 2. Date, time, location • 3. Details of people involved • 4. Chronological sequence of events • 5. Specific threats, injuries, or losses • 6. Available witnesses and digital evidence • 7. Specific assistance requested.
              </p>
            </div>

            {/* Printable Statement Editor */}
            <div className="card printable-area" style={{ marginBottom: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                <h3 style={{ fontSize: '1.15rem' }}>Factual Statement (Editable)</h3>
                <span className="badge badge-teal no-print">Review & Edit</span>
              </div>
              <p style={{ fontSize: '0.82rem', color: 'var(--lt-text-muted)', marginBottom: '0.75rem' }} className="no-print">
                You can directly edit any paragraph or add specific names, dates, or details below before printing:
              </p>

              <textarea
                style={{
                  width: '100%',
                  height: '420px',
                  background: 'var(--lt-bg-deep)',
                  color: '#F8FAFC',
                  fontFamily: 'monospace',
                  fontSize: '0.86rem',
                  lineHeight: '1.6',
                  padding: '1.25rem',
                  borderRadius: '8px',
                  border: '1px solid var(--lt-border)',
                  outline: 'none',
                  whiteSpace: 'pre-wrap'
                }}
                value={policeStatement}
                onChange={e => setPoliceStatement(e.target.value)}
              />
            </div>

            {/* Checklist of Items to Carry */}
            <div className="card no-print">
              <h3 style={{ fontSize: '1.15rem', marginBottom: '0.75rem' }}>Things to Carry to the Police Station</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
                {checklist.map((c, idx) => (
                  <label key={idx} style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', cursor: 'pointer', fontSize: '0.88rem' }}>
                    <input 
                      type="checkbox" 
                      checked={c.checked} 
                      onChange={() => {
                        const updated = [...checklist]
                        updated[idx].checked = !updated[idx].checked
                        setChecklist(updated)
                      }}
                      style={{ width: '16px', height: '16px', accentColor: 'var(--lt-teal)' }}
                    />
                    <span style={{ color: c.checked ? '#fff' : 'var(--lt-text-muted)', textDecoration: c.checked ? 'none' : 'line-through' }}>
                      {c.item}
                    </span>
                  </label>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ----------------- PAGE 5: LEGAL KNOWLEDGE LIBRARY ----------------- */}
        {activeTab === 'library' && (
          <div>
            <div style={{ marginBottom: '1.5rem' }}>
              <h1 style={{ fontSize: '1.9rem', marginBottom: '0.25rem' }}>Legal Knowledge Library</h1>
              <p style={{ color: 'var(--lt-text-muted)', fontSize: '0.92rem' }}>
                Verified provisions under Bharatiya Nyaya Sanhita (BNS 2023), BNSS 2023, BSA 2023, and IT Act 2000.
              </p>
            </div>

            {/* Filters & Search */}
            <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '1.75rem' }}>
              <div style={{ flex: '1 1 280px', position: 'relative' }}>
                <input
                  type="text"
                  className="chat-input"
                  style={{ width: '100%', paddingLeft: '2.5rem' }}
                  placeholder="Search by section, keyword (e.g. 351, threat, theft, FIR, bail)..."
                  value={librarySearch}
                  onChange={e => setLibrarySearch(e.target.value)}
                />
                <Search size={16} color="var(--lt-text-muted)" style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)' }} />
              </div>

              {/* Category Pills */}
              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                {['All', 'Threat', 'Assault', 'Fraud', 'Cybercrime', 'Theft', 'Rights_Procedure'].map(cat => (
                  <button
                    key={cat}
                    className={`btn ${selectedCategory === cat ? 'btn-teal' : 'btn-outline'}`}
                    style={{ padding: '0.4rem 0.85rem', fontSize: '0.8rem' }}
                    onClick={() => setSelectedCategory(cat)}
                  >
                    {cat}
                  </button>
                ))}
              </div>
            </div>

            {/* Provisions Cards List */}
            <div className="card-grid">
              {libraryProvisions
                .filter(p => selectedCategory === 'All' || p.category === selectedCategory)
                .filter(p => !librarySearch || JSON.stringify(p).toLowerCase().includes(librarySearch.toLowerCase()))
                .map((p, idx) => (
                  <div key={idx} className="card" style={{ display: 'flex', flexDirection: 'column' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                      <span className="badge badge-teal">{p.category}</span>
                      <a href={p.source_url} target="_blank" rel="noreferrer" style={{ fontSize: '0.72rem', color: 'var(--lt-teal)', display: 'inline-flex', alignItems: 'center', gap: '3px' }}>
                        India Code <ExternalLink size={10} />
                      </a>
                    </div>

                    <strong style={{ fontSize: '1.02rem', color: '#FFFFFF', marginBottom: '0.2rem' }}>
                      {p.act}
                    </strong>
                    <div style={{ fontSize: '0.92rem', fontWeight: 700, color: 'var(--lt-teal)', marginBottom: '0.75rem' }}>
                      Section {p.section_number}: {p.title}
                    </div>

                    <p style={{ fontSize: '0.86rem', color: '#CBD5E1', flex: 1, marginBottom: '1rem' }}>
                      {p.plain_explanation}
                    </p>

                    {p.conditions_exceptions && (
                      <div style={{ background: 'var(--lt-bg-deep)', padding: '0.65rem', borderRadius: '6px', fontSize: '0.75rem', color: 'var(--lt-text-muted)' }}>
                        ℹ️ {p.conditions_exceptions}
                      </div>
                    )}
                  </div>
                ))}
            </div>
          </div>
        )}

        {/* ----------------- PAGE 6: LEGAL DOCUMENT ANALYZER ----------------- */}
        {activeTab === 'doc' && (
          <div>
            <div style={{ marginBottom: '1.5rem' }}>
              <h1 style={{ fontSize: '1.9rem', marginBottom: '0.25rem' }}>Legal Document Analyzer</h1>
              <p style={{ color: 'var(--lt-text-muted)', fontSize: '0.92rem' }}>
                Paste legal notices, summons excerpts, or FIR copies to get plain-language explanations of complex terminology.
              </p>
            </div>

            <div style={{ display: 'flex', gap: '1.75rem', flexWrap: 'wrap' }}>
              <div style={{ flex: '1 1 360px', minWidth: 0, width: '100%' }}>
                <form onSubmit={handleDocAnalyze} className="card">
                  <h3 style={{ fontSize: '1.15rem', marginBottom: '0.75rem' }}>Paste Legal Document Text</h3>
                  <textarea
                    style={{
                      width: '100%',
                      height: '240px',
                      background: 'var(--lt-bg-deep)',
                      color: '#fff',
                      padding: '1rem',
                      borderRadius: '8px',
                      border: '1px solid var(--lt-border)',
                      outline: 'none',
                      fontSize: '0.88rem',
                      marginBottom: '1rem'
                    }}
                    placeholder="Paste text from a police notice, court summons, or complaint draft here (e.g., 'Notice under Section 35(3) BNSS regarding Cr. No. 128/2026 for cognizable offence...')"
                    value={docText}
                    onChange={e => setDocText(e.target.value)}
                  />

                  <button className="btn btn-teal" type="submit" disabled={isDocLoading || !docText.trim()}>
                    {isDocLoading ? "Analyzing..." : "Analyze Document Text"}
                  </button>
                </form>
              </div>

              <div style={{ flex: '1 1 420px', minWidth: 0, width: '100%' }}>
                {docAnalysis ? (
                  <div className="card">
                    <h3 style={{ fontSize: '1.18rem', marginBottom: '0.5rem' }}>Analysis Results</h3>
                    <p style={{ color: '#E2E8F0', fontSize: '0.88rem', marginBottom: '1rem' }}>{docAnalysis.summary}</p>

                    {/* Identified Reference Numbers & Dates */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1.25rem' }}>
                      <div style={{ background: 'var(--lt-bg-deep)', padding: '0.75rem', borderRadius: '8px' }}>
                        <span style={{ fontSize: '0.72rem', color: 'var(--lt-text-muted)', display: 'block' }}>Dates Found:</span>
                        <strong style={{ fontSize: '0.85rem' }}>{docAnalysis.dates_found?.join(', ') || "None"}</strong>
                      </div>
                      <div style={{ background: 'var(--lt-bg-deep)', padding: '0.75rem', borderRadius: '8px' }}>
                        <span style={{ fontSize: '0.72rem', color: 'var(--lt-text-muted)', display: 'block' }}>Reference Codes:</span>
                        <strong style={{ fontSize: '0.85rem' }}>{docAnalysis.case_references?.join(', ') || "None"}</strong>
                      </div>
                    </div>

                    {/* Explained Terms */}
                    <div style={{ marginBottom: '1.25rem' }}>
                      <h4 style={{ fontSize: '0.95rem', color: 'var(--lt-teal)', marginBottom: '0.5rem' }}>Explained Legal Terms:</h4>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                        {(docAnalysis.explained_terms || []).map((t: any, idx: number) => (
                          <div key={idx} style={{ background: 'var(--lt-bg-deep)', padding: '0.75rem', borderRadius: '6px', fontSize: '0.82rem' }}>
                            <strong style={{ color: 'var(--lt-teal)' }}>{t.term}:</strong> {t.plain_meaning}
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Recommended Questions to Ask an Advocate */}
                    <div>
                      <h4 style={{ fontSize: '0.95rem', color: 'var(--lt-teal)', marginBottom: '0.5rem' }}>Questions to Discuss with a Lawyer:</h4>
                      <ul style={{ paddingLeft: '1.2rem', fontSize: '0.82rem', color: '#CBD5E1' }}>
                        {(docAnalysis.recommended_questions || []).map((q: string, idx: number) => (
                          <li key={idx} style={{ marginBottom: '0.25rem' }}>{q}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ) : (
                  <div className="card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '300px', textAlign: 'center' }}>
                    <FileText size={48} color="var(--lt-border)" style={{ marginBottom: '1rem' }} />
                    <p style={{ color: 'var(--lt-text-muted)', fontSize: '0.88rem', maxWidth: '350px' }}>
                      Paste a document excerpt on the left to extract reference codes, deadlines, and plain-language definitions.
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* ----------------- PAGE 7: ABOUT & PRIVACY ----------------- */}
        {activeTab === 'about' && (
          <div style={{ maxWidth: '820px', margin: '0 auto' }}>
            <h1 style={{ fontSize: '2.15rem', marginBottom: '0.5rem' }}>About Legal Tantra</h1>
            <p style={{ color: 'var(--lt-text-muted)', fontSize: '1rem', marginBottom: '2rem' }}>
              Empowering ordinary citizens with legal awareness, rights literacy, and factual preparation.
            </p>

            <div className="card" style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ fontSize: '1.18rem', color: 'var(--lt-teal)', marginBottom: '0.75rem' }}>Our Mission</h3>
              <p style={{ fontSize: '0.92rem', lineHeight: '1.7', color: '#E2E8F0', marginBottom: '0.75rem' }}>
                When an incident occurs, approaching a police station can feel intimidating. Citizens are often unaware of which Indian statutes apply, whether an act constitutes a cognizable offence, or what their fundamental procedural rights are.
              </p>
              <p style={{ fontSize: '0.92rem', lineHeight: '1.7', color: '#E2E8F0' }}>
                <strong>Legal Tantra</strong> bridges this divide through source-grounded conversational AI. It helps victims and witnesses organize facts chronologically, understand provisions under the Bharatiya Nyaya Sanhita (BNS 2023), and exercise their right to a First Information Report (FIR) under Section 173 of the Bharatiya Nagarik Suraksha Sanhita (BNSS 2023).
              </p>
            </div>

            <div className="card" style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ fontSize: '1.18rem', color: 'var(--lt-teal)', marginBottom: '0.75rem' }}>Privacy & Data Protection Principles</h3>
              <ul style={{ paddingLeft: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.88rem', color: '#CBD5E1' }}>
                <li><strong>No Mandatory Registration:</strong> You can use all core AI features without submitting your full legal name, phone number, or Aadhaar credentials.</li>
                <li><strong>Zero Permanent Profile Tracking:</strong> Session records are scoped to temporary IDs and can be cleared instantly using the "Clear Session" button.</li>
                <li><strong>Local Zero-Dependency Storage:</strong> Sensitive facts are never sold or shared with commercial advertising brokers.</li>
                <li><strong>Voice Audio Not Stored:</strong> Voice input is processed on-the-fly and transcripts can be reviewed and edited prior to submission.</li>
              </ul>
            </div>

            <div className="card" style={{ borderLeft: '4px solid var(--lt-warning)' }}>
              <h3 style={{ fontSize: '1.18rem', color: 'var(--lt-warning)', marginBottom: '0.75rem' }}>Legal & AI Disclaimer</h3>
              <p style={{ fontSize: '0.85rem', lineHeight: '1.6', color: '#CBD5E1', margin: 0 }}>
                Legal Tantra is an educational and factual preparation platform. The AI assistant provides preliminary information grounded in verified statutes from India Code. It does not provide binding legal determinations, court judgments, or replace consultation with an appropriately qualified advocate. In situations involving immediate danger, always contact the police directly at 112.
              </p>
            </div>
          </div>
        )}
      </main>

      {/* ================= FOOTER (Distinct Charcoal Obsidian Palette) ================= */}
      <footer className="lt-footer no-print">
        <div className="lt-footer-inner">
          {/* Col 1: Brand & Tagline */}
          <div className="lt-footer-col">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '0.75rem' }}>
              <Scale size={22} color="var(--lt-teal)" />
              <strong style={{ fontSize: '1.2rem', color: '#fff' }}>LEGAL TANTRA</strong>
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--lt-text-muted)', lineHeight: '1.6', marginBottom: '1rem' }}>
              {t.brandTagline}
            </p>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.75rem', background: 'rgba(16, 185, 129, 0.1)', color: 'var(--lt-success)', padding: '0.25rem 0.65rem', borderRadius: '14px', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
              <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: 'var(--lt-success)' }}></span>
              <span>BNS, BNSS, BSA 2023 Verified</span>
            </div>
          </div>

          {/* Col 2: Navigation Links */}
          <div className="lt-footer-col">
            <h4>QUICK NAVIGATION</h4>
            <ul className="lt-footer-links">
              <li><span onClick={() => setActiveTab('home')}>{t.navHome}</span></li>
              <li><span onClick={() => setActiveTab('chat')}>{t.navChat}</span></li>
              <li><span onClick={loadAnalysis}>{t.navAnalysis}</span></li>
              <li><span onClick={loadPoliceStatement}>{t.navPolice}</span></li>
              <li><span onClick={() => setActiveTab('library')}>{t.navLibrary}</span></li>
              <li><span onClick={() => setActiveTab('doc')}>{t.navDoc}</span></li>
            </ul>
          </div>

          {/* Col 3: Emergency Helplines */}
          <div className="lt-footer-col">
            <h4>EMERGENCY HELPLINES (INDIA)</h4>
            <div className="lt-footer-emergency-badge">
              <span>National Emergency</span>
              <strong style={{ color: 'var(--lt-danger)' }}>112</strong>
            </div>
            <div className="lt-footer-emergency-badge">
              <span>Women Helpline</span>
              <strong style={{ color: 'var(--lt-warning)' }}>1091</strong>
            </div>
            <div className="lt-footer-emergency-badge">
              <span>Cyber Fraud Helpline</span>
              <strong style={{ color: 'var(--lt-teal)' }}>1930</strong>
            </div>
            <div className="lt-footer-emergency-badge">
              <span>Medical Ambulance</span>
              <strong style={{ color: 'var(--lt-success)' }}>108</strong>
            </div>
          </div>

          {/* Col 4: Statutory Legal Source & DPDP */}
          <div className="lt-footer-col">
            <h4>STATUTORY SOURCES</h4>
            <p style={{ fontSize: '0.8rem', color: 'var(--lt-text-muted)', lineHeight: '1.6', marginBottom: '0.75rem' }}>
              All provisions reference official gazetted legislation from <a href="https://www.indiacode.nic.in" target="_blank" rel="noreferrer" style={{ textDecoration: 'underline' }}>India Code</a>.
            </p>
            <p style={{ fontSize: '0.78rem', color: 'var(--lt-text-muted)', lineHeight: '1.5' }}>
              Aligned with privacy principles under India's Digital Personal Data Protection (DPDP) Act.
            </p>
          </div>
        </div>

        {/* Footer Bottom Row */}
        <div className="lt-footer-bottom">
          <div>
            © {new Date().getFullYear()} Legal Tantra. Educational and factual preparation platform for Indian citizens.
          </div>
          <div style={{ display: 'flex', gap: '1.25rem' }}>
            <span style={{ cursor: 'pointer' }} onClick={() => setActiveTab('about')}>Privacy Policy</span>
            <span style={{ cursor: 'pointer' }} onClick={() => setActiveTab('about')}>Legal Disclaimers</span>
            <span style={{ cursor: 'pointer' }} onClick={() => setShowEmergencyModal(true)}>Emergency SOS</span>
          </div>
        </div>
      </footer>
      </div>

      {/* Speech Review & Edit Modal */}
      {showTranscriptModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(5, 11, 24, 0.88)', backdropFilter: 'blur(6px)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1200, padding: '1.25rem'
        }}>
          <div className="card" style={{ maxWidth: '520px', width: '100%' }}>
            <h3 style={{ fontSize: '1.18rem', marginBottom: '0.4rem' }}>{t.micReviewTitle}</h3>
            <p style={{ color: 'var(--lt-text-muted)', fontSize: '0.82rem', marginBottom: '0.85rem' }}>{t.micReviewDesc}</p>
            
            <textarea
              style={{
                width: '100%', height: '120px', background: 'var(--lt-bg-deep)', color: '#fff',
                padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--lt-border)',
                outline: 'none', fontSize: '0.92rem', marginBottom: '1.25rem'
              }}
              value={transcriptCandidate}
              onChange={e => setTranscriptCandidate(e.target.value)}
            />

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
              <button className="btn btn-outline" onClick={() => setShowTranscriptModal(false)}>
                {t.micCancel}
              </button>
              <button 
                className="btn btn-teal" 
                onClick={() => {
                  setShowTranscriptModal(false)
                  sendMessage(transcriptCandidate)
                  setTranscriptCandidate('')
                }}
              >
                {t.micSubmit}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Emergency Contacts Modal */}
      {showEmergencyModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(5, 11, 24, 0.88)', backdropFilter: 'blur(6px)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1200, padding: '1.25rem'
        }}>
          <div className="card" style={{ maxWidth: '560px', width: '100%', border: '1px solid var(--lt-danger)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h3 style={{ fontSize: '1.2rem', color: 'var(--lt-danger)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <AlertOctagon size={20} /> National Emergency Helplines (India)
              </h3>
              <button className="btn btn-outline" style={{ padding: '0.2rem 0.55rem' }} onClick={() => setShowEmergencyModal(false)}>✕</button>
            </div>

            <p style={{ fontSize: '0.85rem', color: 'var(--lt-text-muted)', marginBottom: '1.15rem' }}>
              If you or anyone around you is in immediate physical danger, call emergency services directly:
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'var(--lt-bg-deep)', padding: '0.75rem 1rem', borderRadius: '8px' }}>
                <div>
                  <strong style={{ fontSize: '0.95rem' }}>112 — National Emergency Helpline</strong>
                  <div style={{ fontSize: '0.75rem', color: 'var(--lt-text-muted)' }}>Police, Fire, Ambulance all-in-one across India</div>
                </div>
                <a href="tel:112" className="btn btn-danger" style={{ padding: '0.4rem 0.8rem' }}>Call 112</a>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'var(--lt-bg-deep)', padding: '0.75rem 1rem', borderRadius: '8px' }}>
                <div>
                  <strong style={{ fontSize: '0.95rem' }}>1091 — Women Helpline</strong>
                  <div style={{ fontSize: '0.75rem', color: 'var(--lt-text-muted)' }}>24x7 support for women facing violence or harassment</div>
                </div>
                <a href="tel:1091" className="btn btn-danger" style={{ padding: '0.4rem 0.8rem' }}>Call 1091</a>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'var(--lt-bg-deep)', padding: '0.75rem 1rem', borderRadius: '8px' }}>
                <div>
                  <strong style={{ fontSize: '0.95rem' }}>1930 — National Cyber Crime Helpline</strong>
                  <div style={{ fontSize: '0.75rem', color: 'var(--lt-text-muted)' }}>Immediate reporting for online financial fraud (Golden Hour)</div>
                </div>
                <a href="tel:1930" className="btn btn-danger" style={{ padding: '0.4rem 0.8rem' }}>Call 1930</a>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'var(--lt-bg-deep)', padding: '0.75rem 1rem', borderRadius: '8px' }}>
                <div>
                  <strong style={{ fontSize: '0.95rem' }}>108 — Ambulance / Medical Care</strong>
                  <div style={{ fontSize: '0.75rem', color: 'var(--lt-text-muted)' }}>Urgent medical assistance & hospital transit</div>
                </div>
                <a href="tel:108" className="btn btn-danger" style={{ padding: '0.4rem 0.8rem' }}>Call 108</a>
              </div>
            </div>

            <div style={{ marginTop: '1.25rem', textAlign: 'right' }}>
              <button className="btn btn-outline" onClick={() => setShowEmergencyModal(false)}>Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
