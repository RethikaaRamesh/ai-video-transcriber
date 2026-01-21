import os
from flask import Flask, request, render_template
import yt_dlp
import whisper

app = Flask(__name__)

# --- FFmpeg path for Windows ---
FFMPEG_PATH = r"C:\ffmpeg\ffmpeg\bin"
os.environ["PATH"] += os.pathsep + FFMPEG_PATH

# Ensure downloads folder exists
os.makedirs("downloads", exist_ok=True)

# Load Whisper model
print("Loading Whisper model...")
model = whisper.load_model("tiny")  # tiny is fast on CPU
print("Model loaded successfully!")

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    transcript_text = ""
    if request.method == "POST":
        youtube_url = request.form.get("url")
        if youtube_url:
            try:
                # Step 1: Download audio
                ydl_opts = {
                    "format": "bestaudio/best",
                    "outtmpl": "downloads/%(id)s.%(ext)s",
                    "postprocessors": [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }],
                    "ffmpeg_location": os.path.join(FFMPEG_PATH, "ffmpeg.exe")
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(youtube_url, download=True)
                    audio_file = f"downloads/{info['id']}.mp3"

                # Step 2: Transcribe audio
                result = model.transcribe(audio_file)
                raw_text = result['text']

                # Step 3: Split into paragraphs (every 2–3 sentences)
                paragraphs = raw_text.replace(". ", ".\n\n")
                transcript_text = paragraphs.strip()

                message = "✅ Transcription completed successfully!"

            except Exception as e:
                message = f"❌ Error: {e}"

    return render_template("index.html", message=message, transcript=transcript_text)


if __name__ == "__main__":
    app.run(debug=True)
