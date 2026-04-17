import os
import base64
import time
import re
import argparse
import hashlib
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
import json
from typing import Any, Dict, List

# ---------- CONFIG ----------
ROOT_FOLDER = Path("rendered_pages")
OUTPUT_FOLDER = Path("output_html")
CHUNK_SIZE = 5

# ---------- INIT ----------
load_dotenv()
_api_key = os.getenv("GEMINI_API_KEY") or ""
if not _api_key.strip():
    raise RuntimeError("Missing GEMINI_API_KEY. Add it to .env or your environment variables.")

def _mask_key(k: str) -> str:
    k = (k or "").strip()
    if len(k) <= 8:
        return "*" * len(k)
    return f"{k[:3]}...{k[-4:]}"

print(f"[INFO] Using GEMINI_API_KEY={_mask_key(_api_key)}")
genai.configure(api_key=_api_key)

model = genai.GenerativeModel("gemini-2.5-flash")

# ---------- HELPERS ----------

class QuotaExhaustedError(RuntimeError):
    pass

def _is_quota_exhausted(exc: Exception) -> bool:
    msg = str(exc)
    return ("RESOURCE_EXHAUSTED" in msg) or ("Quota exceeded" in msg) or ("generate_content_free_tier_requests" in msg)

def _compute_wait_seconds(exc: Exception, default_seconds: float, attempt_idx: int) -> float:
    """
    Use provider retry hints when present; otherwise exponential backoff.
    attempt_idx is 0-based.
    """
    msg = str(exc)
    match = re.search(r"retry in (\d+\.?\d*)s", msg, flags=re.IGNORECASE)
    if match:
        try:
            return float(match.group(1)) + 2
        except Exception:
            pass
    # exponential backoff with cap
    return min(60.0, default_seconds * (2 ** attempt_idx))

