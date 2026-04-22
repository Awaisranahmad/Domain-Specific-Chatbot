import streamlit as st
import os
import base64
import io
import json
import datetime
from PIL import Image
from groq import Groq

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="MediAssist AI Pro",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# DARK MEDICAL PROFESSIONAL CSS
# =========================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

    /* ── ROOT THEME ── */
    :root {
        --bg-base:      #0A0F1A;
        --bg-surface:   #111827;
        --bg-card:      #141E2E;
        --bg-elevated:  #1A2535;
        --border:       rgba(56,189,248,0.12);
        --border-glow:  rgba(56,189,248,0.35);
        --accent:       #38BDF8;
        --accent-dim:   rgba(56,189,248,0.15);
        --accent-2:     #818CF8;
        --accent-3:     #34D399;
        --accent-warn:  #FBBF24;
        --accent-danger:#F87171;
        --text-primary: #E2EAF4;
        --text-muted:   #64748B;
        --text-dim:     #94A3B8;
        --radius:       16px;
        --radius-sm:    10px;
        --radius-lg:    24px;
    }

    /* ── GLOBAL ── */
    html, body, [data-testid="stAppViewContainer"] {
        background: var(--bg-base) !important;
        font-family: 'DM Sans', sans-serif;
        color: var(--text-primary);
    }

    [data-testid="stSidebar"] {
        background: var(--bg-surface) !important;
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"] * { color: var(--text-primary) !important; }

    .main .block-container {
        padding: 1.5rem 2rem;
        max-width: 1600px;
    }

    h1,h2,h3,h4,h5,h6 {
        font-family: 'Syne', sans-serif !important;
        color: var(--text-primary) !important;
    }

    hr { border-color: var(--border) !important; }

    /* ── CARDS ── */
    .med-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        padding: 24px;
        margin-bottom: 20px;
        transition: border-color 0.2s, box-shadow 0.2s;
    }
    .med-card:hover {
        border-color: var(--border-glow);
        box-shadow: 0 0 28px rgba(56,189,248,0.06);
    }
    .med-card-sm {
        background: var(--bg-elevated);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 16px 20px;
        margin-bottom: 14px;
    }

    /* ── SECTION TITLE ── */
    .sec-title {
        font-family: 'Syne', sans-serif;
        font-size: 1rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: var(--accent) !important;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* ── STAT BADGES ── */
    .stat-row { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 16px; }
    .stat-badge {
        background: var(--bg-elevated);
        border: 1px solid var(--border);
        border-radius: var(--radius-sm);
        padding: 10px 16px;
        flex: 1;
        min-width: 100px;
        text-align: center;
    }
    .stat-badge .val { font-family:'Syne',sans-serif; font-size:1.4rem; font-weight:800; color:var(--accent); }
    .stat-badge .lbl { font-size:0.72rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.06em; }

    /* ── CHAT BUBBLES ── */
    .bubble-user {
        background: linear-gradient(135deg, #0369A1, #0EA5E9);
        color: #fff;
        padding: 12px 16px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0 12px auto;
        width: fit-content;
        max-width: 82%;
        font-size: 0.94rem;
        line-height: 1.55;
        box-shadow: 0 4px 16px rgba(14,165,233,0.2);
    }
    .bubble-ai {
        background: var(--bg-elevated);
        border: 1px solid var(--border);
        border-left: 3px solid var(--accent-2);
        color: var(--text-primary);
        padding: 12px 16px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 0 12px 0;
        max-width: 88%;
        font-size: 0.93rem;
        line-height: 1.65;
    }
    .bubble-warn {
        background: rgba(251,191,36,0.1);
        border: 1px solid rgba(251,191,36,0.3);
        border-left: 3px solid var(--accent-warn);
        color: #FDE68A;
        padding: 12px 16px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 0 12px 0;
        max-width: 88%;
        font-size: 0.93rem;
        line-height: 1.65;
    }
    .bubble-ts {
        font-size: 0.72rem;
        color: var(--text-muted);
        margin-top: -8px;
        margin-bottom: 10px;
        padding: 0 4px;
    }
    .bubble-ts-right { text-align: right; }

    /* ── DISCLAIMER ── */
    .disclaimer {
        background: rgba(248,113,113,0.08);
        border: 1px solid rgba(248,113,113,0.25);
        border-left: 4px solid var(--accent-danger);
        color: #FCA5A5;
        padding: 14px 18px;
        border-radius: var(--radius);
        font-size: 0.87rem;
        line-height: 1.6;
    }

    /* ── REPORT BOX ── */
    .report-box {
        background: var(--bg-base);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 18px;
        font-size: 0.9rem;
        line-height: 1.7;
        color: var(--text-dim);
        white-space: pre-wrap;
        max-height: 400px;
        overflow-y: auto;
    }
    .report-box::-webkit-scrollbar { width: 4px; }
    .report-box::-webkit-scrollbar-thumb { background: var(--accent-dim); border-radius: 4px; }

    /* ── BUTTONS ── */
    .stButton > button {
        background: var(--accent-dim) !important;
        color: var(--accent) !important;
        border: 1px solid var(--border-glow) !important;
        border-radius: 12px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover {
        background: rgba(56,189,248,0.25) !important;
        box-shadow: 0 0 18px rgba(56,189,248,0.2) !important;
        transform: translateY(-1px) !important;
    }
    .stDownloadButton > button {
        background: rgba(52,211,153,0.12) !important;
        color: var(--accent-3) !important;
        border: 1px solid rgba(52,211,153,0.3) !important;
        border-radius: 12px !important;
        font-weight: 500 !important;
    }

    /* ── INPUTS ── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: var(--bg-base) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.93rem !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--border-glow) !important;
        box-shadow: 0 0 0 2px rgba(56,189,248,0.12) !important;
    }
    .stTextInput > label, .stTextArea > label { color: var(--text-muted) !important; font-size: 0.85rem !important; }

    /* ── SELECT / RADIO ── */
    .stSelectbox > div > div { background: var(--bg-base) !important; border: 1px solid var(--border) !important; border-radius: 12px !important; color: var(--text-primary) !important; }
    .stRadio > div > label { color: var(--text-dim) !important; }
    .stRadio > div > label:has(input:checked) { color: var(--accent) !important; }

    /* ── TABS ── */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--bg-surface) !important;
        border-radius: 14px !important;
        padding: 4px !important;
        gap: 2px !important;
        border: 1px solid var(--border) !important;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px !important;
        color: var(--text-muted) !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.88rem !important;
        padding: 8px 18px !important;
    }
    .stTabs [aria-selected="true"] {
        background: var(--accent-dim) !important;
        color: var(--accent) !important;
        font-weight: 600 !important;
    }
    .stTabs [data-baseweb="tab-panel"] { padding-top: 20px !important; }

    /* ── METRICS ── */
    [data-testid="metric-container"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        padding: 14px !important;
    }
    [data-testid="metric-container"] label { color: var(--text-muted) !important; font-size:0.8rem !important; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] { color: var(--accent) !important; font-family:'Syne',sans-serif !important; }

    /* ── FILE UPLOADER ── */
    [data-testid="stFileUploader"] section {
        background: var(--bg-elevated) !important;
        border: 1.5px dashed var(--border-glow) !important;
        border-radius: var(--radius) !important;
    }
    [data-testid="stFileUploader"] button {
        background: var(--accent-dim) !important;
        color: var(--accent) !important;
        border-radius: 10px !important;
        border: 1px solid var(--border-glow) !important;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] { color: var(--text-muted) !important; }

    /* ── EXPANDER ── */
    .streamlit-expanderHeader {
        background: var(--bg-elevated) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-primary) !important;
        font-family: 'DM Sans', sans-serif !important;
    }
    .streamlit-expanderContent { background: var(--bg-card) !important; }

    /* ── CHECKBOX ── */
    .stCheckbox > label { color: var(--text-dim) !important; }

    /* ── INFO/WARNING/ERROR BOXES ── */
    .stInfo { background: rgba(56,189,248,0.08) !important; border-color: var(--border-glow) !important; color: var(--accent) !important; border-radius: var(--radius-sm) !important; }
    .stWarning { background: rgba(251,191,36,0.08) !important; color: var(--accent-warn) !important; border-radius: var(--radius-sm) !important; }
    .stSuccess { background: rgba(52,211,153,0.08) !important; color: var(--accent-3) !important; border-radius: var(--radius-sm) !important; }
    .stError { background: rgba(248,113,113,0.08) !important; color: var(--accent-danger) !important; border-radius: var(--radius-sm) !important; }

    /* ── CAPTION ── */
    .stCaption { color: var(--text-muted) !important; }

    /* ── TAG PILL ── */
    .tag-pill {
        display: inline-block;
        background: var(--accent-dim);
        color: var(--accent);
        border: 1px solid var(--border-glow);
        border-radius: 100px;
        padding: 3px 12px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        margin-right: 6px;
        margin-bottom: 4px;
    }
    .tag-pill.green { background: rgba(52,211,153,0.12); color: var(--accent-3); border-color: rgba(52,211,153,0.3); }
    .tag-pill.warn  { background: rgba(251,191,36,0.12); color: var(--accent-warn); border-color: rgba(251,191,36,0.3); }
    .tag-pill.red   { background: rgba(248,113,113,0.12); color: var(--accent-danger); border-color: rgba(248,113,113,0.3); }

    /* ── SYMPTOM SELECTOR ── */
    .symptom-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 10px 0 16px 0;
    }

    /* ── HISTORY ITEM ── */
    .history-item {
        background: var(--bg-elevated);
        border: 1px solid var(--border);
        border-radius: var(--radius-sm);
        padding: 10px 14px;
        margin-bottom: 8px;
        cursor: pointer;
        transition: border-color 0.15s;
    }
    .history-item:hover { border-color: var(--border-glow); }
    .history-item .hi-title { font-size:0.87rem; font-weight:600; color:var(--text-primary); }
    .history-item .hi-date { font-size:0.75rem; color:var(--text-muted); margin-top:2px; }

    /* ── VITALS ── */
    .vital-row { display: grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap: 10px; margin: 12px 0; }
    .vital-box {
        background: var(--bg-elevated);
        border: 1px solid var(--border);
        border-radius: var(--radius-sm);
        padding: 12px;
        text-align: center;
    }
    .vital-box.normal { border-color: rgba(52,211,153,0.3); }
    .vital-box.warn { border-color: rgba(251,191,36,0.3); }
    .vital-box.danger { border-color: rgba(248,113,113,0.3); }
    .vital-box .v-val { font-family:'Syne',sans-serif; font-size:1.3rem; font-weight:800; }
    .vital-box.normal .v-val { color: var(--accent-3); }
    .vital-box.warn .v-val { color: var(--accent-warn); }
    .vital-box.danger .v-val { color: var(--accent-danger); }
    .vital-box .v-lbl { font-size:0.72rem; color:var(--text-muted); margin-top:2px; }

    /* ── HEADER LOGO AREA ── */
    .app-header {
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 8px 0 20px 0;
        border-bottom: 1px solid var(--border);
        margin-bottom: 24px;
    }
    .app-header .logo-icon {
        width: 48px; height: 48px;
        background: var(--accent-dim);
        border: 1px solid var(--border-glow);
        border-radius: 14px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.5rem;
    }
    .app-header .app-name {
        font-family: 'Syne', sans-serif;
        font-size: 1.5rem;
        font-weight: 800;
        color: var(--text-primary);
    }
    .app-header .app-sub {
        font-size: 0.82rem;
        color: var(--text-muted);
        margin-top: 2px;
    }

    /* ── SIDEBAR LOGO ── */
    .sb-logo {
        text-align: center;
        padding: 16px 0 8px 0;
        border-bottom: 1px solid var(--border);
        margin-bottom: 16px;
    }
    .sb-logo .icon { font-size: 2.4rem; }
    .sb-logo .name {
        font-family: 'Syne', sans-serif;
        font-size: 1.1rem;
        font-weight: 800;
        color: var(--accent);
        margin-top: 6px;
    }
    .sb-logo .ver { font-size: 0.75rem; color: var(--text-muted); }

    /* ── EMPTY STATE ── */
    .empty-state {
        text-align: center;
        padding: 40px 24px;
        color: var(--text-muted);
        border: 1.5px dashed var(--border);
        border-radius: var(--radius-lg);
    }
    .empty-state .es-icon { font-size: 2.8rem; margin-bottom: 10px; }

    /* ── SPINNER ── */
    .stSpinner > div { border-top-color: var(--accent) !important; }

    /* ── SCROLLBAR ── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: var(--bg-elevated); border-radius: 6px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--border-glow); }

    /* ── CHAT SCROLL ── */
    .chat-scroll {
        max-height: 460px;
        overflow-y: auto;
        padding-right: 4px;
        margin-bottom: 12px;
    }
    .chat-scroll::-webkit-scrollbar { width: 4px; }
    .chat-scroll::-webkit-scrollbar-thumb { background: var(--bg-elevated); border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# PROMPTS
# =========================================================
MEDICAL_DISCLAIMER = (
    "MediAssist AI Pro is an informational tool ONLY. It is NOT a licensed healthcare provider. "
    "It cannot diagnose illnesses, prescribe medication, or replace professional medical advice. "
    "For urgent or severe symptoms, seek IMMEDIATE medical care."
)

SYSTEM_PROMPT = """You are MediAssist AI Pro — a professional, calm, and knowledgeable medical information assistant.

Your scope:
- Explain medical terminology in simple language
- Summarize and interpret medical reports
- Answer general health & wellness questions
- Provide safe, conservative, informational guidance

Hard rules:
1. NEVER diagnose a condition.
2. NEVER prescribe medication.
3. NEVER claim to be a doctor or licensed professional.
4. If symptoms sound urgent (chest pain, stroke signs, severe bleeding, difficulty breathing), immediately tell the user to seek emergency care.
5. For medicine questions: give only cautious, general informational suggestions; always say "verify with your doctor/pharmacist".
6. Be concise, empathetic, and professional.
7. Use clear formatting with bullet points and sections when explaining complex topics.
8. End EVERY response with: "⚕️ Note: I am an AI assistant, not a licensed doctor. Please consult a qualified healthcare professional for medical advice."
"""

VISION_PROMPT = """You are MediAssist AI Pro — a medical report image analyzer.

Your task:
- Carefully read the uploaded medical report image.
- Extract ALL visible data: patient info (if shown), test names, values, units, reference ranges, dates.
- Clearly flag values that are HIGH ↑, LOW ↓, or ABNORMAL based on reference ranges shown.
- Organize findings in structured sections.
- Explain what each test measures in simple terms.
- If text is blurry or unreadable, clearly state that.
- Do NOT diagnose or invent values.

Format your response with clear headings and sections.
End with: "⚕️ Note: I am an AI assistant, not a doctor. Please consult a qualified healthcare professional."
"""

MEDICINE_PROMPT = """You are MediAssist AI Pro providing cautious medicine information.

Rules:
- Do NOT diagnose, prescribe, or claim any medicine is definitely safe for the user.
- Provide only cautious, general, non-personalized informational suggestions.
- Mention common OTC options only if clearly appropriate and safe.
- Always advise consulting a doctor or pharmacist before taking any medication.
- Mention common cautions, contraindications at a high level only.
- If the condition sounds serious, advise urgent medical review immediately.
- End with: "⚕️ Note: I am an AI assistant, not a licensed doctor. Please consult a qualified healthcare professional for medical advice."
"""

SYMPTOM_CHECKER_PROMPT = """You are MediAssist AI Pro — performing a symptom assessment.

Given the user's symptoms, provide:
1. **Possible Causes**: List 3-5 possible (not definitive) explanations, from most to least common.
2. **Urgency Level**: Rate as 🟢 Non-urgent / 🟡 Monitor / 🔴 Seek immediate care — with brief reason.
3. **Self-Care Tips**: Safe, general supportive care suggestions.
4. **When to See a Doctor**: Clear criteria for when professional evaluation is needed.
5. **Questions to Ask Your Doctor**: 3-4 relevant questions.

Important: This is NOT a diagnosis. Always be clear about uncertainty.
End with: "⚕️ Note: I am an AI assistant, not a licensed doctor. Please consult a qualified healthcare professional for medical advice."
"""

HEALTH_SUMMARY_PROMPT = """You are MediAssist AI Pro — creating a health session summary.

Based on the conversation history provided, create a structured Health Session Summary including:
- Key topics discussed
- Important findings from any reports
- Recommendations given
- Action items for the patient
- Questions remaining unanswered

Format it professionally as a brief health note.
End with the standard disclaimer.
"""

# =========================================================
# HELPERS
# =========================================================
def get_groq_client():
    api_key = st.secrets.get("GROQ_API_KEY", "") or os.getenv("GROQ_API_KEY", "")
    if not api_key:
        st.error("❌ GROQ_API_KEY is missing. Add it in Streamlit secrets or environment variables.")
        st.stop()
    return Groq(api_key=api_key)

def get_models():
    text_model   = st.secrets.get("GROQ_TEXT_MODEL",   os.getenv("GROQ_TEXT_MODEL",   "llama-3.3-70b-versatile"))
    vision_model = st.secrets.get("GROQ_VISION_MODEL", os.getenv("GROQ_VISION_MODEL", "meta-llama/llama-4-maverick-17b-128e-instruct"))
    return text_model, vision_model

def resize_image_bytes(file_bytes: bytes, max_size=(1200, 1200)) -> bytes:
    img = Image.open(io.BytesIO(file_bytes))
    if img.mode != "RGB":
        img = img.convert("RGB")
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=88, optimize=True)
    return buf.getvalue()

