from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import requests as http_client
import os

# Load API key from .env file (keeps it out of source code)
load_dotenv()

app = Flask(__name__)

# 🔑 Uses GROQ_API_KEY env variable
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = """
You are a virtual Hydration Coach.

Rules:
- Only answer hydration-related questions.
- Reject unrelated questions politely.
- Give clear and friendly answers.
"""

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    if not GROQ_API_KEY:
        return jsonify({"error": "GROQ_API_KEY is not configured. "
                        "Set it in the Render dashboard under Environment."}), 500
    try:
        data = request.get_json()

        user_message = data.get("message")
        history = data.get("history", [])

        # 🧠 Build messages list (OpenAI-compatible format)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
        ]

        for msg in history:
            role = "assistant" if msg["role"] == "model" else msg["role"]
            messages.append({
                "role": role,
                "content": msg["parts"]
            })

        # Add new message
        messages.append({
            "role": "user",
            "content": user_message
        })

        # Call Groq API directly via HTTP
        response = http_client.post(
            GROQ_API_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1024,
            },
            timeout=30,
        )

        if response.status_code != 200:
            return jsonify({"error": f"API error ({response.status_code}): {response.text}"}), 500

        result = response.json()
        reply = result["choices"][0]["message"]["content"]
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)