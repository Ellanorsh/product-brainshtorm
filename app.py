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
        "instruction": "Ты продуктовый менеджер и твоя задача проанализировать изначальный запрос и найти подкрепляющую статистику, которая позволит улучшить изначальную гипотезу. Например: если гипотеза включает какое-то улучшение и  изменение, поискать исследования, которые бы подтверждали, что такие изменения хорошо отражаются на продукте и увеличивают ключевые метрики (указать какие)"
    },
    {
        "bot_name": "🕵️‍♀️ Настя",
        "instruction": "Ты продуктовый менеджер и твоя задача проанализировать изначальный запрос и понять, как должна выглядеть предлагаемая функция. Основываясь на этом понимании тебе нужно подготовить список существующих конкурирующих или похожих сервисов, где такая функция хорошо реализована. К каждому сервису дать небольшой комментарий, почему ты считаешь, что эта функция там хорошо реализована и есть ли у неё дополнительные уникальные особенности. Например: если запрос описывает изменения в форме регистрации, то идеальным результатом будет список сервисов с понятной и удобной формой регистрации и выделенем, что вот в этом сервисе есть хорошие UI находки, в этом - правильные подсказки пользователю, а в этом чистый и лакончный дизайн и ничто не отвлекает пользователя."
    },
    {
        "bot_name": "👨‍💻 Артур",
        "instruction": "Ты технический лидер проекта и твоя задача проанализировать изначальный запрос и оценить его с точки зрения реализуемости и дать оценку по требуемым техническим ресурсам (нужны ли интеграции со сторонними сервисами, сколько разработчиков и каких потребуется, нужны ли девопсы, дизайнеры, аналитики и тд). Есть ли критические с технической точки зрения корнер кейсы, которые обязательно нужно предусмотреть, чтобы описание реализации было полным."
    },
    {
        "bot_name": "🔍 Свати",
        "instruction": "Ты технический аналитик и твоя задача проанализировать изначальный запрос и продумать все возможные корнер кейсы и необходимые дополнительные сценарии, которые нужно поддержать."
    },
    {
        "bot_name": "📅 Лена",
        "instruction": "Ты менеджер проекта и твоя задача проанализировать изначальный запрос, ответы всех остальных ботов и составить два плана проекта (примерный роадмап). Один план для MVP и реализации только успешного сценария и второй с реализацией всех сценариев и корнер кейсов. В планах обязательно должны быть предварительные оценки по количеству необходимых человекочасов разработчиков, тестирования и других специалистов, которых нужно привлечь."
    },
    {
        "bot_name": "🧠 Денис",
        "instruction": "Ты ведущий разработчик. Твоя задача проанализировать изначальный запрос и с технической и практической стороны дать конструктивную критику, какие проблемы ты видишь в этом запросе, почему он плохо составлен, почему идея нежизнеспособна, почему текущее решение уже достаточное и более хорошее."
    }
]

@app.route("/", methods=["GET"])
def index():
@app.route("/", methods=["GET"])
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>Product Brainstorm</title>
  <style>
    body { font-family: Arial, sans-serif; background: #f4f4f4; margin: 0; padding: 2rem; }
    .container { max-width: 800px; margin: 0 auto; background: white; padding: 2rem; border-radius: 8px; }
    .bot-block { margin-bottom: 2rem; padding: 1rem; background: #f9f9f9; border-left: 4px solid #ccc; border-radius: 4px; position: relative; }
    .bot-name { font-weight: bold; margin-bottom: 0.5rem; }
    .copy-btn { position: absolute; top: 1rem; right: 1rem; background: #eee; border: none; padding: 5px 10px; cursor: pointer; }
    .copy-btn:hover { background: #ddd; }
    #copy-all { margin-top: 1rem; background: #007bff; color: white; border: none; padding: 10px 20px; cursor: pointer; border-radius: 4px; }
    #copy-all:hover { background: #0056b3; }
  </style>
</head>
<body>
  <div class="container">
    <h1>💡 Отправить продуктовую идею</h1>
    <textarea id="idea" rows="4" style="width:100%;" placeholder="Введите вашу идею здесь..."></textarea><br><br>
    <button onclick="sendIdea()">Отправить</button>
    <h2>Ответы ботов:</h2>
    <div id="responses"></div>
    <button id="copy-all" style="display:none;" onclick="copyAll()">📋 Скопировать всё</button>
  </div>

<script>
  async function sendIdea() {
    const idea = document.getElementById("idea").value;
    const responseDiv = document.getElementById("responses");
    const copyAllBtn = document.getElementById("copy-all");
    responseDiv.innerHTML = "⏳ Генерация ответов...";
    copyAllBtn.style.display = "none";

    const res = await fetch("/submit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ idea })
    });

    const data = await res.json();
    if (data.error) {
      responseDiv.innerHTML = `<div style="color:red;">Ошибка: ${data.error}</div>`;
      return;
    }

    let fullText = `💡 Запрос:\n${idea}\n\n`;

    responseDiv.innerHTML = data.map((bot, index) => {
      const botText = `${bot.bot_name}:\n${bot.answer}`;
      fullText += `${botText}\n\n`;
      return `
        <div class="bot-block">
          <div class="bot-name">${bot.bot_name}</div>
          <pre id="bot-answer-${index}" style="white-space:pre-wrap;">${bot.answer}</pre>
          <button class="copy-btn" onclick="copyText('bot-answer-${index}')">📋 Скопировать</button>
        </div>
      `;
    }).join("");

    window.fullCopyText = fullText.trim();
    copyAllBtn.style.display = "inline-block";
  }

  function copyText(elementId) {
    const text = document.getElementById(elementId).innerText;
    navigator.clipboard.writeText(text).then(() => {
      alert("Скопировано!");
    });
  }

  function copyAll() {
    navigator.clipboard.writeText(window.fullCopyText).then(() => {
      alert("Все ответы скопированы!");
    });
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
