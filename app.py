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
    
    .stApp {
        background: #ffffff;
        color: #1e293b;
    }
    h1, h2, h3 {
        font-family: 'Space Grotesk', sans-serif;
        color: #4338ca;
        letter-spacing: -0.02em;
    }
    
    /* Chat Bubbles - Improved */
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
    
    /* Visualization Box */
    .visual-box {
        background: #f0f9ff;
        border: 2px dashed #0ea5e9;
        border-radius: 16px;
        padding: 18px;
        margin: 15px 0;
        text-align: center;
        font-size: 1.1rem;
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
    st.error("⚠️ GROQ_API_KEY missing! Add it in Streamlit Secrets.")
    st.stop()

# ====================== ENHANCED SYSTEM PROMPT ======================
SYSTEM_PROMPT = """
You are MediAssist, an elite professional AI Medical Assistant.
Your job is to give accurate, empathetic, and helpful information about health, wellness, medicine, fitness, nutrition, and biology.

STRICT RULES:
1. ONLY answer health, medical, fitness, or wellness related questions.
2. If the question is unrelated (coding, politics, math, etc.), politely refuse and say you are a medical assistant.
3. ALWAYS end every response with this disclaimer:
   "Note: I am an AI, not a licensed doctor. Please consult a qualified healthcare professional for medical advice."

Keep your answer clear and structured. The system will add a graphical visualization separately.
"""

# ====================== VISUALIZATION ENGINE (matplotlib) ======================
def create_health_visualization(query: str):
    """
    Generate a matplotlib figure based on the user's query.
    Returns a PIL Image or matplotlib figure object.
    """
    query_lower = query.lower()
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.set_facecolor('#f0f9ff')
    fig.patch.set_facecolor('#ffffff')
    
    # Exercise / Yoga / Physical Activity
    if any(word in query_lower for word in ['exercise', 'yoga', 'pose', 'stretch', 'workout', 'asana', 'surya', 'tadasana', 'downward dog']):
        # Draw a simple stick figure doing a pose
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        # Head
        circle = plt.Circle((5, 8), 0.6, color='#3b82f6', ec='#1e293b', lw=2)
        ax.add_patch(circle)
        # Body
        ax.plot([5, 5], [7.4, 4], color='#3b82f6', lw=3)
        # Arms
        ax.plot([5, 3.5], [6, 5], color='#3b82f6', lw=3)
        ax.plot([5, 6.5], [6, 5], color='#3b82f6', lw=3)
        # Legs
        ax.plot([5, 3.8], [4, 1.8], color='#3b82f6', lw=3)
        ax.plot([5, 6.2], [4, 1.8], color='#3b82f6', lw=3)
        ax.set_title("🧘 Suggested Pose Visualization", fontsize=12, color='#4338ca')
        ax.axis('off')
        
    # Body part specific (e.g., knee, back, shoulder)
    elif any(word in query_lower for word in ['knee', 'back', 'shoulder', 'neck', 'hip', 'ankle']):
        body_part = next((w for w in ['knee', 'back', 'shoulder', 'neck', 'hip', 'ankle'] if w in query_lower), 'body')
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        # Simple body outline
        ax.plot([5,5],[2,8], 'gray', lw=2)  # spine
        ax.plot([3,7],[7,7], 'gray', lw=2)  # shoulders
        ax.plot([2,8],[5,5], 'gray', lw=2)  # hips
        # Highlight the specific part
        if body_part == 'knee':
            ax.plot(5, 3.5, 'ro', markersize=20, label='Knee')
            ax.annotate('Knee', (5, 3.5), textcoords="offset points", xytext=(10,10), ha='center', color='red')
        elif body_part == 'back':
            ax.fill_between([4,6], [4,4], [7,7], color='red', alpha=0.4, label='Back')
        elif body_part == 'shoulder':
            ax.plot(3,7, 'ro', markersize=20)
            ax.plot(7,7, 'ro', markersize=20)
            ax.annotate('Shoulders', (5,7.2), ha='center', color='red')
        else:
            ax.plot(5,5, 'ro', markersize=20)
            ax.annotate(body_part.capitalize(), (5,5), textcoords="offset points", xytext=(0,10), ha='center', color='red')
        ax.set_title(f"📍 {body_part.capitalize()} Highlight", fontsize=12, color='#4338ca')
        ax.axis('off')
        
    # Nutrition / Diet
    elif any(word in query_lower for word in ['diet', 'nutrition', 'calorie', 'protein', 'vitamin']):
        categories = ['Carbs', 'Proteins', 'Fats', 'Vitamins']
        values = [40, 30, 20, 10]
        colors = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6']
        ax.pie(values, labels=categories, colors=colors, autopct='%1.0f%%', startangle=90, wedgeprops={'edgecolor': 'white'})
        ax.set_title("🥗 Nutritional Balance Guide", fontsize=12, color='#4338ca')
        
    # General health / fitness
    else:
        # Health meter
        metrics = ['Hydration', 'Sleep', 'Activity', 'Mindfulness']
        scores = [75, 65, 80, 70]
        bars = ax.bar(metrics, scores, color=['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b'])
        ax.set_ylim(0, 100)
        ax.set_ylabel('Score (%)')
        ax.set_title("💪 Your Wellness Snapshot", fontsize=12, color='#4338ca')
        for bar, score in zip(bars, scores):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, f'{score}%', ha='center', fontsize=9)
            
    plt.tight_layout()
    return fig

