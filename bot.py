from flask import Flask, request
import requests
import json
import os

TOKEN = "8616514786:AAG5Kffc5xJLvdb_AUA2G4crTrC_dKUCcN8"
ADMIN_ID = 777430200
URL = "https://your-app.onrender.com/webhook"

app = Flask(__name__)

USERS_FILE = "users.json"


# ----------------------
# DB
# ----------------------
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f)


def get_user(chat_id):
    users = load_users()
    chat_id = str(chat_id)

    if chat_id not in users:
        users[chat_id] = {
            "code": f"U{len(users)+1:03d}",
            "blocked": False
        }
        save_users(users)

    return users[chat_id]


def set_block(chat_id, value=True):
    users = load_users()
    chat_id = str(chat_id)

    if chat_id in users:
        users[chat_id]["blocked"] = value
        save_users(users)


def find_chat_by_code(code):
    users = load_users()
    for chat_id, data in users.items():
        if data["code"] == code:
            return int(chat_id)
    return None


# ----------------------
# Telegram API
# ----------------------
def send_message(chat_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text
    }

    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)

    requests.post(url, data=payload)


def send_action_buttons(code, chat_id):
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "✉️ Reply", "callback_data": f"reply|{code}"},
                {"text": "🚫 Block", "callback_data": f"block|{chat_id}"}
            ]
        ]
    }
    return keyboard


# ----------------------
# Webhook
# ----------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if not data:
        return "ok"

    # ---------------- callback buttons ----------------
    if "callback_query" in data:
        cq = data["callback_query"]
        data_text = cq["data"]

        if data_text.startswith("block|"):
            chat_id = data_text.split("|")[1]
            set_block(chat_id, True)
            send_message(ADMIN_ID, "🚫 کاربر بلاک شد")
            return "ok"

        if data_text.startswith("reply|"):
            code = data_text.split("|")[1]
            send_message(ADMIN_ID, f"✉️ Reply mode:\n/reply {code} متن")
            return "ok"

    # ---------------- message ----------------
    message = data.get("message")
    if not message:
        return "ok"

    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    # ADMIN
    if chat_id == ADMIN_ID:

        if text.startswith("/reply"):
            parts = text.split(" ", 2)
            if len(parts) < 3:
                send_message(ADMIN_ID, " /reply U001 text")
                return "ok"

            code = parts[1]
            msg = parts[2]

            target = find_chat_by_code(code)
            if not target:
                send_message(ADMIN_ID, "❌ کاربر پیدا نشد")
                return "ok"

            send_message(target, f"💬 پاسخ:\n\n{msg}")
            send_message(ADMIN_ID, "🌊 ارسال شد")
            return "ok"

        return "ok"

    # USER
    user = get_user(chat_id)

    if user["blocked"]:
        return "ok"

    code = user["code"]
    first_name = message["from"].get("first_name", "user")
    username = message["from"].get("username", "ندارد")

    admin_text = f"""📩 {code}
☀️ {first_name}
🌊 @{username}

{text}"""

    send_message(
        ADMIN_ID,
        admin_text,
        reply_markup=send_action_buttons(code, chat_id)
    )

    send_message(chat_id, "ارسال شد 🌊")

    return "ok"


# ----------------------
if __name__ == "__main__":
    requests.post(f"https://api.telegram.org/bot{TOKEN}/setWebhook", data={"url": URL})
    app.run(host="0.0.0.0", port=10000)
