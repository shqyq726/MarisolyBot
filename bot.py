from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import asyncio

TOKEN = "8681244479:AAHqAg2hYNu8HHHJ5NgWbcqrZQmDY77a2KI"
ADMIN_ID = 777430200
BASE_URL = "https://marisolybot.onrender.com"

app = Flask(__name__)

bot = Bot(token=TOKEN)
application = Application.builder().token(TOKEN).build()

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌊 خوش اومدی!")

# پیام ناشناس
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    await bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📩 پیام:\n{text}"
    )

    await update.message.reply_text("✅ ارسال شد")

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# webhook
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    asyncio.run(application.process_update(update))
    return "ok"

@app.route("/")
def home():
    return "Bot is running"

# set webhook
@app.route("/setwebhook")
def setwebhook():
    bot.set_webhook(f"{BASE_URL}/webhook")
    return "Webhook set!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
