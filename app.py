# app.py
from flask import Flask, request, jsonify, render_template
import requests
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from newspaper import Article

load_dotenv()

app = Flask(__name__)

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', 'your_google_api_key')
GOOGLE_CSE_ID = os.getenv('GOOGLE_CSE_ID', 'your_custom_search_engine_id')

def google_search(query):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "q": query,
        "num": 1
    }
    resp = requests.get(url, params=params)
    data = resp.json()
    if "items" in data and len(data["items"]) > 0:
        snippet = data["items"][0].get("snippet", "No answer found.")
        return snippet
    return "No answer found."

def fetch_main_text(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        # Remove boilerplate: filter out very short lines and lines with menu/footer/ads keywords
        lines = [line.strip() for line in article.text.split('\n') if len(line.strip()) > 40]
        keywords = ["menu", "footer", "advert", "cookie", "privacy", "subscribe", "sign up", "login", "copyright", "all rights reserved", "contact", "newsletter", "terms", "policy", "related articles", "share"]
        filtered = [line for line in lines if not any(kw in line.lower() for kw in keywords)]
        cleaned = '\n'.join(filtered)
        return cleaned[:1000]
    except Exception:
        return ""

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    user_input = data.get("question", "")

    # Multilingual search keywords for Turkish, German, French, and English
    search_keywords = [
        # English
        "who", "what", "when", "where", "why", "how", "define", "information", "search", "find", "show", "weather", "news", "capital", "population", "distance", "meaning", "explain",
        # Turkish
        "kim", "ne", "ne zaman", "nerede", "neden", "nasıl", "tanımla", "bilgi", "ara", "bul", "göster", "hava durumu", "haberler", "başkent", "nüfus", "mesafe", "anlam", "açıkla",
        # German
        "wer", "was", "wann", "wo", "warum", "wie", "definieren", "informationen", "suchen", "finden", "zeigen", "wetter", "nachrichten", "hauptstadt", "bevölkerung", "entfernung", "bedeutung", "erklären",
        # French
        "qui", "quoi", "quand", "où", "pourquoi", "comment", "définir", "information", "rechercher", "trouver", "montrer", "météo", "nouvelles", "capitale", "population", "distance", "signification", "expliquer",
    ]
    if any(word in user_input.lower() for word in search_keywords):
        # Google search for top 3 results (no domain filtering)
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": GOOGLE_API_KEY,
            "cx": GOOGLE_CSE_ID,
            "q": user_input,
            "num": 3
        }
        resp = requests.get(url, params=params)
        data = resp.json()
        snippets = []
        if "items" in data:
            for item in data["items"]:
                link = item.get("link")
                if link:
                    text = fetch_main_text(link)
                    if text:
                        snippets.append(f"Source: {link}\n{text}")
        context = '\n\n'.join(snippets)
        prompt = f"Use the following web sources to answer the user's question as truthfully as possible.\n\n{context}\n\nUser question: {user_input}"
        # Call LLM with web context
        try:
            response = requests.post(
                "http://localhost:11434/v1/chat/completions",
                headers={"Content-Type": "application/json"},
                json={
                    "model": "nous-hermes",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                },
                timeout=120
            )
            result = response.json()
            ai_text = result["choices"][0]["message"]["content"].strip()
            return jsonify({"response": ai_text})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    try:
        # Call local Nous-Hermes LLM via Ollama (OpenAI-compatible endpoint)
        response = requests.post(
            "http://localhost:11434/v1/chat/completions",
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
