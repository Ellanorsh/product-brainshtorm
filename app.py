from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI
import os
import re

app = Flask(__name__)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# --- Bots ---
bots = [
    {
        "bot_name": "🤓 Vika",
        "instruction": "You are a product manager. Your task is to analyze the initial request and find supporting statistics that can help improve the original hypothesis. For example: if the hypothesis includes a suggested improvement or change, look for studies that confirm such changes have a positive impact on the product and lead to growth in key metrics and specify which metrics."
    },
    {
        "bot_name": "🕵️‍♀️ Nastya",
        "instruction": "You are a product manager. Your task is to analyze the initial request and understand what the proposed feature should look like. Based on that understanding, prepare a list of existing competing or similar services where this feature is well implemented. For each service, add a brief comment explaining why you believe the feature is well implemented there and whether it has any additional unique aspects. For example: if the request describes changes to a registration form, an ideal result would be a list of services with clear and user-friendly registration forms, highlighting that one service has great UI solutions, another has helpful guidance for users, and a third has a clean and minimalistic design that keeps the user focused."
    },
    {
        "bot_name": "👨‍💻 Artur",
        "instruction": "You are the technical lead of the project. Your task is to analyze the initial request and evaluate it in terms of feasibility, and provide an assessment of the required technical resources e.g., whether third-party integrations are needed, how many developers and of what kind are required, whether DevOps, designers, analysts, etc. are needed. Identify any critical technical edge cases that must be considered to make the implementation plan complete."
    },
    {
        "bot_name": "🔍 Swati",
        "instruction": "You are a technical analyst. Your task is to analyze the initial request and think through all possible edge cases and additional scenarios that should be supported."
    },
    {
        "bot_name": "📅 Elena",
        "instruction": "You are the project manager. Your task is to analyze the initial request, review the responses from all other bots, and create two project plans, rough roadmaps: one for an MVP covering only the happy path, and another covering all scenarios and edge cases. Both plans must include preliminary estimates for the number of developer hours, testing, and any other specialists required."
    },
    {
        "bot_name": "🧠 Denis",
        "instruction": "You are the lead developer. Your task is to analyze the initial request and provide constructive criticism from a technical and practical perspective. What problems do you see in the request? Why is it poorly formulated? Why is the idea not viable? Why might the current solution be sufficient or even better?"
    }
]

@app.route("/", methods=["GET"])
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>Product Brainstorm</title>
  <style>
    body {
      background-color: #f7f7f8;
      font-family: 'Segoe UI', sans-serif;
      padding: 40px;
    }
    .container {
      max-width: 800px;
      margin: 0 auto;
      background: #fff;
      padding: 30px;
      border-radius: 12px;
      box-shadow: 0 0 12px rgba(0,0,0,0.05);
    }
    textarea {
      width: 100%;
      padding: 12px;
      font-size: 16px;
      border-radius: 8px;
      border: 1px solid #ccc;
      margin-bottom: 16px;
    }
    button {
      background-color: #10a37f;
      color: white;
      border: none;
      padding: 12px 24px;
      font-size: 16px;
      border-radius: 8px;
      cursor: pointer;
    }
    button:hover {
      background-color: #0f9774;
    }
    .response {
      background-color: #f0f0f0;
      padding: 16px;
      border-radius: 8px;
      margin-top: 20px;
      white-space: pre-wrap;
    }
    .bot-label {
      font-weight: bold;
      margin-bottom: 6px;
      color: #333;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>💡 Submit a product feature idea</h1>
    <textarea id="idea" rows="4" placeholder="Submit your idea here..."></textarea>
    <button onclick="sendIdea()">Submit</button>

    <div id="responses"></div>
<div id="copy-all-container" style="display:none; margin-top: 20px;">
  <button onclick="copyAll()" style="background-color:#444;">📋 Copy all</button>
</div>
  </div>

  <script src="/static/script.js"></script>
</body>
</html>
""")

@app.route("/generate_for_bot", methods=["POST"])
def generate_for_bot():
    try:
        data = request.get_json()
        idea = data.get("idea", "").strip()
        bot_id = data.get("bot_id")

        bot = next((b for b in bots if b["bot_name"] == bot_id), None)
        if not bot:
            return jsonify({"error": "Unknown bot"}), 400

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": bot["instruction"]},
                {"role": "user", "content": idea}
            ],
            temperature=0.7
        )

        return jsonify({
            "bot_name": bot["bot_name"],
            "answer": response.choices[0].message.content.strip()
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
