from flask import Flask, request, jsonify
import requests
import os
import json
import traceback

app = Flask(__name__)

# نقرأ المتغيرات من الـ Environment (من Render)
GUPSHUP_API_KEY = os.environ.get("GUPSHUP_API_KEY")
GUPSHUP_SOURCE = os.environ.get("GUPSHUP_SOURCE")


@app.route("/gupshup/send", methods=["POST"])
def send_message():
    try:
        # استقبل JSON من الريكوست الخارجي (الموبايل / Respond.ai)
        data = request.get_json(silent=True) or {}

        to = data.get("to")
        message = data.get("message")

        # لو ناقص to أو message نرجع Error واضح
        if not to or not message:
            return jsonify({
                "ok": False,
                "error": "Missing 'to' or 'message' in JSON body",
                "received_body": data
            }), 400

        # تأكد من وجود الـ API KEY و SOURCE
        if not GUPSHUP_API_KEY or not GUPSHUP_SOURCE:
            return jsonify({
                "ok": False,
                "error": "Missing GUPSHUP_API_KEY or GUPSHUP_SOURCE env vars",
                "has_api_key": bool(GUPSHUP_API_KEY),
                "has_source": bool(GUPSHUP_SOURCE),
            }), 500

        # URL بتاع Gupshup
        url = "https://api.gupshup.io/wa/api/v1/msg"

        # جسم الرسالة اللي هيتبعت كـ JSON string
        msg_obj = {
            "type": "text",
            "text": message
        }

        # هنا بنبعت FORM مش JSON
        payload = {
            "channel": "whatsapp",
            "source": GUPSHUP_SOURCE,
            "src.name": "009871",              # اسم الـ App بتاعك في Gupshup
            "destination": to,
            "message": json.dumps(msg_obj),    # JSON string جوا الـ form
        }

        headers = {
            "apikey": GUPSHUP_API_KEY,
            "Content-Type": "application/x-www-form-urlencoded"
        }

        # نبعت الريكوست لـ Gupshup
        resp = requests.post(url, data=payload, headers=headers, timeout=15)

        # نحاول نقرأ JSON من رد Gupshup
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
        # لو حصل Error غير متوقع
        traceback.print_exc()
        return jsonify({
            "ok": False,
            "error": str(e),
            "type": type(e).__name__
        }), 500


@app.route("/gupshup/incoming", methods=["POST"])
def incoming():
    # أي رسالة جاية من Gupshup هتظهر في اللوج هنا
    print("Incoming Message:", request.json)
    return jsonify({"ok": True})


@app.route("/")
def root():
    return "Gupshup Python Webhook Running ✔"


if __name__ == "__main__":
    # للتجربة لوكال؛ Render بيستخدم gunicorn بره
    app.run(host="0.0.0.0", port=3000)
