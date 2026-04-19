
# 🩺 MediAssist AI

**Your Personal Health & Wellness AI Assistant**

MediAssist AI is a powerful, intelligent chatbot that provides professional, empathetic, and accurate information about health, fitness, nutrition, and medical topics. It supports both text‑based queries and **medical report image analysis** using advanced AI models from Groq. Visualizations (graphs, stick figures, body highlights) are generated **only when you ask for them** – no auto‑clutter.

---

## ✨ Features

- 🤖 **AI‑powered medical Q&A** – Get instant, reliable answers about symptoms, exercises, yoga, diet, medications, and general wellness.
- 🖼️ **Medical report image analysis** – Upload a photo of a lab report or prescription; the AI extracts key values, reference ranges, and highlights abnormalities.
- 📊 **On‑demand visualizations** – Ask for a “diagram”, “chart”, “stick figure”, or “visualization” to see relevant graphs (e.g., nutrition pie chart, body part highlight, exercise pose).
- 💬 **Chat history** – Full conversation history is saved during the session.
- 🗑️ **New Chat** – Clear the conversation with one click.
- 🌐 **Streamlit Cloud ready** – Works seamlessly on Streamlit Community Cloud.
- 🎨 **Modern UI** – Clean light theme, chat bubbles, responsive layout.

---

## 🧠 How It Works

- **Text queries** are processed by Groq’s `llama-3.3-70b-versatile` model.
- **Medical report images** are resized automatically (to avoid size limits) and sent to Groq’s vision model `meta-llama/llama-4-scout-17b-16e-instruct` for analysis.
- **Visualizations** are created using `matplotlib` (stick figures, body maps, pie charts, bar graphs) **only when the user explicitly asks** (keywords like “show me a diagram”, “visualize”, “draw”, “graph”).
- All data stays within the session – no external storage.

---

## 📦 Requirements

- Python 3.10 or higher
- Groq API key ([Get one for free](https://console.groq.com/))

### Required Python packages

```
streamlit
langchain-groq
langchain-core
matplotlib
pillow
groq
```

Install them with:

```bash
pip install streamlit langchain-groq langchain-core matplotlib pillow groq
```

---

## 🚀 Setup & Run

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/medicassist-ai.git
cd medicassist-ai
```

2. **Set up your Groq API key**

   - Create a file named `.streamlit/secrets.toml` in the project root and add:

     ```toml
     GROQ_API_KEY = "your-groq-api-key-here"
     ```

   - Alternatively, you can set an environment variable `GROQ_API_KEY`.

3. **Run the app**

```bash
streamlit run app.py
```

4. **Open your browser** at `http://localhost:8501` and start chatting!

---

## 📖 Usage Examples

### 💬 Text‑only conversation

> **You:** What are the benefits of drinking warm water with lemon in the morning?  
> **MediAssist:** [gives a detailed, empathetic answer with disclaimer]

### 🖼️ Medical report analysis

1. Click the **📎 button** next to the chat input.
2. Upload a photo of your blood test report or prescription.
3. The AI will extract and summarise the key findings.

### 📊 Ask for a visualization

> **You:** Show me a visualization of a healthy diet plate.  
> **MediAssist:** [answers text + displays a pie chart with macros]

> **You:** Draw a stick figure for a yoga pose that helps back pain.  
> **MediAssist:** [text + a stick‑figure diagram]

> **You:** Visualize the wellness snapshot.  
> **MediAssist:** [text + bar chart of hydration, sleep, activity, mindfulness]

> **You:** What is the normal range for thyroid? (no chart)  
> **MediAssist:** [text only – no automatic graph]

---

## 🛠️ Tech Stack

- **Frontend & Framework** – Streamlit
- **LLM** – Groq (Llama 3.3 70B for text, Llama 4 Scout 17B for vision)
- **Visualisation** – Matplotlib
- **Image Processing** – Pillow (PIL)
- **Language** – Python 3.10+

---

## ⚠️ Important Disclaimer

> **MediAssist AI is an AI assistant, not a licensed medical professional.**  
> All information provided is for educational and informational purposes only.  
> Always consult a qualified healthcare provider for medical advice, diagnosis, or treatment.

---

## 📄 License

This project is open‑source and available under the [MIT License](LICENSE).

---

## 🙏 Acknowledgements

- [Groq](https://groq.com/) for high‑performance LLM APIs.
- [Streamlit](https://streamlit.io/) for the amazing web app framework.
- [LangChain](https://www.langchain.com/) for simplifying LLM orchestration.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!  
Feel free to check the [issues page](https://github.com/yourusername/medicassist-ai/issues).

---

**Made with ❤️ for better health awareness**
```

You can adjust the GitHub repository link and any other details to match your actual project. This README is clear, feature‑complete, and inviting for users.
