from flask import Flask, request, jsonify, render_template
import os

app = Flask(__name__)  # <-- сначала создаём объект Flask

print("TEMPLATE_FOLDER:", os.path.abspath("templates"))

@app.route("/")
def home():
    return render_template("index.html")  # <-- потом используем app
