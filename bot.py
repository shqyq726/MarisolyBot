from flask import Flask, request
import requests

TOKEN = "8616514786:AAG5Kffc5xJLvdb_AUA2G4crTrC_dKUCcN8"
ADMIN_ID = 777430200
URL = "https://marisolybot.onrender.com/webhook"

app = Flask(__name__)


def set_webhook():
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
    requests.post(url, data={"url": URL})


def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": text})


@app.route("/")
def home():
    return "Bot is running!"


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if not data:
        return "no data"

    message = data.get("message")

    if not message:
        return "no message"

    text = message.get("text")
    chat_id = message["chat"]["id"]

    if text == "/start":
        send_message(chat_id, "🌊 خوش اومدی به Marisol")
    else:
        send_message(ADMIN_ID, f"📩 پیام:\n{text}")
        send_message(chat_id, "ارسال شد 🌊")

    return "ok"


if __name__ == "__main__":
    set_webhook()
    app.run(host="0.0.0.0", port=10000)
