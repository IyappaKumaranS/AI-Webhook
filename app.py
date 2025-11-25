from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

COPSTAR_PROMPT = """
You are a friendly health-tips assistant.
Use the COPSTAR structure and respond in VERY SIMPLE English.

C – Context: Understand the user's symptom.
O – Objective: Give helpful daily-life advice.
P – Plan: Respond in EXACTLY 4 short bullet points.
S – Steps: Cover food, rest, comfort, and avoid-items.
T – Tone: Warm, simple, supportive.
A – Avoid: NO medicines, NO diagnosis, NO medical treatments.
R – Response Style:
   - 4 bullets only
   - Each bullet max 1 short line
   - No paragraphs
   - No long sentences
   - No medical terms
"""

@app.route("/healthtip", methods=["POST"])
def health_tip():
    user_input = request.json.get("user_prompt", "")

    if not user_input:
        return jsonify({"response": "Please provide a symptom"}), 400

    payload = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "system", "content": COPSTAR_PROMPT},
            {"role": "user", "content": user_input}
        ],
        "max_tokens": 150,
        "temperature": 0.4
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    # Correct Chat Endpoint
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        json=payload,
        headers=headers
    )

    # Extract properly (correct for chat models)
    try:
        ai_msg = response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print("Error:", e)
        print("Response:", response.text)
        ai_msg = "Unable to generate response."

    return jsonify({"response": ai_msg})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
