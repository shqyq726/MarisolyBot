from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from flask import Flask, request
import asyncio

TOKEN = "8681244479:AAHqAg2hYNu8HHHJ5NgWbcqrZQmDY77a2KI"
ADMIN_ID = 777430200

app = Flask(__name__)

application = Application.builder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌊 خوش اومدی!")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📩 پیام:\n{text}"
    )

    await update.message.reply_text("ارسال شد ✅")

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

# مهم: اینجا باید application خودش update رو handle کنه
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)

    # مهم‌ترین تغییر:
    asyncio.get_event_loop().create_task(application.process_update(update))

    return "ok"

@app.route("/")
def home():
    return "Bot is running"

@app.route("/setwebhook")
def setwebhook():
    application.bot.set_webhook("https://marisolybot.onrender.com/webhook")
    return "Webhook set!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
