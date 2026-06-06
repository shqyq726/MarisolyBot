from flask import Flask, request
import requests
import json
import os

TOKEN = "8616514786:AAEWF9AdXPmYQuVXihGdmd_-Ir8z6bIeyD8"
ADMIN_ID = 777430200
URL = "https://your-app.onrender.com/webhook"

REPLY_MAP_FILE = "reply_map.json"
USERS_FILE = "users.json"

app = Flask(__name__)

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

def load_map():
    if os.path.exists(REPLY_MAP_FILE):
        with open(REPLY_MAP_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_map(data):
    with open(REPLY_MAP_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)

# ================= TELEGRAM =================

def send_message(chat_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text
    }

    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)

    requests.post(url, data=payload)

def send_media(chat_id, file_id, media_type, caption=None, reply_markup=None):

    methods = {
        "photo": "sendPhoto",
        "video": "sendVideo",
        "voice": "sendVoice",
        "audio": "sendAudio",
        "document": "sendDocument",
        "sticker": "sendSticker",
        "animation": "sendAnimation",
        "video_note": "sendVideoNote",
    }

    keys = {
        "photo": "photo",
        "video": "video",
        "voice": "voice",
        "audio": "audio",
        "document": "document",
        "sticker": "sticker",
        "animation": "animation",
        "video_note": "video_note",
    }

    url = f"https://api.telegram.org/bot{TOKEN}/{methods[media_type]}"

    payload = {
        "chat_id": chat_id,
        keys[media_type]: file_id
    }

    # ⚠️ فقط اگر اجازه داشت caption بفرست
    if caption and media_type not in ["sticker", "video_note"]:
        payload["caption"] = caption

    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)

    r = requests.post(url, data=payload)
    print(media_type, r.text)

# ================= BUTTONS =================

def buttons(code, chat_id):
    return {
        "inline_keyboard": [[
            {"text": "💬 ریپلای", "callback_data": f"reply|{code}"},
            {"text": "🚫 بلاک", "callback_data": f"block|{chat_id}"},
            {"text": "✅ آنبلاک", "callback_data": f"unblock|{chat_id}"}
        ]]
    }

# ================= WEBHOOK =================

@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.get_json()
    if not data:
        return "ok"

    # ========== CALLBACK ==========
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

    # 🔥 ریپلای مستقیم (TEXT + MEDIA)
    if msg.get("reply_to_message"):

        replied_id = msg["reply_to_message"]["message_id"]
        mp = load_map()

        if str(replied_id) in mp:
            target = mp[str(replied_id)]["chat_id"]

            # ===== TEXT =====
            if msg.get("text"):
                send_message(target, f"☀️ پاسخ:\n\n{text}")

            # ===== PHOTO =====
            elif msg.get("photo"):
                file_id = msg["photo"][-1]["file_id"]
                send_media(target, file_id, "photo")

            # ===== VIDEO =====
            elif msg.get("video"):
                send_media(target, msg["video"]["file_id"], "video")

            # ===== VOICE =====
            elif msg.get("voice"):
                send_media(target, msg["voice"]["file_id"], "voice")

            # ===== AUDIO =====
            elif msg.get("audio"):
                send_media(target, msg["audio"]["file_id"], "audio")

            # ===== DOCUMENT =====
            elif msg.get("document"):
                send_media(target, msg["document"]["file_id"], "document")

            # ===== STICKER =====
            elif msg.get("sticker"):
                send_media(target, msg["sticker"]["file_id"], "sticker")

            # ===== GIF =====
            elif msg.get("animation"):
                send_media(target, msg["animation"]["file_id"], "animation")

            # ===== VIDEO NOTE =====
            elif msg.get("video_note"):
                send_media(target, msg["video_note"]["file_id"], "video_note")

            send_message(ADMIN_ID, "🌊 ارسال شد")

        else:
            send_message(ADMIN_ID, "❌ این پیام قابل ریپلای نیست")

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

        resp = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={
                "chat_id": ADMIN_ID,
                "text": header + "\n\n" + text,
                "reply_markup": json.dumps(buttons(code, chat_id))
            }
        )

        msg_id = resp.json()["result"]["message_id"]

        mp = load_map()
        mp[str(msg_id)] = {
            "chat_id": chat_id,
            "code": code
        }
        save_map(mp)

        send_message(chat_id, "ارسال شد 🌊")
        return "ok"

    # ========= PHOTO =========
    elif msg.get("photo"):
        file_id = msg["photo"][-1]["file_id"]

        send_media(ADMIN_ID, file_id, "photo", caption=header, reply_markup=buttons(code, chat_id))
        send_message(chat_id, "ارسال شد 🌊")
        return "ok"

    # ========= VIDEO =========
    elif msg.get("video"):
        send_media(ADMIN_ID, msg["video"]["file_id"], "video", caption=header, reply_markup=buttons(code, chat_id))
        send_message(chat_id, "ارسال شد 🌊")
        return "ok"

    # ========= VOICE =========
    elif msg.get("voice"):
        send_media(ADMIN_ID, msg["voice"]["file_id"], "voice", caption=header, reply_markup=buttons(code, chat_id))
        send_message(chat_id, "ارسال شد 🌊")
        return "ok"

    # ========= AUDIO =========
    elif msg.get("audio"):
        send_media(ADMIN_ID, msg["audio"]["file_id"], "audio", caption=header, reply_markup=buttons(code, chat_id))
        send_message(chat_id, "ارسال شد 🌊")
        return "ok"

    # ========= STICKER =========
    elif msg.get("sticker"):
        send_media(ADMIN_ID, msg["sticker"]["file_id"], "sticker")
        send_message(chat_id, "ارسال شد 🌊")
        return "ok"

    # ========= ANIMATION =========
    elif msg.get("animation"):
        send_media(ADMIN_ID, msg["animation"]["file_id"], "animation", caption=header, reply_markup=buttons(code, chat_id))
        send_message(chat_id, "ارسال شد 🌊")
        return "ok"

    # ========= VIDEO NOTE =========
    elif msg.get("video_note"):
        send_media(ADMIN_ID, msg["video_note"]["file_id"], "video_note")
        send_message(chat_id, "ارسال شد 🌊")
        return "ok"

    # ========= DOCUMENT =========
    elif msg.get("document"):
        send_media(ADMIN_ID, msg["document"]["file_id"], "document", caption=header, reply_markup=buttons(code, chat_id))
        send_message(chat_id, "ارسال شد 🌊")
        return "ok"


# ================= START =================

if __name__ == "__main__":
    requests.post(f"https://api.telegram.org/bot{TOKEN}/setWebhook", data={"url": URL})
    app.run(host="0.0.0.0", port=10000)
