"""
📦 إنشاء دفعة من فيديوهات القرآن (شورتس) دفعة واحدة في مجلد واحد.

الاستخدام:
    python generate_batch.py                # ينشئ 50 فيديو في مجلد batch_output
    BATCH_COUNT=20 python generate_batch.py # ينشئ 20 فيديو
    OUTPUT_DIR=my_videos python generate_batch.py

كل فيديو يستخدم آية عشوائية مختلفة تلقائياً (بفضل used_ayahs.json الموجود في المشروع)،
ولا يتوقف عند فشل فيديو واحد، بل يكمل الباقي ويطبع تقريراً نهائياً.
"""

from __future__ import annotations

import logging
import os
import sys
import time

import Quran  # يعيد استخدام render_one() من Quran.py

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

BATCH_COUNT = int(os.environ.get("BATCH_COUNT", "50"))
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "batch_output")


def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    succeeded: list[str] = []
    failed = 0

    start = time.time()

    for i in range(1, BATCH_COUNT + 1):
        output_name = f"quran_short_{i:03d}.mp4"
        output_path = os.path.join(OUTPUT_DIR, output_name)

        logger.info(f"🎬 [{i}/{BATCH_COUNT}] بدء إنشاء الفيديو...")

        try:
            Quran.render_one(output_path)
            succeeded.append(output_path)
            logger.info(f"✅ [{i}/{BATCH_COUNT}] تم الحفظ: {output_path}")
        except Exception as e:
            failed += 1
            logger.error(f"❌ [{i}/{BATCH_COUNT}] فشل إنشاء الفيديو: {e}")
            continue

    elapsed = time.time() - start
    logger.info(
        f"🎉 انتهت الدفعة: {len(succeeded)} نجح / {failed} فشل "
        f"من أصل {BATCH_COUNT} — الوقت الإجمالي: {elapsed/60:.1f} دقيقة"
    )

    if not succeeded:
        sys.exit(1)


if __name__ == "__main__":
    main()
