from flask import Flask, request
import requests

TOKEN = "8681244479:AAFBkhHZRG32Te0mY_7yIA_ZBVU6V6Ldl7Q"
ADMIN_ID = 777430200

app = Flask(__name__)

users = set()
blocked = set()
pending = {}   # id -> chat_id


def send(chat_id, text):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": chat_id, "text": text}
    )


@app.route("/")
def home():
    return "Bot is running"


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if not data:
        return "ok"

    msg = data.get("message", {})
    chat_id = msg.get("chat", {}).get("id")
    text = msg.get("text", "")

    if not chat_id:
        return "ok"

    # ثبت کاربر
    users.add(chat_id)

    # اگر بلاک شده
    if chat_id in blocked:
        return "blocked"

    # دستورات
    if text == "/start":
        send(chat_id, "🌊 خوش اومدی به چت ناشناس")

    elif text == "/block":
        blocked.add(chat_id)
        send(chat_id, "🚫 بلاک شدی")

    elif text == "/unblock":
        blocked.discard(chat_id)
        send(chat_id, "✅ آنبلاک شدی")

    elif text.startswith("/reply"):
        try:
            parts = text.split(" ", 2)
            target_id = int(parts[1])
            answer = parts[2]

            send(target_id, f"💬 جواب ناشناس:\n{answer}")
            send(chat_id, "🌊 ارسال شد")

        except:
            send(chat_id, "❌ فرمت درست: /reply id message")

    else:
        # پیام ناشناس به ادمین
        msg_id = len(pending) + 1
        pending[msg_id] = chat_id

        send(ADMIN_ID,
f"""📩 پیام ناشناس #{msg_id}

{text}

برای جواب:
 /reply {msg_id} جواب شما
""")

        send(chat_id, "📨 پیام شما ارسال شد")

    return "ok"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
