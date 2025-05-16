import os
print("TEMPLATE_FOLDER:", os.path.abspath("templates"))

@app.route("/")
def home():
    print("⚡️ Рендер шаблона запущен")
    return render_template("index.html")
