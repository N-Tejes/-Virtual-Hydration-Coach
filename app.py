from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
import os

app = Flask(__name__)

# 🔑 Uses GEMINI_API_KEY env variable (set it on your deployment platform)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY", "AIzaSyA-rk9QOMU6ksYYtxE0BNY9jcfwufKEi3M"))

model = genai.GenerativeModel("gemini-flash-latest")

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
    try:
        data = request.get_json()

        user_message = data.get("message")
        history = data.get("history", [])

        # 🧠 Convert history to Gemini format
        chat_history = [
            {"role": "user", "parts": [SYSTEM_PROMPT]},
            {"role": "model", "parts": ["Got it. I am your Hydration Coach."]}
        ]

        for msg in history:
            chat_history.append({
                "role": msg["role"],
                "parts": [msg["parts"]]
            })

        # Add new message
        chat_history.append({
            "role": "user",
            "parts": [user_message]
        })

        # Generate response
        response = model.generate_content(chat_history)

        return jsonify({"reply": response.text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)