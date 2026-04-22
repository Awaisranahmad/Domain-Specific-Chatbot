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
# CUSTOM CSS
# =========================================================
st.markdown(
    """
    <style>
        .main {
            background: #F8FAFC;
        }

        h1, h2, h3, h4 {
            color: #1E3A8A !important;
        }

        .soft-card {
            background: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 20px;
            padding: 18px;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
            margin-bottom: 16px;
        }

        .sidebar-card {
            background: linear-gradient(180deg, #ffffff, #f8fbff);
            border: 1px solid #E5E7EB;
            border-radius: 18px;
            padding: 16px;
            margin-bottom: 14px;
        }

        .disclaimer-box {
            background: #FEF2F2;
            border-left: 4px solid #DC2626;
            color: #991B1B;
            padding: 12px 14px;
            border-radius: 10px;
            font-size: 0.92rem;
            line-height: 1.5;
        }

        .chat-user {
            background: linear-gradient(135deg, #2563EB, #7C3AED);
            color: white;
            padding: 14px 16px;
            border-radius: 18px 18px 6px 18px;
            margin: 10px 0 14px auto;
            width: fit-content;
            max-width: 88%;
            box-shadow: 0 8px 18px rgba(37, 99, 235, 0.18);
        }

        .chat-ai {
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-left: 5px solid #8B5CF6;
            color: #0F172A;
            padding: 14px 16px;
            border-radius: 18px 18px 18px 6px;
            margin: 10px 0 14px 0;
            max-width: 95%;
        }

        .tiny-muted {
            font-size: 0.88rem;
            color: #64748B;
        }

        .section-title {
            font-size: 1.05rem;
            font-weight: 700;
            color: #0F172A;
            margin-bottom: 0.75rem;
        }

        .upload-hint {
            color: #475569;
            font-size: 0.92rem;
            margin-top: -4px;
        }

        .stButton>button {
            background: #6D28D9;
            color: white;
            border: none;
            border-radius: 12px;
            padding: 0.55rem 1rem;
            font-weight: 600;
        }

        .stButton>button:hover {
            background: #5B21B6;
            color: white;
        }

        .stDownloadButton>button {
            border-radius: 12px;
            font-weight: 600;
        }

        .report-box {
            white-space: pre-wrap;
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 16px;
            padding: 14px;
            min-height: 280px;
            line-height: 1.65;
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
# APP
# =========================================================
def main():
    init_state()

    client = get_groq_client()
    text_model, vision_model = get_models()

    # SIDEBAR
    with st.sidebar:
        st.markdown("## 🩺 MediAssist AI Pro")
        st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
        st.markdown("### Models")
        text_model = st.text_input("Text model", value=text_model)
        vision_model = st.text_input("Vision model", value=vision_model)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
        st.markdown("### Safety")
        st.markdown(f'<div class="disclaimer-box">{MEDICAL_DISCLAIMER}</div>', unsafe_allow_html=True)
        safety_ok = st.checkbox("I understand the disclaimer")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
        if st.button("Clear history", use_container_width=True):
            st.session_state.messages = []
            st.session_state.report_summary = ""
            st.session_state.uploaded_name = ""
            st.session_state.uploaded_preview = None
            st.session_state.last_action = ""
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    if not safety_ok:
        st.info("Please accept the disclaimer in the sidebar to continue.")
        st.stop()

    # HEADER
    st.markdown("# 🩺 MediAssist AI Pro")
    st.markdown("Medical report analysis, safe medical Q&A, and medicine guidance support.")
    st.markdown("---")

    # MAIN LAYOUT
    left, right = st.columns([1.45, 1.0], gap="large")

    # LEFT COLUMN
    with left:
        st.markdown('<div class="soft-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Patient Interaction & Chat</div>', unsafe_allow_html=True)

        # Top action row: upload + text + send + medicine suggestion
        c1, c2, c3, c4 = st.columns([1.15, 5.2, 1.2, 2.0], vertical_alignment="bottom")

        with c1:
            uploaded_file = st.file_uploader(
                "📎 Upload",
                type=["jpg", "jpeg", "png"],
                label_visibility="visible",
                help="Upload a medical report image",
            )

        with c2:
            user_text = st.text_input(
                "Type your question",
                placeholder="Ask about the report, symptoms, tests, or health terms...",
                label_visibility="collapsed",
            )

        with c3:
            send_clicked = st.button("Send", use_container_width=True)

        with c4:
            med_clicked = st.button("Medicine suggestion", use_container_width=True)

        st.markdown('<div class="upload-hint">Upload a report, then ask a question. The right panel will show the extracted analysis.</div>', unsafe_allow_html=True)

        # Upload processing
        if uploaded_file is not None and uploaded_file.name != st.session_state.uploaded_name:
            st.session_state.uploaded_name = uploaded_file.name

            raw_bytes = uploaded_file.getvalue()
            resized_bytes = resize_image_bytes(raw_bytes)
            st.session_state.uploaded_preview = resized_bytes

            with st.spinner("Analyzing report image..."):
                try:
                    report_text = analyze_image(client, vision_model, resized_bytes)
                    st.session_state.report_summary = report_text
                    st.session_state.last_action = "upload"
                except Exception as e:
                    st.session_state.report_summary = f"Error analyzing image: {e}"
                    st.session_state.last_action = "upload_error"

            st.rerun()

        # Send message
        if (send_clicked or st.session_state.last_action == "send_pending") and user_text.strip():
            st.session_state.last_action = "send_pending"

            if is_urgent(user_text):
                urgent_reply = (
                    "Your message mentions symptoms that may need urgent medical attention. "
                    "Please seek immediate care from a doctor or emergency service if symptoms are severe or worsening.\n\n"
                    "Note: I am an AI assistant, not a licensed doctor. Please consult a qualified healthcare professional for medical advice."
                )
                st.session_state.messages.append({"role": "user", "content": user_text})
                st.session_state.messages.append({"role": "assistant", "content": urgent_reply})
                st.session_state.last_action = ""
                st.rerun()

            with st.spinner("Generating response..."):
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

        # Medicine suggestion button
        if med_clicked:
            source_text = user_text.strip() or st.session_state.report_summary.strip()
            if not source_text:
                st.warning("Add a text query or upload a report first.")
            else:
                with st.spinner("Generating cautious medicine guidance..."):
                    try:
                        messages = [
                            {"role": "system", "content": build_medicine_prompt(st.session_state.report_summary, user_text)},
                            {"role": "user", "content": source_text},
                        ]
                        med_response = groq_text(client, text_model, messages, max_tokens=850)
                        st.session_state.messages.append(
                            {"role": "user", "content": f"Medicine guidance request: {source_text}"}
                        )
                        st.session_state.messages.append(
                            {"role": "assistant", "content": med_response}
                        )
                    except Exception as e:
                        st.session_state.messages.append(
                            {"role": "assistant", "content": f"Error generating medicine guidance: {e}"}
                        )
                st.rerun()

        # History
        st.markdown("---")
        st.markdown('<div class="section-title">Conversation History</div>', unsafe_allow_html=True)

        if not st.session_state.messages:
            st.info("No conversation yet. Ask a question or upload a medical report.")
        else:
            for msg in st.session_state.messages:
                render_message(msg["role"], msg["content"])

        st.markdown("</div>", unsafe_allow_html=True)

    # RIGHT COLUMN
    with right:
        st.markdown('<div class="soft-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Clinical Insights</div>', unsafe_allow_html=True)

        if st.session_state.uploaded_preview:
            st.image(st.session_state.uploaded_preview, caption="Uploaded report preview", use_container_width=True)
            st.write("")

        if st.session_state.report_summary:
            st.markdown("### Extracted Report Data")
            st.markdown(
                f'<div class="report-box">{st.session_state.report_summary}</div>',
                unsafe_allow_html=True
            )

            st.write("")
            st.markdown("### Export")
            export_text = (
                "MediAssist AI Pro Report Summary\n\n"
                f"{MEDICAL_DISCLAIMER}\n\n"
                "EXTRACTED REPORT DATA\n"
                f"{st.session_state.report_summary}\n\n"
                "CONVERSATION HISTORY\n"
            )
            for msg in st.session_state.messages:
                export_text += f"\n[{msg['role'].upper()}]\n{msg['content']}\n"

            st.download_button(
                "Download summary TXT",
                data=export_text,
                file_name="mediassist_summary.txt",
                mime="text/plain",
                use_container_width=True,
            )
        else:
            st.markdown(
                """
                <div style="
                    background:#FFFFFF;
                    border:1px dashed #CBD5E1;
                    border-radius:16px;
                    padding:22px;
                    color:#64748B;
                    text-align:center;">
                    Upload a medical report to generate structured clinical insights here.
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.caption("MediAssist AI Pro • Informational only • Not a substitute for professional medical advice.")

if __name__ == "__main__":
    main()
