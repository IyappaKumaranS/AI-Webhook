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
- ONLY calculate BMI if the user clearly provides BOTH height AND weight.
- If either height or weight is missing → IGNORE BMI completely and give normal COPSTAR symptom tips.
- If BMI < 18.5 → Underweight suggestions: healthy weight-gain foods, balanced proteins, good sleep.
- If BMI 18.5–24.9 → Normal BMI: suggest maintenance habits, light exercise, balanced diet.
- If BMI 25+ → High BMI: suggest gentle workouts, lighter meals, portion control.
- Do NOT mention formulas, BMI numbers, or calculations.
- ALWAYS respond in EXACTLY 4 bullet points.

General Task:
- If user gives symptoms: explain briefly and provide lifestyle/food precautions.
- If user gives height+weight: provide BMI-based suggestions.
- Suggest what to avoid.
- NO medication.

Formatting Rules:
- Respond in EXACTLY 4 bullets.
- Each bullet must start with "- ".
- No extra text before or after the bullets.
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
        "max_tokens": 200,
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
