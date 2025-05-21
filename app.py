from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI
import os
import traceback

app = Flask(__name__)

# --- Настройка клиента OpenAI ---
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
        "instruction": "Ты технический аналитик. Подумай о корнер-кейсах и дополнительных сценариях."
    },
    {
        "bot_name": "📅 Лена",
        "instruction": "Ты менеджер проекта и твоя задача проанализировать изначальный запрос, ответы всех остальных ботов и составить два плана проекта (примерный роадмап). Один план для MVP и реализации только успешного сценария и второй с реализацией всех сценариев и корнер кейсов. В планах обязательно должны быть предварительные оценки по количеству необходимых человекочасов разработчиков, тестирования и других специалистов, которых нужно привлечь."
    },
    {
        "bot_name": "🧠 Денис",
        "instruction": "Ты ведущий разработчик. Дай критическую оценку: почему гипотеза может быть плохой, зачем это вообще нужно."
    }
]

# --- Генерация ответов ---
def generate_bot_responses(user_prompt: str):
    responses = []
    artur_answer = None

    for bot in bots:
        print(f"🟡 Генерация ответа от {bot['bot_name']}")
        full_prompt = f"{bot['instruction']}\n\nПользовательский запрос: {user_prompt}"

        if bot["bot_name"] == "📅 Лена" and artur_answer:
            full_prompt += f"\n\nОтвет Артура:\n{artur_answer}"

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": bot["instruction"]},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7
            )
            answer = response.choices[0].message.content.strip()

            if bot["bot_name"] == "👨‍💻 Артур":
                artur_answer = answer

            responses.append({
                "bot_name": bot["bot_name"],
                "answer": answer
            })

        except Exception as e:
            print(f"❌ Ошибка у {bot['bot_name']}: {e}")
            traceback.print_exc()
            responses.append({
                "bot_name": bot["bot_name"],
                "answer": f"⚠️ Ошибка генерации ответа: {str(e)}"
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

      const res = await fetch("/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ idea })
      });

      const data = await res.json();
      if (data.error) {
        responseDiv.innerHTML = "❌ Ошибка: " + data.error;
        return;
      }

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

# --- POST: генерация идей ---
@app.route("/submit", methods=["POST"])
def submit():
    try:
        data = request.get_json()
        idea = data.get("idea", "").strip()
        print("📩 Получен запрос:", idea)

        if not idea:
            return jsonify({"error": "Поле идеи не заполнено."}), 400

        results = generate_bot_responses(idea)
        print("✅ Ответы отправлены.")
        return jsonify(results)

    except Exception as e:
        print("❌ Ошибка в обработчике submit:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
