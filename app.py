from flask import Flask, request, jsonify, send_file, make_response
from flask_cors import CORS
import yt_dlp
import os
import uuid
import re

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


# ================= ROOT =================
@app.route("/")
def home():
    return "YouTube PRO Backend Running"


# ================= HANDLE PREFLIGHT =================
@app.route("/<path:path>", methods=["OPTIONS"])
def options_handler(path):
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
    return response


# ================= VIDEO INFO =================
@app.route("/info", methods=["POST"])
def info():
    data = request.get_json()
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
            "duration": info.get("duration")
        })

    except Exception as e:
        return jsonify({"error": "Video fetch failed"}), 500


# ================= BEST VIDEO =================
@app.route("/best", methods=["POST"])
def best():
    data = request.get_json()
    url = data.get("url")

    filename = re.sub(r"[^\w\-_. ]", "_", str(uuid.uuid4())) + ".mp4"
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)

    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "outtmpl": filepath,
        "quiet": True,
        "noplaylist": True,
        "nocheckcertificate": True
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

    filename = re.sub(r"[^\w\-_. ]", "_", str(uuid.uuid4())) + ".mp3"
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

    except Exception as e:
        return jsonify({"error": "Audio extraction failed"}), 500


if __name__ == "__main__":
    app.run()
