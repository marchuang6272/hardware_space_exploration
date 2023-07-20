"""
Flask app to launch visualizer in a web browser
"""
from flask import Flask, send_file

app = Flask(__name__)


@app.route("/")
def index():
    return send_file("generated_files/html/top_module.html")


@app.route("/<name>")
def display_html(name):
    filename = f"{name}.html"
    return send_file("generated_files/html/" + name + ".html")


if __name__ == "__main__":
    app.run(debug=True)
