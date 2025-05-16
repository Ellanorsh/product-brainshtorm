from flask import Flask, request, jsonify, render_template_string
import os

app = Flask(__name__)

@app.route("/")
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>Product Brainstorm</title>
    </head>
    <body>
      <h1>💡 Отправить продуктовую идею</h1>
      <textarea id="idea" rows="4" cols="60" placeholder="Введите вашу идею здесь..."></textarea><br><br>
      <button onclick="sendIdea()">Отправить</button>

      <h2>Ответы ботов:</h2>
      <div id="responses"></div>

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

    # Примитивные заглушки — здесь ты позже вставишь вызов OpenAI
    bots = [
        {"bot_name": "UX Bot", "answer": f"Предлагаю упростить путь пользователя для: {idea}"},
        {"bot_name": "Growth Bot", "answer": f"Можно A/B протестировать новый шаг регистрации"},
        {"bot_name": "PM Bot", "answer": f"Влияние на метрику активации нужно оценить"}
    ]

    return jsonify(bots)

if __name__ == "__main__":
    app.run(debug=True)