def to_data_url(image_bytes: bytes) -> str:
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"

URGENT_FLAGS = [
    "chest pain", "shortness of breath", "difficulty breathing", "trouble breathing",
    "can't breathe", "cannot breathe", "fainting", "unconscious", "loss of consciousness",
    "severe bleeding", "stroke", "one sided weakness", "face drooping", "arm weakness",
    "speech difficulty", "suicidal", "seizure", "blue lips", "cyanosis",
    "severe headache", "worst headache", "sudden headache", "heart attack",
    "crushing chest", "stabbing chest", "pressure chest"
]

def is_urgent(text: str) -> bool:
    t = text.lower()
    return any(flag in t for flag in URGENT_FLAGS)

def ts_now() -> str:
    return datetime.datetime.now().strftime("%I:%M %p")

def date_now() -> str:
    return datetime.datetime.now().strftime("%b %d, %Y %I:%M %p")

def groq_text(client, model, messages, max_tokens=1000, temp=0.35):
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temp,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content.strip()

def analyze_image(client, vision_model, image_bytes: bytes) -> str:
    data_url = to_data_url(image_bytes)
    resp = client.chat.completions.create(
        model=vision_model,
        temperature=0.2,
        max_tokens=1400,
        messages=[
            {"role": "system", "content": VISION_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analyze this medical report image. Extract and structure all visible information."},
                    {"type": "image_url", "image_url": {"url": data_url}}
                ]
            }
        ],
    )
    return resp.choices[0].message.content.strip()

