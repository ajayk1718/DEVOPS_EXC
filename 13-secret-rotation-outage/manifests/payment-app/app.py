from flask import Flask
import os

app = Flask(__name__)

TOKEN = os.getenv("API_TOKEN")

@app.route("/")
def home():

    supplied = os.getenv("CLIENT_TOKEN", "")

    if supplied == TOKEN:
        return "200 OK - Authorized"

    return "401 Unauthorized"

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )
