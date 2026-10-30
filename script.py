from __future__ import annotations

import os

from Quran import QuranScene as Quran, render_one, shorts_output


if __name__ == "__main__":
    render_one(os.environ.get("OUTPUT_FILE", shorts_output))

