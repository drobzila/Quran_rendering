"""
📤 رفع كل الفيديوهات من مجلد محلي إلى مجلد على Google Drive، باستخدام Service Account.

الإعداد المطلوب (مرة واحدة فقط):
1) أنشئ مشروع على Google Cloud Console وفعّل "Google Drive API".
2) أنشئ Service Account، ثم أنشئ له مفتاح JSON (Key) وحمّله.
3) على Google Drive، أنشئ مجلداً مخصصاً للفيديوهات وشاركه (Share) مع
   بريد الـ Service Account (ينتهي بـ @...gserviceaccount.com) بصلاحية "Editor".
4) خذ "Folder ID" من رابط المجلد (الجزء الأخير من الرابط بعد /folders/).
5) في إعدادات مستودع GitHub، أضف Secrets التالية:
   - GDRIVE_SA_KEY        -> محتوى ملف JSON كاملاً (انسخه كنص كما هو)
   - GDRIVE_FOLDER_ID     -> الـ Folder ID من الخطوة 4

الاستخدام محلياً:
    python upload_drive.py --folder batch_output --drive-folder-id XXXXXXXX \
        --key-file gdrive_service_account.json
"""

from __future__ import annotations

import argparse
import glob
import logging
import os
import sys

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def get_drive_service(key_file: str):
    creds = service_account.Credentials.from_service_account_file(key_file, scopes=SCOPES)
    return build("drive", "v3", credentials=creds)


def upload_file(service, file_path: str, folder_id: str) -> dict:
    file_metadata = {
        "name": os.path.basename(file_path),
        "parents": [folder_id],
    }
    media = MediaFileUpload(file_path, resumable=True)
    uploaded = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id, name, webViewLink")
        .execute()
    )
    logger.info(f"✅ تم رفع {file_path} -> {uploaded.get('webViewLink')}")
    return uploaded


def upload_folder(folder_path: str, drive_folder_id: str, key_file: str) -> int:
    if not os.path.exists(key_file):
        logger.error(f"❌ ملف مفتاح الحساب الخدمي غير موجود: {key_file}")
        return 0

    service = get_drive_service(key_file)

    videos = sorted(glob.glob(os.path.join(folder_path, "*.mp4")))
    if not videos:
        logger.warning(f"⚠️ لا توجد فيديوهات (.mp4) في المجلد: {folder_path}")
        return 0

    logger.info(f"📤 سيتم رفع {len(videos)} فيديو إلى Google Drive...")

    uploaded_count = 0
    for v in videos:
        try:
            upload_file(service, v, drive_folder_id)
            uploaded_count += 1
        except Exception as e:
            logger.error(f"❌ فشل رفع {v}: {e}")

    logger.info(f"🎉 تم رفع {uploaded_count} من أصل {len(videos)} فيديو بنجاح")
    return uploaded_count


def main() -> None:
    parser = argparse.ArgumentParser(description="رفع مجلد فيديوهات إلى Google Drive")
    parser.add_argument("--folder", default="batch_output", help="المجلد المحلي الذي يحتوي الفيديوهات")
    parser.add_argument("--drive-folder-id", required=True, help="معرّف مجلد Google Drive الهدف")
    parser.add_argument("--key-file", default="gdrive_service_account.json", help="مسار ملف مفتاح Service Account")
    args = parser.parse_args()

    uploaded = upload_folder(args.folder, args.drive_folder_id, args.key_file)
    if uploaded == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
