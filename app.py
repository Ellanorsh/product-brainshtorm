from flask import Flask, request, jsonify, render_template
import os

app = Flask(__name__)  # создаём Flask-приложение

print("TEMPLATE_FOLDER:", os.path.abspath("templates"))

@app.route("/")
def home():
    html = render_template("index.html")
    response = make_response(html)
    response.headers['Content-Type'] = 'text/html'
    return response

# запуск локально (Heroku игнорирует этот блок, но он нужен для отладки)
if __name__ == "__main__":
    app.run(debug=True)
