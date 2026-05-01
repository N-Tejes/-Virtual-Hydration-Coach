from flask import Flask, request, jsonify, render_template
from google import genai
from dotenv import load_dotenv
import os

# Load API key from .env file (keeps it out of source code)
load_dotenv()

app = Flask(__name__)

# 🔑 Uses GEMINI_API_KEY env variable (set it before running the app)
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

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
        return jsonify({"error": "GEMINI_API_KEY is not configured. "
                        "Set it in the Render dashboard under Environment."}), 500
    try:
        data = request.get_json()

        user_message = data.get("message")
        history = data.get("history", [])

        # 🧠 Build contents list for Gemini
        contents = [
            {"role": "user", "parts": [{"text": SYSTEM_PROMPT}]},
            {"role": "model", "parts": [{"text": "Got it. I am your Hydration Coach."}]}
        ]

        for msg in history:
            contents.append({
                "role": msg["role"],
                "parts": [{"text": msg["parts"]}]
            })

        # Add new message
        contents.append({
            "role": "user",
            "parts": [{"text": user_message}]
        })

        # Generate response
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=contents
        )

        return jsonify({"reply": response.text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)