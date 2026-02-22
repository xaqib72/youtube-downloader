from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import uuid

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


@app.route("/")
def home():
    return "YouTube Backend Running"


# ================= VIDEO INFO =================
@app.route("/info", methods=["POST"])
def info():
    data = request.get_json()
    url = data.get("url")

    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "noplaylist": True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        return jsonify({
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "duration": info.get("duration")
        })

    except Exception as e:
        return jsonify({"error": "Video fetch failed"}), 500


# ================= BEST VIDEO (HD AUTO MERGE) =================
@app.route("/best", methods=["POST"])
def best():
    data = request.get_json()
    url = data.get("url")

    filename = str(uuid.uuid4()) + ".mp4"
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)

    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "outtmpl": filepath,
        "quiet": True,
        "noplaylist": True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return send_file(filepath, as_attachment=True)

    except Exception as e:
        return jsonify({"error": "Video download failed"}), 500


# ================= MP3 =================
@app.route("/mp3", methods=["POST"])
def mp3():
    data = request.get_json()
    url = data.get("url")

    filename = str(uuid.uuid4()) + ".mp3"
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
        "noplaylist": True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return send_file(filepath, as_attachment=True)

    except Exception as e:
        return jsonify({"error": "MP3 extraction failed"}), 500


if __name__ == "__main__":
    app.run()
