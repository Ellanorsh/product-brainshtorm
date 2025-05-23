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
    .copy-btn {
      background-color: #10a37f;
      color: white;
      border: none;
      padding: 6px 12px;
      font-size: 12px;
      border-radius: 6px;
      cursor: pointer;
      margin-left: 8px;
      vertical-align: middle;
    }
    .copy-btn:hover {
      background-color: #0f9774;
    }
    #copy-all-btn {
      background-color: #10a37f;
      color: white;
      border: none;
      padding: 12px 24px;
      font-size: 16px;
      border-radius: 8px;
      cursor: pointer;
      display: block;
      margin-top: 20px;
      margin-left: auto;
      margin-right: auto;
    }
    #copy-all-btn:hover {
      background-color: #0f9774;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>💡 Отправить продуктовую идею</h1>
    <textarea id="idea" rows="4" placeholder="Введите вашу идею здесь..."></textarea>
    <button onclick="sendIdea()">Отправить</button>

    <div id="responses"></div>
    <button id="copy-all-btn">Copy All</button>
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
          responseBlocks[i].innerHTML = `<div class='bot-label'>${data.bot_name}:</div>${format(data.answer)}`;
          const copyButton = document.createElement('button');
          copyButton.innerText = 'Copy';
          copyButton.classList.add('copy-btn');
          // Inline styles removed, will be handled by CSS
          responseBlocks[i].appendChild(copyButton);

          copyButton.addEventListener('click', () => {
            const responseClone = responseBlocks[i].cloneNode(true);
            // Remove the bot label and the button itself from the clone
            responseClone.querySelector('.bot-label').remove();
            responseClone.querySelector('.copy-btn').remove();
            
            const textToCopy = responseClone.innerText.trim();
            navigator.clipboard.writeText(textToCopy).then(() => {
              copyButton.innerText = 'Copied!';
              setTimeout(() => {
                copyButton.innerText = 'Copy';
              }, 2000);
            }).catch(err => {
              console.error('Failed to copy text: ', err);
              // Optionally, provide feedback to the user that copy failed
            });
          });
        }
      }
    }

    function copyAllConversation() {
      const ideaText = document.getElementById("idea").value;
      if (!ideaText && document.querySelectorAll(".response").length === 0) {
        alert("Nothing to copy!");
        return;
      }

      let conversationText = "Initial Idea:\n" + ideaText;
      const responseBlocks = document.querySelectorAll(".response");
      const copyAllBtn = document.getElementById('copy-all-btn');

      responseBlocks.forEach(block => {
        const botLabelElement = block.querySelector('.bot-label');
        if (!botLabelElement) return; // Skip if no bot label (e.g. initial loading message)

        const botName = botLabelElement.innerText.replace(':', '').trim();
        
        // Clone the block to safely remove elements for text extraction
        const blockClone = block.cloneNode(true);
        blockClone.querySelector('.bot-label').remove();
        const copyBtnInClone = blockClone.querySelector('.copy-btn');
        if (copyBtnInClone) {
          copyBtnInClone.remove();
        }
        
        // Handle cases where response might just be the "⏳ Ждем ответ..."
        const answerText = blockClone.innerText.trim();
        if (answerText === "⏳ Ждем ответ..." || answerText === "" || answerText.startsWith("❌ Ошибка:")) {
            conversationText += `\n\n${botName}:\n${answerText}`;
        } else {
            conversationText += `\n\n${botName}:\n${answerText}`;
        }
      });

      navigator.clipboard.writeText(conversationText).then(() => {
        const originalText = copyAllBtn.innerText;
        copyAllBtn.innerText = 'Copied All!';
        setTimeout(() => {
          copyAllBtn.innerText = originalText;
        }, 2000);
      }).catch(err => {
        console.error('Failed to copy all text: ', err);
        alert('Failed to copy conversation.');
      });
    }
    
    // Setup event listener for the copy all button
    // Ensure the button is present in the DOM before attaching listener
    // One way is to put this script at the end of body or use DOMContentLoaded
    // For this template string, it's fine as is because script runs after HTML.
    // However, to be super safe, especially if script was in <head>:
    // document.addEventListener('DOMContentLoaded', () => {
    //  const copyAllBtn = document.getElementById('copy-all-btn');
    //  if(copyAllBtn) {
    //    copyAllBtn.onclick = copyAllConversation;
    //  }
    // });
    // Simplified for now as the button is defined before this part of the script.
    // Wait for the DOM to be fully loaded before attaching event listeners
    // This is a more robust way
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            const btn = document.getElementById('copy-all-btn');
            if(btn) btn.onclick = copyAllConversation;
        });
    } else {
        // DOMContentLoaded has already fired
        const btn = document.getElementById('copy-all-btn');
        if(btn) btn.onclick = copyAllConversation;
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