def encode_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def chunk_list(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


def load_images(folder):
    return sorted(folder.glob("*.png"))

def _extract_json_object(text: str) -> dict:
    """
    Best-effort JSON extraction. The model sometimes returns extra text;
    we recover the first top-level JSON object we can parse.
    """
    if not text:
        raise ValueError("Empty model output")

    # Fast path
    try:
        return json.loads(text)
    except Exception:
        pass

    # Strip code fences / markdown
    cleaned = re.sub(r"```(?:json)?", "", text, flags=re.IGNORECASE).replace("```", "").strip()

    # Find a JSON object span
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("Could not locate JSON object in model output")

    candidate = cleaned[start:end + 1]
    return json.loads(candidate)

# 🔥 CLEAN MODEL OUTPUT
def clean_html(output: str) -> str:
    if not output:
        return ""

    # Remove any markdown fences anywhere in output (some models nest them)
    output = re.sub(r"```(?:html|css|javascript|js)?", "", output, flags=re.IGNORECASE)
    output = output.replace("```", "").strip()

    # Keep only LAST HTML doc if multiple exist
    parts = re.split(r"<!DOCTYPE html>", output)
    if len(parts) > 1:
        output = "<!DOCTYPE html>" + parts[-1]

    return output.strip()


# 🔥 SAFE GENERATION (RETRY LOGIC)
def safe_generate_chunk_html(chunk, max_retries=5):
    for attempt in range(max_retries):
        try:
            return generate_chunk_html(chunk)

        except Exception as e:
            if _is_quota_exhausted(e):
                raise QuotaExhaustedError(str(e)) from e

            wait_time = _compute_wait_seconds(e, default_seconds=6.0, attempt_idx=attempt)
            print(f"[WARN] Request failed (attempt {attempt+1}/{max_retries}). {type(e).__name__}: {str(e)[:240]}")
            print(f"[INFO] Waiting {wait_time:.1f}s...")
            time.sleep(wait_time)

    raise Exception("Failed after retries")

def safe_generate_chunk_data(chunk, max_retries=5):
    for attempt in range(max_retries):
        try:
            return generate_chunk_data(chunk)
        except Exception as e:
            if _is_quota_exhausted(e):
                raise QuotaExhaustedError(str(e)) from e

            wait_time = _compute_wait_seconds(e, default_seconds=6.0, attempt_idx=attempt)
            print(f"[WARN] Request failed (attempt {attempt+1}/{max_retries}). {type(e).__name__}: {str(e)[:240]}")
            print(f"[INFO] Waiting {wait_time:.1f}s...")
            time.sleep(wait_time)

    raise Exception("Failed after retries")

def generate_chunk_data(image_paths):
    prompt = """
You are extracting structured lesson content for an educational web app.

The inputs are images of PDF pages. DO NOT recreate the PDF layout.

Return ONLY valid JSON (no markdown, no explanation).

Schema:
{
  "chunk_summary": "1-3 sentence summary of what these pages teach",
  "grade_hint": "if obvious, else empty string",
  "topic_hint": "short topic phrase if obvious, else empty string",
  "concepts": [
    { "title": "string", "bullets": ["string"] }
  ],
  "vocabulary": [
    { "term": "string", "meaning": "string" }
  ],
  "activities": [
    { "type": "matching|sorting|fill_blanks|short_answer|mcq|true_false|other", "prompt": "string", "items": [] }
  ],
  "questions": [
    { "q": "string", "type": "mcq|true_false|short_answer|fill_blank", "options": ["string"], "answer": "string", "explain": "string" }
  ],
  "notes_for_interactions": ["game / interaction ideas grounded in the content"]
}

Rules:
- Keep language age-appropriate and concise.
- Prefer extracting over inventing. If something isn't present, omit it.
- If pages are mostly images with labels, extract the labels and likely intent.
"""

    contents = [prompt]

    for img_path in image_paths:
        contents.append({
            "mime_type": "image/png",
            "data": encode_image(img_path)
        })

    response = model.generate_content(contents)

    return response.text


# 🔥 LEGACY HTML GENERATION (kept for fallback / debugging)
def generate_chunk_html(image_paths):
    prompt = """
You are an expert educational product designer building interactive learning experiences for students.

Your task is NOT to recreate the PDF.

Your task is to transform the lesson content into an engaging, gamified, interactive learning experience.

---

CONTEXT:

These images represent pages from a lesson.

Infer the grade level and difficulty automatically from the content.

---

CORE OBJECTIVE:

Design a FUN, INTERACTIVE, and IMMERSIVE learning experience — not a static page.

This should feel like a mini educational game, not a document.

---

STRICT RULES:

1. DO NOT copy page layout or structure
2. DO NOT recreate textbook formatting
3. DO NOT use heavy inline styles
4. DO NOT invent image paths or external assets
5. DO NOT output markdown (no ```html)
6. DO NOT create multiple HTML documents

---

ADAPTIVE DESIGN (VERY IMPORTANT):

Adapt UI, tone, and interaction based on level:

- Lower grades → playful, colorful, highly interactive, minimal text
- Middle grades → balanced interaction + explanation
- Higher grades → cleaner UI, structured, deeper content

---

YOU MUST INCLUDE:

1. Structured learning flow:
   - Introduction (simple and engaging)
   - Core Concepts (broken into small chunks)
   - Interactive Activities
   - Exercises / Practice
   - Quick Quiz / Assessment

2. Interactivity:
   - clickable elements
   - input fields
   - instant feedback
   - at least one game-like interaction (matching / fill / quiz)

3. Gamification:
   - progress indicator OR feedback system
   - encouraging messages
   - playful responses

4. Motion & UI polish:
   - hover effects
   - smooth transitions
   - animated feedback (CSS or JS)
   - visually engaging but not cluttered

---

UI SYSTEM REQUIREMENTS:

- Use reusable CSS classes (NOT inline styling everywhere)
- Keep layout clean and centered
- Use soft, consistent color palette
- Make it mobile-friendly
- Maintain consistency across sections

---

JAVASCRIPT:

- All JS should be at the bottom
- Keep it simple and reliable
- No external dependencies required

---

OUTPUT FORMAT:

Return ONE complete HTML file:

- Proper <head> with CSS
- Structured <body> with sections
- Clean, readable code
- All JS included at the bottom

---

IMPORTANT:

Focus on:
- clarity
- engagement
- interactivity
- consistency

Avoid:
- over-design
- unnecessary complexity
- copying textbook layout
"""

    contents = [prompt]

    for img_path in image_paths:
        img_base64 = encode_image(img_path)
        contents.append({
            "mime_type": "image/png",
            "data": img_base64
        })

    response = model.generate_content(contents)

    return response.text

# 🔥 EXTRACT BODY CONTENT (CRITICAL FIX)
def extract_body(html):
    match = re.search(r"<body.*?>(.*)</body>", html, re.DOTALL)
    return match.group(1) if match else html


# 🔥 BUILD FINAL SINGLE HTML
def build_final_html(chunks_html):
    body_content = "\n".join([extract_body(h) for h in chunks_html])

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Lesson</title>
<style>
body {{
  font-family: Arial;
  padding: 20px;
  max-width: 900px;
  margin: auto;
}}
</style>
</head>
<body>

{body_content}

</body>
</html>
"""

def _pick_theme_from_topic(topic: str) -> dict:
    t = (topic or "").lower()
    if any(k in t for k in ["space", "planet", "solar", "universe", "moon"]):
        return {"primary": "#2B4C7E", "primary_dark": "#1E3558", "accent": "#FFB703", "bg1": "#0B1020", "bg2": "#101B3A"}
    if any(k in t for k in ["computer", "technology", "digital", "keyboard"]):
        return {"primary": "#1F6A75", "primary_dark": "#155158", "accent": "#F49040", "bg1": "#ede9fe", "bg2": "#d1fae5"}
    if any(k in t for k in ["plant", "animal", "science", "matter", "water", "air"]):
        return {"primary": "#166534", "primary_dark": "#14532d", "accent": "#22c55e", "bg1": "#ecfccb", "bg2": "#dcfce7"}
    return {"primary": "#334155", "primary_dark": "#1f2937", "accent": "#f59e0b", "bg1": "#eef2ff", "bg2": "#ecfeff"}

def render_lesson_html(lesson: dict) -> str:
    title = (lesson.get("title") or "Interactive Lesson").strip()
    subtitle = (lesson.get("subtitle") or "").strip()
    topic = (lesson.get("topic") or "").strip()
    grade = (lesson.get("grade") or "").strip()
    theme = lesson.get("theme") or _pick_theme_from_topic(topic or title)
    sections = lesson.get("sections") or []
    quiz = lesson.get("quiz") or {}
    three_spec = lesson.get("three_spec") or {}

    safe_title = html_escape(title)
    safe_subtitle = html_escape(subtitle)

    payload = json.dumps(
        {"title": title, "subtitle": subtitle, "topic": topic, "grade": grade, "sections": sections, "quiz": quiz, "three_spec": three_spec},
        ensure_ascii=False,
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>{safe_title}</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{
      --primary: {theme["primary"]};
      --primary-dark: {theme["primary_dark"]};
      --accent: {theme["accent"]};
      --glass-bg: rgba(255,255,255,0.90);
      --white: #fff;
      --text: #0f172a;
      --muted: rgba(15,23,42,0.72);
      --shadow: 0 10px 30px rgba(0,0,0,0.12);
      --radius: 16px;
      --tap: 44px;
    }}
    html {{ scroll-behavior: smooth; }}
    body {{
      font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
      min-height: 100vh;
      padding: 16px;
      color: var(--text);
      background: linear-gradient(135deg, {theme["bg1"]} 0%, {theme["bg2"]} 100%);
      line-height: 1.55;
    }}
    /* full-bleed background, but a wide centered content rail like the reference */
    .wrap {{
      width: min(1280px, 100%);
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}
    .sticky {{ position: sticky; top: 10px; z-index: 50; }}
    .header {{
      background: linear-gradient(135deg, var(--primary), var(--primary-dark));
      color: #fff;
      border-radius: var(--radius);
      padding: 1.25rem 1.1rem;
      box-shadow: var(--shadow);
    }}
    .header h1 {{ font-size: clamp(1.35rem, 4.8vw, 2.15rem); font-weight: 900; display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }}
    .header p {{ margin-top: 0.5rem; opacity: 0.95; font-size: clamp(0.98rem, 3.2vw, 1.12rem); }}
    .meta {{ margin-top: 0.65rem; display: flex; flex-wrap: wrap; gap: 10px; }}
    .pill {{ background: rgba(255,255,255,0.14); border: 1px solid rgba(255,255,255,0.22); padding: 0.35rem 0.7rem; border-radius: 999px; font-weight: 700; font-size: 0.9rem; }}
    .panel {{
      background: var(--glass-bg);
      border-radius: var(--radius);
      padding: 1rem 1.1rem;
      box-shadow: var(--shadow);
      border: 1px solid rgba(0,0,0,0.06);
    }}
    .row {{ display: flex; gap: 12px; align-items: center; justify-content: space-between; flex-wrap: wrap; }}
    .progress {{ height: 10px; background: rgba(15,23,42,0.12); border-radius: 999px; overflow: hidden; }}
    .progress > div {{ height: 100%; width: 0%; background: linear-gradient(90deg, var(--primary), var(--accent)); transition: width 0.4s ease; }}
    .btn {{
      min-height: var(--tap);
      padding: 0.75rem 1rem;
      border-radius: 999px;
      border: 1px solid rgba(0,0,0,0.10);
      background: var(--white);
      cursor: pointer;
      font-weight: 800;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.2s ease;
      -webkit-tap-highlight-color: transparent;
      touch-action: manipulation;
    }}
    .btn:active {{ transform: scale(0.99); }}
    .btn.primary {{
      background: linear-gradient(135deg, var(--primary), var(--primary-dark));
      color: #fff;
      border-color: rgba(255,255,255,0.15);
      box-shadow: 0 12px 28px rgba(31,106,117,0.22);
    }}
    .grid {{ display: grid; grid-template-columns: repeat(12, 1fr); gap: 12px; }}
    .col-7 {{ grid-column: span 7; }}
    .col-5 {{ grid-column: span 5; }}
    @media (max-width: 900px) {{ .col-7, .col-5 {{ grid-column: span 12; }} }}
    .card {{
      background: rgba(255,255,255,0.96);
      border: 1px solid rgba(0,0,0,0.06);
      border-radius: var(--radius);
      padding: 1.1rem 1.1rem;
      box-shadow: 0 8px 28px rgba(0,0,0,0.08);
    }}
    .card h3 {{
      color: var(--primary);
      font-size: 1.2rem;
      display: flex;
      gap: 10px;
      align-items: center;
      margin-bottom: 0.65rem;
      padding-bottom: 0.5rem;
      border-bottom: 2px solid rgba(244,144,64,0.65);
    }}
    /* Reference-style content sections */
    .content-section {{
      background: var(--glass-bg);
      border-radius: var(--radius);
      padding: 1.25rem;
      box-shadow: var(--shadow);
      border: 1px solid rgba(0,0,0,0.06);
    }}
    .muted {{ color: var(--muted); }}
    .list {{ margin-left: 1.1rem; display: grid; gap: 0.35rem; }}
    .canvasBox {{
      position: relative;
      border-radius: var(--radius);
      overflow: hidden;
      background: radial-gradient(circle at 30% 20%, rgba(255,255,255,0.10), rgba(0,0,0,0.05));
      border: 1px solid rgba(0,0,0,0.08);
      min-height: 280px;
    }}
    canvas {{ width: 100%; height: 100%; display: block; }}
    .hint {{
      position: absolute; left: 12px; bottom: 12px;
      background: rgba(0,0,0,0.45); color: #fff;
      padding: 0.5rem 0.75rem; border-radius: 999px;
      font-size: 0.9rem; font-weight: 800;
      backdrop-filter: blur(6px);
    }}
    .quiz {{ display: grid; gap: 10px; }}
    .q {{ padding: 0.9rem; border-radius: var(--radius); background: rgba(15,23,42,0.04); border: 1px solid rgba(0,0,0,0.06); }}
    .q h4 {{ color: var(--primary); margin-bottom: 0.6rem; }}
    .opts {{ display: grid; gap: 8px; }}
    .opt {{ min-height: var(--tap); padding: 0.75rem 0.8rem; border-radius: var(--radius); border: 2px solid transparent; background: rgba(15,23,42,0.06); cursor: pointer; text-align: left; font-weight: 700; }}
    .opt:hover {{ border-color: rgba(31,106,117,0.35); }}
    .opt.selected {{ background: rgba(31,106,117,0.14); border-color: rgba(31,106,117,0.55); }}
    .toast {{ display:none; margin-top: 0.75rem; padding: 0.75rem; border-radius: var(--radius); font-weight: 800; }}
    .toast.show {{ display:block; }}
    .toast.good {{ background: #d4edda; border: 1px solid #28a745; color: #155724; }}
    .toast.bad {{ background: #f8d7da; border: 1px solid #dc3545; color: #721c24; }}
    .section {{ scroll-margin-top: 92px; }}
    .section + .section {{ margin-top: 14px; }}
    .section-head {{ display:flex; align-items:flex-start; justify-content:space-between; gap: 12px; flex-wrap: wrap; }}
    .section-kicker {{ font-weight: 950; color: var(--primary); }}
    .chip2 {{ background: rgba(15,23,42,0.05); border: 1px solid rgba(0,0,0,0.06); padding: 0.25rem 0.6rem; border-radius: 999px; font-weight: 900; }}

    /* Practice cards */
    .practice {{ display: grid; gap: 10px; margin-top: 10px; }}
    .pq {{ border-radius: var(--radius); border: 1px solid rgba(0,0,0,0.06); background: rgba(15,23,42,0.03); padding: 12px; }}
    .pq h4 {{ margin: 0 0 8px 0; color: var(--primary-dark); font-size: 1.05rem; }}
    .pq textarea, .pq input {{
      width: 100%;
      border-radius: 12px;
      border: 2px solid rgba(31,106,117,0.22);
      padding: 0.75rem;
      font-weight: 800;
      background: rgba(255,255,255,0.9);
      min-height: 44px;
    }}
    .pq textarea {{ min-height: 96px; resize: vertical; }}
    .answer {{ display:none; margin-top: 10px; border-radius: 12px; padding: 10px; background: #fff; border: 1px solid rgba(0,0,0,0.06); }}
    .answer.show {{ display:block; }}
    .answer strong {{ color: var(--primary); }}

    /* 3D tooltip */
    .tip {{
      position: absolute;
      left: 12px;
      top: 12px;
      right: 12px;
      display:none;
      background: rgba(0,0,0,0.55);
      color: #fff;
      padding: 10px 12px;
      border-radius: 14px;
      font-weight: 850;
      backdrop-filter: blur(8px);
    }}
    .tip.show {{ display:block; }}

    /* Games (premium baseline like 07.html) */
    .game {{ margin-top: 12px; border-radius: var(--radius); border: 1px solid rgba(0,0,0,0.06); background: rgba(255,255,255,0.98); overflow: hidden; }}
    .game-head {{ padding: 0.9rem 1rem; background: linear-gradient(135deg, rgba(31,106,117,0.10), rgba(244,144,64,0.10)); border-bottom: 1px solid rgba(0,0,0,0.06); }}
    .game-title {{ font-weight: 950; color: var(--primary); display: flex; align-items: center; gap: 10px; }}
    .game-sub {{ margin-top: 4px; color: var(--muted); font-weight: 750; }}
    .game-actions {{ padding: 0.9rem 1rem; display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }}
    .btn.small {{ padding: 0.6rem 0.9rem; min-height: 40px; font-size: 0.95rem; }}

    .match-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; padding: 12px; }}
    @media (max-width: 720px) {{ .match-grid {{ grid-template-columns: 1fr; }} }}
    .match-col {{ border-radius: var(--radius); border: 1px solid rgba(0,0,0,0.06); padding: 10px; background: rgba(15,23,42,0.03); }}
    .match-h {{ font-weight: 900; color: var(--primary-dark); margin: 4px 6px 10px; }}
    .match-list {{ display: grid; gap: 10px; }}
    .chip {{ min-height: 44px; padding: 0.7rem 0.85rem; border-radius: 999px; border: 1px solid rgba(0,0,0,0.10); background: #fff; cursor: grab; font-weight: 850; text-align: left; }}
    .chip.dragging {{ opacity: 0.6; }}
    .drop {{ border-radius: var(--radius); padding: 0.75rem; border: 2px dashed rgba(31,106,117,0.35); background: rgba(255,255,255,0.65); transition: transform 0.15s ease, background 0.15s ease; }}
    .drop.over {{ transform: scale(1.01); background: rgba(244,144,64,0.08); }}
    .drop-text {{ font-weight: 850; margin-bottom: 8px; }}
    .drop-slot {{ min-height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-weight: 900; background: rgba(15,23,42,0.05); color: rgba(15,23,42,0.70); }}
    .drop-slot.filled {{ background: rgba(31,106,117,0.12); color: var(--primary-dark); }}

    .blanks {{ display: grid; gap: 10px; padding: 12px; }}
    .blank-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; align-items: center; }}
    @media (max-width: 520px) {{ .blank-row {{ grid-template-columns: 1fr; }} }}
    .blank-pattern {{ font-weight: 950; letter-spacing: 2px; color: var(--primary-dark); background: rgba(15,23,42,0.04); border: 1px solid rgba(0,0,0,0.06); border-radius: 12px; padding: 0.75rem; text-align: center; }}
    .blank-in {{ min-height: 44px; border-radius: 12px; border: 2px solid rgba(31,106,117,0.22); padding: 0.7rem 0.8rem; font-weight: 900; letter-spacing: 1px; }}
    .blank-in:focus {{ outline: none; border-color: rgba(31,106,117,0.55); box-shadow: 0 0 0 4px rgba(31,106,117,0.10); }}

    .tf {{ display: grid; gap: 10px; padding: 12px; }}
    .tf-row {{ display: flex; gap: 10px; align-items: center; justify-content: space-between; flex-wrap: wrap; padding: 10px; border-radius: var(--radius); border: 1px solid rgba(0,0,0,0.06); background: rgba(255,255,255,0.75); }}
    .tf-text {{ flex: 1; min-width: 220px; font-weight: 800; }}
    .tf-btns {{ display: flex; gap: 8px; }}
    .tf-btn {{ min-height: 44px; padding: 0.6rem 0.9rem; border-radius: 999px; border: 2px solid rgba(31,106,117,0.28); background: rgba(31,106,117,0.06); font-weight: 950; cursor: pointer; }}
    .tf-btn.selected {{ background: linear-gradient(135deg, var(--primary), var(--primary-dark)); color: #fff; border-color: rgba(255,255,255,0.18); }}
  </style>
</head>
<body>
  <div class="wrap">
    <header class="header">
      <h1><i class="fas fa-meteor"></i> {safe_title}</h1>
      <p>{safe_subtitle if safe_subtitle else "Tap through, play the games, and test your skills."}</p>
      <div class="meta" id="metaRow"></div>
    </header>

    <section class="panel sticky" aria-label="Progress">
      <div class="row">
        <div style="display:flex; flex-direction:column; gap:6px; flex:1; min-width: 200px;">
          <div style="display:flex; justify-content:space-between; gap:12px; align-items:center; flex-wrap:wrap;">
            <div style="font-weight:900; color: var(--primary);">Scroll progress</div>
            <div class="muted" style="font-weight:800;"><span id="stepNow">1</span> / <span id="stepTotal">1</span></div>
          </div>
          <div class="progress"><div id="progressFill"></div></div>
        </div>
        <div style="display:flex; gap:10px; flex-wrap:wrap;">
          <button class="btn" id="btnTop"><i class="fas fa-arrow-up"></i> Top</button>
          <button class="btn primary" id="btnNextSection">Next section <i class="fas fa-arrow-down"></i></button>
        </div>
      </div>
    </section>

    <section class="content-section section" id="section-3d">
      <div class="section-head">
        <div>
          <div class="section-kicker"><i class="fas fa-cube"></i> Interactive 3D</div>
          <div class="muted">This 3D scene is tied to the lesson topic. Tap parts to learn.</div>
        </div>
        <div class="chip2" id="sceneLabel">Scene</div>
      </div>
      <div style="height:10px"></div>
      <div id="matterControls" style="display:none; gap:10px; flex-wrap:wrap; margin-bottom: 10px;">
        <button class="btn small" data-matter="solid"><i class="fas fa-cube"></i> Solid</button>
        <button class="btn small" data-matter="liquid"><i class="fas fa-tint"></i> Liquid</button>
        <button class="btn small" data-matter="gas"><i class="fas fa-wind"></i> Gas</button>
      </div>
      <div class="canvasBox" id="canvasBox">
        <canvas id="sceneCanvas"></canvas>
        <div class="tip" id="sceneTip"></div>
        <div class="hint"><i class="fas fa-hand-pointer"></i> Drag / pinch</div>
      </div>
    </section>

    <main id="sections"></main>
  </div>

  <script>
  const LESSON = {payload};

  function esc(s) {{
    return String(s ?? "")
      .replaceAll("&","&amp;")
      .replaceAll("<","&lt;")
      .replaceAll(">","&gt;")
      .replaceAll("\\"","&quot;")
      .replaceAll("'","&#39;");
  }}

  const sections = Array.isArray(LESSON.sections) ? LESSON.sections : [];
  const total = Math.max(1, sections.length);

  const stepNow = document.getElementById('stepNow');
  const stepTotal = document.getElementById('stepTotal');
  const progressFill = document.getElementById('progressFill');
  const sectionsRoot = document.getElementById('sections');

  stepTotal.textContent = total;

  function setProgress(currentIndex) {{
    const idx = Math.max(0, Math.min(total - 1, Number(currentIndex) || 0));
    stepNow.textContent = String(idx + 1);
    progressFill.style.width = `${{Math.round(((idx + 1) / total) * 100)}}%`;
  }}

  function renderSectionCard(s, index) {{
    const title = esc(s.title || `Section ${{index+1}}`);
    const icon = esc(s.icon || "fa-star");
    const desc = esc(s.description || "");
    const bullets = Array.isArray(s.bullets) ? s.bullets : [];
    const activity = s.activity || null;
    const games = Array.isArray(s.games) ? s.games : [];
    const practice = Array.isArray(s.practice) ? s.practice : [];

    let html = `
      <section class="content-section section" id="sec-${{index}}">
        <div class="section-head">
          <div>
            <h3><i class="fas ${{icon}}"></i> ${{title}}</h3>
            ${{desc ? `<p class="muted">${{desc}}</p>` : ``}}
          </div>
          <div class="chip2">#${{index+1}}</div>
        </div>
    `;

    if (bullets.length) {{
      html += `<ul class="list">` + bullets.map(b => `<li>${{esc(b)}}</li>`).join('') + `</ul>`;
    }}

    function renderGame(g, gameIdx) {{
      const type = String(g?.type || '');
      const title = esc(g?.title || 'Game');
      const prompt = esc(g?.prompt || '');

      if (type === 'matching' && Array.isArray(g?.pairs)) {{
        const pairs = g.pairs.slice(0, 8);
        const left = pairs.map((p, i) => ({{ id: `l_${{i}}`, text: String(p.left || '') }}));
        const right = pairs.map((p, i) => ({{ id: `r_${{i}}`, text: String(p.right || ''), match: `l_${{i}}` }}));
        // shuffle right
        for (let i = right.length - 1; i > 0; i--) {{
          const j = Math.floor(Math.random() * (i + 1));
          [right[i], right[j]] = [right[j], right[i]];
        }}
        return `
          <div class="game">
            <div class="game-head">
              <div class="game-title"><i class="fas fa-puzzle-piece"></i> ${{title}}</div>
              <div class="game-sub">${{prompt}}</div>
            </div>
            <div class="match-grid" data-game="matching" data-gi="${{gameIdx}}">
              <div class="match-col">
                <div class="match-h">Words</div>
                <div class="match-list">
                  ${{left.map(x => `<button class="chip drag" draggable="true" data-id="${{esc(x.id)}}">${{esc(x.text)}}</button>`).join('')}}
                </div>
              </div>
              <div class="match-col">
                <div class="match-h">Meanings</div>
                <div class="match-list">
                  ${{right.map(x => `<div class="drop" data-accept="${{esc(x.match)}}" data-filled=""><div class="drop-text">${{esc(x.text)}}</div><div class="drop-slot">Drop here</div></div>`).join('')}}
                </div>
              </div>
            </div>
            <div class="game-actions">
              <button class="btn primary small" data-action="check-matching" data-gi="${{gameIdx}}"><i class="fas fa-check"></i> Check</button>
              <div class="toast" data-toast="matching-${{gameIdx}}"></div>
            </div>
          </div>
        `;
      }}

      if (type === 'fill_blanks' && Array.isArray(g?.items)) {{
        const items = g.items.slice(0, 8);
        return `
          <div class="game">
            <div class="game-head">
              <div class="game-title"><i class="fas fa-keyboard"></i> ${{title}}</div>
              <div class="game-sub">${{prompt}}</div>
            </div>
            <div class="blanks" data-game="blanks" data-gi="${{gameIdx}}">
              ${{items.map((it, i) => `
                <div class="blank-row">
                  <div class="blank-pattern">${{esc(it.pattern || '')}}</div>
                  <input class="blank-in" inputmode="text" autocomplete="off" autocapitalize="characters" data-answer="${{esc((it.answer||'').toUpperCase())}}" placeholder="Type word" />
                </div>
              `).join('')}}
            </div>
            <div class="game-actions">
              <button class="btn primary small" data-action="check-blanks" data-gi="${{gameIdx}}"><i class="fas fa-check"></i> Check</button>
              <div class="toast" data-toast="blanks-${{gameIdx}}"></div>
            </div>
          </div>
        `;
      }}

      if (type === 'true_false' && Array.isArray(g?.items)) {{
        const items = g.items.slice(0, 8);
        return `
          <div class="game">
            <div class="game-head">
              <div class="game-title"><i class="fas fa-check-circle"></i> ${{title}}</div>
              <div class="game-sub">${{prompt}}</div>
            </div>
            <div class="tf" data-game="tf" data-gi="${{gameIdx}}">
              ${{items.map((it, i) => `
                <div class="tf-row" data-ans="${{it.answer ? 'true' : 'false'}}">
                  <div class="tf-text">${{esc(it.text || '')}}</div>
                  <div class="tf-btns">
                    <button class="tf-btn" data-v="true">True</button>
                    <button class="tf-btn" data-v="false">False</button>
                  </div>
                </div>
              `).join('')}}
            </div>
            <div class="game-actions">
              <button class="btn primary small" data-action="check-tf" data-gi="${{gameIdx}}"><i class="fas fa-check"></i> Check</button>
              <div class="toast" data-toast="tf-${{gameIdx}}"></div>
            </div>
          </div>
        `;
      }}

      // fallback to a simple MCQ block
      if (type === 'mcq' && g?.q && Array.isArray(g?.options)) {{
        const opts = g.options.slice(0, 4);
        const correct = typeof g.answer_index === 'number' ? g.answer_index : -1;
        return `
          <div class="game">
            <div class="game-head">
              <div class="game-title"><i class="fas fa-gamepad"></i> ${{title}}</div>
              <div class="game-sub">${{prompt}}</div>
            </div>
            <div class="q">
              <div style="font-weight:900; margin-bottom: 10px;">${{esc(g.q)}}</div>
              <div class="opts">
                ${{opts.map((o,i)=>`<button class="opt" data-gi="${{gameIdx}}" data-opt="${{i}}" data-correct="${{correct}}">${{esc(o)}}</button>`).join('')}}
              </div>
              <div class="toast" data-toast="mcq-${{gameIdx}}"></div>
            </div>
          </div>
        `;
      }}

      return '';
    }}

    if (games.length) {{
      html += `<div style="height:10px"></div>` + games.map((g, i) => renderGame(g, i)).join('');
    }}

    if (practice.length) {{
      html += `<div style="height:10px"></div><div class="practice">`;
      practice.forEach((p, pi) => {{
        const pt = String(p?.type || '');
        const q = esc(p?.q || '');
        const ans = esc(p?.answer || '');
        const ex = esc(p?.explain || '');
        const id = `p_${{index}}_${{pi}}`;
        if (pt === 'short_answer') {{
          html += `
            <div class="pq">
              <h4><i class="fas fa-question-circle"></i> ${{q}}</h4>
              <textarea id="${{id}}_in" placeholder="Type your answer..."></textarea>
              <div style="display:flex; gap:10px; flex-wrap:wrap; margin-top:10px;">
                <button class="btn primary small" data-action="show-answer" data-target="${{id}}"><i class="fas fa-eye"></i> Show answer</button>
              </div>
              <div class="answer" id="${{id}}_ans"><strong>Answer:</strong> ${{ans}}${{ex ? `<div class="muted" style="margin-top:6px;">${{ex}}</div>` : ''}}</div>
            </div>
          `;
        }} else if (pt === 'fill_blank') {{
          html += `
            <div class="pq">
              <h4><i class="fas fa-pen"></i> ${{q}}</h4>
              <input id="${{id}}_in" placeholder="Type the missing word(s)..." data-answer="${{ans}}" />
              <div style="display:flex; gap:10px; flex-wrap:wrap; margin-top:10px;">
                <button class="btn primary small" data-action="check-one-blank" data-target="${{id}}"><i class="fas fa-check"></i> Check</button>
                <button class="btn small" data-action="show-answer" data-target="${{id}}"><i class="fas fa-eye"></i> Show</button>
              </div>
              <div class="toast" data-toast="blankone-${{id}}"></div>
              <div class="answer" id="${{id}}_ans"><strong>Answer:</strong> ${{ans}}${{ex ? `<div class="muted" style="margin-top:6px;">${{ex}}</div>` : ''}}</div>
            </div>
          `;
        }} else if (pt === 'true_false') {{
          html += `
            <div class="pq">
              <h4><i class="fas fa-check-circle"></i> True/False</h4>
              <div class="muted" style="font-weight:850; margin-bottom:8px;">${{q}}</div>
              <div class="tf-btns">
                <button class="tf-btn" data-action="tf-one" data-v="true" data-target="${{id}}">True</button>
                <button class="tf-btn" data-action="tf-one" data-v="false" data-target="${{id}}">False</button>
              </div>
              <div class="toast" data-toast="tfone-${{id}}"></div>
              <div class="answer" id="${{id}}_ans"><strong>Answer:</strong> ${{ans}}${{ex ? `<div class="muted" style="margin-top:6px;">${{ex}}</div>` : ''}}</div>
            </div>
          `;
        }}
      }});
      html += `</div>`;
    }}

    if (activity && activity.type === 'mcq' && activity.q) {{
      const opts = Array.isArray(activity.options) ? activity.options : [];
      html += `
        <div style="height:10px"></div>
        <div class="q">
          <h4><i class="fas fa-gamepad"></i> Quick challenge</h4>
          <div style="font-weight:900; margin-bottom: 10px;">${{esc(activity.q)}}</div>
          <div class="opts">
            ${{opts.map((o,i)=>`<button class="opt" data-opt="${{i}}">${{esc(o)}}</button>`).join('')}}
          </div>
          <div class="toast" id="toast"></div>
        </div>
      `;
      setTimeout(() => {{
        const toast = document.getElementById('toast');
        document.querySelectorAll('.opt').forEach(btn => {{
          btn.addEventListener('click', () => {{
            document.querySelectorAll('.opt').forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');
            const chosen = Number(btn.dataset.opt);
            const correct = typeof activity.answer_index === 'number' ? activity.answer_index : -1;
            const ok = chosen === correct;
            toast.className = 'toast show ' + (ok ? 'good' : 'bad');
            toast.textContent = ok ? (activity.correct_text || 'Correct!') : (activity.incorrect_text || 'Try again!');
          }});
        }});
      }}, 0);
    }}

    html += `</section>`;
    return html;
  }}

  // Meta pills
  const meta = document.getElementById('metaRow');
  const pills = [];
  if (LESSON.grade) pills.push({{label: `Grade: ${{LESSON.grade}}`, icon: 'fa-graduation-cap'}});
  if (LESSON.topic) pills.push({{label: LESSON.topic, icon: 'fa-tag'}});
  pills.forEach(p => {{
    const el = document.createElement('div');
    el.className = 'pill';
    el.innerHTML = `<i class="fas ${{p.icon}}"></i> ${{esc(p.label)}}`;
    meta.appendChild(el);
  }});

  // ---- Single-page render ----
  function bindGameHandlers() {{
    // Matching drag/drop
    document.querySelectorAll('[data-game="matching"]').forEach(gameEl => {{
      let dragged = null;
      gameEl.querySelectorAll('.drag').forEach(chip => {{
        chip.addEventListener('dragstart', () => {{ dragged = chip; chip.classList.add('dragging'); }});
        chip.addEventListener('dragend', () => {{ chip.classList.remove('dragging'); }});
      }});
      gameEl.querySelectorAll('.drop').forEach(drop => {{
        drop.addEventListener('dragover', (e) => {{ e.preventDefault(); drop.classList.add('over'); }});
        drop.addEventListener('dragleave', () => drop.classList.remove('over'));
        drop.addEventListener('drop', (e) => {{
          e.preventDefault();
          drop.classList.remove('over');
          if (!dragged) return;
          drop.setAttribute('data-filled', dragged.getAttribute('data-id') || '');
          const slot = drop.querySelector('.drop-slot');
          if (slot) {{
            slot.textContent = dragged.textContent || 'Dropped';
            slot.classList.add('filled');
          }}
        }});
      }});
    }});

    // TF selection (games)
    document.querySelectorAll('[data-game="tf"] .tf-row').forEach(row => {{
      row.querySelectorAll('.tf-btn').forEach(btn => {{
        btn.addEventListener('click', () => {{
          row.querySelectorAll('.tf-btn').forEach(b => b.classList.remove('selected'));
          btn.classList.add('selected');
          row.setAttribute('data-picked', btn.getAttribute('data-v'));
        }});
      }});
    }});

    // MCQ inside games
    document.querySelectorAll('.opt[data-gi]').forEach(btn => {{
      btn.addEventListener('click', () => {{
        const gi = btn.getAttribute('data-gi');
        const correct = Number(btn.getAttribute('data-correct'));
        const chosen = Number(btn.getAttribute('data-opt'));
        btn.parentElement?.querySelectorAll('.opt').forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');
        const toast = document.querySelector(`[data-toast="mcq-${{gi}}"]`);
        if (!toast) return;
        const ok = chosen === correct && correct >= 0;
        toast.className = 'toast show ' + (ok ? 'good' : 'bad');
        toast.textContent = ok ? 'Nice! You got it.' : 'Try again.';
      }});
    }});

    // Check buttons
    document.querySelectorAll('[data-action="check-matching"]').forEach(btn => {{
      btn.addEventListener('click', () => {{
        const gi = btn.getAttribute('data-gi');
        const game = document.querySelector(`[data-game="matching"][data-gi="${{gi}}"]`);
        const toast = document.querySelector(`[data-toast="matching-${{gi}}"]`);
        if (!game || !toast) return;
        const drops = Array.from(game.querySelectorAll('.drop'));
        const total = drops.length;
        let ok = 0;
        drops.forEach(d => {{
          const accept = d.getAttribute('data-accept');
          const filled = d.getAttribute('data-filled');
          if (accept && filled && accept === filled) ok++;
        }});
        toast.className = 'toast show ' + (ok === total ? 'good' : 'bad');
        toast.textContent = ok === total ? 'Perfect match!' : `You got ${{ok}}/${{total}}. Try again.`;
      }});
    }});

    document.querySelectorAll('[data-action="check-blanks"]').forEach(btn => {{
      btn.addEventListener('click', () => {{
        const gi = btn.getAttribute('data-gi');
        const box = document.querySelector(`[data-game="blanks"][data-gi="${{gi}}"]`);
        const toast = document.querySelector(`[data-toast="blanks-${{gi}}"]`);
        if (!box || !toast) return;
        const inputs = Array.from(box.querySelectorAll('.blank-in'));
        const total = inputs.length;
        let ok = 0;
        inputs.forEach(inp => {{
          const ans = String(inp.getAttribute('data-answer') || '');
          const v = String(inp.value || '').trim().toUpperCase();
          if (v && v === ans) ok++;
        }});
        toast.className = 'toast show ' + (ok === total ? 'good' : 'bad');
        toast.textContent = ok === total ? 'Great job!' : `You got ${{ok}}/${{total}}. Keep going.`;
      }});
    }});

    document.querySelectorAll('[data-action="check-tf"]').forEach(btn => {{
      btn.addEventListener('click', () => {{
        const gi = btn.getAttribute('data-gi');
        const box = document.querySelector(`[data-game="tf"][data-gi="${{gi}}"]`);
        const toast = document.querySelector(`[data-toast="tf-${{gi}}"]`);
        if (!box || !toast) return;
        const rows = Array.from(box.querySelectorAll('.tf-row'));
        const total = rows.length;
        let ok = 0;
        rows.forEach(r => {{
          const ans = r.getAttribute('data-ans');
          const pick = r.getAttribute('data-picked');
          if (pick && ans && pick === ans) ok++;
        }});
        toast.className = 'toast show ' + (ok === total ? 'good' : 'bad');
        toast.textContent = ok === total ? 'All correct!' : `You got ${{ok}}/${{total}}. Try again.`;
      }});
    }});
  }}

  function renderAll() {{
    sectionsRoot.innerHTML = sections.map((s, i) => renderSectionCard(s, i)).join('');

    // Practice buttons
    document.querySelectorAll('[data-action="show-answer"]').forEach(btn => {{
      btn.addEventListener('click', () => {{
        const id = btn.getAttribute('data-target');
        const el = document.getElementById(`${{id}}_ans`);
        if (el) el.classList.toggle('show');
      }});
    }});
    document.querySelectorAll('[data-action="check-one-blank"]').forEach(btn => {{
      btn.addEventListener('click', () => {{
        const id = btn.getAttribute('data-target');
        const inp = document.getElementById(`${{id}}_in`);
        const toast = document.querySelector(`[data-toast="blankone-${{id}}"]`);
        if (!inp || !toast) return;
        const ans = String(inp.getAttribute('data-answer') || '').trim().toLowerCase();
        const v = String(inp.value || '').trim().toLowerCase();
        const ok = ans && v && v === ans;
        toast.className = 'toast show ' + (ok ? 'good' : 'bad');
        toast.textContent = ok ? 'Correct!' : 'Try again (or tap Show).';
      }});
    }});
    document.querySelectorAll('[data-action="tf-one"]').forEach(btn => {{
      btn.addEventListener('click', () => {{
        const id = btn.getAttribute('data-target');
        const pick = btn.getAttribute('data-v');
        const wrap = btn.closest('.pq');
        if (wrap) wrap.querySelectorAll('.tf-btn').forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');
        const ans = (document.getElementById(`${{id}}_ans`)?.textContent || '').toLowerCase();
        const ok = ans.includes(pick);
        const toast = document.querySelector(`[data-toast="tfone-${{id}}"]`);
        if (!toast) return;
        toast.className = 'toast show ' + (ok ? 'good' : 'bad');
        toast.textContent = ok ? 'Correct!' : 'Not quite — tap Show.';
      }});
    }});

    bindGameHandlers();
  }}

  function setupScrollProgress() {{
    const cards = Array.from(document.querySelectorAll('.section[id^="sec-"]'));
    if (!cards.length) {{
      setProgress(0);
      return;
    }}
    setProgress(0);
    const obs = new IntersectionObserver((entries) => {{
      const visible = entries
        .filter(e => e.isIntersecting)
        .sort((a,b) => b.intersectionRatio - a.intersectionRatio)[0];
      if (!visible) return;
      const id = visible.target.getAttribute('id') || '';
      const n = Number(id.replace('sec-',''));
      if (!Number.isNaN(n)) setProgress(n);
    }}, {{ root: null, threshold: [0.25, 0.35, 0.5, 0.65] }});
    cards.forEach(c => obs.observe(c));

    document.getElementById('btnTop')?.addEventListener('click', () => window.scrollTo({{top: 0, behavior: 'smooth'}}));
    document.getElementById('btnNextSection')?.addEventListener('click', () => {{
      const current = Number(stepNow.textContent || '1') - 1;
      const next = Math.min(cards.length - 1, current + 1);
      cards[next]?.scrollIntoView({{behavior:'smooth', block:'start'}});
    }});
  }}

  // ---- Relevant 3D templates ----
  let scene, camera, renderer, raycaster, mouse;
  let interactiveObjects = [];
  let isDragging = false;
  let last = {{x:0,y:0}};
  let theta = 0.6, phi = 0.9, radius = 8.5;

  function sceneTemplate() {{
    const s = LESSON.three_spec || {{}};
    const scene = String(s.scene || '').trim();
    if (scene) return scene;
    // fallback
    const t = String(LESSON.topic || LESSON.title || '').toLowerCase();
    if (t.includes('computer')) return 'computer_parts';
    if (t.includes('matter') || t.includes('solid') || t.includes('liquid') || t.includes('gas')) return 'matter_states';
    return 'ambient';
  }}

  function seedValue() {{
    const s = LESSON.three_spec || {{}};
    return String(s.variant_seed || LESSON.topic || LESSON.title || 'seed');
  }}

  function seededRandomFactory(seedStr) {{
    // xmur3 + mulberry32
    function xmur3(str) {{
      let h = 1779033703 ^ str.length;
      for (let i = 0; i < str.length; i++) {{
        h = Math.imul(h ^ str.charCodeAt(i), 3432918353);
        h = (h << 13) | (h >>> 19);
      }}
      return function() {{
        h = Math.imul(h ^ (h >>> 16), 2246822507);
        h = Math.imul(h ^ (h >>> 13), 3266489909);
        return (h ^= h >>> 16) >>> 0;
      }}
    }}
    function mulberry32(a) {{
      return function() {{
        let t = a += 0x6D2B79F5;
        t = Math.imul(t ^ (t >>> 15), t | 1);
        t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
      }}
    }}
    const seedFn = xmur3(seedStr);
    const rand = mulberry32(seedFn());
    return rand;
  }}

  function resize() {{
    const canvas = document.getElementById('sceneCanvas');
    const box = canvas.parentElement;
    const w = box.clientWidth;
    const h = Math.max(280, Math.round(w * 0.72));
    box.style.height = h + 'px';
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h, false);
  }}

  function setCam() {{
    const x = radius * Math.sin(phi) * Math.cos(theta);
    const y = radius * Math.cos(phi);
    const z = radius * Math.sin(phi) * Math.sin(theta);
    camera.position.set(x, y, z);
    camera.lookAt(0, 0, 0);
  }}

  function init3d() {{
    const canvas = document.getElementById('sceneCanvas');
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0b1020);
    camera = new THREE.PerspectiveCamera(60, 1, 0.1, 100);
    renderer = new THREE.WebGLRenderer({{canvas, antialias:true, alpha:false}});
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

    const amb = new THREE.AmbientLight(0xffffff, 0.7);
    scene.add(amb);
    const p = new THREE.PointLight(0xffffff, 1.2);
    p.position.set(5, 7, 4);
    scene.add(p);

    const grid = new THREE.GridHelper(14, 14, 0x2a355a, 0x1f2a44);
    grid.position.y = -2.5;
    scene.add(grid);

    const label = document.getElementById('sceneLabel');
    const tip = document.getElementById('sceneTip');
    const template = sceneTemplate();
    const rand = seededRandomFactory(seedValue());
    const matterControls = document.getElementById('matterControls');
    if (label) {{
      label.textContent =
        template === 'computer_parts' ? 'Computer parts'
        : template === 'matter_states' ? 'States of matter'
        : 'Ambient';
    }}

    if (matterControls) {{
      matterControls.style.display = template === 'matter_states' ? 'flex' : 'none';
    }}

    interactiveObjects = [];

    function addComputerParts() {{
      // per-PDF variations (colors + slight positioning) from seeded random
      const monColor = new THREE.Color().setHSL(0.52 + rand()*0.08, 0.85, 0.55);
      const kbColor = new THREE.Color().setHSL(0.58 + rand()*0.08, 0.25, 0.65);
      const cpuColor = new THREE.Color().setHSL(0.28 + rand()*0.10, 0.75, 0.45);

      const mon = new THREE.Mesh(
        new THREE.BoxGeometry(3.6, 2.2, 0.25),
        new THREE.MeshStandardMaterial({{color: monColor, roughness: 0.35, metalness: 0.15, emissive: 0x000000}})
      );
      mon.position.set((rand()-0.5)*0.25, 0.2 + (rand()-0.5)*0.15, (rand()-0.5)*0.2);
      mon.userData = {{label: 'Monitor', text: 'The monitor shows what the computer is doing (pictures and words).'}};
      scene.add(mon);
      interactiveObjects.push(mon);

      const stand = new THREE.Mesh(
        new THREE.BoxGeometry(0.6, 0.6, 0.6),
        new THREE.MeshStandardMaterial({{color: 0x64748b, roughness: 0.6}})
      );
      stand.position.set(0, -1.2, 0);
      scene.add(stand);

      const kb = new THREE.Mesh(
        new THREE.BoxGeometry(3.8, 0.25, 1.4),
        new THREE.MeshStandardMaterial({{color: kbColor, roughness: 0.55, metalness: 0.05, emissive: 0x000000}})
      );
      kb.position.set((rand()-0.5)*0.35, -1.8, 1.2 + (rand()-0.5)*0.25);
      kb.userData = {{label: 'Keyboard', text: 'The keyboard helps us type letters and numbers.'}};
      scene.add(kb);
      interactiveObjects.push(kb);

      const ms = new THREE.Mesh(
        new THREE.SphereGeometry(0.45, 24, 24),
        new THREE.MeshStandardMaterial({{color: 0xf59e0b, roughness: 0.35, metalness: 0.10, emissive: 0x000000}})
      );
      ms.scale.set(1.2, 0.8, 1.4);
      ms.position.set(2.3, -1.8, 1.0);
      ms.userData = {{label: 'Mouse', text: 'The mouse helps us point, click, and drag on the screen.'}};
      scene.add(ms);
      interactiveObjects.push(ms);

      const cpu = new THREE.Mesh(
        new THREE.BoxGeometry(1.4, 2.8, 1.2),
        new THREE.MeshStandardMaterial({{color: cpuColor, roughness: 0.45, metalness: 0.08, emissive: 0x000000}})
      );
      cpu.position.set(-3.0 + (rand()-0.5)*0.35, -0.7, -0.5 + (rand()-0.5)*0.35);
      cpu.userData = {{label: 'CPU (Tower)', text: 'The CPU is the brain of the computer. It helps the computer think and work.'}};
      scene.add(cpu);
      interactiveObjects.push(cpu);

      const dotGeom = new THREE.SphereGeometry(0.08, 12, 12);
      for (let i = 0; i < 18; i++) {{
        const d = new THREE.Mesh(dotGeom, new THREE.MeshBasicMaterial({{color: 0xffffff}}));
        d.userData = {{
          t: Math.random() * Math.PI * 2,
          r: 2.6 + Math.random() * 1.2,
          y: -0.2 + Math.random() * 0.6,
          s: 0.6 + Math.random() * 0.8,
          label: 'Data',
          text: 'Information moves inside a computer to help it work.'
        }};
        d.position.set(Math.cos(d.userData.t) * d.userData.r, d.userData.y, Math.sin(d.userData.t) * d.userData.r);
        scene.add(d);
        interactiveObjects.push(d);
      }}
    }}

    function addMatterStates() {{
      // Simple, content-relevant 3D: molecules behave differently per state.
      // (We can extend later with temperature slider like your 07.html.)
      const state = {{value: 'solid'}};
      const molGeom = new THREE.SphereGeometry(0.24, 24, 24);
      const mols = [];

      function colorFor(s) {{
        if (s === 'solid') return new THREE.Color(0x8B5CF6);
        if (s === 'liquid') return new THREE.Color(0x3B82F6);
        return new THREE.Color(0x10B981);
      }}

      function resetMolecules(s) {{
        // clear previous
        mols.forEach(m => scene.remove(m));
        mols.length = 0;

        const baseColor = colorFor(s);
        const matBase = new THREE.MeshStandardMaterial({{color: baseColor, roughness: 0.35, metalness: 0.08, emissive: 0x000000}});

        if (s === 'solid') {{
          let idx = 0;
          for (let x = -2; x <= 2; x += 1) {{
            for (let y = -1; y <= 1; y += 1) {{
              for (let z = -1; z <= 1; z += 1) {{
                if (idx++ > 20) break;
                const m = new THREE.Mesh(molGeom, matBase.clone());
                m.position.set(x*0.55, y*0.55, z*0.55);
                m.userData.v = new THREE.Vector3((rand()-0.5)*0.004, (rand()-0.5)*0.004, (rand()-0.5)*0.004);
                m.userData.label = 'Solid';
                m.userData.text = 'In solids, molecules stay close together.';
                scene.add(m); mols.push(m); interactiveObjects.push(m);
              }}
            }}
          }}
        }} else if (s === 'liquid') {{
          for (let i = 0; i < 22; i++) {{
            const m = new THREE.Mesh(molGeom, matBase.clone());
            m.position.set((rand()-0.5)*3.2, (rand()-0.2)*1.8, (rand()-0.5)*3.2);
            m.userData.v = new THREE.Vector3((rand()-0.5)*0.02, (rand()-0.5)*0.012, (rand()-0.5)*0.02);
            m.userData.label = 'Liquid';
            m.userData.text = 'In liquids, molecules slide past each other.';
            scene.add(m); mols.push(m); interactiveObjects.push(m);
          }}
        }} else {{
          for (let i = 0; i < 24; i++) {{
            const m = new THREE.Mesh(molGeom, matBase.clone());
            m.position.set((rand()-0.5)*6.5, (rand()-0.1)*3.8, (rand()-0.5)*6.5);
            m.userData.v = new THREE.Vector3((rand()-0.5)*0.045, (rand()-0.5)*0.035, (rand()-0.5)*0.045);
            m.userData.label = 'Gas';
            m.userData.text = 'In gases, molecules move freely and spread out.';
            scene.add(m); mols.push(m); interactiveObjects.push(m);
          }}
        }}
      }}

      // Hook buttons
      if (matterControls) {{
        matterControls.querySelectorAll('[data-matter]').forEach(btn => {{
          btn.addEventListener('click', () => {{
            const s = String(btn.getAttribute('data-matter') || 'solid');
            state.value = s;
            resetMolecules(s);
          }});
        }});
      }}

      resetMolecules(state.value);
    }}

    function addAmbient() {{
      const geom = new THREE.SphereGeometry(0.22, 24, 24);
      for (let i = 0; i < 22; i++) {{
        const m = new THREE.MeshStandardMaterial({{
          color: new THREE.Color().setHSL(0.55 + (Math.random()*0.12), 0.85, 0.55),
          emissive: 0x000000,
          roughness: 0.35,
          metalness: 0.15
        }});
        const s = new THREE.Mesh(geom, m);
        s.position.set((Math.random()-0.5)*6, (Math.random()-0.15)*4, (Math.random()-0.5)*6);
        s.userData.v = new THREE.Vector3((Math.random()-0.5)*0.014, (Math.random()-0.5)*0.012, (Math.random()-0.5)*0.014);
        s.userData.label = 'Spark';
        s.userData.text = 'Tap objects to explore.';
        scene.add(s);
        interactiveObjects.push(s);
      }}
    }}

    if (template === 'computer_parts') addComputerParts();
    else if (template === 'matter_states') addMatterStates();
    else addAmbient();

    raycaster = new THREE.Raycaster();
    mouse = new THREE.Vector2();
    setCam();
    resize();
    window.addEventListener('resize', resize);

    function pointerPos(e) {{
      const rect = canvas.getBoundingClientRect();
      const x = (('touches' in e) ? e.touches[0].clientX : e.clientX) - rect.left;
      const y = (('touches' in e) ? e.touches[0].clientY : e.clientY) - rect.top;
      return {{x, y, rect}};
    }}

    function onDown(e) {{
      isDragging = true;
      const p = pointerPos(e);
      last = {{x: p.x, y: p.y}};
    }}
    function onMove(e) {{
      if (!isDragging) return;
      const p = pointerPos(e);
      const dx = (p.x - last.x) / p.rect.width;
      const dy = (p.y - last.y) / p.rect.height;
      last = {{x: p.x, y: p.y}};
      theta -= dx * 3.2;
      phi = Math.min(Math.PI - 0.15, Math.max(0.15, phi + dy * 2.6));
      setCam();
    }}
    function onUp() {{ isDragging = false; }}
    function onWheel(e) {{
      radius = Math.min(13, Math.max(4.8, radius + Math.sign(e.deltaY) * 0.6));
      setCam();
    }}
    canvas.addEventListener('mousedown', onDown);
    canvas.addEventListener('mousemove', onMove);
    canvas.addEventListener('mouseup', onUp);
    canvas.addEventListener('mouseleave', onUp);
    canvas.addEventListener('wheel', (e)=>{{ e.preventDefault(); onWheel(e); }}, {{passive:false}});
    canvas.addEventListener('touchstart', (e)=>{{ onDown(e); }}, {{passive:true}});
    canvas.addEventListener('touchmove', (e)=>{{ onMove(e); }}, {{passive:true}});
    canvas.addEventListener('touchend', onUp, {{passive:true}});

    canvas.addEventListener('click', (e)=>{{
      const rect = canvas.getBoundingClientRect();
      mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -(((e.clientY - rect.top) / rect.height) * 2 - 1);
      raycaster.setFromCamera(mouse, camera);
      const hits = raycaster.intersectObjects(interactiveObjects, true);
      if (hits.length) {{
        const obj = hits[0].object;
        if (obj.material && obj.material.emissive) {{
          obj.material.emissive = new THREE.Color(0xF59E0B);
          setTimeout(()=>{{ if (obj.material && obj.material.emissive) obj.material.emissive = new THREE.Color(0x000000); }}, 350);
        }}
        if (tip) {{
          const labelTxt = obj.userData?.label ? String(obj.userData.label) : 'Explore';
          const bodyTxt = obj.userData?.text ? String(obj.userData.text) : 'Tap different parts to learn.';
          tip.innerHTML = `<strong>${{esc(labelTxt)}}:</strong> ${{esc(bodyTxt)}}`;
          tip.classList.add('show');
          setTimeout(() => tip.classList.remove('show'), 3000);
        }}
      }}
    }});
  }}

  function animate() {{
    requestAnimationFrame(animate);
    interactiveObjects.forEach(o => {{
      if (o.userData && o.userData.v) {{
        o.position.add(o.userData.v);
        if (Math.abs(o.position.x) > 3.2) o.userData.v.x *= -1;
        if (o.position.y > 2.8 || o.position.y < -1.6) o.userData.v.y *= -1;
        if (Math.abs(o.position.z) > 3.2) o.userData.v.z *= -1;
      }}
      if (o.userData && o.userData.t !== undefined) {{
        o.userData.t += 0.015 * (o.userData.s || 1);
        o.position.x = Math.cos(o.userData.t) * o.userData.r;
        o.position.z = Math.sin(o.userData.t) * o.userData.r;
      }}
    }});
    renderer.render(scene, camera);
  }}

  function start() {{
    renderAll();
    setupScrollProgress();
    init3d();
    animate();
  }}
  start();
  </script>
</body>
</html>"""

def html_escape(s: str) -> str:
    return (
        (s or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )

def build_lesson_json_from_chunks(chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Deterministically merge extracted chunks into a single lesson JSON that our renderer can trust.
    """
    concepts = []
    vocab = []
    questions = []
    activities = []
    topic_hint = ""
    grade_hint = ""

    for ch in chunks:
        if not topic_hint and ch.get("topic_hint"):
            topic_hint = str(ch.get("topic_hint")).strip()
        if not grade_hint and ch.get("grade_hint"):
            grade_hint = str(ch.get("grade_hint")).strip()
        concepts.extend(ch.get("concepts") or [])
        vocab.extend(ch.get("vocabulary") or [])
        activities.extend(ch.get("activities") or [])
        questions.extend(ch.get("questions") or [])

    def _norm(s: Any) -> str:
        return str(s or "").strip()

    def _fingerprint_text() -> str:
        parts: List[str] = []
        if topic_hint:
            parts.append(topic_hint)
        for c in concepts[:12]:
            parts.append(_norm(c.get("title")))
            for b in (c.get("bullets") or [])[:8]:
                parts.append(_norm(b))
        for v in vocab[:24]:
            parts.append(_norm(v.get("term")))
            parts.append(_norm(v.get("meaning")))
        for q in questions[:12]:
            parts.append(_norm(q.get("q")))
            parts.append(_norm(q.get("answer")))
        joined = "\n".join([p for p in parts if p])
        return joined

    def _content_hash_short(s: str) -> str:
        h = hashlib.sha1((s or "").encode("utf-8", errors="ignore")).hexdigest()
        return h[:12]

    def _choose_three_scene_from_content() -> str:
        """
        Choose a 3D scene family from extracted content keywords.
        This is per-PDF because the fingerprint/seed varies per PDF even within same subject.
        """
        txt = _fingerprint_text().lower()
        # Matter / states keywords
        if any(k in txt for k in ["solid", "liquid", "gas", "states of matter", "molecules", "evapor", "melting", "freezing"]):
            return "matter_states"
        # Computer keywords
        if any(k in txt for k in ["computer", "keyboard", "mouse", "monitor", "cpu", "laptop", "desktop", "tablet", "smartphone"]):
            return "computer_parts"
        return "ambient"

    content_fingerprint = _fingerprint_text()
    variant_seed = _content_hash_short(content_fingerprint)
    three_scene = _choose_three_scene_from_content()
    three_spec = {
        "scene": three_scene,
        "variant_seed": variant_seed,
        "hint": topic_hint or "",
    }

    def _make_vocab_matching(vocab_items: List[Dict[str, Any]]) -> Dict[str, Any] | None:
        pairs = []
        for v in vocab_items:
            term = _norm(v.get("term"))
            meaning = _norm(v.get("meaning"))
            if term and meaning:
                pairs.append({"left": term, "right": meaning})
        pairs = pairs[:6]
        if len(pairs) < 3:
            return None
        return {
            "type": "matching",
            "title": "Match the Words",
            "prompt": "Drag each word to its meaning.",
            "pairs": pairs,
        }

    def _make_true_false_from_bullets(concept_items: List[Dict[str, Any]]) -> Dict[str, Any] | None:
        def looks_like_statement(x: str) -> bool:
            s = _norm(x)
            if not s:
                return False
            low = s.lower()
            # filter imperatives / learning objectives / fragments
            if re.match(r"^(define|know|learn|match|fill|write|draw|collect|make|name|list|choose|answer)\b", low):
                return False
            if low.endswith(":"):
                return False
            # Require a verb-like pattern for a factual statement
            if not re.search(r"\b(is|are|was|were|has|have|can|helps?|used|uses|make|makes)\b", low):
                return False
            # Avoid super short fragments like "Desktop Computer"
            if len(s.split()) < 5:
                return False
            return True

        stmts = []
        for c in concept_items:
            for b in (c.get("bullets") or []):
                s = _norm(b)
                if len(s) < 12 or len(s) > 160:
                    continue
                if not looks_like_statement(s):
                    continue
                # Normalize punctuation for consistency
                if not re.search(r"[.!?]$", s):
                    s = s + "."
                stmts.append({"text": s, "answer": True, "explain": "This statement matches what you learned."})
        stmts = stmts[:5]
        if len(stmts) < 3:
            return None
        return {"type": "true_false", "title": "True or False", "prompt": "Decide if each statement is true.", "items": stmts}

    def _make_fill_blanks_from_vocab(vocab_items: List[Dict[str, Any]]) -> Dict[str, Any] | None:
        items = []
        for v in vocab_items:
            term = _norm(v.get("term")).upper()
            if len(term) < 4 or len(term) > 10 or " " in term:
                continue
            # mask 2 letters
            mask_idx = {1, max(1, len(term) - 2)}
            pattern = "".join("_" if i in mask_idx else ch for i, ch in enumerate(term))
            items.append({"answer": term, "pattern": pattern})
        items = items[:5]
        if len(items) < 3:
            return None
        return {"type": "fill_blanks", "title": "Fill the Missing Letters", "prompt": "Type the missing letters.", "items": items}

    # Normalize extracted activities/questions into our game schema
    normalized_games: List[Dict[str, Any]] = []

    def _valid_game(g: Dict[str, Any]) -> bool:
        gt = _norm(g.get("type"))
        if gt == "matching":
            pairs = g.get("pairs") or g.get("items") or []
            return isinstance(pairs, list) and len(pairs) >= 3
        if gt == "fill_blanks":
            items = g.get("items") or []
            return isinstance(items, list) and len(items) >= 3
        if gt == "true_false":
            items = g.get("items") or []
            return isinstance(items, list) and len(items) >= 3
        if gt == "mcq":
            return bool(_norm(g.get("q"))) and isinstance(g.get("options"), list) and len(g.get("options")) >= 2
        if gt == "sorting":
            items = g.get("items") or []
            return isinstance(items, list) and len(items) >= 4
        return False

    # Prefer extracted activities if they already specify a known type
    for a in activities:
        at = _norm(a.get("type"))
        if at in {"matching", "sorting", "fill_blanks", "true_false", "mcq"}:
            if _valid_game(a):
                normalized_games.append(a)

    # If nothing usable came back, synthesize games from vocab/concepts (deterministic, no extra tokens)
    if not any(_norm(g.get("type")) == "matching" for g in normalized_games):
        m = _make_vocab_matching(vocab)
        if m:
            normalized_games.append(m)
    if not any(_norm(g.get("type")) == "fill_blanks" and _valid_game(g) for g in normalized_games):
        fb = _make_fill_blanks_from_vocab(vocab)
        if fb:
            normalized_games.append(fb)
    if not any(_norm(g.get("type")) == "true_false" and _valid_game(g) for g in normalized_games):
        tf = _make_true_false_from_bullets(concepts)
        if tf:
            normalized_games.append(tf)

    # Pull multiple MCQs if present (for quiz section)
    mcqs = [q for q in questions if (q.get("type") == "mcq" and q.get("q") and isinstance(q.get("options"), list))]
    practice_qs = [q for q in questions if q.get("type") in {"short_answer", "fill_blank", "true_false"} and q.get("q")]

    # Build sections: Intro + concepts + vocab + one quiz section
    sections = []
    sections.append({
        "title": "Welcome",
        "icon": "fa-rocket",
        "description": "Let’s learn by playing. Use Next/Back, and try the mini challenges.",
        "bullets": [
            "Read the key ideas in small steps",
            "Play at least one activity",
            "Finish with a quick quiz",
        ],
    })

    for c in concepts[:5]:
        title = (c.get("title") or "Key idea").strip()
        bullets = [b for b in (c.get("bullets") or []) if isinstance(b, str) and b.strip()][:6]
        if not bullets:
            continue
        sections.append({"title": title, "icon": "fa-lightbulb", "description": "", "bullets": bullets})

    if vocab:
        bullets = [f'{v.get("term","").strip()}: {v.get("meaning","").strip()}'.strip(": ").strip()
                   for v in vocab[:10]]
        bullets = [b for b in bullets if b and ":" in b]
        if bullets:
            sections.append({"title": "Vocabulary", "icon": "fa-book", "description": "New words you’ll use today.", "bullets": bullets})

    # Add a dedicated "Play" section that can host richer game UIs
    if normalized_games:
        sections.append({
            "title": "Play Zone",
            "icon": "fa-gamepad",
            "description": "Play quick games to practice what you learned.",
            "bullets": [],
            "games": normalized_games[:3],
        })

    # Practice / Q&A (prevents “missing word / Q&A” from disappearing)
    practice_items: List[Dict[str, Any]] = []
    for q in practice_qs[:8]:
        qt = _norm(q.get("type"))
        if qt == "fill_blank":
            practice_items.append({
                "type": "fill_blank",
                "q": _norm(q.get("q")),
                "answer": _norm(q.get("answer")),
                "explain": _norm(q.get("explain")),
            })
        elif qt == "short_answer":
            practice_items.append({
                "type": "short_answer",
                "q": _norm(q.get("q")),
                "answer": _norm(q.get("answer")),
                "explain": _norm(q.get("explain")),
            })
        elif qt == "true_false":
            practice_items.append({
                "type": "true_false",
                "q": _norm(q.get("q")),
                "answer": _norm(q.get("answer")),
                "explain": _norm(q.get("explain")),
            })

    if practice_items:
        sections.append({
            "title": "Practice",
            "icon": "fa-pen-to-square",
            "description": "Answer these to check your understanding.",
            "bullets": [],
            "practice": practice_items,
        })

    # Quiz payload (multi-question)
    quiz_items = []
    for q in mcqs[:6]:
        opts = [str(o) for o in (q.get("options") or [])][:4]
        ans = _norm(q.get("answer"))
        answer_index = -1
        for i, o in enumerate(opts):
            if _norm(o).lower() == ans.lower():
                answer_index = i
                break
        quiz_items.append({
            "q": _norm(q.get("q")),
            "options": opts,
            "answer_index": answer_index,
            "explain": _norm(q.get("explain")),
        })

    quiz_payload = {"items": quiz_items}

    title = f"{topic_hint}".strip() if topic_hint else "Interactive Lesson"
    subtitle = "An immersive, interactive lesson experience."
    return {
        "title": title,
        "subtitle": subtitle,
        "topic": topic_hint,
        "grade": grade_hint,
        "sections": sections[:10],
        "quiz": quiz_payload,
        "three_spec": three_spec,
    }

# ---------- MAIN ----------

def process_pdf_folder(pdf_folder, *, max_retries: int = 3, chunk_size: int = CHUNK_SIZE):
    print(f"\nProcessing: {pdf_folder}")

    images = load_images(pdf_folder)
    chunks = list(chunk_list(images, max(1, int(chunk_size))))

    extracted_chunks = []

    quota_exhausted = False

    for i, chunk in enumerate(chunks):
        print(f"  Chunk {i+1}/{len(chunks)}")

        # Stage 1: extract structured JSON per chunk (cheaper, more reliable than direct HTML).
        try:
            raw = safe_generate_chunk_data(chunk, max_retries=max_retries)
            data = _extract_json_object(raw)
            extracted_chunks.append(data)
        except QuotaExhaustedError as e:
            quota_exhausted = True
            print("[ERROR] Gemini quota exhausted. Stopping generation for this run.")
            break
        except Exception as e:
            print(f"[WARN] JSON extraction failed, falling back to HTML for this chunk. ({e})")
            try:
                raw_html = safe_generate_chunk_html(chunk, max_retries=max_retries)
                cleaned_html = clean_html(raw_html)
                extracted_chunks.append({"concepts": [], "vocabulary": [], "questions": [], "activities": [], "topic_hint": "", "grade_hint": "", "chunk_summary": "", "legacy_html": cleaned_html})
            except QuotaExhaustedError:
                quota_exhausted = True
                print("[ERROR] Gemini quota exhausted (during fallback). Stopping generation for this run.")
                break

        time.sleep(12)  # safety delay

    if quota_exhausted:
        return

    # If we have any legacy_html, stitch them; otherwise render from merged JSON.
    legacy_chunks = [c.get("legacy_html") for c in extracted_chunks if c.get("legacy_html")]
    if legacy_chunks:
        final_html = build_final_html([str(h) for h in legacy_chunks])
    else:
        lesson = build_lesson_json_from_chunks(extracted_chunks)
        final_html = render_lesson_html(lesson)

    output_path = OUTPUT_FOLDER / pdf_folder.relative_to(ROOT_FOLDER)
    output_path = output_path.with_suffix(".html")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(final_html, encoding="utf-8")

    print(f"[OK] Saved: {output_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", type=str, default="", help="Process only one rendered_pages subfolder, e.g. 'class 1/computer/01'")
    parser.add_argument("--chunk-size", type=int, default=CHUNK_SIZE)
    parser.add_argument("--max-retries", type=int, default=3)
    args = parser.parse_args()

    if args.only:
        folder = (ROOT_FOLDER / args.only).resolve()
        if not folder.exists():
            # Try relative as-is (Windows separators)
            folder = (ROOT_FOLDER / Path(args.only)).resolve()
        process_pdf_folder(
            folder,
            max_retries=max(1, int(args.max_retries)),
            chunk_size=max(1, int(args.chunk_size)),
        )
        return

    pdf_folders = [p for p in ROOT_FOLDER.rglob("*") if p.is_dir() and list(p.glob("*.png"))]
    for folder in pdf_folders:
        process_pdf_folder(
            folder,
            max_retries=max(1, int(args.max_retries)),
            chunk_size=max(1, int(args.chunk_size)),
        )
        time.sleep(15)  # extra buffer between PDFs


if __name__ == "__main__":
    main()