import streamlit as st
import os
from datetime import datetime

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

# ====================== PREMIUM MEDICAL UI ======================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@500;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        color: #1e293b;
    }
    h1, h2, h3 {
        font-family: 'Space Grotesk', sans-serif;
        color: #4338ca;
        letter-spacing: -0.02em;
    }
    
    /* Chat Bubbles */
    .chat-user {
        background: linear-gradient(135deg, #3b82f6, #6366f1);
        color: white;
        padding: 14px 20px;
        border-radius: 20px 20px 4px 20px;
        max-width: 78%;
        margin: 12px 0 12px auto;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
    }
    .chat-ai {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 5px solid #8b5cf6;
        color: #1e293b;
        padding: 14px 20px;
        border-radius: 20px 20px 20px 4px;
        max-width: 78%;
        margin: 12px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    
    .visualization-box {
        background: #f0f9ff;
        border: 2px dashed #0ea5e9;
        border-radius: 16px;
        padding: 16px;
        margin: 12px 0;
        text-align: center;
    }
    
    .stButton>button {
        border-radius: 12px;
        height: 52px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ====================== API SETUP ======================
groq_api = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
if not groq_api:
    st.error("⚠️ GROQ_API_KEY missing! Add in Streamlit Secrets.")
    st.stop()

# ====================== ENHANCED SYSTEM PROMPT (Visualization Support) ======================
SYSTEM_PROMPT = """
You are MediAssist, a highly professional and empathetic AI Medical Assistant.

CORE RULES:
- ONLY answer questions related to health, medicine, wellness, fitness, nutrition, biology, or symptoms.
- If user asks anything outside medical domain, politely refuse and remind them you are a medical assistant.
- ALWAYS end your response with: "Note: I am an AI, not a licensed doctor. Please consult a qualified healthcare professional for medical advice."

VISUALIZATION RULE (Very Important):
- When user asks about **exercises, yoga poses, stretches, body parts, symptoms, or any physical activity**, 
  you MUST provide:
  1. Clear step-by-step explanation
  2. A simple **visualization** using emojis and markdown (e.g., body diagram, pose steps)
  3. Put the visualization inside a box like this:
     **Visualization:**
     ```visual
     [your emoji + text diagram here]
     Be warm, clear, and professional.
"""
@st.cache_resource
def get_medical_llm():
return ChatGroq(
groq_api_key=groq_api,
model_name="llama-3.3-70b-versatile",
temperature=0.2
)
llm = get_medical_llm()
====================== SESSION STATE ======================
if "messages" not in st.session_state:
st.session_state.messages = []
====================== SIDEBAR ======================
with st.sidebar:
st.markdown("# 🩺 MediAssist")
st.caption("Professional Health Assistant")
st.divider()
st.selectbox("Model", ["llama-3.3-70b-versatile"], disabled=True)
temperature = st.slider("Creativity Level", 0.0, 0.5, 0.2, 0.05)
st.divider()
if st.button("🗑️ New Chat", use_container_width=True):
st.session_state.messages = []
st.rerun()
====================== MAIN UI ======================
st.markdown("🩺 MediAssist AI", unsafe_allow_html=True)
st.markdown("Your Trusted Health & Wellness Companion", unsafe_allow_html=True)
Display Chat History
for msg in st.session_state.messages:
if isinstance(msg, HumanMessage):
st.markdown(f"{msg.content}", unsafe_allow_html=True)
elif isinstance(msg, AIMessage):
st.markdown(f"{msg.content}", unsafe_allow_html=True)
Chat Input
if user_input := st.chat_input("Ask anything about health, symptoms, exercises, nutrition..."):
Show user message immediately
st.markdown(f"{user_input}", unsafe_allow_html=True)
with st.spinner("Thinking medically..."):
LangChain Chain
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
Save messages
st.session_state.messages.append(HumanMessage(content=user_input))
st.session_state.messages.append(AIMessage(content=response.content))
st.rerun()
Footer
st.markdown("""

    MediAssist AI • Not a substitute for professional medical advice • Always consult a doctor

""", unsafe_allow_html=True)
```
