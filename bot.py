from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)
import asyncio
import base64
import json
import os
import time

BOT_TOKEN = os.environ["BOT_TOKEN"]
TELEGRAM_CHAT_ID = int(os.environ["TELEGRAM_CHAT_ID"])
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY", "drobzila/Quran_rendering")
GITHUB_BRANCH = os.environ.get("GITHUB_BRANCH", "main")
APPROVAL_FILE = "pending_approval.json"
RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_REPOSITORY}/{GITHUB_BRANCH}/{APPROVAL_FILE}"
API_URL = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/contents/{APPROVAL_FILE}"

sent_requests = set()


def github_headers():
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2026-03-10",
    }


def load_pending():
    import requests

    try:
        response = requests.get(
            RAW_URL,
            params={"t": int(time.time())},
            timeout=10,
        )
        if response.status_code != 200:
            return None
        return response.json()
    except Exception:
        return None


def update_pending(data):
    import requests

    get_response = requests.get(API_URL, headers=github_headers(), timeout=10)
    get_response.raise_for_status()
    sha = get_response.json()["sha"]

    encoded = base64.b64encode(
        json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    ).decode("ascii")

    response = requests.put(
        API_URL,
        headers=github_headers(),
        json={
            "message": f"telegram approval: {data.get('status', 'update')}",
            "content": encoded,
            "sha": sha,
            "branch": GITHUB_BRANCH,
        },
        timeout=15,
    )
    response.raise_for_status()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 البوت يعمل بنجاح.")


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Pong")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start\n"
        "/ping\n"
        "/help\n\n"
        "سيصلك اقتراح الآية هنا للموافقة عليه."
    )


async def handle_approval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.message.chat_id != TELEGRAM_CHAT_ID:
        await query.answer("غير مصرح لك باستخدام هذه الأزرار.", show_alert=True)
        return

    data = query.data or ""
    if ":" not in data:
        return

    action, request_id = data.split(":", 1)
    if action not in {"approve", "reject"}:
        return

    pending = await asyncio.to_thread(load_pending)
    if not pending or pending.get("request_id") != request_id:
        await query.edit_message_text("⚠️ هذا الاقتراح لم يعد متاحًا.")
        return

    if pending.get("status") != "pending":
        await query.edit_message_text("ℹ️ تمت معالجة هذا الاقتراح مسبقًا.")
        return

    pending["status"] = "approved" if action == "approve" else "rejected"
    pending["approved_by"] = query.from_user.id
    pending["approved_at"] = int(time.time())

    try:
        await asyncio.to_thread(update_pending, pending)
    except Exception as exc:
        await query.edit_message_text(f"❌ تعذر حفظ القرار: {exc}")
        return

    if action == "approve":
        await query.edit_message_text(
            "✅ تمت الموافقة على الآية.\n🎬 سيبدأ إنشاء الفيديو الآن."
        )
    else:
        await query.edit_message_text(
            "🔄 تم رفض الآية.\nسيبحث النظام عن آية أخرى في التشغيل الحالي."
        )


async def poll_approvals(application: Application):
    while True:
        pending = await asyncio.to_thread(load_pending)

        if pending and pending.get("status") == "pending":
            request_id = pending.get("request_id")

            if request_id and request_id not in sent_requests:
                surah_name = pending.get("surah_name", "غير معروف")
                surah = pending.get("surah")
                ayah = pending.get("ayah")
                text = pending.get("text", "").strip()
                duration = pending.get("duration", 0)

                message = (
                    "📖 اقتراح آية جديدة\n\n"
                    f"🕌 السورة: {surah_name}"
                    f" ({surah})\n"
                    f"🔢 الآية: {ayah}\n\n"
                    f"﴿ {text} ﴾\n\n"
                    f"⏱ مدة التلاوة: {duration:.2f} ثانية\n\n"
                    "هل تعتمد هذه الآية للفيديو؟"
                )

                keyboard = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            "✅ اعتماد",
                            callback_data=f"approve:{request_id}",
                        ),
                        InlineKeyboardButton(
                            "🔄 آية أخرى",
                            callback_data=f"reject:{request_id}",
                        ),
                    ]
                ])

                try:
                    await application.bot.send_message(
                        chat_id=TELEGRAM_CHAT_ID,
                        text=message,
                        reply_markup=keyboard,
                    )
                    sent_requests.add(request_id)
                except Exception as exc:
                    print(f"Telegram send error: {exc}")

        await asyncio.sleep(3)


async def post_init(application: Application):
    application.create_task(poll_approvals(application))


def main():
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(handle_approval, pattern=r"^(approve|reject):"))

    print("Bot started...")
    app.run_polling()


if __name__ == "__main__":
    main()