def save_session_to_history():
    """Save current session to history."""
    if not st.session_state.messages:
        return
    session = {
        "id": date_now(),
        "date": date_now(),
        "messages": st.session_state.messages.copy(),
        "report_summary": st.session_state.report_summary,
        "uploaded_name": st.session_state.uploaded_name,
        "vitals": st.session_state.vitals.copy(),
    }
    st.session_state.session_history.insert(0, session)
    if len(st.session_state.session_history) > 20:
        st.session_state.session_history = st.session_state.session_history[:20]

def init_state():
    defaults = {
        "messages": [],
        "report_summary": "",
        "uploaded_name": "",
        "uploaded_preview": None,
        "last_action": "",
        "session_history": [],
        "active_tab": 0,
        "vitals": {
            "bp_systolic": "", "bp_diastolic": "",
            "heart_rate": "", "temperature": "",
            "spo2": "", "weight": "", "height": "",
        },
        "selected_symptoms": [],
        "symptom_result": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def render_bubble(role, content, timestamp=""):
    if role == "user":
        st.markdown(f'<div class="bubble-user">{content}</div>', unsafe_allow_html=True)
        if timestamp:
            st.markdown(f'<div class="bubble-ts bubble-ts-right">{timestamp}</div>', unsafe_allow_html=True)
    elif role == "warn":
        st.markdown(f'<div class="bubble-warn">{content}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bubble-ai">{content}</div>', unsafe_allow_html=True)
        if timestamp:
            st.markdown(f'<div class="bubble-ts">{timestamp}</div>', unsafe_allow_html=True)

def classify_vital(name, value):
    """Returns normal/warn/danger class."""
    try:
        v = float(value)
    except:
        return "normal"
    rules = {
        "heart_rate":    [(60, 100, "normal"), (50, 110, "warn")],
        "spo2":          [(95, 100, "normal"), (90, 100, "warn")],
        "temperature":   [(36.1, 37.2, "normal"), (35.5, 38.5, "warn")],
        "bp_systolic":   [(90, 120, "normal"), (80, 140, "warn")],
        "bp_diastolic":  [(60, 80, "normal"), (50, 90, "warn")],
    }
    if name in rules:
        for lo, hi, cls in rules[name]:
            if lo <= v <= hi:
                return cls
        return "danger"
    return "normal"

# =========================================================
# MAIN APP
# =========================================================
def main():
    init_state()
    client = get_groq_client()
    text_model, vision_model = get_models()

    # ──────────── SIDEBAR ────────────
    with st.sidebar:
        st.markdown("""
        <div class="sb-logo">
            <div class="icon">🩺</div>
            <div class="name">MediAssist AI Pro</div>
            <div class="ver">v3.0 · Advanced Edition</div>
        </div>
        """, unsafe_allow_html=True)

        # Model config
        with st.expander("⚙️ Model Configuration", expanded=False):
            text_model   = st.text_input("Text model",   value=text_model,   key="sb_tm")
            vision_model = st.text_input("Vision model", value=vision_model, key="sb_vm")

        # Patient Profile
        st.markdown("### 👤 Patient Profile")
        p_name = st.text_input("Patient Name",  placeholder="Optional",       key="p_name")
        p_age  = st.text_input("Age",           placeholder="e.g. 35",        key="p_age")
        p_sex  = st.selectbox("Biological Sex", ["—", "Male", "Female", "Other"], key="p_sex")
        p_cond = st.text_area("Known Conditions", placeholder="e.g. Diabetes, Hypertension…", height=70, key="p_cond")

        if p_name or p_age or (p_sex != "—"):
            st.markdown(f"""
            <div class="med-card-sm" style="margin-top:8px;">
                <span class="tag-pill">{p_name or 'Patient'}</span>
                {"<span class='tag-pill green'>Age "+p_age+"</span>" if p_age else ""}
                {"<span class='tag-pill'>"+p_sex+"</span>" if p_sex != "—" else ""}
            </div>
            """, unsafe_allow_html=True)

        # Safety Disclaimer
        st.markdown("---")
        st.markdown('<div class="disclaimer">' + MEDICAL_DISCLAIMER + '</div>', unsafe_allow_html=True)
        safety_ok = st.checkbox("✅ I understand and accept this disclaimer", value=False, key="safety")

        # Session controls
        st.markdown("---")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            if st.button("💾 Save Session", use_container_width=True):
                save_session_to_history()
                st.success("Session saved!")
        with col_s2:
            if st.button("🗑️ New Session", use_container_width=True):
                save_session_to_history()
                st.session_state.messages = []
                st.session_state.report_summary = ""
                st.session_state.uploaded_name = ""
                st.session_state.uploaded_preview = None
                st.session_state.last_action = ""
                st.session_state.symptom_result = ""
                st.session_state.selected_symptoms = []
                st.rerun()

        # Session Stats
        n_sessions = len(st.session_state.session_history)
        total_msgs = sum(len(s["messages"]) for s in st.session_state.session_history) + len(st.session_state.messages)
        st.markdown(f"""
        <div style="margin-top:12px;">
            <div style="font-size:0.8rem;color:var(--text-muted);margin-bottom:6px;">SESSION STATS</div>
            <div class="stat-row">
                <div class="stat-badge"><div class="val">{n_sessions}</div><div class="lbl">Sessions</div></div>
                <div class="stat-badge"><div class="val">{total_msgs}</div><div class="lbl">Messages</div></div>
                <div class="stat-badge"><div class="val">{len(st.session_state.messages)//2}</div><div class="lbl">This Chat</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    if not safety_ok:
        st.markdown("""
        <div style="text-align:center;padding:80px 40px;">
            <div style="font-size:3rem;margin-bottom:16px;">🩺</div>
            <h2 style="font-family:'Syne',sans-serif;color:var(--text-primary);">MediAssist AI Pro</h2>
            <p style="color:var(--text-muted);max-width:400px;margin:0 auto;">
                Please read and accept the medical disclaimer in the sidebar to continue.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    # ──────────── HEADER ────────────
    patient_label = ""
    if p_name:
        patient_label = f" · {p_name}"
        if p_age:
            patient_label += f", {p_age}"
        if p_sex != "—":
            patient_label += f", {p_sex}"

    st.markdown(f"""
    <div class="app-header">
        <div class="logo-icon">🩺</div>
        <div>
            <div class="app-name">MediAssist AI Pro{patient_label}</div>
            <div class="app-sub">Medical report analysis · Symptom checker · Medicine guidance · Health tracking</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ──────────── TABS ────────────
    tab_chat, tab_report, tab_symptoms, tab_vitals, tab_history = st.tabs([
        "💬 Chat Assistant",
        "📋 Report Analysis",
        "🔍 Symptom Checker",
        "❤️ Vitals Tracker",
        "📂 Session History",
    ])

    # ════════════════════════════════════════════
    # TAB 1 — CHAT ASSISTANT
    # ════════════════════════════════════════════
    with tab_chat:
        left, right = st.columns([1.6, 1.0], gap="large")

        with left:
            st.markdown('<div class="med-card">', unsafe_allow_html=True)
            st.markdown('<div class="sec-title">💬 Conversation</div>', unsafe_allow_html=True)

            # Chat history
            st.markdown('<div class="chat-scroll">', unsafe_allow_html=True)
            if not st.session_state.messages:
                st.markdown("""
                <div class="empty-state">
                    <div class="es-icon">🩺</div>
                    <p>Ask a medical question, upload a report in the Report tab, or use the Symptom Checker.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                for msg in st.session_state.messages:
                    render_bubble(msg["role"], msg["content"], msg.get("ts", ""))
            st.markdown('</div>', unsafe_allow_html=True)

            # Input row
            st.markdown("---")
            user_text = st.text_area(
                "Your message",
                placeholder="Ask about your report, symptoms, health terms, medications…",
                height=90,
                key="chat_input",
                label_visibility="collapsed",
            )

            btn_cols = st.columns([2, 2, 2, 1])
            with btn_cols[0]:
                send_clicked = st.button("➤ Send Message", use_container_width=True, key="send_btn")
            with btn_cols[1]:
                med_clicked  = st.button("💊 Medicine Info", use_container_width=True, key="med_btn")
            with btn_cols[2]:
                sum_clicked  = st.button("📝 Session Summary", use_container_width=True, key="sum_btn")
            with btn_cols[3]:
                clr_clicked  = st.button("🗑️", use_container_width=True, key="clr_chat")

            st.markdown("</div>", unsafe_allow_html=True)

        # Right: quick context panel
        with right:
            st.markdown('<div class="med-card">', unsafe_allow_html=True)
            st.markdown('<div class="sec-title">📊 Context Panel</div>', unsafe_allow_html=True)

            # Report snippet
            if st.session_state.report_summary:
                st.markdown('<span class="tag-pill green">✓ Report Loaded</span>', unsafe_allow_html=True)
                with st.expander("View Report Summary", expanded=False):
                    st.markdown(f'<div class="report-box">{st.session_state.report_summary[:800]}{"…" if len(st.session_state.report_summary) > 800 else ""}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="tag-pill warn">No Report</span>', unsafe_allow_html=True)
                st.caption("Upload a report in the Report Analysis tab to give context to the AI.")

            st.markdown("---")

            # Patient context
            if p_cond:
                st.markdown("**Known Conditions**")
                for c in [x.strip() for x in p_cond.replace(",", "\n").split("\n") if x.strip()]:
                    st.markdown(f'<span class="tag-pill red">⚠ {c}</span>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

            # Vitals snapshot
            vitals_filled = {k: v for k, v in st.session_state.vitals.items() if v}
            if vitals_filled:
                st.markdown("**Vitals Snapshot**")
                vital_labels = {
                    "bp_systolic": "BP Sys.", "bp_diastolic": "BP Dia.",
                    "heart_rate": "HR (bpm)", "temperature": "Temp °C",
                    "spo2": "SpO₂ %", "weight": "Weight kg", "height": "Height cm"
                }
                for k, v in vitals_filled.items():
                    cls = classify_vital(k, v)
                    colors = {"normal": "var(--accent-3)", "warn": "var(--accent-warn)", "danger": "var(--accent-danger)"}
                    st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid var(--border);">
                        <span style="font-size:0.83rem;color:var(--text-muted);">{vital_labels.get(k, k)}</span>
                        <span style="font-size:0.9rem;font-weight:600;color:{colors[cls]};">{v}</span>
                    </div>
                    """, unsafe_allow_html=True)

            # Quick prompts
            st.markdown("---")
            st.markdown("**Quick Actions**")
            qp_cols = st.columns(2)
            with qp_cols[0]:
                if st.button("🔬 Explain Tests", use_container_width=True):
                    st.session_state["inject_prompt"] = "Can you explain the tests in my medical report in simple language?"
                if st.button("💊 Common Meds", use_container_width=True):
                    st.session_state["inject_prompt"] = "What are common medications for the conditions found in my report?"
            with qp_cols[1]:
                if st.button("🍎 Diet Tips", use_container_width=True):
                    st.session_state["inject_prompt"] = "What dietary changes would be beneficial based on my report?"
                if st.button("🏃 Exercise", use_container_width=True):
                    st.session_state["inject_prompt"] = "What exercise recommendations are appropriate for my condition?"

            st.markdown("</div>", unsafe_allow_html=True)

        # ── Process injected quick prompts ──
        if "inject_prompt" in st.session_state and st.session_state.inject_prompt:
            inj = st.session_state.inject_prompt
            st.session_state.inject_prompt = ""
            with st.spinner("🤔 Thinking…"):
                try:
                    msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
                    if st.session_state.report_summary:
                        msgs.append({"role": "system", "content": f"Report:\n{st.session_state.report_summary}"})
                    if p_cond:
                        msgs.append({"role": "system", "content": f"Patient known conditions: {p_cond}"})
                    msgs.extend(st.session_state.messages[-8:])
                    msgs.append({"role": "user", "content": inj})
                    reply = groq_text(client, text_model, msgs, max_tokens=950)
                    st.session_state.messages.append({"role": "user", "content": inj, "ts": ts_now()})
                    st.session_state.messages.append({"role": "assistant", "content": reply, "ts": ts_now()})
                except Exception as e:
                    st.error(f"Error: {e}")
            st.rerun()

        # ── Process send ──
        if clr_clicked:
            st.session_state.messages = []
            st.rerun()

        if send_clicked and user_text.strip():
            if is_urgent(user_text):
                urgent_reply = (
                    "⚠️ **URGENT: Your symptoms may require immediate medical attention.**\n\n"
                    "Please call emergency services or go to the nearest emergency room immediately if you are experiencing:\n"
                    "- Chest pain or pressure\n- Difficulty breathing\n- Signs of stroke (face drooping, arm weakness, speech difficulty)\n- Severe bleeding\n- Loss of consciousness\n\n"
                    "Do NOT wait. Please seek immediate professional medical care.\n\n"
                    "⚕️ Note: I am an AI assistant, not a licensed doctor. Please consult a qualified healthcare professional for medical advice."
                )
                st.session_state.messages.append({"role": "user", "content": user_text, "ts": ts_now()})
                st.session_state.messages.append({"role": "warn", "content": urgent_reply, "ts": ts_now()})
                st.rerun()

            with st.spinner("🤔 Thinking…"):
                try:
                    msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
                    if st.session_state.report_summary:
                        msgs.append({"role": "system", "content": f"Medical report context:\n{st.session_state.report_summary}"})
                    if p_cond:
                        msgs.append({"role": "system", "content": f"Patient known conditions: {p_cond}"})
                    if p_age and p_sex != "—":
                        msgs.append({"role": "system", "content": f"Patient: {p_age} years old, {p_sex}"})
                    msgs.extend(st.session_state.messages[-12:])
                    msgs.append({"role": "user", "content": user_text})
                    reply = groq_text(client, text_model, msgs, max_tokens=1000)
                    st.session_state.messages.append({"role": "user",      "content": user_text, "ts": ts_now()})
                    st.session_state.messages.append({"role": "assistant", "content": reply,     "ts": ts_now()})
                except Exception as e:
                    st.error(f"Error: {e}")
            st.rerun()

        if med_clicked:
            src = (user_text.strip() or st.session_state.report_summary.strip() or "general health query")
            with st.spinner("💊 Getting medicine information…"):
                try:
                    msgs = [
                        {"role": "system", "content": MEDICINE_PROMPT},
                        {"role": "user",   "content": src},
                    ]
                    if st.session_state.report_summary:
                        msgs.insert(1, {"role": "system", "content": f"Report context:\n{st.session_state.report_summary}"})
                    reply = groq_text(client, text_model, msgs, max_tokens=900)
                    st.session_state.messages.append({"role": "user",      "content": f"💊 Medicine info: {src[:120]}", "ts": ts_now()})
                    st.session_state.messages.append({"role": "assistant", "content": reply, "ts": ts_now()})
                except Exception as e:
                    st.error(f"Error: {e}")
            st.rerun()

        if sum_clicked and st.session_state.messages:
            history_text = "\n".join([f"[{m['role'].upper()}]: {m['content']}" for m in st.session_state.messages])
            with st.spinner("📝 Generating session summary…"):
                try:
                    msgs = [
                        {"role": "system", "content": HEALTH_SUMMARY_PROMPT},
                        {"role": "user",   "content": f"Conversation:\n{history_text}"},
                    ]
                    reply = groq_text(client, text_model, msgs, max_tokens=700)
                    st.session_state.messages.append({"role": "user",      "content": "📝 Generate session summary", "ts": ts_now()})
                    st.session_state.messages.append({"role": "assistant", "content": reply, "ts": ts_now()})
                except Exception as e:
                    st.error(f"Error: {e}")
            st.rerun()

    # ════════════════════════════════════════════
    # TAB 2 — REPORT ANALYSIS
    # ════════════════════════════════════════════
    with tab_report:
        col_up, col_res = st.columns([1, 1.4], gap="large")

        with col_up:
            st.markdown('<div class="med-card">', unsafe_allow_html=True)
            st.markdown('<div class="sec-title">📋 Upload Report</div>', unsafe_allow_html=True)

            uploaded_file = st.file_uploader(
                "Drop medical report image (JPG/PNG)",
                type=["jpg", "jpeg", "png"],
                label_visibility="collapsed",
                key="file_uploader",
            )

            if uploaded_file:
                analyze_btn = st.button("🔍 Analyze Report", use_container_width=True, key="analyze_btn")

                if (uploaded_file.name != st.session_state.uploaded_name) or analyze_btn:
                    st.session_state.uploaded_name = uploaded_file.name
                    raw_bytes = uploaded_file.getvalue()
                    resized   = resize_image_bytes(raw_bytes)
                    st.session_state.uploaded_preview = resized

                    with st.spinner("🔍 AI analyzing your report…"):
                        try:
                            report_text = analyze_image(client, vision_model, resized)
                            st.session_state.report_summary = report_text
                            st.success("✅ Report analyzed successfully!")
                        except Exception as e:
                            st.error(f"Analysis error: {e}")
                            st.session_state.report_summary = f"Error: {e}"
                    st.rerun()

            if st.session_state.uploaded_preview:
                st.markdown("**Uploaded Report**")
                st.image(st.session_state.uploaded_preview, use_container_width=True)
                st.caption(f"📄 {st.session_state.uploaded_name}")
            else:
                st.markdown("""
                <div class="empty-state">
                    <div class="es-icon">📋</div>
                    <p>Upload a JPG or PNG of your medical report (blood tests, X-ray reports, lab results, etc.)</p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        with col_res:
            st.markdown('<div class="med-card">', unsafe_allow_html=True)
            st.markdown('<div class="sec-title">🔬 Extracted Clinical Data</div>', unsafe_allow_html=True)

            if st.session_state.report_summary:
                st.markdown(f'<div class="report-box">{st.session_state.report_summary}</div>', unsafe_allow_html=True)

                st.markdown("---")

                # Ask specific question about report
                report_q = st.text_input("Ask a specific question about this report…", key="report_q")
                if st.button("Ask About Report ➤", key="report_q_btn") and report_q.strip():
                    with st.spinner("Analyzing…"):
                        try:
                            msgs = [
                                {"role": "system", "content": SYSTEM_PROMPT},
                                {"role": "system", "content": f"Report context:\n{st.session_state.report_summary}"},
                                {"role": "user",   "content": report_q},
                            ]
                            reply = groq_text(client, text_model, msgs, max_tokens=800)
                            st.session_state.messages.append({"role": "user",      "content": f"📋 About report: {report_q}", "ts": ts_now()})
                            st.session_state.messages.append({"role": "assistant", "content": reply, "ts": ts_now()})
                            st.success("Answer added to Chat tab ✓")
                        except Exception as e:
                            st.error(f"Error: {e}")

                # Export
                st.markdown("---")
                export_text = (
                    "═══════════════════════════════════════\n"
                    "       MediAssist AI Pro — Session Report\n"
                    f"       Generated: {date_now()}\n"
                    "═══════════════════════════════════════\n\n"
                    f"DISCLAIMER: {MEDICAL_DISCLAIMER}\n\n"
                    "PATIENT INFO\n" + "─"*40 + "\n"
                    f"Name: {p_name or 'Not provided'}\n"
                    f"Age: {p_age or 'Not provided'}\n"
                    f"Sex: {p_sex if p_sex != '—' else 'Not provided'}\n"
                    f"Known Conditions: {p_cond or 'None noted'}\n\n"
                    "EXTRACTED REPORT DATA\n" + "─"*40 + "\n"
                    f"{st.session_state.report_summary}\n\n"
                    "CONVERSATION HISTORY\n" + "─"*40 + "\n"
                )
                for msg in st.session_state.messages:
                    export_text += f"\n[{msg['role'].upper()} — {msg.get('ts', '')}]\n{msg['content']}\n"

                st.download_button(
                    "📥 Download Full Report (TXT)",
                    data=export_text,
                    file_name=f"mediassist_report_{datetime.date.today()}.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
            else:
                st.markdown("""
                <div class="empty-state">
                    <div class="es-icon">🔬</div>
                    <p>Upload and analyze a report to see extracted clinical data here.</p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

    # ════════════════════════════════════════════
    # TAB 3 — SYMPTOM CHECKER
    # ════════════════════════════════════════════
    with tab_symptoms:
        st.markdown('<div class="med-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">🔍 Symptom Checker</div>', unsafe_allow_html=True)
        st.caption("Select symptoms or describe them in text. This is NOT a diagnostic tool.")

        # Common symptom quick-select
        COMMON_SYMPTOMS = [
            "Fever", "Headache", "Cough", "Sore Throat", "Fatigue",
            "Nausea", "Vomiting", "Diarrhea", "Abdominal Pain", "Back Pain",
            "Chest Pain", "Shortness of Breath", "Dizziness", "Rash",
            "Joint Pain", "Muscle Pain", "Runny Nose", "Loss of Appetite",
            "Swelling", "Palpitations", "Insomnia", "Anxiety",
        ]

        st.markdown("**Quick Select Common Symptoms:**")
        cols_sym = st.columns(4)
        for i, sym in enumerate(COMMON_SYMPTOMS):
            with cols_sym[i % 4]:
                checked = st.checkbox(sym, key=f"sym_{sym}", value=sym in st.session_state.selected_symptoms)
                if checked and sym not in st.session_state.selected_symptoms:
                    st.session_state.selected_symptoms.append(sym)
                elif not checked and sym in st.session_state.selected_symptoms:
                    st.session_state.selected_symptoms.remove(sym)

        st.markdown("---")
        extra_symptoms = st.text_area(
            "Describe additional symptoms or details:",
            placeholder="e.g. Fever for 3 days, 38.5°C, worse at night, with dry cough…",
            height=90,
            key="extra_sym",
        )

        # Duration & severity
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            duration = st.selectbox("Duration", ["Just started", "1-3 days", "4-7 days", "1-2 weeks", "2+ weeks"], key="sym_dur")
        with sc2:
            severity = st.selectbox("Severity", ["Mild", "Moderate", "Severe", "Very Severe"], key="sym_sev")
        with sc3:
            getting  = st.selectbox("Trend", ["Getting worse", "Same", "Getting better"], key="sym_trend")

        check_btn = st.button("🔍 Check Symptoms", use_container_width=True, key="check_sym_btn")

        if check_btn:
            selected_str = ", ".join(st.session_state.selected_symptoms) if st.session_state.selected_symptoms else ""
            all_symptoms = selected_str
            if extra_symptoms.strip():
                all_symptoms += (", " if all_symptoms else "") + extra_symptoms.strip()

            if not all_symptoms:
                st.warning("Please select or describe at least one symptom.")
            else:
                patient_context = ""
                if p_age: patient_context += f"Age: {p_age}. "
                if p_sex != "—": patient_context += f"Sex: {p_sex}. "
                if p_cond: patient_context += f"Known conditions: {p_cond}. "

                query = (
                    f"Patient symptoms: {all_symptoms}. "
                    f"Duration: {duration}. Severity: {severity}. Trend: {getting}. "
                    f"{patient_context}"
                )

                with st.spinner("🔍 Analyzing symptoms…"):
                    try:
                        msgs = [
                            {"role": "system", "content": SYMPTOM_CHECKER_PROMPT},
                            {"role": "user",   "content": query},
                        ]
                        result = groq_text(client, text_model, msgs, max_tokens=1100)
                        st.session_state.symptom_result = result
                        st.session_state.messages.append({"role": "user",      "content": f"🔍 Symptom check: {all_symptoms}", "ts": ts_now()})
                        st.session_state.messages.append({"role": "assistant", "content": result, "ts": ts_now()})
                    except Exception as e:
                        st.error(f"Error: {e}")

        if st.session_state.symptom_result:
            st.markdown("---")
            st.markdown("**Assessment Result:**")
            st.markdown(f'<div class="bubble-ai">{st.session_state.symptom_result}</div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # ════════════════════════════════════════════
    # TAB 4 — VITALS TRACKER
    # ════════════════════════════════════════════
    with tab_vitals:
        st.markdown('<div class="med-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">❤️ Vitals & Health Metrics</div>', unsafe_allow_html=True)

        vc1, vc2, vc3, vc4 = st.columns(4)
        vitals_map = [
            ("bp_systolic",  "Blood Pressure (Systolic mmHg)",  "e.g. 120",  vc1),
            ("bp_diastolic", "Blood Pressure (Diastolic mmHg)", "e.g. 80",   vc2),
            ("heart_rate",   "Heart Rate (bpm)",                "e.g. 72",   vc3),
            ("temperature",  "Temperature (°C)",                "e.g. 36.6", vc4),
        ]
        for key, label, ph, col in vitals_map:
            with col:
                val = st.text_input(label, placeholder=ph, value=st.session_state.vitals[key], key=f"vi_{key}")
                st.session_state.vitals[key] = val

        vc5, vc6, vc7, _ = st.columns(4)
        vitals_map2 = [
            ("spo2",   "SpO₂ (%)",     "e.g. 98", vc5),
            ("weight", "Weight (kg)",  "e.g. 70",  vc6),
            ("height", "Height (cm)",  "e.g. 175", vc7),
        ]
        for key, label, ph, col in vitals_map2:
            with col:
                val = st.text_input(label, placeholder=ph, value=st.session_state.vitals[key], key=f"vi_{key}")
                st.session_state.vitals[key] = val

        # Visual display
        filled = {k: v for k, v in st.session_state.vitals.items() if v}
        if filled:
            st.markdown("---")
            st.markdown("**Vitals Overview**")
            vital_labels = {
                "bp_systolic": "BP Systolic", "bp_diastolic": "BP Diastolic",
                "heart_rate": "Heart Rate", "temperature": "Temperature",
                "spo2": "SpO₂", "weight": "Weight", "height": "Height"
            }
            vital_units = {
                "bp_systolic": "mmHg", "bp_diastolic": "mmHg",
                "heart_rate": "bpm", "temperature": "°C",
                "spo2": "%", "weight": "kg", "height": "cm"
            }
            cols_v = st.columns(len(filled))
            for i, (k, v) in enumerate(filled.items()):
                cls = classify_vital(k, v)
                status = {"normal": "✅ Normal", "warn": "⚠️ Borderline", "danger": "🔴 Abnormal"}[cls]
                with cols_v[i]:
                    st.metric(
                        label=vital_labels.get(k, k),
                        value=f"{v} {vital_units.get(k,'')}",
                        delta=status,
                    )

            # BMI calc
            if st.session_state.vitals["weight"] and st.session_state.vitals["height"]:
                try:
                    w = float(st.session_state.vitals["weight"])
                    h = float(st.session_state.vitals["height"]) / 100
                    bmi = w / (h * h)
                    if bmi < 18.5: bmi_cat, bmi_cls = "Underweight", "warn"
                    elif bmi < 25: bmi_cat, bmi_cls = "Normal Weight", "normal"
                    elif bmi < 30: bmi_cat, bmi_cls = "Overweight", "warn"
                    else:          bmi_cat, bmi_cls = "Obese", "danger"

                    st.markdown("---")
                    bmi_cols = st.columns([1, 2])
                    with bmi_cols[0]:
                        st.metric("BMI", f"{bmi:.1f}", bmi_cat)
                    with bmi_cols[1]:
                        st.markdown(f"""
                        <div class="vital-box {bmi_cls}" style="text-align:left;padding:16px;">
                            <div style="font-size:0.8rem;color:var(--text-muted);margin-bottom:6px;">BMI INTERPRETATION</div>
                            <div class="v-val">{bmi:.1f} — {bmi_cat}</div>
                            <div style="font-size:0.8rem;color:var(--text-muted);margin-top:4px;">
                                Normal range: 18.5 – 24.9
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                except:
                    pass

            # Ask AI about vitals
            st.markdown("---")
            if st.button("🤖 Ask AI About My Vitals", use_container_width=True, key="vitals_ai"):
                vitals_str = ", ".join([f"{vital_labels.get(k,k)}: {v} {vital_units.get(k,'')}" for k,v in filled.items()])
                query = f"Please review these vitals and let me know if anything looks concerning: {vitals_str}"
                if p_age: query += f" Patient age: {p_age}."
                if p_sex != "—": query += f" Sex: {p_sex}."
                if p_cond: query += f" Known conditions: {p_cond}."

                with st.spinner("Analyzing vitals…"):
                    try:
                        msgs = [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user",   "content": query},
                        ]
                        reply = groq_text(client, text_model, msgs, max_tokens=700)
                        st.session_state.messages.append({"role": "user",      "content": query[:120], "ts": ts_now()})
                        st.session_state.messages.append({"role": "assistant", "content": reply, "ts": ts_now()})
                        st.success("Analysis added to Chat tab ✓")
                    except Exception as e:
                        st.error(f"Error: {e}")

        else:
            st.markdown("""
            <div class="empty-state">
                <div class="es-icon">❤️</div>
                <p>Enter your vitals above to see an overview and get AI analysis.</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # ════════════════════════════════════════════
    # TAB 5 — SESSION HISTORY
    # ════════════════════════════════════════════
    with tab_history:
        st.markdown('<div class="med-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">📂 Session History</div>', unsafe_allow_html=True)

        if not st.session_state.session_history:
            st.markdown("""
            <div class="empty-state">
                <div class="es-icon">📂</div>
                <p>No saved sessions yet. Click "Save Session" in the sidebar to save your current session.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Summary stats
            sc1, sc2, sc3, sc4 = st.columns(4)
            with sc1: st.metric("Total Sessions", len(st.session_state.session_history))
            with sc2: st.metric("Total Messages", sum(len(s["messages"]) for s in st.session_state.session_history))
            with sc3: st.metric("Reports Analyzed", sum(1 for s in st.session_state.session_history if s["report_summary"]))
            with sc4: st.metric("Current Session Msgs", len(st.session_state.messages))

            st.markdown("---")

            for i, session in enumerate(st.session_state.session_history):
                with st.expander(f"📅 Session {i+1} — {session['date']} | {len(session['messages'])} messages", expanded=(i == 0)):
                    if session.get("uploaded_name"):
                        st.markdown(f'<span class="tag-pill green">📋 {session["uploaded_name"]}</span>', unsafe_allow_html=True)

                    if session.get("report_summary"):
                        st.markdown("**Report Summary:**")
                        st.markdown(f'<div class="report-box">{session["report_summary"][:400]}…</div>', unsafe_allow_html=True)

                    st.markdown("**Conversation:**")
                    for msg in session["messages"][-6:]:
                        render_bubble(msg["role"], msg["content"][:300] + ("…" if len(msg["content"]) > 300 else ""), msg.get("ts", ""))

                    rcol1, rcol2 = st.columns(2)
                    with rcol1:
                        if st.button(f"📂 Restore Session {i+1}", key=f"restore_{i}", use_container_width=True):
                            st.session_state.messages      = session["messages"].copy()
                            st.session_state.report_summary = session["report_summary"]
                            st.session_state.vitals         = session.get("vitals", st.session_state.vitals)
                            st.success(f"Session {i+1} restored!")
                            st.rerun()
                    with rcol2:
                        # Export this session
                        export = "\n".join([f"[{m['role'].upper()}]: {m['content']}" for m in session["messages"]])
                        st.download_button(
                            f"📥 Export Session {i+1}",
                            data=export,
                            file_name=f"session_{i+1}_{datetime.date.today()}.txt",
                            mime="text/plain",
                            use_container_width=True,
                            key=f"dl_{i}",
                        )

            st.markdown("---")
            if st.button("🗑️ Clear All History", use_container_width=True):
                st.session_state.session_history = []
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # ──────────── FOOTER ────────────
    st.markdown("---")
    st.markdown("""
    <div style="text-align:center;padding:8px 0 4px;color:var(--text-muted);font-size:0.8rem;">
        🩺 <strong style="color:var(--accent);">MediAssist AI Pro v3.0</strong> · 
        Powered by Groq + LLaMA · 
        For informational purposes only · 
        Not a substitute for professional medical advice
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
