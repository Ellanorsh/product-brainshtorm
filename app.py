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
      position: relative;
    }
    .bot-label {
      font-weight: bold;
      margin-bottom: 6px;
      color: #333;
    }
    .copy-btn {
      position: absolute;
      top: 10px;
      right: 10px;
      background: #e0e0e0;
      border: none;
      padding: 6px 12px;
      font-size: 14px;
      cursor: pointer;
      border-radius: 6px;
    }
    .copy-btn:hover {
      background: #d5d5d5;
    }
    #copy-all {
      margin-top: 20px;
      background: #007bff;
    }
    #copy-all:hover {
      background: #0056b3;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>💡 Отправить продуктовую идею</h1>
    <textarea id="idea" rows="4" placeholder="Введите вашу идею здесь..."></textarea>
    <button onclick="sendIdea()">Отправить</button>

    <div id="responses"></div>
    <button id="copy-all" style="display:none;" onclick="copyAll()">📋 Скопировать всё</button>
  </div>

  <script>
    const bots = ["🤓 Вика", "🕵️‍♀️ Настя", "👨‍💻 Артур", "🔍 Свати", "📅 Лена", "🧠 Денис"];
    let fullText = "";

    function format(text) {
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
      const copyAllBtn = document.getElementById("copy-all");
      responseDiv.innerHTML = "";
      fullText = `💡 Запрос:\n${idea}\n\n`;
      copyAllBtn.style.display = "none";

      for (const bot of bots) {
        const block = document.createElement("div");
        block.className = "response";
        block.innerHTML = `<div class='bot-label'>${bot}:</div><div class='content'>⏳ Ждем ответ...</div>`;
        responseDiv.appendChild(block);
      }

      const blocks = document.querySelectorAll(".response");

      for (let i = 0; i < bots.length; i++) {
        const bot = bots[i];
        const block = blocks[i].querySelector(".content");

        try {
          const res = await fetch("/generate_for_bot", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ idea, bot_id: bot })
          });

          const data = await res.json();
          if (data.error) {
            block.innerHTML = `❌ Ошибка: ${data.error}`;
          } else {
            block.innerHTML = format(data.answer);

            const plainText = `${bot}:\n${data.answer}\n\n`;
            fullText += plainText;

            const copyBtn = document.createElement("button");
            copyBtn.className = "copy-btn";
            copyBtn.textContent = "📋 Скопировать";
            copyBtn.onclick = () => {
              navigator.clipboard.writeText(`${bot}:\n${data.answer}`).then(() =>
                alert("Скопировано!")
              );
            };
            blocks[i].appendChild(copyBtn);
          }
        } catch (err) {
          block.innerHTML = "Ошибка запроса";
        }
      }

      window.fullCopyText = fullText.trim();
      copyAllBtn.style.display = "inline-block";
    }

    function copyAll() {
      navigator.clipboard.writeText(window.fullCopyText).then(() =>
        alert("Все ответы скопированы!")
      );
    }
  </script>
</body>
</html>

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
