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
    title: str = "",
):
    """Send a best-effort notification when a Quran video is exported."""
    if not BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("ℹ️ Telegram notification skipped: BOT_TOKEN/TELEGRAM_CHAT_ID not set.")
        return False

    message = (
        "🌿 نسمات القرآن\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "✨ بفضل الله، تم تجهيز تلاوة قرآنية جديدة!\n\n"
        f"📖 السورة: {surah_name}\n"
        f"🔢 الآية: {ayah}\n"
        f"⏱ مدة التلاوة: {duration:.1f} ثانية\n\n"
        + (f"🎬 عنوان الفيديو:\n{title}\n\n" if title else "")
        + f"﴿ {text.strip()} ﴾\n\n"
        f"📂 الملف: {os.path.basename(output_path)}\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🤍 اللهم اجعل القرآن نوراً لقلوبنا.\n"
        "🔔 نسمات القرآن | ذكرٌ وطمأنينة"
    )

    response = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id": TELEGRAM_CHAT_ID, "text": message},
        timeout=15,
    )
    response.raise_for_status()
    print("📨 تم إرسال إشعار Telegram بنجاح.")
    return True


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌿 أهلاً بك في نسمات القرآن\n\n"
        "🤍 نسعى لنشر آيات القرآن الكريم لتكون ذكرى وطمأنينة.\n"
        "سيصلك إشعار عند تجهيز فيديو جديد."
    )


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 البوت متصل ويعمل.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start — التعريف بالبوت\n"
        "/ping — اختبار الاتصال\n"
        "/help — المساعدة\n\n"
        "📨 البوت مخصص لإشعارات مشروع نسمات القرآن."
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
