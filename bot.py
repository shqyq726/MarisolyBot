from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, filters, ContextTypes
import os

TOKEN = "8681244479:AAHqAg2hYNu8HHHJ5NgWbcqrZQmDY77a2KI"
ADMIN_ID = 777430200
URL = "https://marisolybot.onrender.com"

app = Flask(__name__)
bot = Bot(token=TOKEN)

# Dispatcher
dispatcher = Dispatcher(bot=bot, update_queue=None)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌊 خوش اومدی! پیام ناشناس بفرست")

# پیام ناشناس
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    await bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📩 پیام ناشناس:\n\n{user_text}"
    )

    await update.message.reply_text("✅ ارسال شد!")

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Webhook route
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

@app.route("/")
def home():
    return "Bot is running"

# set webhook
@app.route("/setwebhook")
def set_webhook():
    bot.set_webhook(url=f"{URL}/{TOKEN}")
    return "Webhook set!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
