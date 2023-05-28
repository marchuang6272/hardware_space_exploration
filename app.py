from flask import Flask, send_file

app = Flask(__name__)
html_file = "generated_files/display.html"


@app.route("/")
def index():
    return send_file(html_file)


if __name__ == "__main__":
    app.run(debug=True)
