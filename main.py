import os

from flask import Flask, redirect, render_template, request


app = Flask(__name__)


@app.route("/")
def index():

    remaining = 3.8
    total=6.8

    # Render the HTML page current syringe status
    return render_template("tracker.html", remaining=remaining, total=total)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 4000))
    app.run(host="0.0.0.0", port=port)