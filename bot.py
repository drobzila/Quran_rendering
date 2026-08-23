from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os
import requests

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")


def notify_exported(
    surah_name: str,
    surah: int,
    ayah: int,
    text: str,
    duration: float,
    output_path: str,
):
    """Send a non-blocking-in-spirit notification about an exported video.

    This function is intentionally best-effort: Telegram failure must never
    make the Quran rendering job fail.
    """
    if not BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("ℹ️ Telegram notification skipped: BOT_TOKEN/TELEGRAM_CHAT_ID not set.")
        return False

    message = (
        "🎬 تم تصدير فيديو جديد بنجاح!\n\n"
        f"🕌 السورة: {surah_name} ({surah})\n"
        f"🔢 الآية: {ayah}\n"
        f"⏱ مدة التلاوة: {duration:.2f} ثانية\n\n"
        f"﴿ {text.strip()} ﴾\n\n"
        f"📁 الملف: {os.path.basename(output_path)}\n\n"
        "ℹ️ هذا إشعار فقط؛ لا يحتاج الفيديو إلى أي موافقة من Telegram."
    )

    response = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
        },
        timeout=15,
    )
    response.raise_for_status()
    print("📨 تم إرسال إشعار Telegram بنجاح.")
    return True


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 البوت يعمل بنجاح.\n\n"
        "سيتم إرسال إشعار لك تلقائيًا عند تصدير فيديو جديد."
    )


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Pong")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start\n"
        "/ping\n"
        "/help\n\n"
        "📨 Telegram هنا للإشعارات فقط، ولا يوقف عملية الرندر."
    )


def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN غير مضبوط")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("help", help_command))

    print("Bot started...")
    app.run_polling()


if __name__ == "__main__":
    main()
