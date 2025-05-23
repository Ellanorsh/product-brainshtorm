from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI
import os
import re

app = Flask(__name__)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# --- Боты ---
bots = [
    {
        "bot_name": "🤓 Вика",
        "instruction": "Ты продуктовый менеджер и твоя задача проанализировать изначальный запрос и найти подкрепляющую статистику, которая позволит улучшить изначальную гипотезу..."
    },
    {
        "bot_name": "🕵️‍♀️ Настя",
        "instruction": "Ты продуктовый менеджер и твоя задача проанализировать изначальный запрос и понять, как должна выглядеть предлагаемая функция..."
    },
    {
        "bot_name": "👨‍💻 Артур",
        "instruction": "Ты технический лидер проекта и твоя задача проанализировать изначальный запрос и оценить его с точки зрения реализуемости..."
    },
    {
        "bot_name": "🔍 Свати",
        "instruction": "Ты технический аналитик и твоя задача проанализировать изначальный запрос и продумать все возможные корнер кейсы..."
    },
    {
        "bot_name": "📅 Лена",
        "instruction": "Ты менеджер проекта и твоя задача проанализировать изначальный запрос, ответы всех остальных ботов и составить два плана проекта..."
    },
    {
        "bot_name": "🧠 Денис",
        "instruction": "Ты ведущий разработчик. Твоя задача проанализировать изначальный запрос и с технической и практической стороны дать конструктивную критику..."
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
    <h1>💡 Отправить продуктовую идею</h1>
    <textarea id="idea" rows="4" placeholder="Введите вашу идею здесь..."></textarea>
    <button onclick="sendIdea()">Отправить</button>

    <div id="responses"></div>
  </div>

  <script>
    const bots = ["🤓 Вика", "🕵️‍♀️ Настя", "👨‍💻 Артур", "🔍 Свати", "📅 Лена", "🧠 Денис"];

    function format(text) {
      // преобразует список и абзацы
      const html = text
        .replace(/\\n{2,}/g, '</p><p>')
        .replace(/\\n/g, '<br>')
        .replace(/(\\d+\\.\\s.+?)(?=\\d+\\.\\s|$)/gs, (match) => {
          const items = match.trim().split(/\\n/).map(item => `<li>${item.replace(/^\\d+\\.\\s/, '')}</li>`).join('');
          return `<ol>${items}</ol>`;
        });
      return "<p>" + html + "</p>";
    }

    async function sendIdea() {
      const idea = document.getElementById("idea").value;
      const responseDiv = document.getElementById("responses");
      responseDiv.innerHTML = "⏳ Генерация ответов...";

      responseDiv.innerHTML = "";
      for (const bot of bots) {
        responseDiv.innerHTML += `<div class='response'><div class='bot-label'>${bot}:</div>⏳ Ждем ответ...</div>`;
      }

      for (let i = 0; i < bots.length; i++) {
        const bot = bots[i];
        const res = await fetch("/generate_for_bot", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ idea, bot_id: bot })
        });

        const data = await res.json();
        const responseBlocks = document.querySelectorAll(".response");
        if (data.error) {
          responseBlocks[i].innerHTML = `<div class='bot-label'>${bot}:</div>❌ Ошибка: ${data.error}`;
        } else {
          
          const formatted = format(data.answer);
          const plainText = data.answer.replace(/"/g, '&quot;').replace(/'/g, "&#039;");
          responseBlocks[i].innerHTML = `
            <div class='bot-label'>${data.bot_name}:</div>
            <div class="formatted-answer">${formatted}</div>
            <button onclick="copyText('${plainText}')" style="margin-top:10px;">📋 Скопировать</button>
          `;
    
        }
      }
    }
  
    function copyText(text) {
      const textarea = document.createElement("textarea");
      textarea.value = text.replace(/<br>/g, "\n").replace(/<[^>]+>/g, "");
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand("copy");
      document.body.removeChild(textarea);
      alert("Скопировано!");
    }
    </script>
    
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
