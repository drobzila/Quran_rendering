from __future__ import annotations

import argparse
import glob
import logging
import os
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def get_drive_service(credentials_file: str, token_file: str):
    creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    if creds.expired and creds.refresh_token:
        logger.info("🔄 Refreshing access token...")
        creds.refresh(Request())

        with open(token_file, "w") as f:
            f.write(creds.to_json())

    return build("drive", "v3", credentials=creds)


def upload_file(service, file_path: str, folder_id: str):
    metadata = {
        "name": os.path.basename(file_path),
        "parents": [folder_id],
    }

    media = MediaFileUpload(file_path, resumable=True)

    return (
        service.files()
        .create(
            body=metadata,
            media_body=media,
            fields="id,name,webViewLink",
        )
        .execute()
    )


def upload_folder(folder_path, drive_folder_id, credentials_file, token_file):

    if not os.path.exists(credentials_file):
        logger.error("credentials.json غير موجود")
        return 0

    if not os.path.exists(token_file):
        logger.error("token.json غير موجود")
        return 0

    service = get_drive_service(credentials_file, token_file)

    videos = sorted(glob.glob(os.path.join(folder_path, "*.mp4")))

    if not videos:
        logger.warning("لا توجد فيديوهات")
        return 0

    logger.info(f"📤 سيتم رفع {len(videos)} فيديو...")

    uploaded = 0

    for video in videos:
        try:
            result = upload_file(service, video, drive_folder_id)

            logger.info(
                f"✅ {os.path.basename(video)} -> {result['webViewLink']}"
            )

            uploaded += 1

        except Exception as e:
            logger.error(f"❌ {video}: {e}")

    logger.info(f"🎉 تم رفع {uploaded}/{len(videos)}")

    return uploaded


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--folder", default="batch_output")
    parser.add_argument("--drive-folder-id", required=True)
    parser.add_argument("--credentials", default="credentials.json")
    parser.add_argument("--token", default="token.json")

    args = parser.parse_args()

    uploaded = upload_folder(
        args.folder,
        args.drive_folder_id,
        args.credentials,
        args.token,
    )

    if uploaded == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
