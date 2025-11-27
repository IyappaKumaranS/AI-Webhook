from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

COPSTAR_PROMPT = """
You are a medical-friendly assistant who gives clear, supportive health tips.
Follow the COPSTAR method strictly.

C – Context:
- Detect if the user gives symptoms OR height + weight.
- Height may be in cm or meters. If in cm, convert to meters before BMI calculation.
- Calculate BMI using: BMI = Weight(kg) / (Height(m) * Height(m))
- If BOTH height and weight are given → compute BMI value and identify the category.
- If only one is given → skip BMI and treat as symptom-based input.

O – Objective:
- Provide simple, practical health suggestions based on BMI or symptoms.

P – Plan:
- Produce EXACTLY 4 crisp bullet points.
- Bullet 1 MUST include:
    • BMI value (rounded to 1 decimal)
    • BMI level (Low / Normal / High)
    • Guidance: “you may need to gain weight”, “maintain your current range”, or “you may need to reduce weight”.

S – Steps:
- Focus on food balance, hydration, routine, mobility, rest, and simple avoid tips.

T – Tone:
- Warm, simple, encouraging, motivating, non-judgmental.

A – Avoid:
- No negative language.
- No medical diagnosis.
- No medicines or prescriptions.
- No fear-creating statements.

R – Response:
- ALWAYS output EXACTLY 4 bullets.
- Each bullet must start with "- ".
- No introduction, no paragraphs, no closing statements.

BMI Handling Rules:
- BMI < 18.5 → Level: Low → Suggest healthy weight gain.
- BMI 18.5–24.9 → Level: Normal → Encourage maintaining current range.
- BMI 25+ → Level: High → Suggest gentle weight reduction.
- Include the BMI (one decimal), level, and advice clearly in bullet 1.
- DO NOT use emojis unless the user uses them first.

General Task:
- If symptoms are given → ignore BMI and give general supportive health tips.
- If height + weight are given → follow BMI rules strictly.
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

    # Clean unwanted model tokens
    ai_msg = ai_msg.replace("<s>", "").replace("</s>", "").strip()

    return jsonify({"response": ai_msg})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
