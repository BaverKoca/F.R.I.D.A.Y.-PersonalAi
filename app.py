# app.py
from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    user_input = data.get("question", "")

    try:
        # Call local Nous-Hermes LLM (OpenAI-compatible endpoint)
        response = requests.post(
            "http://localhost:5001/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json={
                "model": "nous-hermes",
                "messages": [
                    {"role": "user", "content": user_input}
                ]
            },
            timeout=60
        )
        result = response.json()
        ai_text = result["choices"][0]["message"]["content"].strip()
        return jsonify({"response": ai_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
