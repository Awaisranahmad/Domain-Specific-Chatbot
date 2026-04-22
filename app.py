import streamlit as st
import os
import base64
import pandas as pd
from PIL import Image
import io
from groq import Groq

# =========================================================
# 1) PAGE CONFIGURATION & THEME
# =========================================================
st.set_page_config(
    page_title="MediAssist AI Pro",
    page_icon="⚕️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main {
        background-color: #F8FAFC;
    }
    h1, h2, h3, h4 {
        color: #1E3A8A;
    }
    .stButton>button {
        background-color: #6D28D9;
        color: white;
        border-radius: 10px;
        border: none;
        padding: 0.55rem 1rem;
    }
    .stButton>button:hover {
        background-color: #5B21B6;
        color: white;
    }
    .disclaimer-box {
        background-color: #FEF2F2;
        border-left: 4px solid #DC2626;
        padding: 12px 14px;
        margin-bottom: 18px;
        color: #991B1B;
        font-size: 0.92em;
        border-radius: 8px;
    }
    .insights-panel {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 14px;
        box-shadow: 0 4px 14px -2px rgba(0, 0, 0, 0.08);
        border-top: 4px solid #6D28D9;
    }
    .small-muted {
        color: #64748B;
        font-size: 0.92rem;
    }
    .user-msg {
        background: linear-gradient(135deg, #2563EB, #7C3AED);
        color: white;
        padding: 12px 16px;
        border-radius: 16px 16px 4px 16px;
        margin-bottom: 10px;
    }
    .ai-msg {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-left: 5px solid #8B5CF6;
        color: #0F172A;
        padding: 12px 16px;
        border-radius: 16px 16px 16px 4px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2) SYSTEM CONSTANTS & PROMPTS
# =========================================================
MEDICAL_DISCLAIMER = """
**CRITICAL DISCLAIMER:** MediAssist AI Pro is an informational tool only. 
It is NOT a licensed healthcare provider. The AI cannot and will not diagnose illnesses, 
prescribe medications, or provide definitive medical advice. Always consult a certified 
doctor before making any health decisions.
"""

SYSTEM_PROMPT = """
You are MediAssist AI Pro, an advanced medical data summarization assistant.

Your primary role:
- Explain medical terminology
- Summarize lab reports
- Answer health-related questions in clear, accessible language
- Stay professional, cautious, and objective

STRICT RULES:
1. NEVER diagnose a condition.
2. NEVER prescribe medication or treatments.
3. NEVER claim to replace a doctor.
4. If the user describes acute, severe, or life-threatening symptoms, tell them to seek emergency medical care immediately.
5. If the report is unclear, say that some parts are unreadable.
6. Always keep the tone calm, respectful, and medically responsible.
7. End every response with:
   "Note: I am an AI assistant, not a licensed doctor. Please consult a qualified healthcare professional for medical advice."
"""

VISION_PROMPT = """
You are MediAssist AI Pro, a medical report image analyzer.

Task:
- Read the uploaded medical report carefully.
- Extract visible medical text, test names, values, units, and reference ranges.
- Identify abnormal, high, low, or flagged values if visible.
- Summarize the report clearly in simple language.
- Do not diagnose.
- Do not hallucinate unreadable text.
- If something is unclear, mention that it may be difficult to read.

End with:
"Note: I am an AI assistant, not a doctor. Please consult a qualified healthcare professional."
"""

# =========================================================
# 3) CORE LOGIC CLASSES
# =========================================================
class DocumentProcessor:
    """Handles image preparation for the multimodal LLM."""

    @staticmethod
    def encode_image(uploaded_file):
        """Resizes image and encodes it to base64."""
        image = Image.open(uploaded_file)

        if image.mode != "RGB":
            image = image.convert("RGB")

        # Resize for faster API calls and lower memory usage
        image.thumbnail((1024, 1024))

        buffered = io.BytesIO()
        image.save(buffered, format="JPEG", quality=85, optimize=True)
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    @staticmethod
    def image_to_bytes(uploaded_file):
        """Return resized image bytes for preview or saving."""
        image = Image.open(uploaded_file)
        if image.mode != "RGB":
            image = image.convert("RGB")
        image.thumbnail((1024, 1024))
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG", quality=85, optimize=True)
        return buffered.getvalue()


class GroqInferenceEngine:
    """Manages API calls to Groq for both vision and text generation."""

    def __init__(self, api_key: str, vision_model: str, text_model: str):
        self.client = Groq(api_key=api_key)
        self.vision_model = vision_model
        self.text_model = text_model

    def analyze_medical_image(self, base64_image: str) -> str:
        """Extracts medical data from uploaded report image."""
        try:
            response = self.client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {
                        "role": "system",
                        "content": VISION_PROMPT
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyze this medical report image and extract all visible medical data in a structured format."
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                            }
                        ]
                    }
                ],
                temperature=0.2,
                max_tokens=1200
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error processing image: {str(e)}"

    def generate_chat_response(self, chat_history: list) -> str:
        """Generates a response using text model and conversation history."""
        try:
            messages = [{"role": "system", "content": SYSTEM_PROMPT}] + chat_history
            response = self.client.chat.completions.create(
                model=self.text_model,
                messages=messages,
                temperature=0.4,
                max_tokens=1200
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error generating response: {str(e)}"


# =========================================================
# 4) UTILITIES
# =========================================================
def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "report_summary" not in st.session_state:
        st.session_state.report_summary = None
    if "api_key_valid" not in st.session_state:
        st.session_state.api_key_valid = False
    if "last_uploaded_name" not in st.session_state:
        st.session_state.last_uploaded_name = None
    if "engine" not in st.session_state:
        st.session_state.engine = None


def is_urgent_symptom(text: str) -> bool:
    urgent_keywords = [
        "chest pain", "shortness of breath", "difficulty breathing", "trouble breathing",
        "fainting", "unconscious", "severe bleeding", "stroke", "one sided weakness",
        "suicidal", "severe headache", "blue lips", "seizure", "confusion"
    ]
    text_lower = text.lower()
    return any(k in text_lower for k in urgent_keywords)


def render_chat_message(role: str, content: str):
    if role == "user":
        st.markdown(f'<div class="user-msg">{content}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="ai-msg">{content}</div>', unsafe_allow_html=True)


# =========================================================
# 5) MAIN APP
# =========================================================
def main():
    initialize_session_state()

    # ---------- Sidebar ----------
    with st.sidebar:
        st.title("⚕️ MediAssist Pro")
        st.markdown("### Configuration")

        groq_api_key = st.secrets.get("GROQ_API_KEY", "") or os.getenv("GROQ_API_KEY", "")
        if not groq_api_key:
            groq_api_key = st.text_input("Enter Groq API Key", type="password")

        vision_model = st.secrets.get("GROQ_VISION_MODEL", os.getenv("GROQ_VISION_MODEL", "llama-3.2-11b-vision-preview"))
        text_model = st.secrets.get("GROQ_TEXT_MODEL", os.getenv("GROQ_TEXT_MODEL", "llama3-70b-8192"))

        st.markdown("#### Model Settings")
        vision_model = st.text_input("Vision Model", value=vision_model)
        text_model = st.text_input("Text Model", value=text_model)

        if groq_api_key:
            st.session_state.api_key_valid = True
            st.session_state.engine = GroqInferenceEngine(
                api_key=groq_api_key,
                vision_model=vision_model,
                text_model=text_model
            )
            st.success("Groq API ready.")
        else:
            st.session_state.api_key_valid = False
            st.warning("Please provide a Groq API Key to continue.")

        st.markdown("---")
        st.markdown("### Safety Protocol")
        safety_agreed = st.checkbox("I agree to the Medical Disclaimer")

        st.markdown(f'<div class="disclaimer-box">{MEDICAL_DISCLAIMER}</div>', unsafe_allow_html=True)

        if st.button("Clear Session", use_container_width=True):
            st.session_state.messages = []
            st.session_state.report_summary = None
            st.session_state.last_uploaded_name = None
            st.rerun()

    # ---------- Main Header ----------
    st.markdown("# ⚕️ MediAssist AI Pro")
    st.markdown("An advanced multimodal medical assistant for report analysis and health Q&A.")
    st.markdown("---")

    # ---------- Access Control ----------
    if not safety_agreed:
        st.info("👈 Please agree to the medical disclaimer in the sidebar to begin.")
        st.stop()

    if not st.session_state.api_key_valid or st.session_state.engine is None:
        st.stop()

    engine = st.session_state.engine

    # ---------- Main Layout ----------
    col1, col2 = st.columns([6, 4], gap="large")

    # =========================================================
    # COLUMN 1: Upload + Chat
    # =========================================================
    with col1:
        st.markdown("## Patient Interaction & Chat")

        uploaded_file = st.file_uploader(
            "Upload Medical Report (JPG, JPEG, PNG)",
            type=["jpg", "jpeg", "png"]
        )

        if uploaded_file is not None and uploaded_file.name != st.session_state.last_uploaded_name:
            st.session_state.last_uploaded_name = uploaded_file.name

            with st.spinner("Analyzing medical report via Groq Vision..."):
                try:
                    b64_image = DocumentProcessor.encode_image(uploaded_file)
                    extracted_data = engine.analyze_medical_image(b64_image)

                    st.session_state.report_summary = extracted_data
                    st.session_state.messages.append({
                        "role": "system",
                        "content": f"A medical report was uploaded. Extracted contents:\n{extracted_data}"
                    })
                    st.success("Report parsed successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to analyze image: {str(e)}")

        st.markdown("---")

        st.markdown("### Conversation")
        for msg in st.session_state.messages:
            if msg["role"] != "system":
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        prompt = st.chat_input("Ask a question about your report or health terms...")

        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("user"):
                st.markdown(prompt)

            if is_urgent_symptom(prompt):
                urgent_reply = (
                    "Your message includes symptoms that may need urgent medical attention. "
                    "Please seek immediate care from a doctor or emergency service if symptoms are severe or worsening.\n\n"
                    "Note: I am an AI assistant, not a licensed doctor. Please consult a qualified healthcare professional for medical advice."
                )
                with st.chat_message("assistant"):
                    st.markdown(urgent_reply)
                st.session_state.messages.append({"role": "assistant", "content": urgent_reply})
                st.rerun()

            with st.chat_message("assistant"):
                with st.spinner("Consulting knowledge base..."):
                    try:
                        response = engine.generate_chat_response(st.session_state.messages)
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    except Exception as e:
                        error_msg = f"Error generating response: {str(e)}"
                        st.markdown(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})

    # =========================================================
    # COLUMN 2: Report Summary + Export
    # =========================================================
    with col2:
        st.markdown("## Clinical Insights")

        if st.session_state.report_summary:
            st.markdown('<div class="insights-panel">', unsafe_allow_html=True)
            st.markdown("### 📄 Extracted Report Data")
            st.markdown(st.session_state.report_summary)

            st.markdown("---")
            st.markdown("### 📥 Export")

            export_data = (
                "MediAssist AI Pro Summary\n\n"
                f"{MEDICAL_DISCLAIMER}\n\n"
                "REPORT DATA:\n"
                f"{st.session_state.report_summary}"
            )

            st.download_button(
                label="Download Summary Report",
                data=export_data,
                file_name="mediassist_summary.txt",
                mime="text/plain",
                use_container_width=True
            )

            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="insights-panel" style="color: #64748B; text-align: center;">
                <p>Upload a medical document to generate structured clinical insights.</p>
            </div>
            """, unsafe_allow_html=True)

    # ---------- Footer ----------
    st.markdown("---")
    st.caption("MediAssist AI Pro • Informational only • Not a substitute for professional medical advice.")


if __name__ == "__main__":
    main()
