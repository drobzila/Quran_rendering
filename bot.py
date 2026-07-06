from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)
import os

BOT_TOKEN = os.environ["BOT_TOKEN"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 البوت يعمل بنجاح."
    )


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Pong")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start\n"
        "/ping\n"
        "/help"
    )


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("help", help_command))

    print("Bot started...")

    app.run_polling()


if __name__ == "__main__":
    main()
