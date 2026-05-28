from manim import *
import requests
import os
import random
from mutagen.mp3 import MP3

# =========================
# 🔥 PRELOAD DATA (قبل المشهد)
# =========================

def preload_surah(surah_number, reciter):
    url = f"https://api.alquran.cloud/v1/surah/{surah_number}/{reciter}"
    data = requests.get(url, timeout=20).json()["data"]

    os.makedirs("audio_temp", exist_ok=True)

    for ayah in data["ayahs"]:
        path = f"audio_temp/ayah_{ayah['numberInSurah']}.mp3"

        if not os.path.exists(path):
            r = requests.get(ayah["audio"], stream=True)
            with open(path, "wb") as f:
                for chunk in r.iter_content(1024):
                    if chunk:
                        f.write(chunk)

    return data


# =========================
# 🎬 SCENE
# =========================

class Quran(Scene):
    def construct(self):

        SURAH_NUMBER = 33
        RECITER = "ar.husary"

        # ⚡ تحميل مسبق (مهم جدًا)
        surah_data = preload_surah(SURAH_NUMBER, RECITER)

        surah_name = surah_data["name"]
        ayahs_list = surah_data["ayahs"]

        # =========================
        # 🌿 الخلفية
        # =========================

        bg = Rectangle(
            width=config.frame_width,
            height=config.frame_height,
            stroke_width=0
        ).set_color_by_gradient("#f2fff7", "#ffffff")

        self.add(bg)

        # =========================
        # 🫧 فقاعات محسّنة (أخف)
        # =========================

        bubbles = VGroup()

        for _ in range(40):  # أقل = أسرع
            bubble = Circle(
                radius=random.uniform(0.2, 0.5),
                stroke_width=1,
                stroke_opacity=0.2,
                fill_opacity=random.uniform(0.1, 0.25),
                color="#43a047",
            )

            bubble.move_to([
                random.uniform(-7, 7),
                random.uniform(-4, 4),
                0
            ])

            bubble.vx = random.uniform(-0.2, 0.2)
            bubble.vy = random.uniform(-0.2, 0.2)

            bubbles.add(bubble)

        def move_bubbles(mob, dt):
            for b in mob:
                b.shift([b.vx * dt, b.vy * dt, 0])

                if abs(b.get_x()) > 7:
                    b.vx *= -1
                if abs(b.get_y()) > 4:
                    b.vy *= -1

        bubbles.add_updater(move_bubbles)
        self.add(bubbles)

        # =========================
        # 🪟 الصندوق الزجاجي
        # =========================

        box = RoundedRectangle(
            width=10.5,
            height=3.5,
            corner_radius=0.4,
            fill_opacity=0.75,
            fill_color="#ffffff",
            stroke_color="#2e7d32",
            stroke_opacity=0.4,
            stroke_width=2
        )

        self.play(FadeIn(box, scale=0.9), run_time=1)

        # =========================
        # 📖 عرض الآيات
        # =========================

        for i, ayah in enumerate(ayahs_list):

            text = ayah["text"]
            num = ayah["numberInSurah"]
            audio_path = f"audio_temp/ayah_{num}.mp3"

            # 🎧 مدة الصوت
            duration = MP3(audio_path).info.length

            # 🕌 تحسين البسملة
            if i == 0 and SURAH_NUMBER not in [1, 9]:
                if text.startswith("بِسْمِ ٱللَّهِ"):
                    text = text.replace("بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ", "").strip()
                    if not text:
                        text = "بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ"

            # ✨ النص
            quran_text = MarkupText(
                f'<span foreground="#1b5e20">« {text} »</span>',
                font="Amiri",
                font_size=34
            )

            info = MarkupText(
                f'<span foreground="#555555">📖 سورة {surah_name} - آية {num}</span>',
                font_size=16
            )

            # 📏 ضبط الحجم
            if quran_text.width > box.width - 1:
                quran_text.scale((box.width - 1.2) / quran_text.width)

            quran_text.move_to(box.get_center() + UP * 0.25)
            info.next_to(quran_text, DOWN, buff=0.3)

            # 🎧 تشغيل الصوت
            self.add_sound(audio_path)

            # ✨ دخول ناعم
            self.play(
                FadeIn(quran_text, shift=UP * 0.2),
                FadeIn(info, shift=UP * 0.2),
                run_time=0.8
            )

            # ⏱️ مزامنة أدق
            self.wait(max(0.5, duration - 1.2))

            # خروج ناعم
            if i != len(ayahs_list) - 1:
                self.play(
                    FadeOut(quran_text),
                    FadeOut(info),
                    run_time=0.4
                )

        self.wait(2)
