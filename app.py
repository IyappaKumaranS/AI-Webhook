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
   - 6 bullets only
   - Each bullet max 1 short line
   - No paragraphs
   - No big sentences
   - No medical terms

Your job:
- Say what the symptom may mean in very simple words
- Suggest easy foods to take
- Suggest simple comfort steps (dress, room, rest)
- Say what to avoid
- KEEP IT VERY SIMPLE AND SHORT

Output example style:
- Drink warm water or light soups
- Wear soft clothes and rest in a calm place
- Avoid cold drinks and heavy work
"""

@app.route("/healthtip", methods=["POST"])
def health_tip():
    user_input = request.json.get("user_prompt", "")
    
    if not user_input:
        return jsonify({"response": "Please provide a symptom"}), 400

    final_prompt = COPSTAR_PROMPT + "\nUser Symptom: " + user_input

    payload = {
        "model": "mistralai/mistral-7b-instruct",
        "prompt": final_prompt,
        "max_tokens": 150,
        "temperature": 0.5
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/completions",
        json=payload,
        headers=headers
    )

    try:
        ai_msg = response.json()["choices"][0]["text"]
    except:
        ai_msg = "Unable to generate response."

    return jsonify({"response": ai_msg})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
