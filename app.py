import os, uuid, subprocess
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

FILES_DIR = os.path.join(os.getcwd(), "files")
os.makedirs(FILES_DIR, exist_ok=True)

def public_base_url():
    proto = request.headers.get("X-Forwarded-Proto", request.scheme)
    host = request.headers.get("X-Forwarded-Host", request.host)
    return f"{proto}://{host}"

@app.get("/")
def home():
    return "✅ YouTube to MP4 API running"

@app.post("/download")
def download_video():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "Missing URL"}), 400

    video_id = str(uuid.uuid4())
    filename = f"{video_id}.mp4"
    output_path = os.path.join(FILES_DIR, filename)

    try:
        subprocess.run([
            "yt-dlp", "-f", "mp4", "-S", "res:1080", "-o", output_path, url
        ], check=True)

        public_url = f"{public_base_url()}/files/{filename}"
        return jsonify({"success": True, "video_url": public_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.get("/files/<path:filename>")
def serve_file(filename):
    return send_from_directory(FILES_DIR, filename)
