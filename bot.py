from flask import Flask, request
import requests
import json
import os

TOKEN = "8616514786:AAG5Kffc5xJLvdb_AUA2G4crTrC_dKUCcN8"
ADMIN_ID = 777430200
URL = "https://marisolybot.onrender.com/webhook"

app = Flask(__name__)

USERS_FILE = "users.json"


# ----------------------
# فایل کاربران
# ----------------------

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f)


def get_user_code(chat_id):
    users = load_users()

    chat_id = str(chat_id)

    if chat_id in users:
        return users[chat_id]["code"]

    new_code = f"U{len(users)+1:03d}"

    users[chat_id] = {
        "code": new_code
    }

    save_users(users)

    return new_code


def get_chat_id_by_code(code):
    users = load_users()

    for chat_id, data in users.items():
        if data["code"] == code:
            return int(chat_id)

    return None


# ----------------------
# تلگرام
# ----------------------

def set_webhook():
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/setWebhook",
        data={"url": URL}
    )


def send_message(chat_id, text):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={
            "chat_id": chat_id,
            "text": text
        }
    )


# ----------------------
# صفحات
# ----------------------

@app.route("/")
def home():
    return "Bot is running!"


@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.get_json()

    if not data:
        return "ok"

    message = data.get("message")

    if not message:
        return "ok"

    text = message.get("text", "")
    chat_id = message["chat"]["id"]

    first_name = message["from"].get("first_name", "")
    username = message["from"].get("username", "ندارد")

    # ادمین
    if chat_id == ADMIN_ID:

        if text.startswith("/reply"):

            parts = text.split(" ", 2)

            if len(parts) < 3:
                send_message(
                    ADMIN_ID,
                    "فرمت:\n/reply U001 سلام"
                )
                return "ok"

            code = parts[1]
            reply_text = parts[2]

            target_chat = get_chat_id_by_code(code)

            if not target_chat:
                send_message(
                    ADMIN_ID,
                    "کاربر پیدا نشد."
                )
                return "ok"

            send_message(
                target_chat,
                f"💌 پاسخ ناشناس:\n\n{reply_text}"
            )

            send_message(
                ADMIN_ID,
                "🌊 ارسال شد"
            )

        return "ok"

    # کاربر عادی

    if text == "/start":
        send_message(
            chat_id,
            "🌊 خوش اومدی به Marisol"
        )
        return "ok"

    user_code = get_user_code(chat_id)

    admin_text = (
        f"☀️ {user_code}\n"
        f"🌊 {first_name}\n"
        f"🌱 @{username}\n\n"
        f"{text}"
    )

    send_message(
        ADMIN_ID,
        admin_text
    )

    send_message(
        chat_id,
        "ارسال شد 🌊"
    )

    return "ok"


if __name__ == "__main__":
    set_webhook()
    app.run(host="0.0.0.0", port=10000)
