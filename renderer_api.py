from __future__ import annotations

import os
import threading
import traceback
import uuid
from pathlib import Path

from flask import Flask, jsonify, request, send_file

import Quran

app = Flask(__name__)

API_KEY = os.getenv("RENDERER_API_KEY", "").strip()
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "renderer_output"
OUTPUT_DIR.mkdir(exist_ok=True)

jobs: dict[str, dict] = {}
lock = threading.Lock()
render_lock = threading.Lock()


def authorized():
    if not API_KEY:
        return False
    return request.headers.get("X-Renderer-Key", "") == API_KEY


def run_render(job_id: str):
    output_path = OUTPUT_DIR / f"{job_id}.mp4"
    with lock:
        jobs[job_id] = {"status": "rendering", "error": None}

    try:
        # Quran.py uses shared working files, so only one render is allowed.
        with render_lock:
            Quran.render_one(str(output_path))

        title = ""
        title_file = BASE_DIR / "title.txt"
        if title_file.exists():
            title = title_file.read_text(encoding="utf-8").strip()

        if not output_path.exists() or output_path.stat().st_size == 0:
            raise RuntimeError("لم يتم إنشاء ملف الفيديو")

        with lock:
            jobs[job_id] = {
                "status": "completed",
                "error": None,
                "title": title,
                "file": str(output_path),
                "size": output_path.stat().st_size,
            }
    except Exception as exc:
        traceback.print_exc()
        with lock:
            jobs[job_id] = {"status": "failed", "error": str(exc)}


@app.get("/")
def health():
    return "Quran renderer is running"


@app.post("/render")
def start_render():
    if not authorized():
        return jsonify({"error": "unauthorized"}), 401

    job_id = uuid.uuid4().hex
    with lock:
        jobs[job_id] = {"status": "queued", "error": None}

    threading.Thread(target=run_render, args=(job_id,), daemon=True).start()
    return jsonify({"job_id": job_id, "status": "queued"}), 202


@app.get("/render/<job_id>")
def render_status(job_id):
    if not authorized():
        return jsonify({"error": "unauthorized"}), 401

    with lock:
        job = jobs.get(job_id)

    if job is None:
        return jsonify({"error": "job_not_found"}), 404

    result = {"job_id": job_id, **job}
    if job.get("status") == "completed":
        result["download_path"] = f"/render/{job_id}/download"
    return jsonify(result)


@app.get("/render/<job_id>/download")
def download_render(job_id):
    if not authorized():
        return jsonify({"error": "unauthorized"}), 401

    with lock:
        job = jobs.get(job_id)

    if not job or job.get("status") != "completed":
        return jsonify({"error": "video_not_ready"}), 409

    path = Path(job["file"])
    if not path.exists():
        return jsonify({"error": "video_file_missing"}), 404

    return send_file(
        path,
        mimetype="video/mp4",
        as_attachment=True,
        download_name=f"Quran_{job_id}.mp4",
    )


@app.delete("/render/<job_id>")
def cleanup_render(job_id):
    if not authorized():
        return jsonify({"error": "unauthorized"}), 401

    with lock:
        job = jobs.pop(job_id, None)

    if not job:
        return jsonify({"error": "job_not_found"}), 404

    file_path = job.get("file")
    if file_path:
        try:
            Path(file_path).unlink(missing_ok=True)
        except OSError as exc:
            return jsonify({"error": "cleanup_failed", "details": str(exc)}), 500

    return jsonify({"status": "deleted", "job_id": job_id})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "10000")))
