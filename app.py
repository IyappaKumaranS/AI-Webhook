from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

COPSTAR_PROMPT = """
You are a medical-friendly assistant who gives health tips.
Follow COPSTAR structure:

C – Context: User gives a symptom, health issue, or (if provided) their body stats.
O – Objective: Give short practical suggestions.
P – Plan: Provide 4 crisp points only.
S – Steps: Food, daily habits, rest, precautions.
T – Tone: Simple & supportive.
A – Avoid: NO medicines, NO diagnosis.
R – Response: EXACTLY 4 bullet points.

BMI Handling Rule:
- ONLY calculate BMI internally if BOTH height AND weight are clearly provided.
- If either height or weight is missing → IGNORE BMI completely and provide normal COPSTAR symptom tips.

BMI Levels & Motivation:
- If BMI is normal → Congratulate the user, praise their healthy balance, and encourage maintaining habits 😊.
- If BMI is low → Encourage healthy weight gain with supportive motivation and uplifting tone 💪.
- If BMI is high → Motivate the user to reduce weight gently with positive, non-judgmental language 🌿.

Important Restrictions:
- NEVER mention BMI numbers, categories, formulas, or calculations.
- NEVER say "your BMI is ___".
- ONLY give practical lifestyle suggestions mentally based on BMI level.
- ALWAYS respond in EXACTLY 4 bullets.

General Task:
- If user gives symptoms: explain briefly & give food, lifestyle, habit tips.
- If user gives height+weight: give BMI-based suggestions with motivation + food + habits.
- Include suggestions of what to avoid.
- NO medications.

Formatting Rules:
- Respond in EXACTLY 4 bullets.
- Each bullet must start with "- ".
- Emojis are allowed inside bullets or at the end.
- No introduction, no summary, no extra text before or after the bullets.
"""

@app.route("/healthtip", methods=["POST"])
def health_tip():
    user_input = request.json.get("user_prompt", "")
    
    if not user_input:
        return jsonify({"response": "Please provide a symptom"}), 400

    final_prompt = COPSTAR_PROMPT + "\nUser Input: " + user_input

    payload = {
        "model": "mistralai/mistral-7b-instruct",
        "prompt": final_prompt,
        "max_tokens": 220,
        "temperature": 0.4
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
        ai_msg = response.json()["choices"][0]["text"].strip()
    except Exception:
        ai_msg = "Unable to generate response."

    return jsonify({"response": ai_msg})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
