from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

GUPSHUP_API_KEY = os.environ.get("GUPSHUP_API_KEY")
GUPSHUP_SOURCE = os.environ.get("GUPSHUP_SOURCE")


@app.route("/gupshup/send", methods=["POST"])
def send_message():
    # 1) استقبل الـ JSON بأمان
    data = request.get_json(silent=True) or {}

    to = data.get("to")
    message = data.get("message")

    # 2) تأكد إن to و message موجودين
    if not to or not message:
        return jsonify({
            "ok": False,
            "error": "Missing 'to' or 'message' in JSON body",
            "received_body": data
        }), 400

    # 3) تأكد إن الـ ENV VARS موجودة
    if not GUPSHUP_API_KEY or not GUPSHUP_SOURCE:
        return jsonify({
            "ok": False,
            "error": "Missing GUPSHUP_API_KEY or GUPSHUP_SOURCE env vars"
        }), 500

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

    # 4) ابعت لـ Gupshup
    resp = requests.post(url, json=payload, headers=headers)

    # 5) حاول تقرأ JSON لو فيه
    try:
        gs_json = resp.json()
    except ValueError:
        # الرد مش JSON (ممكن HTML Error)
        return jsonify({
            "ok": False,
            "status_code": resp.status_code,
            "raw_response": resp.text
        }), 500

    return jsonify({
        "ok": resp.ok,
        "status_code": resp.status_code,
        "gupshup_response": gs_json
    })


@app.route("/gupshup/incoming", methods=["POST"])
def incoming():
    print("Incoming Message:", request.json)
    return jsonify({"ok": True})


@app.route("/")
def root():
    return "Gupshup Python Webhook Running ✔"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
