from flask import Flask, request
import requests
from telegram import Bot, Update

TOKEN = "8681244479:AAHqAg2hYNu8HHHJ5NgWbcqrZQmDY77a2KI"
ADMIN_ID = 777430200

app = Flask(__name__)
bot = Bot(token=TOKEN)

WEBHOOK_URL = "https://marisolybot.onrender.com/webhook"


# ست کردن webhook
def set_webhook():
    requests.get(
        f"https://api.telegram.org/bot{TOKEN}/setWebhook",
        params={"url": WEBHOOK_URL}
    )


@app.route("/")
def home():
    return "Bot is running!"


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    update = Update.de_json(data, bot)

    message = update.message

    if message and message.text:

        # /start
        if message.text == "/start":
            bot.send_message(
                chat_id=message.chat_id,
                text="🌊 خوش اومدی به Marisol\nهرچی می‌خوای ناشناس بفرست ✨"
            )
            return "ok"

        # پیام ناشناس
        bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📩 پیام ناشناس:\n\n{message.text}"
        )

        bot.send_message(
            chat_id=message.chat_id,
            text="🌊 ارسال شد!"
        )

    return "ok"


if __name__ == "__main__":
    set_webhook()
    app.run(host="0.0.0.0", port=10000)
