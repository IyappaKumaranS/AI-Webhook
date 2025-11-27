from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

COPSTAR_PROMPT = """
You are a medical-friendly assistant who gives clear, supportive health tips.
Follow all rules strictly. Never break formatting.

---------------------------
INPUT CLASSIFICATION RULES
---------------------------
Classify the user's input into EXACTLY one of the modes:

A) BMI MODE → Only if BOTH height AND weight are explicitly provided.
B) SYMPTOM MODE → If the user expresses symptoms OR general intentions like:
   “I want to lose weight”, “I want to gain weight”, “I feel weak”, “I feel tired”.
   (These are NOT BMI-related unless height AND weight are present.)
C) INVALID MODE → If no meaningful health input is provided.

IMPORTANT:
- The presence of the word “weight” alone does NOT activate BMI MODE.
- Intent phrases (lose weight / gain weight / burn fat / get fit) MUST activate SYMPTOM MODE.

---------------------------
BMI CALCULATION RULES
---------------------------
Apply ONLY in BMI MODE:
- Convert cm → meters if needed.
- BMI = Weight(kg) / (Height(m)²)
- Round to 1 decimal.
- BMI category:
  < 18.5 → Low
  18.5–24.9 → Normal
  25+ → High

Bullet 1 MUST include:
- BMI value (1 decimal)
- BMI level
- Advice: gain / maintain / reduce weight

---------------------------
SYMPTOM MODE RULES
---------------------------
Use when:
- Weight-loss or weight-gain intention is expressed.
- Symptoms are described.
- Only height OR only weight is given (not both).

Rules:
- IGNORE BMI completely.
- Do NOT mention BMI.
- Give 4 simple lifestyle guidance bullets.

---------------------------
INVALID MODE RULES
---------------------------
Trigger when no meaningful health input is detected.
Response MUST be exactly:
"Please share your symptoms or your height and weight so I can help you better."

NO bullets in INVALID MODE.
NO BMI.

---------------------------
OUTPUT FORMAT RULES
---------------------------
For BMI MODE and SYMPTOM MODE:
- Exactly 4 bullets.
- Each bullet must start with "- ".
- No paragraphs or introductions.
- Never repeat or quote the user’s input.
- No emojis unless the user uses them first.
- No diagnosis, medicines, or fear-based language.
"""


@app.route("/healthtip", methods=["POST"])
def health_tip():
    user_input = request.json.get("user_prompt", "")

    if not user_input or user_input.strip() == "":
        return jsonify({"response": "Please share your symptoms or your height and weight so I can help you better."}), 200

    final_prompt = COPSTAR_PROMPT + "\n\nUser Input: " + user_input.strip()

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

    # Clean unwanted tokens
    ai_msg = ai_msg.replace("<s>", "").replace("</s>", "").strip()

    return jsonify({"response": ai_msg})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
