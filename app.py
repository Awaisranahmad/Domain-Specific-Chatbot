import streamlit as st
import os
try:
    from langchain_groq import ChatGroq
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.messages import HumanMessage, AIMessage
except ModuleNotFoundError as e:
    st.error(f"🚨 Module missing: {e}. Please check requirements.txt")
    st.stop()

# ====================== PAGE CONFIG & LIGHT THEME ======================
st.set_page_config(page_title="MediAssist AI", page_icon="🩺", layout="centered")

# Light Professional Theme (White, Blue, Purple Accents)
st.markdown("""
<style>
    .stApp {
        background-color: #ffffff;
        color: #1e293b;
    }
    h1, h2, h3 {
        color: #4338ca; /* Indigo/Purple */
    }
    .stChatInputContainer {
        border-top: 2px solid #e2e8f0;
    }
    .chat-bubble-user {
        background: linear-gradient(135deg, #3b82f6, #6366f1); /* Blue to Purple */
        color: white;
        padding: 12px 18px;
        border-radius: 18px 18px 4px 18px;
        margin-bottom: 12px;
        max-width: 80%;
        float: right;
        clear: both;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .chat-bubble-ai {
        background-color: #f8fafc;
        color: #334155;
        border: 1px solid #cbd5e1;
        border-left: 4px solid #8b5cf6; /* Purple Accent */
        padding: 12px 18px;
        border-radius: 18px 18px 18px 4px;
        margin-bottom: 12px;
        max-width: 80%;
        float: left;
        clear: both;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .disclaimer {
        color: #64748b;
        font-size: 0.85rem;
        text-align: center;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ====================== API SETUP ======================
groq_api = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")

if not groq_api:
    st.warning("⚠️ Please add your Groq API Key to proceed.")
    st.stop()

# ====================== SYSTEM PROMPT ======================
# Ye prompt AI ko batayega ke usay KYA karna hai aur KYA NAHI karna
SYSTEM_PROMPT = """
You are MediAssist, an elite and professional AI Medical Assistant.
Your primary role is to provide general health, wellness, and medical information.

RULES:
1. ONLY answer questions related to health, medicine, biology, fitness, and wellness.
2. If the user asks about coding, politics, math, or anything outside the medical domain, gently refuse and remind them that you are a medical assistant.
3. ALWAYS include a disclaimer at the end of medical advice stating: "Note: I am an AI, not a doctor. Please consult a healthcare professional for actual medical concerns."
4. Be empathetic, polite, and use clear, professional language.
"""

@st.cache_resource
def get_medical_llm():
    return ChatGroq(
        groq_api_key=groq_api,
        model_name="llama-3.3-70b-versatile",
        temperature=0.2 # Low temperature for accurate, factual responses
    )

llm = get_medical_llm()

# ====================== SESSION STATE ======================
if "messages" not in st.session_state:
    st.session_state.messages = []

# ====================== UI ======================
st.markdown("<h1 style='text-align: center;'>🩺 MediAssist AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b;'>Your Professional Health & Wellness Guide</p>", unsafe_allow_html=True)
st.markdown("---")

# Display Chat History
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        st.markdown(f"<div class='chat-bubble-user'>{msg.content}</div>", unsafe_allow_html=True)
    elif isinstance(msg, AIMessage):
        st.markdown(f"<div class='chat-bubble-ai'>{msg.content}</div>", unsafe_allow_html=True)

# Clear floats
st.markdown("<div style='clear: both;'></div>", unsafe_allow_html=True)

# ====================== CHAT LOGIC ======================
prompt_template = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])

chain = prompt_template | llm

if user_input := st.chat_input("Ask about symptoms, healthy habits, or medical terms..."):
    # Add user message to UI immediately
    st.markdown(f"<div class='chat-bubble-user'>{user_input}</div><div style='clear: both;'></div>", unsafe_allow_html=True)
    
    with st.spinner("Analyzing medical knowledge base..."):
        # Invoke LangChain
        response = chain.invoke({
            "input": user_input,
            "chat_history": st.session_state.messages
        })
        
        # Save to state
        st.session_state.messages.append(HumanMessage(content=user_input))
        st.session_state.messages.append(AIMessage(content=response.content))
        
        # Rerun to update the AI bubble
        st.rerun()

st.markdown("<div class='disclaimer'>MediAssist AI • Not a substitute for professional medical advice.</div>", unsafe_allow_html=True)
