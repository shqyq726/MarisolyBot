from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8681244479:AAHyVMfS1RI85KNIHY7jY1q4gc_L725tkLA"
ADMIN_ID = 777430200

# شروع بات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌊 خوش اومدی به Marisol\n"
        "هرچی می‌خوای ناشناس بفرست ✨"
    )

# گرفتن پیام ناشناس
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.text

    # ارسال به ادمین
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📩 پیام جدید ناشناس:\n\n{user}"
    )

    # جواب به کاربر
    await update.message.reply_text("🌊 ارسال شد!")

# اجرای بات
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == "__main__":
    print("Bot is running...")
    app.run_polling()
