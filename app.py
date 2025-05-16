from flask import Flask, request, jsonify, render_template, make_response
import os

app = Flask(__name__)

print("TEMPLATE_FOLDER:", os.path.abspath("templates"))

@app.route("/")
def home():
    html = render_template("index.html")
    response = make_response(html)
    response.headers['Content-Type'] = 'text/html'
    return response

if __name__ == "__main__":
    app.run(debug=True)
