from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI
import os

app = Flask(__name__)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

bots = [
    {
        "bot_name": "🤓 Вика",
        "instruction": "Ты продуктовый менеджер и твоя задача проанализировать изначальный запрос и найти подкрепляющую статистику, которая позволит улучшить изначальную гипотезу."
    },
    {
        "bot_name": "🕵️‍♀️ Настя",
        "instruction": "Ты продуктовый менеджер и твоя задача подготовить список конкурентов с похожей функцией, описать особенности реализации."
    },
    {
        "bot_name": "👨‍💻 Артур",
        "instruction": "Ты технический лидер. Проанализируй реализуемость, ресурсы и роли."
    },
    {
        "bot_name": "🔍 Свати",
        "instruction": "Ты технический аналитик. Продумай корнер-кейсы и дополнительные сценарии."
    },
    {
        "bot_name": "📅 Лена",
        "instruction": "Ты менеджер проекта. Проанализируй изначальный запрос, ответы Артура, Насти и Свати и составь два плана: MVP и full."
    },
    {
        "bot_name": "🧠 Денис",
        "instruction": "Ты ведущий разработчик. Дай критическую оценку, почему идея может быть плохой или не нужна."
    }
]

@app.route("/", methods=["GET"])
def index():
    return render_template_string("""{% raw %}
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
    const bots = ["🤓 Вика", "🕵️‍♀️ Настя", "👨‍💻 Артур", "🔍 Свати", "📅 Лена", "🧠 Денис"];
    let fullText = "";

    async function sendIdea() {
      const idea = document.getElementById("idea").value;
      const responseDiv = document.getElementById("responses");
      const copyAllBtn = document.getElementById("copy-all");
      responseDiv.innerHTML = "";
      copyAllBtn.style.display = "none";
      fullText = `💡 Запрос:\n${idea}\n\n`;

      for (let i = 0; i < bots.length; i++) {
        const botName = bots[i];
        const botBox = document.createElement("div");
        botBox.className = "bot-block";
        botBox.innerHTML = `<div class="bot-name">${botName}</div><pre id="bot-answer-${i}">⏳...</pre>`;
        responseDiv.appendChild(botBox);

        try {
          const res = await fetch("/generate_for_bot", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ idea: idea, bot_id: botName })
          });
          const data = await res.json();
          const answer = data.answer || "Ошибка ответа";
          document.getElementById(`bot-answer-${i}`).innerText = answer;

          const copyBtn = document.createElement("button");
          copyBtn.innerText = "📋 Скопировать";
          copyBtn.className = "copy-btn";
          copyBtn.onclick = () => {
            navigator.clipboard.writeText(answer).then(() => alert("Скопировано!"));
          };
          botBox.appendChild(copyBtn);

          fullText += `${botName}:\n${answer}\n\n`;
        } catch (err) {
          document.getElementById(`bot-answer-${i}`).innerText = "Ошибка запроса";
        }
      }

      window.fullCopyText = fullText.trim();
      copyAllBtn.style.display = "inline-block";
    }

    function copyAll() {
      navigator.clipboard.writeText(window.fullCopyText).then(() => {
        alert("Все ответы скопированы!");
      });
    }
  </script>
</body>
</html>
{% endraw %}""")

@app.route("/submit", methods=["POST"])
def submit():
    try:
        data = request.get_json()
        idea = data.get("idea", "").strip()
        if not idea:
            return jsonify({"error": "Запрос не может быть пустым"})

        responses = []
        artur_resp, nastya_resp, swati_resp = "", "", ""

        for bot in bots:
            instruction = bot["instruction"]
            if bot["bot_name"] == "📅 Лена":
                instruction += (
                    f"\n\nОтвет Артура:\n{artur_resp}\n\n"
                    f"Ответ Насти:\n{nastya_resp}\n\n"
                    f"Ответ Свати:\n{swati_resp}"
                )

            res = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": instruction},
                    {"role": "user", "content": idea}
                ]
            )
            answer = res.choices[0].message.content.strip()
            if bot["bot_name"] == "👨‍💻 Артур":
                artur_resp = answer
            elif bot["bot_name"] == "🕵️‍♀️ Настя":
                nastya_resp = answer
            elif bot["bot_name"] == "🔍 Свати":
                swati_resp = answer

            responses.append({"bot_name": bot["bot_name"], "answer": answer})

        return jsonify(responses)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)