from flask import Flask, request, jsonify, render_template
from groq import Groq
from dotenv import load_dotenv
import os

# Load API key from .env file (keeps it out of source code)
load_dotenv()

app = Flask(__name__)

# 🔑 Uses GROQ_API_KEY env variable
api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None

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
    if not client:
        return jsonify({"error": "GROQ_API_KEY is not configured. "
                        "Set it in the Render dashboard under Environment."}), 500
    try:
        data = request.get_json()

        user_message = data.get("message")
        history = data.get("history", [])

        # 🧠 Build messages list for Groq (OpenAI-compatible format)
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

        # Generate response using Groq (Llama 3)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
        )

        reply = response.choices[0].message.content
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)