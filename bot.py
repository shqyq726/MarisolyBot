from flask import Flask, request
import requests
import json
import os

TOKEN = "8616514786:AAG5Kffc5xJLvdb_AUA2G4crTrC_dKUCcN8"
ADMIN_ID = 777430200
URL = "https://your-app.onrender.com/webhook"

app = Flask(__name__)

USERS_FILE = "users.json"


# ================= DB =================

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


def set_block(chat_id, value):
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


# ================= TELEGRAM =================

def send_message(chat_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text
    }

    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)

    r = requests.post(url, data=payload)
    print("MSG:", r.text)


def send_media(chat_id, file_id, media_type, caption="", reply_markup=None):

    methods = {
        "photo": "sendPhoto",
        "video": "sendVideo",
        "voice": "sendVoice",
        "audio": "sendAudio",
        "document": "sendDocument"
    }

    keys = {
        "photo": "photo",
        "video": "video",
        "voice": "voice",
        "audio": "audio",
        "document": "document"
    }

    url = f"https://api.telegram.org/bot{TOKEN}/{methods[media_type]}"

    payload = {
        "chat_id": chat_id,
        keys[media_type]: file_id,
        "caption": caption
    }

    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)

    r = requests.post(url, data=payload)
    print("MEDIA:", r.text)


# ================= BUTTONS =================

def buttons(code, chat_id):
    return {
        "inline_keyboard": [[
            {"text": "💬 Reply", "callback_data": f"reply|{code}"},
            {"text": "🚫 Block", "callback_data": f"block|{chat_id}"},
            {"text": "✅ Unblock", "callback_data": f"unblock|{chat_id}"}
        ]]
    }


# ================= WEBHOOK =================

@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.get_json()
    if not data:
        return "ok"

    # ========== CALLBACKS ==========
    if "callback_query" in data:
        cq = data["callback_query"]
        action, value = cq["data"].split("|")

        if action == "block":
            set_block(value, True)
            send_message(ADMIN_ID, "🚫 کاربر بلاک شد")

        elif action == "unblock":
            set_block(value, False)
            send_message(ADMIN_ID, "✅ کاربر آنبلاک شد")

        elif action == "reply":
            send_message(ADMIN_ID, f"☀️ ریپلای:\n/reply {value} پیام")

        return "ok"

    msg = data.get("message")
    if not msg:
        return "ok"

    chat_id = msg["chat"]["id"]
    text = msg.get("text", "")

    # ================= ADMIN =================
    if chat_id == ADMIN_ID:

        if text.startswith("/reply"):
            parts = text.split(" ", 2)
            if len(parts) < 3:
                send_message(ADMIN_ID, " /reply U001 text")
                return "ok"

            code = parts[1]
            reply = parts[2]

            target = find_chat_by_code(code)
            if not target:
                send_message(ADMIN_ID, "❌ کاربر پیدا نشد")
                return "ok"

            send_message(target, f"☀️پاسخ :\n\n{reply}")
            send_message(ADMIN_ID, "✅ پیام ارسال شد")
            return "ok"

        return "ok"

    # ================= USER =================
    user = get_user(chat_id)

    if user["blocked"]:
        return "ok"

    code = user["code"]
    first = msg["from"].get("first_name", "")
    username = msg["from"].get("username", "ندارد")

    header = f"📩 {code}\n☀️ {first}\n🌊 @{username}"

    # ========= TEXT =========
    if msg.get("text"):
        send_message(ADMIN_ID, header + "\n\n" + text, buttons(code, chat_id))
        send_message(chat_id, "🌊 ارسال شد")

    # ========= PHOTO =========
    elif msg.get("photo"):
        file_id = msg["photo"][-1]["file_id"]

        send_media(
            ADMIN_ID,
            file_id,
            "photo",
            caption=header,
            reply_markup=buttons(code, chat_id)
        )

        send_message(chat_id, "🌊 ارسال شد")

    # ========= VIDEO =========
    elif msg.get("video"):
        send_media(
            ADMIN_ID,
            msg["video"]["file_id"],
            "video",
            caption=header,
            reply_markup=buttons(code, chat_id)
        )

        send_message(chat_id, "🌊 ارسال شد")

    # ========= VOICE =========
    elif msg.get("voice"):
        send_media(
            ADMIN_ID,
            msg["voice"]["file_id"],
            "voice",
            caption=header,
            reply_markup=buttons(code, chat_id)
        )

        send_message(chat_id, "🌊 ارسال شد")

    # ========= AUDIO =========
    elif msg.get("audio"):
        send_media(
            ADMIN_ID,
            msg["audio"]["file_id"],
            "audio",
            caption=header,
            reply_markup=buttons(code, chat_id)
        )

        send_message(chat_id,"🌊 ارسال شد")

    # ========= DOCUMENT =========
    elif msg.get("document"):
        send_media(
            ADMIN_ID,
            msg["document"]["file_id"],
            "document",
            caption=header,
            reply_markup=buttons(code, chat_id)
        )

        send_message(chat_id, "🌊 ارسال شد")

    return "ok"


# ================= START =================

if __name__ == "__main__":
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/setWebhook",
        data={"url": URL}
    )

    app.run(host="0.0.0.0", port=10000)
