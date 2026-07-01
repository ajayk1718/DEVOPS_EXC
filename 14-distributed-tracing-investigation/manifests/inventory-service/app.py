from flask import Flask
import requests

app = Flask(__name__)

@app.route("/")
def inventory():

    print("Inventory Service Called")

    response = requests.get(
        "http://payment-service:5000/"
    )

    return "Inventory -> " + response.text

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )
