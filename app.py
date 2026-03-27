from flask import Flask, render_template, request, jsonify
from Brasileirao import chatbot

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get")
def get_response():
    user_msg = request.args.get("msg")
    response = chatbot.respond(user_msg)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)