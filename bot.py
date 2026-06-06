from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import asyncio

TOKEN = "8681244479:AAHqAg2hYNu8HHHJ5NgWbcqrZQmDY77a2KI"
ADMIN_ID = 777430200

app = Flask(__name__)

# ساخت اپ تلگرام
application = Application.builder().token(TOKEN).build()

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌊 خوش اومدی به بات ناشناس!")

# پیام ناشناس
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # ارسال به ادمین
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📩 پیام ناشناس:\n{text}"
    )

    # جواب به کاربر
    await update.message.reply_text("✅ ارسال شد!")

# اضافه کردن handler ها
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


# 📍 webhook route (تلگرام پیام‌ها رو اینجا می‌فرسته)
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.run(application.process_update(update))
    return "ok"


# تست سرور
@app.route("/")
def home():
    return "Bot is running"


# 🚀 ست کردن webhook (فقط یک بار اجرا کن)
@app.route("/setwebhook")
def setwebhook():
    asyncio.run(
        application.bot.set_webhook(
            url="https://marisolybot.onrender.com/webhook"
        )
    )
    return "Webhook set!"


# اجرای Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
