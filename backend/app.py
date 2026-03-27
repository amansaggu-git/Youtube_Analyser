import os
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
from google import genai

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

SYSTEM_INSTRUCTION = """
You are a sharp financial analyst and investment educator. The user will paste transcripts from YouTube videos — mostly personal finance, investing, wealth-building, and retirement stories.

Your job is to extract maximum value from the transcript and present it in this EXACT format below. Follow the format strictly — use proper markdown with blank lines between sections.

---

## 🎯 What This Video Is About

One crisp paragraph — who is this person, what did they do, what is the video claiming.

---

## 💡 Core Concept / Strategy

Explain the main financial concept or strategy in simple terms. If it has a name (e.g. index investing, FIRE, dividend investing), explain what it means.

---

## 📖 Their Story / Journey

Summarize their personal story clearly. Include specific numbers if mentioned — age, corpus, salary, years taken, returns etc. If no personal story, write "Not shared in this video."

---

## ✅ Key Lessons

- Each lesson on its own bullet point
- Must be specific and actionable — no vague advice like "be disciplined"
- Minimum 4 lessons, maximum 7
- Start each bullet with a strong verb (Invest, Avoid, Track, Build, etc.)

---

## ⚠️ Risks & Caveats

- Each risk on its own bullet point
- Include risks they mentioned AND obvious ones they missed
- Be honest, not diplomatic

---

## 🧠 Aman's Takeaway

Write 3 sharp lines directly addressing Aman — a self-directed long-term equity investor, Indian and US markets, 5-10 year horizon, moderate-to-high risk appetite. Make it specific to his context, not generic.

---

Rules:
- Always put a blank line after every heading
- Always put a blank line between bullet points
- Never merge sections together
- Be direct, skip filler
- If transcript is low quality, say so clearly at the top
"""


def extract_video_id(url):
    patterns = [
        r"(?:youtube\.com\/watch\?(?:.*&)?v=)([a-zA-Z0-9_-]{11})",
        r"(?:youtu\.be\/)([a-zA-Z0-9_-]{11})",
        r"(?:youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})",
        r"(?:m\.youtube\.com\/watch\?(?:.*&)?v=)([a-zA-Z0-9_-]{11})",
        r"^([a-zA-Z0-9_-]{11})$",
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None


def format_time(seconds):
    s = int(seconds)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    url = data.get("url", "").strip()

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    video_id = extract_video_id(url)
    if not video_id:
        return jsonify({"error": "Could not extract video ID from URL"}), 400

    # Fetch transcript
    try:
        ytt = YouTubeTranscriptApi()
        try:
            fetched = ytt.fetch(video_id, languages=["en"])
        except Exception:
            fetched = ytt.fetch(video_id)

        transcript = fetched.to_raw_data()
        lines = [f"[{format_time(e['start'])}]  {e['text']}" for e in transcript]
        full_text = "\n".join(lines)
    except Exception as e:
        return jsonify({"error": f"Transcript fetch failed: {str(e)}"}), 400

    # Call Gemini
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=f"Here is the YouTube transcript:\n\n{full_text}",
            config={"system_instruction": SYSTEM_INSTRUCTION},
        )
        analysis = response.text
    except Exception as e:
        return jsonify({"error": f"Gemini analysis failed: {str(e)}"}), 500

    return jsonify({
        "video_id": video_id,
        "segment_count": len(transcript),
        "analysis": analysis
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
