from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import uuid
import re

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


def format_duration(seconds):
    if not seconds:
        return None
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h:02}:{m:02}:{s:02}"
    return f"{m:02}:{s:02}"


@app.route("/")
def home():
    return "YouTube PRO Backend Running"


# ========= VIDEO INFO =========
@app.route("/info", methods=["POST"])
def info():
    data = request.json
    url = data.get("url")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "noplaylist": True,
        "nocheckcertificate": True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            return jsonify({
                "title": info.get("title"),
                "thumbnail": info.get("thumbnail"),
                "duration": format_duration(info.get("duration"))
            })

    except Exception:
        return jsonify({"error": "Video fetch failed"}), 500


# ========= BEST VIDEO =========
@app.route("/best", methods=["POST"])
def best():
    data = request.json
    url = data.get("url")

    filename = re.sub(r'[^\w\-_. ]', '_', str(uuid.uuid4())) + ".mp4"
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)

    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": filepath,
        "merge_output_format": "mp4",
        "quiet": True,
        "noplaylist": True,
        "nocheckcertificate": True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return send_file(filepath, as_attachment=True)

    except Exception:
        return jsonify({"error": "Video download failed"}), 500


# ========= MP3 =========
@app.route("/mp3", methods=["POST"])
def mp3():
    data = request.json
    url = data.get("url")

    filename = re.sub(r'[^\w\-_. ]', '_', str(uuid.uuid4())) + ".mp3"
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": filepath,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "quiet": True,
        "noplaylist": True,
        "nocheckcertificate": True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return send_file(filepath, as_attachment=True)

    except Exception:
        return jsonify({"error": "Audio extraction failed"}), 500


if __name__ == "__main__":
    app.run()
