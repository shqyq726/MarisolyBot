from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "81244479:AAHqAg2hYNu8HHHJ5NgWbcqrZQmDY77a2KI"
ADMIN_ID = 777430200

app = Flask(__name__)

# ساخت اپ تلگرام
bot = Application.builder().token(TOKEN).build()


# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌊 خوش اومدی به Marisol\nهرچی می‌خوای ناشناس بفرست ✨"
    )


# ---------------- MESSAGE ----------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📩 پیام ناشناس:\n\n{text}"
    )

    await update.message.reply_text("🌊 ارسال شد!")


bot.add_handler(CommandHandler("start", start))
bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


# ---------------- WEBHOOK ----------------
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot.bot)
    bot.update_queue.put(update)
    return "ok"


@app.route("/")
def home():
    return "Bot is running!"


# ---------------- SET WEBHOOK (SAFE WAY) ----------------
def set_webhook():
    import requests
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
    requests.get(url, params={"url": "https://marisolybot.onrender.com/webhook"})


set_webhook()


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
