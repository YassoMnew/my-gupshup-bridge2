from flask import Flask, request, jsonify
import requests
import os
import traceback

app = Flask(__name__)

GUPSHUP_API_KEY = os.environ.get("GUPSHUP_API_KEY")
GUPSHUP_SOURCE = os.environ.get("GUPSHUP_SOURCE")


@app.route("/gupshup/send", methods=["POST"])
def send_message():
    try:
        # استقبل الـ JSON بأمان
        data = request.get_json(silent=True) or {}

        to = data.get("to")
        message = data.get("message")

        # تأكد من وجود to و message
        if not to or not message:
            return jsonify({
                "ok": False,
                "error": "Missing 'to' or 'message' in JSON body",
                "received_body": data
            }), 400

        # تأكد من الـ ENV VARS
        if not GUPSHUP_API_KEY or not GUPSHUP_SOURCE:
            return jsonify({
                "ok": False,
                "error": "Missing GUPSHUP_API_KEY or GUPSHUP_SOURCE env vars",
                "GUPSHUP_API_KEY": bool(GUPSHUP_API_KEY),
                "GUPSHUP_SOURCE": bool(GUPSHUP_SOURCE),
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

        resp = requests.post(url, json=payload, headers=headers)

        # جرّب تقرأ JSON من Gupshup
        try:
            gs_json = resp.json()
        except ValueError:
            gs_json = None

        return jsonify({
            "ok": resp.ok,
            "status_code": resp.status_code,
            "gupshup_response": gs_json,
            "raw_response": resp.text
        })

    except Exception as e:
        # لو حصل أي error غير متوقع
        traceback.print_exc()
        return jsonify({
            "ok": False,
            "error": str(e),
            "type": type(e).__name__
        }), 500


@app.route("/gupshup/incoming", methods=["POST"])
def incoming():
    print("Incoming Message:", request.json)
    return jsonify({"ok": True})


@app.route("/")
def root():
    return "Gupshup Python Webhook Running ✔"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
