import os
import requests
from flask import Flask, request
from telegram import Bot, Update

# ======================
# CONFIG
# ======================

TOKEN = os.getenv("TOKEN")  # از Environment Render
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

BASE_URL = "https://marisolybot.onrender.com"
WEBHOOK_URL = f"{BASE_URL}/webhook"

# ======================
# APP
# ======================

app = Flask(__name__)
bot = Bot(token=TOKEN)


# ======================
# SET WEBHOOK
# ======================

def set_webhook():
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
    requests.get(url, params={"url": WEBHOOK_URL})


# ======================
# ROUTES
# ======================

@app.route("/")
def home():
    return "Bot is running!"


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if not data:
        return "no data", 200

    update = Update.de_json(data, bot)

    if update.message and update.message.text:
        text = update.message.text
        chat_id = update.message.chat.id

        if text == "/start":
            bot.send_message(chat_id=chat_id, text="🌊 خوش اومدی به Marisol")

        else:
            bot.send_message(
                chat_id=ADMIN_ID,
                text=f"📩 پیام جدید:\n{text}"
            )

            bot.send_message(chat_id=chat_id, text="ارسال شد 🌊")

    return "ok", 200


# ======================
# START
# ======================

if __name__ == "__main__":
    set_webhook()
    app.run(host="0.0.0.0", port=10000)
