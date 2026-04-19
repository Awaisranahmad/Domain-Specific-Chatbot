import streamlit as st
import os
from datetime import datetime
import matplotlib.pyplot as plt
import io

# --- Imports ---
try:
    from langchain_groq import ChatGroq
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.messages import HumanMessage, AIMessage
except ModuleNotFoundError as e:
    st.error(f"🚨 Module missing: {e}. Please check requirements.txt")
    st.stop()

# ====================== PAGE CONFIG ======================
st.set_page_config(
    page_title="🩺 MediAssist AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== PREMIUM UI ======================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@500;600;700&display=swap');
    
    .stApp { background: #ffffff; color: #1e293b; }
    h1, h2, h3 { 
        font-family: 'Space Grotesk', sans-serif; 
        color: #4338ca; 
        letter-spacing: -0.02em; 
    }
    
    .chat-user {
        background: linear-gradient(135deg, #3b82f6, #6366f1);
        color: white;
        padding: 14px 20px;
        border-radius: 20px 20px 4px 20px;
        max-width: 78%;
        margin: 12px 0 12px auto;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
    }
    .chat-ai {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-left: 5px solid #8b5cf6;
        color: #1e293b;
        padding: 14px 20px;
        border-radius: 20px 20px 20px 4px;
        max-width: 78%;
        margin: 12px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .upload-area {
        border: 2px dashed #4338ca;
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        background: #f8fafc;
    }
</style>
""", unsafe_allow_html=True)

# ====================== API SETUP ======================
groq_api = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
if not groq_api:
    st.error("⚠️ GROQ_API_KEY missing! Add it in Streamlit Secrets.")
    st.stop()

# ====================== IMPROVED SYSTEM PROMPT ======================
SYSTEM_PROMPT = """
You are MediAssist, a professional and empathetic AI Medical Assistant.

STRICT RULES:
- ONLY answer questions related to health, medicine, fitness, nutrition, and wellness.
- If the user uploads a medical image/report, acknowledge it politely and ask for key details (test name, important values, symptoms, etc.) so you can give helpful general information.
- Never say "I cannot see the image". Instead, guide the user to provide text details from the report.
- ALWAYS end every response with: "Note: I am an AI, not a licensed doctor. Please consult a qualified healthcare professional for medical advice."

Be warm, clear, and helpful.
"""

# ====================== LLM ======================
@st.cache_resource
def get_medical_llm():
    return ChatGroq(
        groq_api_key=groq_api,
        model_name="llama-3.3-70b-versatile",
        temperature=0.2
    )

llm = get_medical_llm()

# ====================== SESSION STATE ======================
if "messages" not in st.session_state:
    st.session_state.messages = []

# ====================== SIDEBAR ======================
with st.sidebar:
    st.markdown("# 🩺 MediAssist")
    st.caption("Professional Health & Wellness Assistant")
    st.divider()
    if st.button("🗑️ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ====================== IMAGE UPLOAD (Integrated UI) ======================
st.subheader("📤 Upload Medical Report or Image")
uploaded_file = st.file_uploader(
    "Upload X-ray, blood report, MRI, prescription or any medical image",
    type=["jpg", "jpeg", "png", "pdf"],
    label_visibility="collapsed"
)

if uploaded_file:
    st.image(uploaded_file, caption="✅ Uploaded Medical Report/Image", use_column_width=True)
    st.success("Image uploaded successfully! Now ask any question about it.")

# ====================== MAIN CHAT UI ======================
st.markdown("<h1 style='text-align:center;'>🩺 MediAssist AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#64748b; font-size:1.15rem;'>Your Professional Health & Wellness Companion</p>", unsafe_allow_html=True)
st.markdown("---")

# Display Chat History
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        st.markdown(f'<div class="chat-user">{msg.content}</div>', unsafe_allow_html=True)
    elif isinstance(msg, AIMessage):
        st.markdown(f'<div class="chat-ai">{msg.content}</div>', unsafe_allow_html=True)

# ====================== CHAT INPUT ======================
if user_input := st.chat_input("Ask about symptoms, exercises, your uploaded report, or any health topic..."):
    st.markdown(f'<div class="chat-user">{user_input}</div>', unsafe_allow_html=True)
    
    with st.spinner("Analyzing..."):
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
        
        chain = prompt_template | llm
        response = chain.invoke({
            "input": user_input,
            "chat_history": st.session_state.messages
        })
        
        ai_msg = AIMessage(content=response.content)
        st.session_state.messages.append(HumanMessage(content=user_input))
        st.session_state.messages.append(ai_msg)
        
        st.rerun()

# ====================== DOWNLOAD HISTORY ======================
if st.button("⬇️ Download Full Chat History", use_container_width=True):
    if st.session_state.messages:
        text = "# MediAssist Chat History\n\n"
        for msg in st.session_state.messages:
            if isinstance(msg, HumanMessage):
                text += f"**You:** {msg.content}\n\n"
            else:
                text += f"**MediAssist:** {msg.content}\n\n"
        st.download_button(
            "📥 Download as .md file",
            text,
            file_name=f"MediAssist_Chat_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
            mime="text/markdown"
        )

st.markdown("---")
st.markdown("""
<p style='text-align: center; color: #64748b; font-size: 0.85rem;'>
    MediAssist AI • Not a substitute for professional medical advice • Always consult a doctor
</p>
""", unsafe_allow_html=True)
