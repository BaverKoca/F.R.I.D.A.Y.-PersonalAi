# app.py
from flask import Flask, request, jsonify, render_template
import requests
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from newspaper import Article
from functools import lru_cache
import threading

load_dotenv()

app = Flask(__name__)

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', 'your_google_api_key')
GOOGLE_CSE_ID = os.getenv('GOOGLE_CSE_ID', 'your_custom_search_engine_id')

def google_search(query, num_results=2):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "q": query,
        "num": num_results
    }
    resp = requests.get(url, params=params)
    data = resp.json()
    if "items" in data and len(data["items"]) > 0:
        return [
            {
                "title": item.get("title", "No title"),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", "No answer found.")
            }
            for item in data["items"]
        ]
    return []

def summarize_chunk(chunk, user_question, timeout=30):
    prompt = f"Summarize the following web content for answering the user's question: {user_question}\n\nContent:\n{chunk}"
    result = {'summary': ''}
    def worker():
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
                timeout=timeout
            )
            data = response.json()
            result['summary'] = data["choices"][0]["message"]["content"].strip()
        except Exception:
            result['summary'] = ''
    t = threading.Thread(target=worker)
    t.start()
    t.join(timeout)
    return result['summary']

def fetch_main_text(url, user_question=None, snippet_fallback=None):
    try:
        article = Article(url)
        article.download()
        article.parse()
        # Remove boilerplate: filter out very short lines and lines with menu/footer/ads keywords
        lines = [line.strip() for line in article.text.split('\n') if len(line.strip()) > 40]
        keywords = ["menu", "footer", "advert", "cookie", "privacy", "subscribe", "sign up", "login", "copyright", "all rights reserved", "contact", "newsletter", "terms", "policy", "related articles", "share"]
        filtered = [line for line in lines if not any(kw in line.lower() for kw in keywords)]
        cleaned = '\n'.join(filtered)
        # Chunking and summarization: only use the first chunk (faster)
        chunk_size = 3200
        chunks = [cleaned[i:i+chunk_size] for i in range(0, len(cleaned), chunk_size)]
        if not chunks or not chunks[0].strip():
            return snippet_fallback or "No content found."
        chunk = chunks[0]  # Only summarize the first chunk
        if user_question:
            summary = summarize_chunk(chunk, user_question, timeout=30)
            if summary:
                return summary
            else:
                return snippet_fallback or chunk
        else:
            return chunk
    except Exception:
        return snippet_fallback or "No content found."

# Simple in-memory cache for repeated queries (not persistent, resets on restart)
@lru_cache(maxsize=128)
def cached_fetch_main_text(url, user_question, snippet_fallback):
    return fetch_main_text(url, user_question, snippet_fallback)

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
    show_keywords = ["show", "göster", "montrer", "zeigen"]
    user_words = [w.strip(".,!?") for w in user_input.lower().split()]
    open_images = any(kw in user_words for kw in show_keywords)

    if any(word in user_input.lower() for word in search_keywords):
        more_keywords = ["more", "daha fazla", "mehr", "plus"]
        num_results = 2
        if any(word in user_input.lower() for word in more_keywords):
            num_results = 3
        search_results = google_search(user_input, num_results=num_results)
        snippets = []
        first_link = None
        for idx, item in enumerate(search_results):
            link = item.get("link", "")
            snippet = item.get("snippet", "No snippet available.")
            if idx == 0:
                first_link = link
            if link:
                # Fetch and summarize main content, fallback to snippet
                text = cached_fetch_main_text(link, user_input, snippet)
                if text:
                    snippets.append(f"Source: {link}\n{text}")
        if not snippets:
            return jsonify({"response": "Sorry, I couldn't find relevant web results. Please try rephrasing your question.", "open_images": open_images, "query": user_input})
        context = '\n\n'.join(snippets)
        prompt = f"Use the following web sources to answer the user's question as truthfully as possible.\n\n{context}\n\nUser question: {user_input}"
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
                timeout=60
            )
            result = response.json()
            ai_text = result["choices"][0]["message"]["content"].strip()
            return jsonify({"response": ai_text, "open_images": open_images, "query": user_input})
        except Exception as e:
            return jsonify({"response": f"Error: {str(e)}", "open_images": open_images, "query": user_input})
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
        return jsonify({"response": ai_text, "open_images": False, "query": user_input})
    except Exception as e:
        return jsonify({"response": f"Error: {str(e)}", "open_images": False, "query": user_input})

if __name__ == "__main__":
    app.run(debug=True)
