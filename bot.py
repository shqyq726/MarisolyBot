from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "8681244479:AAHqAg2hYNu8HHHJ5NgWbcqrZQmDY77a2KI"
ADMIN_ID = 777430200

app_flask = Flask(__name__)

# ساخت اپ تلگرام
bot_app = Application.builder().token(TOKEN).build()


# -------- START --------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌊 خوش اومدی به Marisol\n"
        "هرچی می‌خوای ناشناس بفرست ✨"
    )


# -------- MESSAGE --------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # ارسال به ادمین
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📩 پیام جدید ناشناس:\n\n{text}"
    )

    await update.message.reply_text("🌊 ارسال شد!")


# هندلرها
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


# -------- WEBHOOK ROUTE --------
@app_flask.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    bot_app.update_queue.put(update)
    return "ok"


# -------- HOME --------
@app_flask.route("/", methods=["GET"])
def home():
    return "Bot is running!"


# -------- START BOT + SET WEBHOOK --------
import asyncio

async def on_start():
    await bot_app.initialize()
    await bot_app.bot.set_webhook("https://marisolybot.onrender.com/webhook")


asyncio.get_event_loop().run_until_complete(on_start())


# -------- RUN --------
if __name__ == "__main__":
    app_flask.run(host="0.0.0.0", port=10000)
