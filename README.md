# FRIDAY - Personal AI Voice Assistant

FRIDAY is a professional AI voice assistant web app powered by your local Nous-Hermes LLM. Speak your question, get an instant AI response, and see relevant Google search results—all in a clean, user-friendly interface.

---

![Image](https://github.com/user-attachments/assets/eb56e656-171e-42c5-abb0-e4b7bbf44567)

---

## 🚀 Features
- 🎤 **Voice Recognition:** Activate and stop with a button
- 💬 **Instant AI Answers:** Powered by your local Nous-Hermes LLM
- 🌐 **Automatic Google Search:** For every query
- 🖥️ **Minimalist, Responsive UI:** Modern and user-friendly
- 🔒 **Privacy-First:** No data stored, ever

---

## 🛠️ Getting Started

### Prerequisites
- Python 3.8+
- Local Nous-Hermes LLM running (OpenAI-compatible API, e.g., http://localhost:5001)

### Installation
1. **Clone the repository:**
   ```sh
   git clone https://github.com/BaverKoca/F.R.I.D.A.Y.-PersonalAi.git
   cd F.R.I.D.A.Y.-PersonalAi
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **Start your local Nous-Hermes LLM server:**
   - Ensure your model is running and accessible at `http://localhost:5001/v1/chat/completions`.
4. **Run the app:**
   ```sh
   python app.py
   ```
5. **Open your browser:**
   - Go to [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 💡 Usage
- Click **Activate Voice** and ask your question.
- Click **Stop** to end recognition early.
- The AI will answer and a Google search will open in a new tab for your query.

---

## 🧰 Technologies Used
- **Python, Flask**
- **Local Nous-Hermes LLM** (OpenAI-compatible API)
- **JavaScript** (Web Speech API)
- **HTML5 & CSS3**

---

## 📄 License
MIT License

---

> *Created by Baver Koca, 2025.*
