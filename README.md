
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
- 🎨 **Modern UI** – Clean dark theme, chat bubbles, responsive layout.

---

## 🧠 How It Works

- **Text queries** are processed by Groq’s `openai/gpt-oss-120b` model (with automatic fallback to `openai/gpt-oss-20b` if the primary model is ever retired or renamed).
- **Medical report images** are resized automatically (to avoid size limits) and sent to Groq’s vision model `meta-llama/llama-4-maverick-17b-128e-instruct` for analysis.
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
pip install -r requirements.txt
```

---

## 🚀 Setup & Run

1. **Clone the repository**

```bash
git clone https://github.com/Awaisranahmad/Domain-Specific-Chatbot.git
cd Domain-Specific-Chatbot
```

2. **Set up your Groq API key**

   - Copy the example secrets file and fill in your own key:

     ```bash
     cp .streamlit/secrets.toml.example .streamlit/secrets.toml
     ```

     ```toml
     GROQ_API_KEY = "your-groq-api-key-here"
     ```

   - `.streamlit/secrets.toml` is git-ignored, so your key never gets committed.
   - Alternatively, set the environment variable `GROQ_API_KEY`.
   - Optional overrides: `GROQ_TEXT_MODEL` and `GROQ_VISION_MODEL` (in secrets or environment) to change the models without editing code.

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
- **LLM** – Groq (`openai/gpt-oss-120b` for text, Llama 4 Maverick 17B for vision)
- **Visualisation** – Matplotlib
- **Image Processing** – Pillow (PIL)
- **Language** – Python 3.10+

---

## 🧪 Tests

Unit tests cover the model defaults, the model-fallback logic, HTML escaping, urgent-symptom detection, vital classification, and image upload validation. They use stubbed `streamlit`/`groq` modules, so no API key or network is needed:

```bash
python3 -m unittest discover -s tests -v
```

16 tests, all passing.

---

## 🔒 Security

- **No HTML injection:** every user-typed value (chat messages, patient profile, known conditions, vitals, uploaded file names) and every AI-generated reply is HTML-escaped before it is rendered with `unsafe_allow_html=True`.
- **API key protection:** `.streamlit/secrets.toml` is git-ignored; only `.streamlit/secrets.toml.example` (placeholder key) is committed.
- **Upload validation:** report images over 10 MB are rejected, and corrupt/non-image uploads show a friendly error instead of crashing the app.
- **No secrets, no `eval()`, no SQL** in this codebase.

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
Feel free to check the [issues page](https://github.com/Awaisranahmad/Domain-Specific-Chatbot/issues).

---

## 📋 Changelog

- **2026-11-26 — Security & reliability hardening:**
  - Fixed retired Groq models: text default `llama-3.3-70b-versatile` (shut down 2026-08-16) → `openai/gpt-oss-120b`, with automatic fallback to `openai/gpt-oss-20b` on a model-not-found error; vision default confirmed as the live `meta-llama/llama-4-maverick-17b-128e-instruct` (Scout was shut down 2026-07-17).
  - Fixed stored-XSS risk: all user/AI-controlled text rendered with `unsafe_allow_html=True` is now HTML-escaped (`safe_html` helper).
  - Report image uploads are now validated (max 10 MB, corrupt files rejected with a friendly error instead of crashing the app).
  - Added `.gitignore` (protects `.streamlit/secrets.toml` + `.env`), `.streamlit/secrets.toml.example`, MIT `LICENSE`, and a 16-test `tests/` suite (`python3 -m unittest discover -s tests -v`).

---

**Made with ❤️ for better health awareness**
