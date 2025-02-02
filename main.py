import os

from flask import Flask, redirect, render_template, request

app = Flask(__name__)


@app.route("/deepseek")
def deepseek():

    remaining = 3.8
    total=6.8

    # Render the HTML page current syringe status
    return render_template("tracker-deepseek.html", remaining=remaining, total=total)

@app.route("/chatgpt")
def chatgpt():

    remaining = 3.8
    total=6.8

    # Render the HTML page current syringe status
    return render_template("tracker-chatgpt.html", remaining=remaining, total=total)

@app.route("/claude")
def claude():

    remaining = 3.8
    total=6.8

    # Render the HTML page current syringe status
    return render_template("tracker-claude.html", remaining=remaining, total=total)



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 4000))
    app.run(host="0.0.0.0", port=port)