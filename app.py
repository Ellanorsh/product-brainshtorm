from flask import Flask, request, jsonify, render_template_string
import os
import openai

app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Инструкции для каждого бота
bots = [
    {
        "bot_name": "Вика",
        "prompt": "Ты продуктовый менеджер и твоя задача проанализировать изначальный запрос, найти подкрепляющую статистику, которая позволит улучшить изначальную гипотезу."
    },
    {
        "bot_name": "Настя",
        "prompt": "Ты продуктовый менеджер и твоя задача проанализировать изначальный запрос и подготовить список существующих конкурирующих или похожих сервисов, где такая функция хорошо реализована."
    },
    {
        "bot_name": "Артур",
        "prompt": "Ты технический лидер проекта и твоя задача проанализировать изначальный запрос и оценить его с точки зрения реализуемости и дать оценку по требуемым техническим ресурсам (нужны ли интеграции со сторонними сервисами, сколько разработчиков и каких потребуется, нужны ли девопсы, дизайнеры, аналитики и тд)."
    },
    {
        "bot_name": "Свати",
        "prompt": "Ты технический аналитик и твоя задача проанализировать изначальный запрос и продумать возможные корнер кейсы и необходимые дополнительные сценарии, которые нужно поддержать."
    },
    {
        "bot_name": "Лена",
        "prompt": "Ты менеджер проекта и твоя задача проанализировать изначальный запрос, ответ бота Артура и составить план проекта (примерный роадмап)."
    },
    {
        "bot_name": "Денис",
        "prompt": "Ты ведущий разработчик. Твоя задача проанализировать изначальный запрос и с технической и практической стороны дать конструктивную критику, какие проблемы ты видишь в этом запросе, почему он плохо составлен, почему идея нежизнеспособна, почему текущее решение уже достаточное и более хорошее."
    }
]

@app.route("/")
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang=\"en\">
    <head>
      <meta charset=\"UTF-8\">
      <title>Product Brainstorm</title>
    </head>
    <body>
      <h1>💡 Отправить продуктовую идею</h1>
      <textarea id=\"idea\" rows=\"4\" cols=\"60\" placeholder=\"Введите вашу идею здесь...\"></textarea><br><br>
      <button onclick=\"sendIdea()\">Отправить</button>

      <h2>Ответы ботов:</h2>
      <div id=\"responses\"></div>

      <script>
        async function sendIdea() {
          const idea = document.getElementById("idea").value;
          const responseDiv = document.getElementById("responses");
          responseDiv.innerHTML = "⏳ Идёт генерация ответов...";

          const res = await fetch("/submit", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ idea })
          });

          const data = await res.json();
          responseDiv.innerHTML = data.map(bot => `
            <div>
              <strong>${bot.bot_name}</strong>:<br/>
              ${bot.answer}
              <hr/>
            </div>
          `).join("");
        }
      </script>
    </body>
    </html>
    """)

@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json()
    idea = data.get("idea")
    results = []

    for bot in bots:
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": bot["prompt"]},
                    {"role": "user", "content": idea}
                ]
            )
            answer = completion.choices[0].message.content
        except Exception as e:
            answer = f"⚠️ Ошибка: {e}"

        results.append({"bot_name": bot["bot_name"], "answer": answer})

    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
