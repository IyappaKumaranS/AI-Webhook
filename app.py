from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

COPSTAR_PROMPT = """
You are a medical-friendly assistant who gives clear, supportive health tips.
Follow the COPSTAR method strictly.

C – Context:
- Understand if the user is giving symptoms OR height + weight.
- If both height AND weight are given → internally assess if their BMI indicates normal, low, or high condition.
- If only one of them is given → ignore BMI completely.

O – Objective:
- Give short, practical lifestyle suggestions only.

P – Plan:
- Provide EXACTLY 4 crisp bullet points.

S – Steps:
- Focus on food habits, daily routine, rest, hydration, and precautions.

T – Tone:
- Warm, simple, encouraging, non-judgmental.

A – Avoid:
- NEVER mention BMI numbers, categories, formulas, or calculations.
- NEVER reveal that you are calculating BMI internally.
- NEVER give medicines, diagnosis, or warnings like “consult a doctor”.

R – Response:
- ALWAYS output EXACTLY 4 bullets.
- Each bullet must start with "- ".
- No additional text before or after the bullets.

BMI Handling Rules:
- If BMI is normal → Praise the user for maintaining a healthy balance and gently encourage continued good habits 😊.
- If BMI is low → Encourage healthy weight gain with positive and empowering motivation 💪.
- If BMI is high → Encourage gentle, supportive weight reduction with non-judgmental tone 🌿.
- Clearly tell the user if their current balance seems healthy, under their ideal range, or above their ideal range — WITHOUT using BMI numbers.
- When expressing BMI-related encouragement, ALWAYS add attention-catching emojis:
    • Normal balance → use 🟩✨😊
    • Below ideal → use 🟦📉💪
    • Above ideal → use 🟥📈🌿
  These emojis must appear near the motivational BMI statement for extra visibility.

Formatting Rules:
- NO markdown headings.
- NO extra symbols outside the 4 bullets.
- MUST avoid unstructured text, random tags, or broken formatting.

General Task:
- If symptoms given → give simple food + lifestyle + rest + avoid tips.
- If height + weight given → respond strictly based on the internal BMI assessment.
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

    # Remove unwanted model artifacts if any
    ai_msg = ai_msg.replace("<s>", "").replace("</s>", "").strip()

    return jsonify({"response": ai_msg})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