def fig_to_bytes(fig):
    """Convert matplotlib figure to bytes for streamlit display"""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    return buf

# ====================== LLM SETUP ======================
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
    st.selectbox("Model", ["llama-3.3-70b-versatile"], disabled=True)
    temperature = st.slider("Temperature", 0.0, 0.5, 0.2, 0.05)
    st.divider()
    if st.button("🗑️ New Chat", use_container_width=True, type="secondary"):
        st.session_state.messages = []
        st.rerun()

# ====================== MAIN UI ======================
st.markdown("🩺 MediAssist AI", unsafe_allow_html=True)
st.markdown("Your Professional Health & Wellness Guide", unsafe_allow_html=True)
st.markdown("---")

# Display Chat History
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        st.markdown(f'<div class="chat-user">{msg.content}</div>', unsafe_allow_html=True)
    elif isinstance(msg, AIMessage):
        st.markdown(f'<div class="chat-ai">{msg.content}</div>', unsafe_allow_html=True)
        # If the AI message has an associated visualization (stored as metadata), show it
        if hasattr(msg, 'visualization') and msg.visualization:
            st.image(msg.visualization, caption="📊 Generated Visualization", use_column_width=True)

# ====================== CHAT INPUT ======================
if user_input := st.chat_input("Ask about symptoms, exercises, yoga, nutrition, or any health topic..."):
    # Show user message instantly
    st.markdown(f'<div class="chat-user">{user_input}</div>', unsafe_allow_html=True)
    with st.spinner("Thinking medically..."):
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
        
        # Generate visualization based on user query
        fig = create_health_visualization(user_input)
        img_bytes = fig_to_bytes(fig)
        plt.close(fig)  # free memory
        
        # Store AI message with visualization attached
        ai_msg = AIMessage(content=response.content)
        ai_msg.visualization = img_bytes  # custom attribute
        st.session_state.messages.append(HumanMessage(content=user_input))
        st.session_state.messages.append(ai_msg)
        
        # Display AI response and its visualization
        st.markdown(f'<div class="chat-ai">{response.content}</div>', unsafe_allow_html=True)
        st.image(img_bytes, caption="📊 Generated Visualization", use_column_width=True)
        
        st.rerun()

# Footer
st.markdown("""
---
<p style='text-align: center; color: #64748b; font-size: 0.8rem;'>
    MediAssist AI • Not a substitute for professional medical advice • Always consult a doctor
</p>
""", unsafe_allow_html=True)
