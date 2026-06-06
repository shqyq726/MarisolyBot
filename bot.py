from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import asyncio
import os
import requests

# ---------- ENV ----------
TOKEN = os.environ.get("TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))
URL = os.environ.get("URL")

# ---------- Flask ----------
app = Flask(__name__)

# ---------- Telegram App ----------
application = Application.builder().token(TOKEN).build()


# ---------- Handlers ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌊 خوش اومدی به Marisol")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # ارسال به ادمین
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📩 پیام جدید:\n{text}"
    )

    # جواب به کاربر
    await update.message.reply_text("ارسال شد 🌊")


# ثبت هندلرها
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


# ---------- Flask routes ----------
@app.route("/")
def home():
    return "Bot is running!"


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)

    update = Update.de_json(data, application.bot)

    # اجرای async بدون crash
    asyncio.create_task(application.process_update(update))

    return "ok"


# ---------- Set webhook ----------
def set_webhook():
    requests.get(
        f"https://api.telegram.org/bot{TOKEN}/setWebhook",
        params={"url": URL}
    )


# ---------- Run ----------
if __name__ == "__main__":
    set_webhook()
    app.run(host="0.0.0.0", port=10000)
