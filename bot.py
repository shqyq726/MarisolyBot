from flask import Flask, request
from telegram import Bot, Update

TOKEN = "8681244479:AAHqAg2hYNu8HHHJ5NgWbcqrZQmDY77a2KI"
ADMIN_ID = 777430200
URL = "https://marisolybot.onrender.com/webhook"

app = Flask(__name__)
bot = Bot(token=TOKEN)


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
            bot.send_message(chat_id=chat_id, text="🌊 خوش اومدی به Marisol")

        else:
            bot.send_message(chat_id=ADMIN_ID, text=f"📩 پیام:\n{text}")
            bot.send_message(chat_id=chat_id, text="ارسال شد 🌊")

    return "ok"


def set_webhook():
    bot.set_webhook(URL)


if __name__ == "__main__":
    set_webhook()
    app.run(host="0.0.0.0", port=10000)
