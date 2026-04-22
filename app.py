import streamlit as st
import os
import base64
import io
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
# CUSTOM CSS – REFINED COLOR SCHEME & LAYOUT
# =========================================================
st.markdown(
    """
    <style>
        /* Global styles */
        .main {
            background: #F4F7FB;
        }

        h1, h2, h3, h4, h5, h6 {
            color: #1E293B !important;
            font-weight: 600;
        }

        /* Cards */
        .soft-card {
            background: #FFFFFF;
            border-radius: 24px;
            padding: 24px;
            box-shadow: 0 8px 20px rgba(0, 20, 30, 0.06);
            margin-bottom: 24px;
            border: 1px solid #E9EEF2;
            transition: all 0.2s ease;
        }

        .soft-card:hover {
            box-shadow: 0 12px 28px rgba(0, 40, 60, 0.08);
        }

        .sidebar-card {
            background: #FFFFFF;
            border-radius: 20px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid #E2E8F0;
            box-shadow: 0 4px 8px rgba(0,0,0,0.02);
        }

        /* Disclaimer box */
        .disclaimer-box {
            background: #FFF5F5;
            border-left: 6px solid #E53E3E;
            color: #742A2A;
            padding: 16px 18px;
            border-radius: 16px;
            font-size: 0.9rem;
            line-height: 1.6;
            margin-top: 8px;
        }

        /* Chat bubbles */
        .chat-user {
            background: linear-gradient(145deg, #0EA5E9, #3B82F6);
            color: white;
            padding: 14px 18px;
            border-radius: 20px 20px 6px 20px;
            margin: 10px 0 14px auto;
            width: fit-content;
            max-width: 85%;
            box-shadow: 0 8px 16px -6px rgba(14, 165, 233, 0.25);
            font-size: 0.98rem;
            line-height: 1.5;
        }

        .chat-ai {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-left: 5px solid #8B5CF6;
            color: #0F172A;
            padding: 14px 18px;
            border-radius: 20px 20px 20px 6px;
            margin: 10px 0 14px 0;
            max-width: 90%;
            box-shadow: 0 4px 10px -4px rgba(0, 0, 0, 0.02);
            font-size: 0.98rem;
            line-height: 1.6;
        }

        /* Typography */
        .section-title {
            font-size: 1.25rem;
            font-weight: 700;
            color: #0F172A;
            margin-bottom: 1.2rem;
            letter-spacing: -0.01em;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .tiny-muted {
            font-size: 0.85rem;
            color: #64748B;
        }

        .upload-hint {
            color: #475569;
            font-size: 0.9rem;
            margin-top: 6px;
            margin-bottom: 8px;
        }

        /* Buttons */
        .stButton > button {
            background: #0EA5E9;
            color: white;
            border: none;
            border-radius: 14px;
            padding: 0.6rem 1.2rem;
            font-weight: 600;
            font-size: 0.95rem;
            transition: all 0.2s;
            box-shadow: 0 4px 8px -2px rgba(14, 165, 233, 0.2);
            border: 1px solid rgba(255,255,255,0.1);
        }

        .stButton > button:hover {
            background: #0284C7;
            transform: translateY(-1px);
            box-shadow: 0 8px 14px -4px rgba(14, 165, 233, 0.3);
            color: white;
            border-color: rgba(255,255,255,0.2);
        }

        .stDownloadButton > button {
            border-radius: 14px;
            font-weight: 600;
            background: #FFFFFF;
            color: #1E293B;
            border: 1px solid #CBD5E1;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        }

        .stDownloadButton > button:hover {
            background: #F8FAFC;
            border-color: #94A3B8;
            color: #0F172A;
        }

        /* Report display box */
        .report-box {
            white-space: pre-wrap;
            background: #F9FCFE;
            border: 1px solid #DDE7F0;
            border-radius: 20px;
            padding: 20px;
            min-height: 240px;
            line-height: 1.7;
            font-size: 0.95rem;
            color: #1E293B;
            overflow-x: auto;
        }

        /* Upload area custom styling */
        .upload-container {
            background: #F8FAFC;
            border-radius: 20px;
            padding: 16px 18px;
            border: 1.5px dashed #94A3B8;
            margin-bottom: 10px;
            transition: border-color 0.2s;
        }

        .upload-container:hover {
            border-color: #0EA5E9;
        }

        /* File uploader label */
        div[data-testid="stFileUploader"] > section {
            border-radius: 20px;
        }

        div[data-testid="stFileUploader"] button {
            border-radius: 12px !important;
            background: white !important;
            border: 1px solid #CBD5E1 !important;
            color: #1E293B !important;
            font-weight: 500;
        }

        /* Image preview */
        .image-preview-card {
            border-radius: 20px;
            overflow: hidden;
            border: 1px solid #E2E8F0;
            margin-top: 16px;
            margin-bottom: 16px;
            box-shadow: 0 6px 12px -6px rgba(0,0,0,0.05);
        }

        /* Export section */
        .export-section {
            background: #F1F9FE;
            border-radius: 18px;
            padding: 18px;
            margin-top: 24px;
        }

        /* Chat history container */
        .chat-history {
            max-height: 500px;
            overflow-y: auto;
            padding-right: 8px;
            margin-bottom: 16px;
        }

        /* Input row at bottom */
        .chat-input-container {
            background: #FFFFFF;
            border-radius: 20px;
            padding: 12px 12px 12px 16px;
            border: 1px solid #DDE7F0;
            box-shadow: 0 4px 8px -2px rgba(0,0,0,0.02);
            margin-top: 8px;
        }

        /* Placeholder styling */
        .empty-state {
            background: #F8FAFC;
            border: 1.5px dashed #94A3B8;
            border-radius: 24px;
            padding: 32px 24px;
            color: #475569;
            text-align: center;
            margin: 20px 0;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# PROMPTS
# =========================================================
MEDICAL_DISCLAIMER = """
MediAssist AI Pro is an informational tool only. It is not a licensed healthcare provider.
It cannot diagnose illnesses, prescribe medication, or replace a doctor.
For urgent, severe, or worsening symptoms, seek immediate medical care.
"""

SYSTEM_PROMPT = """
You are MediAssist AI Pro, a professional medical assistant.

Your scope:
- Explain medical terms
- Summarize medical reports
- Answer health and wellness questions
- Give safe, conservative, informational guidance only

Hard rules:
1. Never diagnose.
2. Never claim certainty when information is incomplete.
3. Never present yourself as a doctor.
4. If symptoms sound urgent, tell the user to seek immediate care.
5. If the user asks for medicines, provide only cautious informational suggestions, clearly say they must verify with a doctor/pharmacist, and do not give unsafe or high-risk recommendations.
6. Be calm, respectful, and concise.
7. End every answer with:
   "Note: I am an AI assistant, not a licensed doctor. Please consult a qualified healthcare professional for medical advice."
"""

VISION_PROMPT = """
You are MediAssist AI Pro, a medical report image analyzer.

Task:
- Read the uploaded medical report image carefully.
- Extract visible patient details, test names, values, units, and reference ranges.
- Identify values that appear high, low, or flagged if visible.
- Summarize findings clearly in simple language.
- If text is blurry or unreadable, say so.
- Do not diagnose.
- Do not invent missing values.

End with:
"Note: I am an AI assistant, not a doctor. Please consult a qualified healthcare professional."
"""

MEDICINE_PROMPT = """
You are MediAssist AI Pro.

The user wants safe informational medicine guidance based on their message and/or report summary.
Rules:
- Do NOT diagnose.
- Do NOT prescribe.
- Do NOT claim any medicine is safe for every patient.
- Give only cautious, general, non-personalized informational suggestions.
- Prefer supportive care, red-flag warnings, and advice to consult a doctor/pharmacist.
- If the user mentions a condition that could be serious, advise urgent medical review.
- If medication names are mentioned, explain them in a neutral way and mention common cautions only at a high level.
- End with:
  "Note: I am an AI assistant, not a licensed doctor. Please consult a qualified healthcare professional for medical advice."
"""

# =========================================================
# HELPERS
# =========================================================
def get_groq_client():
    api_key = st.secrets.get("GROQ_API_KEY", "") or os.getenv("GROQ_API_KEY", "")
    if not api_key:
        st.error("GROQ_API_KEY is missing. Add it in Streamlit secrets.")
        st.stop()
    return Groq(api_key=api_key)

def get_models():
    text_model = st.secrets.get("GROQ_TEXT_MODEL", os.getenv("GROQ_TEXT_MODEL", "llama-3.3-70b-versatile"))
    vision_model = st.secrets.get(
        "GROQ_VISION_MODEL",
        os.getenv("GROQ_VISION_MODEL", "meta-llama/llama-4-maverick-17b-128e-instruct"),
    )
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

def is_urgent(text: str) -> bool:
    text = text.lower()
    flags = [
        "chest pain", "shortness of breath", "difficulty breathing", "trouble breathing",
        "fainting", "unconscious", "severe bleeding", "stroke", "one sided weakness",
        "suicidal", "seizure", "blue lips", "confusion", "severe headache"
    ]
    return any(flag in text for flag in flags)

def render_message(role: str, content: str):
    if role == "user":
        st.markdown(f'<div class="chat-user">{content}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-ai">{content}</div>', unsafe_allow_html=True)

def groq_text(client, model, messages, max_tokens=900):
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.35,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content.strip()

def analyze_image(client, vision_model, image_bytes: bytes) -> str:
    data_url = to_data_url(image_bytes)
    resp = client.chat.completions.create(
        model=vision_model,
        temperature=0.2,
        max_tokens=1200,
        messages=[
            {"role": "system", "content": VISION_PROMPT},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Analyze this medical report image and extract all visible report information in a clean, structured format."
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": data_url}
                    }
                ]
            }
        ],
    )
    return resp.choices[0].message.content.strip()

def build_chat_prompt(report_summary: str, user_message: str):
    prompt = SYSTEM_PROMPT
    context = []
    if report_summary:
        context.append(f"Medical report summary:\n{report_summary}")
    if user_message:
        context.append(f"User request:\n{user_message}")
    return prompt + "\n\n" + "\n\n".join(context)

def build_medicine_prompt(report_summary: str, user_message: str):
    sections = [MEDICINE_PROMPT]
    if report_summary:
        sections.append(f"Report summary:\n{report_summary}")
    if user_message:
        sections.append(f"User message:\n{user_message}")
    return "\n\n".join(sections)

def init_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "report_summary" not in st.session_state:
        st.session_state.report_summary = ""
    if "uploaded_name" not in st.session_state:
        st.session_state.uploaded_name = ""
    if "uploaded_preview" not in st.session_state:
        st.session_state.uploaded_preview = None
    if "engine_ready" not in st.session_state:
        st.session_state.engine_ready = False
    if "last_action" not in st.session_state:
        st.session_state.last_action = ""

# =========================================================
# MAIN APP
# =========================================================
def main():
    init_state()

    client = get_groq_client()
    text_model, vision_model = get_models()

    # ---------- SIDEBAR ----------
    with st.sidebar:
        st.markdown("## 🩺 MediAssist AI Pro")
        st.markdown("#### Intelligent Medical Assistant")

        st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
        st.markdown("### ⚙️ Model Configuration")
        text_model = st.text_input("Text model", value=text_model, help="Groq text model for chat")
        vision_model = st.text_input("Vision model", value=vision_model, help="Groq vision model for report analysis")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
        st.markdown("### ⚠️ Safety Disclaimer")
        st.markdown(f'<div class="disclaimer-box">{MEDICAL_DISCLAIMER}</div>', unsafe_allow_html=True)
        safety_ok = st.checkbox("I understand and accept the disclaimer", value=False)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
        if st.button("🗑️ Clear conversation & report", use_container_width=True):
            st.session_state.messages = []
            st.session_state.report_summary = ""
            st.session_state.uploaded_name = ""
            st.session_state.uploaded_preview = None
            st.session_state.last_action = ""
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")
        st.caption("v2.1 · Made with ❤️ for better care")

    if not safety_ok:
        st.info("👈 Please accept the disclaimer in the sidebar to continue.")
        st.stop()

    # ---------- HEADER ----------
    col_title, _ = st.columns([6, 1])
    with col_title:
        st.markdown("# 🩺 MediAssist AI Pro")
        st.markdown("##### Medical report analysis, safe Q&A, and medicine guidance — all in one place.")
    st.markdown("---")

    # ---------- MAIN LAYOUT ----------
    left, right = st.columns([1.5, 1.0], gap="large")

    # ========== LEFT COLUMN ==========
    with left:
        # ----- Upload Card (always at top) -----
        st.markdown('<div class="soft-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title"><span>📋 Upload Medical Report</span></div>', unsafe_allow_html=True)

        upload_col1, upload_col2 = st.columns([4, 1])
        with upload_col1:
            uploaded_file = st.file_uploader(
                "Drop your medical report image here (JPG, PNG)",
                type=["jpg", "jpeg", "png"],
                label_visibility="collapsed",
            )
        with upload_col2:
            st.markdown("<br>", unsafe_allow_html=True)  # spacer
            if st.button("📤 Analyze", use_container_width=True, key="analyze_btn"):
                if uploaded_file is not None:
                    st.session_state.last_action = "force_analyze"
                    st.rerun()
                else:
                    st.warning("Please upload an image first.")

        if uploaded_file is not None:
            if (uploaded_file.name != st.session_state.uploaded_name) or (st.session_state.last_action == "force_analyze"):
                st.session_state.uploaded_name = uploaded_file.name
                raw_bytes = uploaded_file.getvalue()
                resized_bytes = resize_image_bytes(raw_bytes)
                st.session_state.uploaded_preview = resized_bytes

                with st.spinner("🔍 Analyzing report image with AI..."):
                    try:
                        report_text = analyze_image(client, vision_model, resized_bytes)
                        st.session_state.report_summary = report_text
                        st.session_state.last_action = ""
                    except Exception as e:
                        st.session_state.report_summary = f"❌ Error analyzing image: {e}"
                        st.session_state.last_action = ""

                st.rerun()

        if st.session_state.uploaded_preview:
            st.markdown('<div class="image-preview-card">', unsafe_allow_html=True)
            st.image(st.session_state.uploaded_preview, caption="📸 Uploaded report preview", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<p class="tiny-muted">Report data extracted and available in right panel →</p>', unsafe_allow_html=True)
        else:
            st.info("👆 Upload a medical report image to begin.")

        st.markdown("</div>", unsafe_allow_html=True)  # end upload card

        # ----- Chat Card with History Above, Input Below -----
        st.markdown('<div class="soft-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title"><span>💬 Conversation</span></div>', unsafe_allow_html=True)

        # --- Chat History (scrollable) ---
        st.markdown('<div class="chat-history">', unsafe_allow_html=True)
        if not st.session_state.messages:
            st.info("No conversation yet. Ask a question or upload a report to start.")
        else:
            for msg in st.session_state.messages:
                render_message(msg["role"], msg["content"])
        st.markdown('</div>', unsafe_allow_html=True)  # end chat-history

        # --- Chat Input Row at Bottom ---
        st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([5.5, 1.2, 1.5])
        with col1:
            user_text = st.text_input(
                "Type your question here...",
                placeholder="Ask about the report, symptoms, tests, or health terms...",
                label_visibility="collapsed",
                key="chat_input",
            )
        with col2:
            send_clicked = st.button("Send ➤", use_container_width=True, key="send_btn")
        with col3:
            med_clicked = st.button("💊 Medicine", use_container_width=True, key="med_btn")
        st.markdown('</div>', unsafe_allow_html=True)  # end chat-input-container

        st.markdown("</div>", unsafe_allow_html=True)  # end chat card

        # Process send (after UI to avoid duplicate rendering issues)
        if (send_clicked or st.session_state.last_action == "send_pending") and user_text.strip():
            st.session_state.last_action = "send_pending"

            if is_urgent(user_text):
                urgent_reply = (
                    "⚠️ **Your message mentions symptoms that may need urgent medical attention.**\n\n"
                    "Please seek immediate care from a doctor or emergency service if symptoms are severe or worsening.\n\n"
                    "Note: I am an AI assistant, not a licensed doctor. Please consult a qualified healthcare professional for medical advice."
                )
                st.session_state.messages.append({"role": "user", "content": user_text})
                st.session_state.messages.append({"role": "assistant", "content": urgent_reply})
                st.session_state.last_action = ""
                st.rerun()

            with st.spinner("🤔 Thinking..."):
                try:
                    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                    if st.session_state.report_summary:
                        messages.append(
                            {
                                "role": "system",
                                "content": f"Relevant medical report summary:\n{st.session_state.report_summary}"
                            }
                        )
                    messages.extend(st.session_state.messages[-10:])
                    messages.append({"role": "user", "content": user_text})

                    response = groq_text(client, text_model, messages, max_tokens=950)
                    st.session_state.messages.append({"role": "user", "content": user_text})
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.session_state.messages.append({"role": "user", "content": user_text})
                    st.session_state.messages.append({"role": "assistant", "content": f"Error generating response: {e}"})

            st.session_state.last_action = ""
            st.rerun()

        if med_clicked:
            source_text = user_text.strip() or st.session_state.report_summary.strip()
            if not source_text:
                st.warning("Please add a text query or upload a report first.")
            else:
                with st.spinner("🧪 Preparing cautious medicine guidance..."):
                    try:
                        messages = [
                            {"role": "system", "content": build_medicine_prompt(st.session_state.report_summary, user_text)},
                            {"role": "user", "content": source_text},
                        ]
                        med_response = groq_text(client, text_model, messages, max_tokens=850)
                        st.session_state.messages.append(
                            {"role": "user", "content": f"💊 Medicine guidance request: {source_text}"}
                        )
                        st.session_state.messages.append(
                            {"role": "assistant", "content": med_response}
                        )
                    except Exception as e:
                        st.session_state.messages.append(
                            {"role": "assistant", "content": f"Error generating medicine guidance: {e}"}
                        )
                st.rerun()

    # ========== RIGHT COLUMN ==========
    with right:
        st.markdown('<div class="soft-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title"><span>🔬 Clinical Insights</span></div>', unsafe_allow_html=True)

        if st.session_state.report_summary:
            st.markdown("### 📄 Extracted Report Data")
            st.markdown(
                f'<div class="report-box">{st.session_state.report_summary}</div>',
                unsafe_allow_html=True
            )

            st.markdown('<div class="export-section">', unsafe_allow_html=True)
            st.markdown("#### 📎 Export Summary")
            export_text = (
                "MediAssist AI Pro Report Summary\n"
                "=====================================\n\n"
                f"{MEDICAL_DISCLAIMER}\n\n"
                "EXTRACTED REPORT DATA\n"
                "----------------------\n"
                f"{st.session_state.report_summary}\n\n"
                "CONVERSATION HISTORY\n"
                "--------------------\n"
            )
            for msg in st.session_state.messages:
                export_text += f"\n[{msg['role'].upper()}]\n{msg['content']}\n"

            st.download_button(
                label="📥 Download as TXT",
                data=export_text,
                file_name="mediassist_summary.txt",
                mime="text/plain",
                use_container_width=True,
            )
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown(
                """
                <div class="empty-state">
                    <span style="font-size: 2.5rem; display: block; margin-bottom: 10px;">📋</span>
                    <h4 style="color: #334155; margin-bottom: 8px;">No report analyzed yet</h4>
                    <p style="font-size: 0.95rem;">Upload a medical report in the left panel to generate structured clinical insights here.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)  # end insights card

    # Footer
    st.markdown("---")
    st.caption("🩺 MediAssist AI Pro · Informational only · Not a substitute for professional medical advice.")

if __name__ == "__main__":
    main()
