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

# Optional Matplotlib for rich diagrams
try:
    import matplotlib.pyplot as plt
    import io
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

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
    
    .viz-container {
        background: #f0f9ff;
        border: 2px dashed #0ea5e9;
        border-radius: 16px;
        padding: 16px;
        margin: 12px 0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ====================== API SETUP ======================
groq_api = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
if not groq_api:
    st.error("⚠️ GROQ_API_KEY missing! Add it in Streamlit Secrets.")
    st.stop()

# ====================== STRONG SYSTEM PROMPT ======================
SYSTEM_PROMPT = """
You are MediAssist, an elite professional AI Medical Assistant.
You provide accurate, empathetic, and helpful information on health, wellness, medicine, fitness, nutrition, and biology.

STRICT RULES:
- ONLY answer health/medical/fitness/wellness related questions.
- If the question is unrelated, politely refuse and remind the user you are a medical assistant.
- ALWAYS end every response with: "Note: I am an AI, not a licensed doctor. Please consult a qualified healthcare professional for medical advice."

VISUALIZATION RULE (Very Important):
- When user asks about exercises, yoga poses, stretches, workouts, body parts, symptoms, or physical activities:
  - Give step-by-step explanation.
  - Always provide a clear **Visualization** using emojis or simple diagram.
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

# ====================== VISUALIZATION FUNCTIONS ======================
def get_visualization(query: str):
    q = query.lower()
    if MATPLOTLIB_AVAILABLE and any(x in q for x in ['exercise', 'yoga', 'pose', 'stretch', 'workout', 'push', 'squat']):
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.set_facecolor('#f8fafc')
        fig.patch.set_facecolor('#f8fafc')
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.plot([5,5],[8,4], color='#3b82f6', lw=6)
        ax.plot([5,2],[6,4], color='#3b82f6', lw=6)
        ax.plot([5,8],[6,4], color='#3b82f6', lw=6)
        ax.set_title("🧘 Exercise Pose Visualization", color='#4338ca', fontsize=14)
        ax.axis('off')
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=120)
        buf.seek(0)
        plt.close(fig)
        return buf.getvalue(), "Matplotlib Image"
    
    # Default rich text visualization (always works)
    if any(x in q for x in ['exercise', 'yoga', 'pose', 'stretch', 'workout']):
        return """
**🧘 Visualization** 
/\
/  \
/    \
/______\
||||
||||
text• Stand straight  
• Raise arms above head  
• Breathe deeply  
• Hold for 10 seconds
""", "Text Visualization"
    
    elif any(x in q for x in ['knee', 'back', 'shoulder', 'neck', 'hip']):
        return "**📍 Focus Area Highlighted**\n🔴 Pain area highlighted in red\n🟢 Gentle movement recommended", "Text Visualization"
    
    elif any(x in q for x in ['diet', 'nutrition', 'protein', 'calorie']):
        return """
**🥗 Balanced Plate**
🍎 Vegetables → 50%  
🍗 Protein     → 25%  
🍚 Carbs       → 25%
""", "Text Visualization"
    
    return "**💡 Wellness Tip:** Stay consistent with small healthy habits daily!", "Text Visualization"

# ====================== SIDEBAR ======================
with st.sidebar:
    st.markdown("# 🩺 MediAssist")
    st.caption("Expert Health & Wellness AI")
    st.divider()
    st.selectbox("Model", ["llama-3.3-70b-versatile"], disabled=True)
    if st.button("🗑️ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ====================== MAIN UI ======================
st.markdown("<h1 style='text-align:center;'>🩺 MediAssist AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#64748b; font-size:1.15rem;'>Your Professional Health & Wellness Companion</p>", unsafe_allow_html=True)
st.markdown("---")

# Display Chat History with Visualization
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        st.markdown(f'<div class="chat-user">{msg.content}</div>', unsafe_allow_html=True)
    elif isinstance(msg, AIMessage):
        st.markdown(f'<div class="chat-ai">{msg.content}</div>', unsafe_allow_html=True)
        # Show visualization if available
        if hasattr(msg, 'viz_data'):
            if isinstance(msg.viz_data, bytes):           # Matplotlib image
                st.image(msg.viz_data, caption="📊 Visualization", use_column_width=True)
            elif isinstance(msg.viz_data, str):           # Text visualization
                st.markdown(f'<div class="viz-container">{msg.viz_data}</div>', unsafe_allow_html=True)

# ====================== CHAT INPUT ======================
if user_input := st.chat_input("Ask about symptoms, exercises, yoga, nutrition, or health..."):
    st.markdown(f'<div class="chat-user">{user_input}</div>', unsafe_allow_html=True)
    
    with st.spinner("Analyzing medical knowledge & generating visualization..."):
        # LangChain response
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
        
        # Generate visualization
        viz_data, viz_type = get_visualization(user_input)
        
        # Create AI message with visualization attached
        ai_msg = AIMessage(content=response.content)
        ai_msg.viz_data = viz_data
        
        # Save to session
        st.session_state.messages.append(HumanMessage(content=user_input))
        st.session_state.messages.append(ai_msg)
        
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<p style='text-align: center; color: #64748b; font-size: 0.85rem;'>
    MediAssist AI • Not a substitute for professional medical advice • Always consult a doctor
</p>
""", unsafe_allow_html=True)
