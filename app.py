import streamlit as st
import os
import base64
import io
import matplotlib.pyplot as plt
from PIL import Image
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from groq import Groq

# ====================== PAGE CONFIG ======================
st.set_page_config(
    page_title="🩺 MediAssist AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== API SETUP ======================
groq_api = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
if not groq_api:
    st.error("⚠️ GROQ_API_KEY missing! Add it in Streamlit Secrets.")
    st.stop()

groq_client = Groq(api_key=groq_api)

# ====================== SYSTEM PROMPTS ======================
TEXT_SYSTEM_PROMPT = """
You are MediAssist, an elite professional AI Medical Assistant.
Answer only health, medical, fitness, or wellness questions.
If unrelated, politely refuse.
Always end with: "Note: I am an AI, not a licensed doctor. Please consult a qualified healthcare professional for medical advice."
"""

VISION_SYSTEM_PROMPT = """
You are MediAssist Medical Report Analyst. Analyze the uploaded medical report image.
Extract key information: test names, values, reference ranges, abnormalities.
Provide a clear summary. Do not diagnose.
Always end with: "Note: I am an AI, not a doctor. Please consult a qualified healthcare professional."
"""

# ====================== RESIZE IMAGE TO AVOID TOO LARGE ERROR ======================
def resize_image(image_bytes, max_size=(1000, 1000)):
    """Resize image to max dimensions while keeping aspect ratio."""
    img = Image.open(io.BytesIO(image_bytes))
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG", quality=85)
    return buffered.getvalue()

# ====================== VISUALIZATION ENGINE ======================
def create_health_visualization(query: str):
    """Generate a matplotlib figure based on query (only called when user asks)."""
    query_lower = query.lower()
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.set_facecolor('#f0f9ff')
    fig.patch.set_facecolor('#ffffff')
    
    if any(w in query_lower for w in ['exercise', 'yoga', 'pose', 'stretch', 'workout']):
        ax.set_xlim(0, 10); ax.set_ylim(0, 10)
        ax.add_patch(plt.Circle((5, 8), 0.6, color='#3b82f6', ec='#1e293b', lw=2))
        ax.plot([5,5], [7.4,4], color='#3b82f6', lw=3)
        ax.plot([5,3.5], [6,5], color='#3b82f6', lw=3)
        ax.plot([5,6.5], [6,5], color='#3b82f6', lw=3)
        ax.plot([5,3.8], [4,1.8], color='#3b82f6', lw=3)
        ax.plot([5,6.2], [4,1.8], color='#3b82f6', lw=3)
        ax.set_title("🧘 Suggested Pose", fontsize=12, color='#4338ca')
        ax.axis('off')
    elif any(w in query_lower for w in ['knee', 'back', 'shoulder', 'neck', 'hip']):
        part = next((w for w in ['knee','back','shoulder','neck','hip'] if w in query_lower), 'body')
        ax.set_xlim(0,10); ax.set_ylim(0,10)
        ax.plot([5,5],[2,8], 'gray', lw=2)
        ax.plot([3,7],[7,7], 'gray', lw=2)
        ax.plot([2,8],[5,5], 'gray', lw=2)
        if part == 'knee':
            ax.plot(5,3.5,'ro',markersize=20); ax.annotate('Knee', (5,3.5), xytext=(10,10), textcoords='offset points', ha='center', color='red')
        elif part == 'back':
            ax.fill_between([4,6], [4,7], color='red', alpha=0.4); ax.text(5,5.5,'Back',ha='center',color='red')
        elif part == 'shoulder':
            ax.plot(3,7,'ro',markersize=20); ax.plot(7,7,'ro',markersize=20); ax.text(5,7.2,'Shoulders',ha='center',color='red')
        else:
            ax.plot(5,5,'ro',markersize=20); ax.annotate(part.capitalize(), (5,5), ha='center', color='red')
        ax.set_title(f"📍 {part.capitalize()}", fontsize=12, color='#4338ca')
        ax.axis('off')
    elif any(w in query_lower for w in ['diet', 'nutrition', 'calorie', 'protein']):
        labels = ['Carbs', 'Protein', 'Fats', 'Vitamins']
        sizes = [40,30,20,10]
        colors = ['#3b82f6','#10b981','#f59e0b','#8b5cf6']
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.0f%%', startangle=90)
        ax.set_title("🥗 Nutritional Balance", fontsize=12, color='#4338ca')
    else:
        metrics = ['Hydration', 'Sleep', 'Activity', 'Mindfulness']
        scores = [75,65,80,70]
        bars = ax.bar(metrics, scores, color=['#3b82f6','#8b5cf6','#10b981','#f59e0b'])
        ax.set_ylim(0,100)
        ax.set_ylabel('Score (%)')
        ax.set_title("💪 Wellness Snapshot", fontsize=12, color='#4338ca')
        for bar, score in zip(bars, scores):
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+2, f'{score}%', ha='center', fontsize=9)
    plt.tight_layout()
    return fig

