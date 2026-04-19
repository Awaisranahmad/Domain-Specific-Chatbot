import streamlit as st
import os
from datetime import datetime
import matplotlib.pyplot as plt
import io
import re

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

# ====================== PREMIUM LIGHT THEME ======================
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
    
    .visual-box {
        background: #f0f9ff;
        border: 2px dashed #0ea5e9;
        border-radius: 16px;
        padding: 18px;
        margin: 15px 0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ====================== API SETUP ======================
groq_api = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
if not groq_api:
    st.error("⚠️ GROQ_API_KEY missing! Add it in Streamlit Secrets.")
    st.stop()

# ====================== SYSTEM PROMPT ======================
SYSTEM_PROMPT = """
You are MediAssist, an elite professional AI Medical Assistant.
You provide accurate, empathetic, and helpful information about health, wellness, medicine, fitness, nutrition, and biology.

STRICT RULES:
- ONLY answer health, medical, fitness, or wellness related questions.
- If the question is unrelated, politely refuse and remind the user you are a medical assistant.
- ALWAYS end every response with: "Note: I am an AI, not a licensed doctor. Please consult a qualified healthcare professional for medical advice."

When user uploads a medical report/image, acknowledge it and give helpful general analysis or ask for specific values if needed.
"""

# ====================== VISUALIZATION ENGINE ======================
def create_health_visualization(query: str):
    query_lower = query.lower()
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.set_facecolor('#f0f9ff')
    fig.patch.set_facecolor('#ffffff')
    
    if any(word in query_lower for word in ['exercise', 'yoga', 'pose', 'stretch', 'workout', 'asana']):
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        circle = plt.Circle((5, 8), 0.6, color='#3b82f6', ec='#1e293b', lw=2)
        ax.add_patch(circle)
        ax.plot([5,5],[7.4,4], color='#3b82f6', lw=4)
        ax.plot([5,3.5],[6,5], color='#3b82f6', lw=4)
        ax.plot([5,6.5],[6,5], color='#3b82f6', lw=4)
        ax.plot([5,3.8],[4,1.8], color='#3b82f6', lw=4)
        ax.plot([5,6.2],[4,1.8], color='#3b82f6', lw=4)
        ax.set_title("🧘 Exercise / Yoga Pose Visualization", fontsize=13, color='#4338ca')
        ax.axis('off')
    
    elif any(word in query_lower for word in ['knee', 'back', 'shoulder', 'neck', 'hip', 'ankle']):
        part = next((w for w in ['knee','back','shoulder','neck','hip','ankle'] if w in query_lower), 'body')
        ax.plot([5,5],[2,8], 'gray', lw=3)
        ax.plot([3,7],[7,7], 'gray', lw=3)
        ax.plot([2,8],[5,5], 'gray', lw=3)
        ax.plot(5, 3.5 if part=='knee' else 5, 'ro', markersize=25)
        ax.set_title(f"📍 {part.capitalize()} Area Highlighted", fontsize=13, color='#4338ca')
        ax.axis('off')
    
    elif any(word in query_lower for word in ['diet', 'nutrition', 'protein', 'calorie']):
        labels = ['Carbs', 'Protein', 'Fats', 'Vitamins']
        sizes = [40, 30, 20, 10]
        colors = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6']
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.0f%%', startangle=90)
        ax.set_title("🥗 Nutritional Balance", fontsize=13, color='#4338ca')
    
    else:
        metrics = ['Hydration', 'Sleep', 'Activity', 'Mindfulness']
        scores = [75, 65, 80, 70]
        bars = ax.bar(metrics, scores, color=['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b'])
        ax.set_ylim(0, 100)
        ax.set_title("💪 Wellness Snapshot", fontsize=13, color='#4338ca')
        for bar, score in zip(bars, scores):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, f'{score}%', ha='center')
    
    plt.tight_layout()
    return fig

def fig_to_bytes(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=120, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return buf.getvalue()

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
if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None

# ====================== SIDEBAR ======================
with st.sidebar:
    st.markdown("# 🩺 MediAssist")
    st.caption("Professional Health & Wellness Assistant")
    st.divider()
    
    st.selectbox("Model", ["llama-3.3-70b-versatile"], disabled=True)
    if st.button("🗑️ New Chat", use_container_width=True, type="secondary"):
        st.session_state.messages = []
        st.session_state.uploaded_image = None
        st.rerun()

# ====================== IMAGE UPLOAD SECTION ======================
st.subheader("📤 Upload Medical Report / Image")
uploaded_file = st.file_uploader("Upload X-ray, blood report, prescription or any medical image (JPG, PNG, PDF)", 
                                 type=["jpg", "jpeg", "png", "pdf"], 
                                 label_visibility="collapsed")

if uploaded_file:
    st.session_state.uploaded_image = uploaded_file
    st.success("✅ Medical image uploaded successfully!")
    st.image(uploaded_file, caption="Uploaded Medical Report/Image", use_column_width=True)

# ====================== MAIN UI ======================
st.markdown("<h1 style='text-align:center;'>🩺 MediAssist AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#64748b; font-size:1.15rem;'>Your Professional Health & Wellness Companion</p>", unsafe_allow_html=True)
st.markdown("---")

# Display Chat History
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        st.markdown(f'<div class="chat-user">{msg.content}</div>', unsafe_allow_html=True)
    elif isinstance(msg, AIMessage):
        st.markdown(f'<div class="chat-ai">{msg.content}</div>', unsafe_allow_html=True)
        if hasattr(msg, 'visualization') and msg.visualization:
            st.image(msg.visualization, caption="📊 Generated Visualization", use_column_width=True)

# ====================== CHAT INPUT ======================
if user_input := st.chat_input("Ask about symptoms, exercises, yoga, nutrition, or any health topic..."):
    st.markdown(f'<div class="chat-user">{user_input}</div>', unsafe_allow_html=True)
    
    with st.spinner("Thinking medically & generating visualization..."):
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
        fig = create_health_visualization(user_input)
        viz_bytes = fig_to_bytes(fig)
        
        # Create AI message with visualization
        ai_msg = AIMessage(content=response.content)
        ai_msg.visualization = viz_bytes
        
        # Save to session
        st.session_state.messages.append(HumanMessage(content=user_input))
        st.session_state.messages.append(ai_msg)
        
        st.rerun()

# ====================== DOWNLOAD & FOOTER ======================
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("⬇️ Download Full Chat History", use_container_width=True):
        if st.session_state.messages:
            history_text = "# MediAssist Chat History\n\n"
            for msg in st.session_state.messages:
                if isinstance(msg, HumanMessage):
                    history_text += f"**You:** {msg.content}\n\n"
                else:
                    history_text += f"**MediAssist:** {msg.content}\n\n"
            
            st.download_button(
                label="📥 Download as Markdown",
                data=history_text,
                file_name=f"MediAssist_Chat_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                mime="text/markdown"
            )

st.markdown("---")
st.markdown("""
<p style='text-align: center; color: #64748b; font-size: 0.85rem;'>
    MediAssist AI • Not a substitute for professional medical advice • Always consult a doctor
</p>
""", unsafe_allow_html=True)
