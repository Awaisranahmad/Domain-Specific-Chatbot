*Fill half with veggies, quarter protein, quarter carbs.*
"""
        else:
            return """
💪 Wellness Tips 
- 💧 Hydrate: 8 glasses/day  
- 😴 Sleep: 7-9 hours  
- 🚶 Move: 30 min daily  
- 🧠 Relax: meditate 5 min  
"""

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
        if hasattr(msg, 'viz_data'):
            if MATPLOTLIB_AVAILABLE and isinstance(msg.viz_data, bytes):
                st.image(msg.viz_data, caption="📊 Generated Visualization", use_column_width=True)
            elif isinstance(msg.viz_data, str):
                st.markdown(msg.viz_data, unsafe_allow_html=False)

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
        
        # Generate visualization
        if MATPLOTLIB_AVAILABLE:
            fig = create_matplotlib_viz(user_input)
            viz_bytes = fig_to_bytes(fig)
            plt.close(fig)
            viz_data = viz_bytes
        else:
            viz_data = create_text_viz(user_input)
        
        # Store AI message
        ai_msg = AIMessage(content=response.content)
        ai_msg.viz_data = viz_data
        st.session_state.messages.append(HumanMessage(content=user_input))
        st.session_state.messages.append(ai_msg)
        
        # Display response and viz
        st.markdown(f'<div class="chat-ai">{response.content}</div>', unsafe_allow_html=True)
        if MATPLOTLIB_AVAILABLE:
            st.image(viz_bytes, caption="📊 Generated Visualization", use_column_width=True)
        else:
            st.markdown(viz_data, unsafe_allow_html=False)
        
        st.rerun()

# Footer
st.markdown("""
---
<p style='text-align: center; color: #64748b; font-size: 0.8rem;'>
    MediAssist AI • Not a substitute for professional medical advice • Always consult a doctor
</p>
""", unsafe_allow_html=True)