def fig_to_bytes(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    return buf

# ====================== LLM SETUP ======================
@st.cache_resource
def get_text_llm():
    return ChatGroq(groq_api_key=groq_api, model_name="llama-3.3-70b-versatile", temperature=0.2)
text_llm = get_text_llm()

# ====================== SESSION STATE ======================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_uploaded" not in st.session_state:
    st.session_state.last_uploaded = None
if "last_text" not in st.session_state:
    st.session_state.last_text = None

# ====================== SIDEBAR ======================
with st.sidebar:
    st.markdown("# 🩺 MediAssist")
    st.caption("Professional Health & Wellness Assistant")
    st.divider()
    if st.button("🗑️ New Chat", use_container_width=True, type="secondary"):
        st.session_state.messages = []
        st.session_state.last_uploaded = None
        st.session_state.last_text = None
        st.rerun()

# ====================== MAIN UI ======================
st.markdown("# 🩺 MediAssist AI")
st.markdown("Your Professional Health & Wellness Guide")
st.markdown("---")

# Display chat history
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        if hasattr(msg, 'image_data'):
            st.markdown(f'<div class="chat-user">📄 [Uploaded Medical Report]</div>', unsafe_allow_html=True)
            st.image(msg.image_data, caption="Uploaded Report", width=200)
            st.markdown(f'<div class="chat-user">*{msg.content}*</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-user">{msg.content}</div>', unsafe_allow_html=True)
    elif isinstance(msg, AIMessage):
        st.markdown(f'<div class="chat-ai">{msg.content}</div>', unsafe_allow_html=True)
        if hasattr(msg, 'visualization') and msg.visualization:
            st.image(msg.visualization, caption="📊 Generated Visualization", use_column_width=True)

# ====================== INPUT AREA ======================
col1, col2 = st.columns([5, 1])
with col1:
    user_input = st.chat_input("Ask about symptoms, exercises, nutrition... or use the 📎 button to upload a medical report")
with col2:
    uploaded_file = st.file_uploader("📎", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

# Process image upload (if new)
if uploaded_file is not None and st.session_state.last_uploaded != uploaded_file.name:
    st.session_state.last_uploaded = uploaded_file.name
    # Resize image to avoid "too large" error
    image_bytes = resize_image(uploaded_file.getvalue())
    human_msg = HumanMessage(content="[Medical Report Image] Please analyze this report.")
    human_msg.image_data = image_bytes
    st.session_state.messages.append(human_msg)
    
    with st.spinner("Analyzing medical report..."):
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        try:
            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": VISION_SYSTEM_PROMPT},
                    {"role": "user", "content": [
                        {"type": "text", "text": "Analyze this medical report."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]}
                ],
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                temperature=0.2,
            )
            analysis = chat_completion.choices[0].message.content
        except Exception as e:
            analysis = f"❌ Error: {str(e)}"
        
        # 🔥 No auto visualization for medical report – only text answer
        ai_msg = AIMessage(content=analysis)
        ai_msg.visualization = None
        st.session_state.messages.append(ai_msg)
    st.rerun()

# Process text input (if new)
elif user_input and st.session_state.last_text != user_input:
    st.session_state.last_text = user_input
    st.session_state.messages.append(HumanMessage(content=user_input))
    with st.spinner("Thinking medically..."):
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", TEXT_SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
        chain = prompt_template | text_llm
        response = chain.invoke({
            "input": user_input,
            "chat_history": st.session_state.messages[:-1]
        })
        
        # 🔥 Only generate visualization if user explicitly asks for it
        viz_keywords = ['visualization', 'visual', 'diagram', 'draw', 'show me', 'graph', 'chart', 'illustrate', 'depict', 'visualise']
        if any(keyword in user_input.lower() for keyword in viz_keywords):
            fig = create_health_visualization(user_input)
            img_bytes = fig_to_bytes(fig)
            plt.close(fig)
            ai_msg = AIMessage(content=response.content)
            ai_msg.visualization = img_bytes
        else:
            ai_msg = AIMessage(content=response.content)
            ai_msg.visualization = None
        
        st.session_state.messages.append(ai_msg)
    st.rerun()

# CSS for chat bubbles
st.markdown("""
<style>
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
</style>
""", unsafe_allow_html=True)

# Footer
st.markdown("""
---
<p style='text-align: center; color: #64748b; font-size: 0.8rem;'>
    MediAssist AI • Not a substitute for professional medical advice • Always consult a doctor
</p>
""", unsafe_allow_html=True)
