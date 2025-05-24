const bots = ["🤓 Вика", "🕵️‍♀️ Настя", "👨‍💻 Артур", "🔍 Свати", "📅 Лена", "🧠 Денис"];

function format(text) {
  const html = text
    .replace(/\n{2,}/g, '</p><p>')
    .replace(/\n/g, '<br>')
    .replace(/(\d+\.\s.+?)(?=\d+\.\s|$)/gs, (match) => {
      const items = match.trim().split(/\n/).map(item => `<li>${item.replace(/^\d+\.\s/, '')}</li>`).join('');
      return `<ol>${items}</ol>`;
    });
  return "<p>" + html + "</p>";
}

async function sendIdea() {
  const idea = document.getElementById("idea").value;
  const responseDiv = document.getElementById("responses");
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
      const formatted = format(data.answer);
      responseBlocks[i].innerHTML = `
        <div class='bot-label'>${data.bot_name}:</div>
        <div class="formatted-answer">${formatted}</div>
        <button onclick="copyText(\`${data.answer}\`)" style="margin-top:10px;">📋 Скопировать</button>
      `;
      if (i === bots.length - 1) {
        document.getElementById("copy-all-container").style.display = "block";
      }
    }
  }
}

function copyText(text) {
  const textarea = document.createElement("textarea");
  textarea.value = text;
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand("copy");
  document.body.removeChild(textarea);
  alert("Скопировано!");
}

function copyAll() {
  const idea = document.getElementById("idea").value.trim();
  const responses = document.querySelectorAll(".response");
  let result = `📝 Идея:\n${idea}\n\n`;

  responses.forEach(el => {
    const botName = el.querySelector(".bot-label").innerText;
    const text = el.querySelector(".formatted-answer")?.innerText || "";
    result += `${botName}\n${text}\n\n`;
  });

  const textarea = document.createElement("textarea");
  textarea.value = result.trim();
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand("copy");
  document.body.removeChild(textarea);
  alert("Все ответы скопированы!");
}