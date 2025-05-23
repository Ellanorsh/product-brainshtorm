
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI
import os

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
        "instruction": "Ты продуктовый менеджер и твоя задача проанализировать изначальный запрос и понять, как должна выглядеть предлагаемая функция. Основываясь на этом понимании тебе нужно подготовить список существующих конкурирующих или похожих сервисов, где такая функция хорошо реализована. К каждому сервису дать небольшой комментарий, почему ты считаешь, что эта функция там хорошо реализована и есть ли у неё дополнительные уникальные особенности."
    },
    {
        "bot_name": "👨‍💻 Артур",
        "instruction": "Ты технический лидер проекта и твоя задача проанализировать изначальный запрос и оценить его с точки зрения реализуемости и дать оценку по требуемым техническим ресурсам."
    },
    {
        "bot_name": "🔍 Свати",
        "instruction": "Ты технический аналитик и твоя задача проанализировать изначальный запрос и продумать все возможные корнер кейсы и необходимые дополнительные сценарии, которые нужно поддержать."
    },
    {
        "bot_name": "📅 Лена",
        "instruction": "Ты менеджер проекта и твоя задача проанализировать изначальный запрос, ответы Артура, Насти и Свати и составить два плана проекта (MVP и полный)."
    },
    {
        "bot_name": "🧠 Денис",
        "instruction": "Ты ведущий разработчик. Проанализируй изначальный запрос и дай техническую критику, почему гипотеза может быть плохой, ненужной или реализована лучше."
    }
]

@app.route("/")
def index():
    return render_template_string("""<!DOCTYPE html>
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
  const bots = {{ bots|tojson }};
  let allAnswers = [];

  async function sendIdea() {
    const idea = document.getElementById("idea").value.trim();
    const responseDiv = document.getElementById("responses");
    const copyAllBtn = document.getElementById("copy-all");
    allAnswers = [];

    if (!idea) {
      alert("Введите идею.");
      return;
    }

    responseDiv.innerHTML = "";
    copyAllBtn.style.display = "none";

    for (let i = 0; i < bots.length; i++) {
      const bot = bots[i];
      const botBlock = document.createElement("div");
      botBlock.className = "bot-block";
      botBlock.innerHTML = \`
        <div class="bot-name">\${bot.bot_name}</div>
        <pre id="bot-answer-\${i}" style="white-space:pre-wrap;">⏳ Генерация ответа...</pre>
      \`;
      responseDiv.appendChild(botBlock);

      const res = await fetch("/generate_for_bot", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ idea: idea, bot_id: bot.bot_name })
      });
      const data = await res.json();
      if (data.error) {
        document.getElementById("bot-answer-" + i).innerText = "Ошибка: " + data.error;
      } else {
        document.getElementById("bot-answer-" + i).innerText = data.answer;
        allAnswers.push(\`\${bot.bot_name}:
\${data.answer}\`);
        const btn = document.createElement("button");
        btn.className = "copy-btn";
        btn.innerText = "📋 Скопировать";
        btn.onclick = () => {
          navigator.clipboard.writeText(\`\${bot.bot_name}:
\${data.answer}\`);
          alert("Скопировано!");
        };
        botBlock.appendChild(btn);
      }

      if (i === bots.length - 1) {
        copyAllBtn.style.display = "inline-block";
      }
    }
  }

  function copyAll() {
    const idea = document.getElementById("idea").value;
    const fullText = "💡 Запрос:\n" + idea + "\n\n" + allAnswers.join("\n\n");
    navigator.clipboard.writeText(fullText).then(() => {
      alert("Все ответы скопированы!");
    });
  }
</script>
</body>
</html>""", bots=bots)

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
