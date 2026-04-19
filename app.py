import streamlit as st
import os

# --- Imports ---
try:
    from langchain_groq import ChatGroq
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.messages import HumanMessage, AIMessage
except ModuleNotFoundError as e:
    st.error(f"🚨 Module missing: {e}. Please check requirements.txt")
    st.stop()

# Try to import matplotlib (optional but recommended)
try:
    import matplotlib.pyplot as plt
    import io
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    st.info("💡 Tip: Install matplotlib for better visualizations: `pip install matplotlib`")

# ====================== PAGE CONFIG ======================
st.set_page_config(
    page_title="🩺 MediAssist AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== CSS STYLES ======================
st.markdown("""
<style>
    .stApp { background: #ffffff; color: #1e293b; }
    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; color: #4338ca; }
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
    .stButton>button { border-radius: 12px; height: 52px; font-weight: 600; }
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
Answer only health, medical, fitness, or wellness questions.
If unrelated, politely refuse.
Always end with: "Note: I am an AI, not a licensed doctor. Please consult a qualified healthcare professional for medical advice."
"""

# ====================== VISUALIZATION FUNCTIONS ======================
if MATPLOTLIB_AVAILABLE:
    def create_matplotlib_viz(query: str):
        q = query.lower()
        fig, ax = plt.subplots(figsize=(6, 4))
        fig.patch.set_facecolor('#f8fafc')
        ax.set_facecolor('#f8fafc')
        
        if any(w in q for w in ['exercise', 'yoga', 'pose', 'stretch', 'workout']):
            ax.set_xlim(0, 10); ax.set_ylim(0, 10)
            ax.add_patch(plt.Circle((5, 8.5), 0.6, color='#3b82f6', ec='#1e293b', lw=2))
            ax.plot([5,5], [7.9, 4.5], color='#3b82f6', lw=3)
            ax.plot([5, 3.2], [6.5, 5.2], color='#3b82f6', lw=3)
            ax.plot([5, 6.8], [6.5, 5.2], color='#3b82f6', lw=3)
            ax.plot([5, 3.5], [4.5, 1.5], color='#3b82f6', lw=3)
            ax.plot([5, 6.5], [4.5, 1.5], color='#3b82f6', lw=3)
            ax.set_title("🧘 Suggested Pose", fontsize=12, color='#4338ca')
            ax.axis('off')
        elif any(w in q for w in ['knee', 'back', 'shoulder', 'neck', 'hip']):
            part = next((w for w in ['knee', 'back', 'shoulder', 'neck', 'hip'] if w in q), 'body')
            ax.plot([5,5],[2,8], 'gray', lw=2)
            ax.plot([3,7],[7,7], 'gray', lw=2)
            ax.plot([2,8],[5,5], 'gray', lw=2)
            if part == 'knee':
                ax.plot(5, 3.5, 'ro', markersize=20)
                ax.annotate('Knee', (5, 3.5), ha='center', color='red')
            elif part == 'back':
                ax.fill_between([4,6], [4,7], color='red', alpha=0.4)
                ax.text(5, 5.5, 'Back', ha='center', color='red')
            elif part == 'shoulder':
                ax.plot(3,7, 'ro', markersize=20); ax.plot(7,7, 'ro', markersize=20)
                ax.text(5, 7.2, 'Shoulders', ha='center', color='red')
            else:
                ax.plot(5,5, 'ro', markersize=20)
                ax.annotate(part.capitalize(), (5,5), ha='center', color='red')
            ax.set_title(f"📍 {part.capitalize()}", fontsize=12, color='#4338ca')
            ax.axis('off')
        elif any(w in q for w in ['diet', 'nutrition', 'calorie', 'protein']):
            labels = ['Carbs', 'Protein', 'Fats', 'Vitamins']
            sizes = [40, 30, 20, 10]
            colors = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6']
            ax.pie(sizes, labels=labels, colors=colors, autopct='%1.0f%%', startangle=90)
            ax.set_title("🥗 Nutritional Balance", fontsize=12, color='#4338ca')
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
    def create_text_viz(query: str) -> str:
        q = query.lower()
        if any(w in q for w in ['exercise', 'yoga', 'pose', 'stretch', 'workout']):
            return "**🧘 Visualization**\n\n• Stand tall, feet hip-width\n• Raise arms overhead\n• Breathe deeply – 5 breaths\n*Gentle movement recommended*"
        elif any(w in q for w in ['knee', 'back', 'shoulder', 'neck', 'hip']):
            part = next((w for w in ['knee', 'back', 'shoulder', 'neck', 'hip'] if w in q), 'body')
            return f"**📍 Focus: {part.capitalize()}**\n\n• 🟢 Gentle movement OK\n• 🟡 Avoid sudden twisting\n• 🔴 If pain persists, see doctor"
        elif any(w in q for w in ['diet', 'nutrition', 'calorie', 'protein']):
            return "**🥗 Balanced Plate**\n\n🍚 Carbs ████████░░ 40%\n🍗 Protein ██████░░░░ 30%\n🥑 Fats ████░░░░░░ 20%\n🥦 Fiber ██░░░░░░░░ 10%"
        else:
            return "**💪 Wellness Check**\n\n💧 Hydration ███████░░░ 70%\n😴 Sleep ██████░░░░ 60%\n🚶 Activity ████████░░ 80%\n🧠 Mindfulness ██████░░░░ 60%"

# ====================== LLM SETUP ======================
@st.cache_resource
def get_medical_llm():
    return ChatGroq(groq_api_key=groq_api, model_name="llama-3.3-70b-versatile", temperature=0.2)
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

# ====================== MAIN UI ======================
st.markdown("# 🩺 MediAssist AI")
st.markdown("Your Professional Health & Wellness Guide")
st.markdown("---")

# Display chat history (without trying to store visualizations in messages)
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        st.markdown(f'<div class="chat-user">{msg.content}</div>', unsafe_allow_html=True)
    elif isinstance(msg, AIMessage):
        st.markdown(f'<div class="chat-ai">{msg.content}</div>', unsafe_allow_html=True)
        # If we had stored a viz with this message, show it (but we'll handle separately)
        if hasattr(msg, 'viz_data'):
            if MATPLOTLIB_AVAILABLE and isinstance(msg.viz_data, bytes):
                st.image(msg.viz_data, caption="📊 Visualization", use_column_width=True)
            else:
                st.markdown(msg.viz_data)

# ====================== CHAT INPUT ======================
user_input = st.chat_input("Ask about symptoms, exercises, yoga, nutrition...")

if user_input:
    # Display user message
    st.markdown(f'<div class="chat-user">{user_input}</div>', unsafe_allow_html=True)
    
    with st.spinner("Analyzing..."):
        # Generate AI response
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
        
        # Generate visualization based on user input
        if MATPLOTLIB_AVAILABLE:
            fig = create_matplotlib_viz(user_input)
            viz_bytes = fig_to_bytes(fig)
            plt.close(fig)
            viz_data = viz_bytes
        else:
            viz_data = create_text_viz(user_input)
        
        # Display AI response
        st.markdown(f'<div class="chat-ai">{response.content}</div>', unsafe_allow_html=True)
        
        # Display visualization immediately
        if MATPLOTLIB_AVAILABLE:
            st.image(viz_bytes, caption="📊 Visualization", use_column_width=True)
        else:
            st.markdown(viz_data)
        
        # Save to session state (store viz data for history)
        ai_msg = AIMessage(content=response.content)
        ai_msg.viz_data = viz_data
        st.session_state.messages.append(HumanMessage(content=user_input))
        st.session_state.messages.append(ai_msg)
        
        st.rerun()
