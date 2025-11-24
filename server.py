from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

GUPSHUP_API_KEY = os.environ.get("GUPSHUP_API_KEY")
GUPSHUP_SOURCE = os.environ.get("GUPSHUP_SOURCE")

@app.route("/gupshup/send", methods=["POST"])
def send_message():
    data = request.json
    
    to = data.get("to")
    message = data.get("message")

    url = "https://api.gupshup.io/wa/api/v1/msg"

    payload = {
        "channel": "whatsapp",
        "source": GUPSHUP_SOURCE,
        "destination": to,
        "message": {
            "type": "text",
            "text": message
        }
    }

    headers = {
        "apikey": GUPSHUP_API_KEY,
        "Content-Type": "application/json"
    }

    resp = requests.post(url, json=payload, headers=headers)

    return jsonify({"ok": True, "gupshup_response": resp.json()})


@app.route("/gupshup/incoming", methods=["POST"])
def incoming():
    print("Incoming Message:", request.json)
    return jsonify({"ok": True})


@app.route("/")
def root():
    return "Gupshup Python Webhook Running ✔"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
