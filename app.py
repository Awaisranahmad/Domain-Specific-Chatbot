• Stand straight  
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
