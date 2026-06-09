from flask import Flask, request
import requests
import json
import os
from supabase import create_client

TOKEN = "8616514786:AAEWF9AdXPmYQuVXihGdmd_-Ir8z6bIeyD8"
ADMIN_ID = 777430200
URL = "https://marisolybot.onrender.com/webhook"

REPLY_MAP_FILE = "reply_map.json"
USERS_FILE = "users.json"

app = Flask(__name__)
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

# ================= DB =================

def get_user(chat_id, first_name="", username=""):

    result = (
        supabase.table("users")
        .select("*")
        .eq("chat_id", str(chat_id))
        .execute()
    )

    if result.data:

        user = result.data[0]

        supabase.table("users").update({
            "first": first_name,
            "username": username
        }).eq("chat_id", str(chat_id)).execute()

        return user

    count = (
        supabase.table("users")
        .select("id")
        .execute()
    )

    code = f"U{len(count.data)+1:03d}"

    user = {
        "chat_id": str(chat_id),
        "code": code,
        "blocked": False,
        "first": first_name,
        "username": username
    }

    supabase.table("users").insert(user).execute()

    send_message(
        int(chat_id),
        "سلام به Marisol خوش اومدی:) 🌊"
    )

    return user


def set_block(chat_id, value):

    supabase.table("users").update({
        "blocked": value
    }).eq(
        "chat_id",
        str(chat_id)
    ).execute()


def load_users():

    result = (
        supabase.table("users")
        .select("*")
        .execute()
    )

    users = {}

    for user in result.data:

        users[str(user["chat_id"])] = {
            "code": user["code"],
            "blocked": user["blocked"],
            "first": user["first"],
            "username": user["username"]
        }

    return users

def load_map():
    if os.path.exists(REPLY_MAP_FILE):
        with open(REPLY_MAP_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_map(data):
    with open(REPLY_MAP_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)

def find_chat_by_code(code):
    users = load_users()
    for chat_id, data in users.items():
        if data["code"] == code:
            return int(chat_id)
    return None

# ================= TELEGRAM =================

def send_message(chat_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}

    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)

    requests.post(url, data=payload)

def send_media(chat_id, file_id, media_type, reply_markup=None):

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

    key = {
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
        key[media_type]: file_id
    }

    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)

    response = requests.post(url, data=payload)

    return response.json()

def answer_callback(callback_id):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery",
        data={
            "callback_query_id": callback_id
        }
    )

# ================= BUTTONS =================

