from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI
import os

# --- Настройка приложения и клиента OpenAI ---
app = Flask(__name__)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# --- Боты ---
bots = [
    {
        "bot_name": "🤓 Вика",
        "instruction": "Ты продуктовый менеджер. Проанализируй запрос, найди статистику, которая усилит гипотезу."
    },
    {
        "bot_name": "🕵️‍♀️ Настя",
        "instruction": "Ты продуктовый менеджер. Подготовь список похожих/конкурирующих сервисов с похожей фичей."
    },
    {
        "bot_name": "👨‍💻 Артур",
        "instruction": "Ты технический лидер. Проанализируй реализуемость идеи, требуемые ресурсы и нужные роли."
    },
    {
        "bot_name": "🔍 Свати",
        "instruction": "Ты технический аналитик. Подумай о корнер-кейсах и дополнительных сценариях."
    },
    {
        "bot_name": "📅 Лена",
        "instruction": "Ты менеджер проекта. Используй запрос и ответ Артура, чтобы составить план проекта."
    },
    {
        "bot_name": "🧠 Денис",
        "instruction": "Ты ведущий разработчик. Дай критическую оценку: почему гипотеза может быть плохой, зачем это вообще нужно."
    }
]

# --- Генерация ответов от всех ботов ---
def generate_bot_responses(user_prompt: str):
    responses = []
    artur_answer = None

    for bot in bots:
        print(f"🟡 Генерация ответа от {bot['bot_name']}...")

        # Если это Лена, добавим в prompt ответ Артура
        messages = [{"role": "system", "content": bot["instruction"]}]
        if bot["bot_name"] == "📅 Лена" and artur_answer:
            user_content = f"{user_prompt}\n\nОтвет Артура:\n{artur_answer}"
        else:
            user_content = user_prompt
        messages.append({"role": "user", "content": user_content})

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7
        )
        answer = response.choices[0].message.content.strip()

        if bot["bot_name"] == "👨‍💻 Артур":
            artur_answer = answer

        responses.append({
            "bot_name": bot["bot_name"],
            "answer": answer
        })

    return responses

# --- Главная страница ---
@app.route("/", methods=["GET"])
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="ru">
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
      responseDiv.innerHTML = "⏳ Генерация ответов...";

      try {
        const res = await fetch("/submit", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ idea })
        });

        if (!res.ok) {
          throw new Error("Ошибка сервера: " + res.status);
        }

        const data = await res.json();

        if (data.error) {
          responseDiv.innerHTML = `<span style="color:red;">⚠️ ${data.error}</span>`;
          return;
        }

        responseDiv.innerHTML = data.map(bot => `
          <div>
            <strong>${bot.bot_name}</strong>:<br/>
            ${bot.answer}
            <hr/>
          </div>
        `).join("");
      } catch (err) {
        responseDiv.innerHTML = `<span style="color:red;">❌ ${err.message}</span>`;
      }
    }
  </script>
</body>
</html>
""")

# --- POST обработка запроса ---
@app.route("/submit", methods=["POST"])
def submit():
    try:
        data = request.get_json()
        idea = data.get("idea", "").strip()
        if not idea:
            return jsonify({"error": "Запрос не должен быть пустым."}), 400

        print("🧠 Получена идея:", idea)
        responses = generate_bot_responses(idea)
        print("✅ Ответы сформированы")

        return jsonify(responses)

    except Exception as e:
        print("❌ Ошибка в /submit:", str(e))
        return jsonify({"error": str(e)}), 500

# --- Запуск локально ---
if __name__ == "__main__":
    app.run(debug=True)
