from flask import Flask, request
from telegram import Bot, Update
import requests

TOKEN = "8681244479:AAFBkhHZRG32Te0mY_7yIA_ZBVU6V6Ldl7Q"
ADMIN_ID = 777430200
URL = "https://your-app.onrender.com/webhook"

app = Flask(__name__)
bot = Bot(token=TOKEN)

def set_webhook():
    requests.get(
        f"https://api.telegram.org/bot{TOKEN}/setWebhook",
        params={"url": URL}
    )

@app.route("/")
def home():
    return "Bot is running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    update = Update.de_json(data, bot)

    if update.message:
        text = update.message.text
        chat_id = update.message.chat.id

        if text == "/start":
            bot.send_message(chat_id=chat_id, text="🌊 خوش اومدی")
        else:
            bot.send_message(chat_id=ADMIN_ID, text=f"📩 {text}")
            bot.send_message(chat_id=chat_id, text="ارسال شد 🌊")

    return "ok"

if __name__ == "__main__":
    set_webhook()
    app.run(host="0.0.0.0", port=10000)