def buttons(code, chat_id):
    return {
        "inline_keyboard": [
            [
                {"text": "ℹ️ INFO", "callback_data": f"info|{chat_id}"}
            ],
            [
                {"text": "🚫 BLOCK", "callback_data": f"block|{chat_id}"},
                {"text": "✅ UNBLOCK", "callback_data": f"unblock|{chat_id}"}
            ],
            [
                {"text": "💬 REPLY", "callback_data": f"reply|{code}"}
            ]
        ]
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

        answer_callback(cq["id"])

        action, value = cq["data"].split("|")

        if action == "block":
            set_block(value, True)
            send_message(ADMIN_ID, "🚫 کاربر بلاک شد")

        elif action == "unblock":
            set_block(value, False)
            send_message(ADMIN_ID, "✅ کاربر آنبلاک شد")

        elif action == "reply":
            send_message(
                ADMIN_ID,
                f"☀️ ریپلای:\n/reply {value} پیام"
            )

        elif action == "info":
            users = load_users()
            user = users.get(str(value))

            if user:

                username = user.get("username") or "-"

                send_message(
                    ADMIN_ID,
                    f"""👤 INFO

📛 NAME: {user.get('first','-')}
📱 USERNAME: @{username}
🆔 CHAT ID: {value}
📌 CODE: {user['code']}
🚫 BLOCKED: {'YES' if user['blocked'] else 'NO'}"""
                )

        return "ok"

    msg = data.get("message")
    if not msg:
        return "ok"

    chat_id = msg["chat"]["id"]
    text = msg.get("text", "")

    first = msg["from"].get("first_name", "")
    username = msg["from"].get("username", "ندارد")

    # ================= ADMIN =================
    if chat_id == ADMIN_ID:

        if msg.get("reply_to_message"):

            replied_id = msg["reply_to_message"]["message_id"]
            mp = load_map()

            if str(replied_id) in mp:
                target = mp[str(replied_id)]["chat_id"]

                if msg.get("text"):
                    send_message(target, f"☀️ پاسخ:\n\n{text}")

                elif msg.get("photo"):
                    send_media(target, msg["photo"][-1]["file_id"], "photo")

                elif msg.get("video"):
                    send_media(target, msg["video"]["file_id"], "video")

                elif msg.get("voice"):
                    send_media(target, msg["voice"]["file_id"], "voice")

                elif msg.get("audio"):
                    send_media(target, msg["audio"]["file_id"], "audio")

                elif msg.get("document"):
                    send_media(target, msg["document"]["file_id"], "document")

                elif msg.get("sticker"):
                    send_media(target, msg["sticker"]["file_id"], "sticker")

                elif msg.get("animation"):
                    send_media(target, msg["animation"]["file_id"], "animation")

                elif msg.get("video_note"):
                    send_media(target, msg["video_note"]["file_id"], "video_note")

                send_message(ADMIN_ID, "🌊 ارسال شد")

            else:
                send_message(ADMIN_ID, "❌ این پیام قابل ریپلای نیست")

            return "ok"
        if text.startswith("/reply"):

            parts = text.split(" ", 2)

            if len(parts) < 3:
                send_message(
                    ADMIN_ID,
                    "❌ فرمت: /reply U001 پیام"
                )
                return "ok"

            code = parts[1].strip()
            reply = parts[2].strip()

            target = find_chat_by_code(code)

            if not target:
                send_message(
                    ADMIN_ID,
                    "❌ کاربر پیدا نشد"
                )
                return "ok"

            send_message(
                target,
                f"☀️ پاسخ:\n\n{reply}"
            )

            send_message(
                ADMIN_ID,
                "🌊 ارسال شد"
            )

            return "ok"
        return "ok"

    # ================= USER =================
    user = get_user(chat_id, first, username)

    if user["blocked"]:
        return "ok"

    # ========= TEXT =========
    if msg.get("text"):

        resp = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={
                "chat_id": ADMIN_ID,
                "text": text,
                "reply_markup": json.dumps(buttons(user["code"], chat_id))
            }
        )

        msg_id = resp.json()["result"]["message_id"]

        mp = load_map()
        mp[str(msg_id)] = {"chat_id": chat_id}
        save_map(mp)

        send_message(chat_id, "ارسال شد 🌊")
        return "ok"

    # ========= PHOTO =========
    elif msg.get("photo"):

        resp = send_media(
            ADMIN_ID,
            msg["photo"][-1]["file_id"],
            "photo",
            reply_markup=buttons(user["code"], chat_id)
        )

        msg_id = resp["result"]["message_id"]

        mp = load_map()
        mp[str(msg_id)] = {"chat_id": chat_id}
        save_map(mp)

    # ========= VIDEO =========
    elif msg.get("video"):

        resp = send_media(
            ADMIN_ID,
            msg["video"]["file_id"],
            "video",
            reply_markup=buttons(user["code"], chat_id)
        )

        msg_id = resp["result"]["message_id"]

        mp = load_map()
        mp[str(msg_id)] = {"chat_id": chat_id}
        save_map(mp)

    # ========= VOICE =========
    elif msg.get("voice"):

        resp = send_media(
            ADMIN_ID,
            msg["voice"]["file_id"],
            "voice",
            reply_markup=buttons(user["code"], chat_id)
        )

        msg_id = resp["result"]["message_id"]

        mp = load_map()
        mp[str(msg_id)] = {"chat_id": chat_id}
        save_map(mp)

    # ========= AUDIO =========
    elif msg.get("audio"):

        resp = send_media(
            ADMIN_ID,
            msg["audio"]["file_id"],
            "audio",
            reply_markup=buttons(user["code"], chat_id)
        )

        msg_id = resp["result"]["message_id"]

        mp = load_map()
        mp[str(msg_id)] = {"chat_id": chat_id}
        save_map(mp)

    # ========= DOCUMENT =========
    elif msg.get("document"):

        resp = send_media(
            ADMIN_ID,
            msg["document"]["file_id"],
            "document",
            reply_markup=buttons(user["code"], chat_id)
        )

        msg_id = resp["result"]["message_id"]

        mp = load_map()
        mp[str(msg_id)] = {"chat_id": chat_id}
        save_map(mp)

    # ========= STICKER =========
    elif msg.get("sticker"):

        resp = send_media(
            ADMIN_ID,
            msg["sticker"]["file_id"],
            "sticker",
            reply_markup=buttons(user["code"], chat_id)
        )

        msg_id = resp["result"]["message_id"]

        mp = load_map()
        mp[str(msg_id)] = {"chat_id": chat_id}
        save_map(mp)

    # ========= ANIMATION =========
    elif msg.get("animation"):

        resp = send_media(
            ADMIN_ID,
            msg["animation"]["file_id"],
            "animation",
            reply_markup=buttons(user["code"], chat_id)
        )

        msg_id = resp["result"]["message_id"]

        mp = load_map()
        mp[str(msg_id)] = {"chat_id": chat_id}
        save_map(mp)

    # ========= VIDEO NOTE =========
    elif msg.get("video_note"):

        resp = send_media(
            ADMIN_ID,
            msg["video_note"]["file_id"],
            "video_note",
            reply_markup=buttons(user["code"], chat_id)
        )

        msg_id = resp["result"]["message_id"]

        mp = load_map()
        mp[str(msg_id)] = {"chat_id": chat_id}
        save_map(mp)

    send_message(chat_id, "ارسال شد 🌊")
    return "ok"

# ================= START =================

if __name__ == "__main__":
    requests.post(f"https://api.telegram.org/bot{TOKEN}/setWebhook", data={"url": URL})
    app.run(host="0.0.0.0", port=10000)
