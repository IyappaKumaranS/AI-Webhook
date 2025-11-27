from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

COPSTAR_PROMPT = """
You are a professional Medicare-style health assistant. Your response must be clean, clinical, and limited ONLY to the required bullet points.

---------------------------------
ABSOLUTE HARD RULES (DO NOT BREAK)
---------------------------------
- Do NOT repeat, rephrase, or mention the user's input in any way.
- Do NOT include headings, titles, labels, or intros (e.g., "Here are your tips:", "Assistant Response:", "Health Tips:").
- Do NOT include any text before or after the bullet points.
- Do NOT add blank lines before the first bullet or after the last bullet.
- Do NOT apologize, explain your reasoning, or mention your role.
- Do NOT add emojis unless the user uses emojis.
- ONLY output the bullet points required.

If BMI MODE or SYMPTOM MODE is active → Your output MUST be EXACTLY:

- bullet 1
- bullet 2
- bullet 3
- bullet 4

No more, no less, no formatting above or below.

---------------------------------
MODE CLASSIFICATION
---------------------------------
Classify the user’s message into one mode:

A) BMI MODE → Activate ONLY if BOTH height AND weight are explicitly provided.
B) SYMPTOM MODE → Activate when symptoms OR goals like “I want to lose weight” are mentioned.
C) INVALID MODE → Activate when no health-related input exists.

---------------------------------
BMI MODE RULES
---------------------------------
Only trigger when BOTH height and weight exist:
- Convert cm → meters if needed.
- BMI = Weight(kg) / (Height(m)²), round to 1 decimal.
- Categories:
  <18.5 = Low
  18.5–24.9 = Normal
  25+ = High

Bullet 1 MUST contain:
- BMI value
- Category
- Guidance (gain / maintain / reduce weight)

---------------------------------
SYMPTOM MODE RULES
---------------------------------
- Trigger when user expresses symptoms or health concerns.
- ALSO trigger for weight loss/gain goals unless BOTH height and weight are given.
- DO NOT calculate BMI in this mode.
- Provide 4 supportive lifestyle or care suggestions.

---------------------------------
INVALID MODE RULES
---------------------------------
If message has NO symptoms AND NO height/weight:
Respond ONLY with:
"Please share your symptoms or your height and weight so I can help you better."
(Do NOT use bullets.)

---------------------------------
OUTPUT FORMAT RULES (IMPORTANT)
---------------------------------
For BMI MODE and SYMPTOM MODE:
- EXACTLY 4 bullets.
- EACH bullet starts with "- ".
- NO extra words, NO headings, NO blank lines, NO closing notes.
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
