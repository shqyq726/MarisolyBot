from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio

TOKEN = "8681244479:AAFBkhHZRG32Te0mY_7yIA_ZBVU6V6Ldl7Q"
ADMIN_ID = 777430200
URL = "https://marisolybot.onrender.com/webhook"

app = Flask(__name__)

# ساخت اپ تلگرام
application = Application.builder().token(TOKEN).build()


# -------- handlers --------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌊 خوش اومدی به Marisol")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))


# -------- Flask webhook --------

@app.route("/")
def home():
    return "Bot is running!"


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)

    update = Update.de_json(data, application.bot)

    # اجرای async داخل Flask
    asyncio.create_task(application.process_update(update))

    return "ok"


# -------- set webhook --------

def set_webhook():
    import requests
    requests.get(
        f"https://api.telegram.org/bot{TOKEN}/setWebhook",
        params={"url": URL}
    )


if __name__ == "__main__":
    set_webhook()
    app.run(host="0.0.0.0", port=10000)
