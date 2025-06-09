# FRIDAY - Personal AI Voice Assistant

FRIDAY is a minimalist, modern, and professional AI voice assistant web app powered by Google Gemini Pro. Speak your question, get an instant AI response, and see relevant Google search results—all in a clean, user-friendly interface.

## Features
- 🎤 Voice recognition (activate and stop with a button)
- 💬 Instant AI-powered answers (using Gemini Pro)
- 🌐 Automatic Google search for every query
- 🖥️ Minimalist, responsive, and modern UI
- 🔒 No data stored—your privacy is respected

## Demo
![FRIDAY Screenshot](screenshot.png)

## Getting Started

### Prerequisites
- Python 3.8+
- A Google Gemini API key

### Installation
1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/PersonalAi-FRIDAY-V2.git
   cd PersonalAi-FRIDAY-V2
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **Set up your API key:**
   - Copy your Gemini API key into `config.py` as `GEMINI_API_KEY = "your-key-here"`

4. **Run the app:**
   ```sh
   python app.py
   ```
5. **Open your browser:**
   - Go to `http://127.0.0.1:5000`

## Usage
- Click **Activate Voice** and ask your question.
- Click **Stop** to end recognition early.
- The AI will answer and a Google search will open in a new tab for your query.

## Technologies Used
- Python, Flask
- Google Gemini Pro API
- JavaScript (Web Speech API)
- HTML5 & CSS3

## License
MIT License

---

*Created by Baver Koca, 2025.*