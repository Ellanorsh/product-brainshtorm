
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI
import os
import concurrent.futures

app = Flask(__name__)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

bots = [
    {
        "bot_name": "🤓 Вика",
        "instruction": "Ты продуктовый менеджер и твоя задача проанализировать изначальный запрос и найти подкрепляющую статистику, которая позволит улучшить изначальную гипотезу. Например: если гипотеза включает какое-то улучшение и изменение, поискать исследования, которые бы подтверждали, что такие изменения хорошо отражаются на продукте и увеличивают ключевые метрики (указать какие)"
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

def ask_openai(instruction, user_prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": instruction},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

def generate_bot_responses(user_prompt):
    responses = {}

    def handle_bot(bot):
        print(f"🟡 Генерация ответа от {bot['bot_name']}")
        if bot["bot_name"] == "📅 Лена":
            while not all(x in responses for x in ["👨‍💻 Артур", "🕵️‍♀️ Настя", "🔍 Свати"]):
                pass
            combined_context = f"{user_prompt}\n\nОтвет Артура: {responses['👨‍💻 Артур']}\n\nОтвет Насти: {responses['🕵️‍♀️ Настя']}\n\nОтвет Свати: {responses['🔍 Свати']}"
            return bot["bot_name"], ask_openai(bot["instruction"], combined_context)
        else:
            return bot["bot_name"], ask_openai(bot["instruction"], user_prompt)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_bot = {executor.submit(handle_bot, bot): bot for bot in bots}
        for future in concurrent.futures.as_completed(future_to_bot):
            bot_name, answer = future.result()
            responses[bot_name] = answer

    return [{"bot_name": bot, "answer": answer} for bot, answer in responses.items()]

@app.route("/", methods=["GET"])
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="ru">
<head><meta charset="UTF-8"><title>Product Brainstorm</title></head>
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
      responseDiv.innerHTML = data.map(bot => `
        <div><strong>${bot.bot_name}</strong>:<br/>${bot.answer}<hr/></div>
      `).join("");
    }
  </script>
</body>
</html>
""")

@app.route("/submit", methods=["POST"])
def submit():
    try:
        data = request.get_json()
        idea = data.get("idea", "").strip()
        if not idea:
            return jsonify({"error": "Запрос не должен быть пустым."}), 400
        print(f"📩 Получен запрос: {idea}")
        responses = generate_bot_responses(idea)
        print("✅ Ответы отправлены.")
        return jsonify(responses)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
