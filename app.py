from flask import Flask, render_template, make_response

app = Flask(__name__)

@app.route("/")
def home():
    html = render_template("index.html")
    response = make_response(html)
    response.headers["Content-Type"] = "text/html"
    return response

if __name__ == "__main__":
    app.run()
