# Quran Rendering

مشروع Python وManim لإنشاء فيديوهات قرآنية عمودية (9:16) بدقة 1080×1920، مع تلاوة صوتية وخيارات متعددة للألوان والزخارف.

## المتطلبات
- Python 3.10 أو أحدث
- FFmpeg
- Manim ومتطلبات Cairo/Pango النظامية
- الحزم الموجودة في `requirements.txt`

## التثبيت
```bash
git clone https://github.com/drobzila/Quran_rendering.git
cd Quran_rendering
python -m pip install -r requirements.txt
```

تأكد من توفر `ffmpeg` و`manim` في PATH، ومن تسجيل خط Amiri في النظام.

## التشغيل
إنشاء نسختين بتصميمين وزخرفتين مختلفتين:
```bash
python Quran.py
```
إنشاء فيديو واحد:
```bash
RENDER_TWO=0 OUTPUT_FILE=Quran_Shorts.mp4 python Quran.py
```
إنشاء دفعة:
```bash
BATCH_COUNT=10 OUTPUT_DIR=batch_output python generate_batch.py
```

## بنية محرك الرندر
- `Quran.py`: نقطة تشغيل متوافقة مع الأوامر القديمة.
- `quran_renderer/config.py`: إعدادات الفيديو، الخط، الألوان، والزخارف المتاحة.
- `quran_renderer/data.py`: تحميل بيانات القرآن وحفظ الآيات التي نجح تصديرها.
- `quran_renderer/audio.py`: تنزيل التلاوة وقراءة مدتها.
- `quran_renderer/selection.py`: اختيار آية والتحقق من مدة التلاوة.
- `quran_renderer/visuals.py`: الخلفيات والزخارف والعناصر المرئية.
- `quran_renderer/scene.py`: مشهد Manim وتنسيق النص العربي.
- `quran_renderer/render.py`: تشغيل Manim ودمج الصوت وإخراج MP4.
- `generate_batch.py`: إنشاء مجموعة فيديوهات.
- `renderer_api.py`: واجهة خدمة الرندر.
- `upload.py` و`upload_drive.py`: الرفع إلى YouTube وGoogle Drive.
- `bot.py`: إشعارات Telegram.

## سلامة نص الآية
تتحقق دالة تنسيق النص من أن الكلمات وترتيبها لم يتغيرا. كما لا تُسجل الآية في `used_ayahs.json` إلا بعد نجاح إنشاء ملف الفيديو النهائي، لتجنب استهلاك الآيات عند فشل الرندر.

## تخصيص التصميم
يمكن تعديل `STYLE_PRESETS` و`MOTIF_KEYS` في `quran_renderer/config.py`. الأنماط الحالية: green وmidnight وroyal وocean وsand وslate. والزخارف: rosette وeight_point_star وnested_medallion وdiamond_lattice وflower وarchwork.

## بيانات التشغيل
تبقى ملفات `quran.json` و`used_ayahs.json` والخط `Amiri-Regular.ttf` في المسار الرئيسي في هذه المرحلة حتى لا تنكسر مسارات GitHub Actions وDocker الحالية.

## GitHub Actions
تم الإبقاء على مسارات Workflow الحالية وأوامرها كما هي؛ يستمر تشغيل `python Quran.py` و`python generate_batch.py` من جذر المشروع.

## الترخيص
لم يتم تحديد ترخيص للمشروع بعد.
