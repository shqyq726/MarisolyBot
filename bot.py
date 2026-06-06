from flask import Flask, request
import requests

TOKEN = "8681244479:AAFBkhHZRG32Te0mY_7yIA_ZBVU6V6Ldl7Q"
ADMIN_ID = 777430200

app = Flask(__name__)

users = set()
blocked = set()
pending = {}  # id -> chat_id


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

    # 👇 ادمین هیچ‌وقت بلاک نمی‌شود
    if chat_id == ADMIN_ID:
        pass
    elif chat_id in blocked:
        return "blocked"

    # ---------------- COMMANDS ----------------

    if text == "/start":
        send(chat_id, "🌊 خوش اومدی به چت ناشناس")

    elif text == "/block":
        if chat_id != ADMIN_ID:
            blocked.add(chat_id)
            send(chat_id, "🚫 بلاک شدی")

    elif text == "/unblock":
        if chat_id != ADMIN_ID:
            blocked.discard(chat_id)
            send(chat_id, "✅ آنبلاک شدی")

    # 🔥 ریست اضطراری (فقط برای تست)
    elif text == "/reset":
        blocked.clear()
        send(chat_id, "♻️ همه بلاک‌ها پاک شد")

    # جواب دادن ادمین به پیام ناشناس
    elif text.startswith("/reply"):
        try:
            parts = text.split(" ", 2)
            target_id = int(parts[1])
            answer = parts[2]

            send(target_id, f"💬 جواب
