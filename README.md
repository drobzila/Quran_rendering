# Quran Rendering

مشروع Python/Manim لإنشاء فيديوهات قصيرة للقرآن الكريم بصيغة عمودية 9:16، مع جلب التلاوة الصوتية وإظهار الآيات بتصميم مناسب لـ YouTube Shorts.

## المميزات
- إنشاء فيديوهات 1080×1920.
- استخدام خط Amiri للنص العربي.
- جلب التلاوات من AlQuran Cloud.
- اختيار آيات لم تُستخدم سابقًا عبر `used_ayahs.json`.
- معالجة الصوت باستخدام Mutagen وPydub.
- إخراج الفيديو عبر Manim وFFmpeg.
- دعم التوليد الفردي والدفعي ورفع الملفات.

## المتطلبات
- Python 3.10+
- FFmpeg
- Manim
- المكتبات الموجودة في `requirements.txt`.

## التثبيت
```bash
git clone https://github.com/drobzila/Quran_rendering.git
cd Quran_rendering
pip install -r requirements.txt
```

تأكد من توفر `ffmpeg` و`manim` في PATH.

## التشغيل
```bash
python Quran.py
```

يمكن استخدام أدوات `generate_batch.py` وملفات الرفع الموجودة في المشروع حسب سير العمل المطلوب.

## الملفات الرئيسية
- `Quran.py` — منطق إنشاء مشاهد وفيديوهات القرآن.
- `generate_batch.py` — التوليد الدفعي.
- `quran.json` — بيانات القرآن المستخدمة في التوليد.
- `used_ayahs.json` — الآيات التي تم استخدامها.
- `Amiri-Regular.ttf` — الخط العربي المستخدم.
- `upload.py` — رفع الفيديوهات.
- `upload_drive.py` — التعامل مع Google Drive.
- `requirements.txt` — متطلبات Python.

## ملاحظات
الفيديو النهائي مصمم أساسًا للمحتوى العمودي القصير. تأكد من امتلاك الحقوق/الأذونات اللازمة للتلاوات والمواد المستخدمة عند النشر.

## الترخيص
لم يتم تحديد ترخيص للمشروع بعد.
