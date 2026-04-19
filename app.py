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

# Try to import matplotlib (optional)
try:
    import matplotlib.pyplot as plt
    import io
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    st.warning("⚠️ matplotlib not installed. Using text-based visualizations. Run `pip install matplotlib` for better visuals.")

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

# ====================== ADVANCED VISUALIZATION ENGINE ======================
if MATPLOTLIB_AVAILABLE:
    def create_matplotlib_viz(query: str):
        """Generate a matplotlib figure based on query."""
        q = query.lower()
        fig, ax = plt.subplots(figsize=(6, 4))
        fig.patch.set_facecolor('#f8fafc')
        ax.set_facecolor('#f8fafc')
        
        # Exercise / Yoga
        if any(word in q for word in ['exercise', 'yoga', 'pose', 'stretch', 'workout', 'asana']):
            ax.set_xlim(0, 10)
            ax.set_ylim(0, 10)
            # Head
            circle = plt.Circle((5, 8.5), 0.6, color='#3b82f6', ec='#1e293b', lw=2)
            ax.add_patch(circle)
            # Torso
            ax.plot([5,5], [7.9, 4.5], color='#3b82f6', lw=3)
            # Arms (dynamic)
            ax.plot([5, 3.2], [6.5, 5.2], color='#3b82f6', lw=3)
            ax.plot([5, 6.8], [6.5, 5.2], color='#3b82f6', lw=3)
            # Legs
            ax.plot([5, 3.5], [4.5, 1.5], color='#3b82f6', lw=3)
            ax.plot([5, 6.5], [4.5, 1.5], color='#3b82f6', lw=3)
            ax.set_title("🧘 Suggested Pose (Stick Figure)", fontsize=12, color='#4338ca')
            ax.axis('off')
            
        # Body part
        elif any(word in q for word in ['knee', 'back', 'shoulder', 'neck', 'hip', 'ankle']):
            part = next((w for w in ['knee', 'back', 'shoulder', 'neck', 'hip', 'ankle'] if w in q), 'body')
            # Body outline
            ax.plot([5,5],[2,8], 'gray', lw=2)
            ax.plot([3,7],[7,7], 'gray', lw=2)
            ax.plot([2,8],[5,5], 'gray', lw=2)
            # Highlight
            if part == 'knee':
                ax.plot(5, 3.5, 'ro', markersize=20)
                ax.annotate('Knee', (5, 3.5), textcoords="offset points", xytext=(10,10), ha='center', color='red', fontweight='bold')
            elif part == 'back':
                ax.fill_between([4,6], [4,4], [7,7], color='red', alpha=0.4)
                ax.text(5, 5.5, 'Back', ha='center', color='red', fontweight='bold')
            elif part == 'shoulder':
                ax.plot(3,7, 'ro', markersize=20)
                ax.plot(7,7, 'ro', markersize=20)
                ax.text(5, 7.2, 'Shoulders', ha='center', color='red', fontweight='bold')
            else:
                ax.plot(5,5, 'ro', markersize=20)
                ax.annotate(part.capitalize(), (5,5), textcoords="offset points", xytext=(0,10), ha='center', color='red', fontweight='bold')
            ax.set_title(f"📍 {part.capitalize()} Highlight", fontsize=12, color='#4338ca')
            ax.axis('off')
            
        # Nutrition
        elif any(word in q for word in ['diet', 'nutrition', 'calorie', 'protein', 'vitamin']):
            labels = ['Carbs', 'Proteins', 'Fats', 'Vitamins']
            sizes = [40, 30, 20, 10]
            colors = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6']
            ax.pie(sizes, labels=labels, colors=colors, autopct='%1.0f%%', startangle=90, wedgeprops={'edgecolor': 'white'})
            ax.set_title("🥗 Nutritional Balance", fontsize=12, color='#4338ca')
            
        # General health
        else:
            metrics = ['Hydration', 'Sleep', 'Activity', 'Mindfulness']
            scores = [75, 65, 80, 70]
            bars = ax.bar(metrics, scores, color=['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b'])
            ax.set_ylim(0, 100)
            ax.set_ylabel('Score (%)')
            ax.set_title("💪 Wellness Snapshot", fontsize=12, color='#4338ca')
            for bar, score in zip(bars, scores):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, f'{score}%', ha='center', fontsize=9)
                
        plt.tight_layout()
        return fig

    def fig_to_bytes(fig):
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        return buf
else:
    # Improved text-based fallback visualizations
    def create_text_viz(query: str) -> str:
        q = query.lower()
        if any(word in q for word in ['exercise', 'yoga', 'pose', 'stretch', 'workout']):
            return """
**🧘 Visualization (Mountain Pose – Tadasana)**  
