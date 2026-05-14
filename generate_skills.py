#!/usr/bin/env python3
"""
OTS Skills Academy — HTML Generator Pipeline
============================================
Reads a course-prompt PDF for each Skills Academy course and generates
13 self-contained HTML pages per course: index.html (course landing /
level selector) + level-01.html … level-12.html.

Folder structure:
    skills-academy/
      logic-building/
        prompt.pdf
      basic-design-theory/
        prompt.pdf

Output (default ./output/skills-academy/<course-slug>/):
    index.html
    level-01.html
    level-02.html
    ...
    level-12.html

Each call attaches the course PDF with prompt caching (ephemeral, 5-min TTL).
The TTL refreshes on every cache hit, so all 13 sequential calls reuse the
cached PDF after the first write — cache reads are ~10% of the input price.

Usage:
    python generate_skills.py                                   # process all courses
    python generate_skills.py --input ./skills-academy          # custom input
    python generate_skills.py --course logic-building           # one course only
    python generate_skills.py --course logic-building --level 5 # one page only
    python generate_skills.py --skip-index                      # skip course landing
    python generate_skills.py --dry-run                         # preview
    python generate_skills.py --force                           # ignore cache
"""

import os
import sys
import time
import base64
import argparse
import hashlib
import json
from pathlib import Path
from datetime import datetime

import anthropic

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ── Config ─────────────────────────────────────────────────────────────────────
DEFAULT_INPUT_DIR  = "./skills-academy"
DEFAULT_OUTPUT_DIR = "./output-skills-academy"
CLAUDE_MODEL       = "claude-sonnet-4-6"
MAX_TOKENS         = 64000
CACHE_FILE         = ".skills_pipeline_cache.json"
LOG_FILE           = "skills_pipeline.log"
RETRY_ATTEMPTS     = 3
RETRY_DELAY_SEC    = 5
COURSE_PDF_NAME    = "prompt.pdf"
TOTAL_LEVELS       = 12
# ──────────────────────────────────────────────────────────────────────────────


# ════════════════════════════════════════════════════════════════════════════════
#  UNIVERSAL SCRIPT RULES
#  Applies to every page (index + 12 levels). Borrowed from the classes pipeline
#  with adjustments for Skills Academy specifics.
# ════════════════════════════════════════════════════════════════════════════════
UNIVERSAL_SCRIPT_RULES = """

═══════════════════════════════════════════════════════════════════════════
UNIVERSAL TECHNICAL RULES — apply to every page in this course
═══════════════════════════════════════════════════════════════════════════

OUTPUT FORMAT:
- Return ONLY raw HTML. No markdown fences. No commentary. No explanation.
- Single self-contained HTML file. All CSS in <style>. All JS in <script> at end of <body>.
- The file must work when opened directly in a browser (file://) — no build step.

JAVASCRIPT SAFETY:
- Never return code that is truncated or incomplete. Every function must close.
  Every event listener must be fully registered. Every <script> tag must close.
- Validate every querySelector with a null check before use.
- Wrap CDN loads in try-catch with graceful fallbacks (CSS transitions if GSAP
  fails, static image if Three.js fails, etc.).
- No console.log left in production code.

THREE.JS — ONLY IF THE LEVEL'S "PAGE DESIGN DIRECTION" EXPLICITLY CALLS FOR IT:
- Use only when the level spec mentions 3D, spatial, network/node, or similar.
- Load from: https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js
- NEVER read offsetWidth at DOMContentLoaded to size the canvas — the element
  may not be laid out yet. Always use ResizeObserver:

  const observer = new ResizeObserver(entries => {
    const w = entries[0].contentRect.width;
    const h = Math.min(500, w * 0.56);
    renderer.setSize(w, h);
    canvas.style.width = w + 'px';
    canvas.style.height = h + 'px';
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  });
  observer.observe(wrap);

- The Three.js scene must fill the FULL width of its container — never a corner.

DIAGRAMS:
- For flowcharts, decision trees, state diagrams, sequence diagrams: use
  Mermaid.js (https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js).
  Initialize with mermaid.initialize({ startOnLoad: true, theme: 'dark' or
  'default' as suits the level palette }).
- For everything else (icons, illustrations, decorative shapes): inline SVG.

ANIMATIONS:
- Use GSAP for entrance and interaction animations:
  https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js
  https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js
- Use canvas-confetti for level-complete celebrations:
  https://cdn.jsdelivr.net/npm/canvas-confetti@1.9.2/dist/confetti.browser.min.js
- Animation durations: 0.3s–0.8s. No longer.
- Respect prefers-reduced-motion — disable non-essential animation when set.

ACCESSIBILITY:
- All interactive elements: minimum 48×48px touch target.
- ARIA labels on icon-only buttons.
- Minimum contrast ratio 4.5:1 (this overrides aesthetic choices when in conflict).
- Full keyboard navigation. Visible focus states.

PERFORMANCE:
- Page weight target: under 600 KB (no heavy frameworks beyond the CDNs above).
- font-display: swap on every Google Font.
- IntersectionObserver to defer animation until elements are visible.
- loading="lazy" on below-fold images.

MOBILE-FIRST:
- Breakpoints: 320px / 768px / 1200px.
- No horizontal scroll at any breakpoint.
- All drag-drop activities must work with touch events, not just mouse.

═══════════════════════════════════════════════════════════════════════════
SKILLS ACADEMY — CROSS-PAGE CONTRACT (CRITICAL)
═══════════════════════════════════════════════════════════════════════════

These rules ensure the 13 pages of this course work together as ONE coherent
product. Every page MUST honor these conventions exactly.

FILE NAMING (hardcoded — do not deviate):
- Course landing page:  index.html
- Level pages:          level-01.html, level-02.html, level-03.html,
                        level-04.html, level-05.html, level-06.html,
                        level-07.html, level-08.html, level-09.html,
                        level-10.html, level-11.html, level-12.html
- All pages live in the same directory (flat — no subfolders for levels).
- Use two-digit zero-padded numbering: level-01.html NOT level-1.html.

NAVIGATION (hardcoded paths):
- Every level page has a "Previous" link → level-{N-1}.html
  (Level 1's Previous goes to index.html)
- Every level page has a "Next" link → level-{N+1}.html
  (Level 12's Next goes to index.html with a completion query param)
- Every page has a "Home" / course-title link → index.html
- Breadcrumb on level pages: "OTS Skills Academy → {Course Name} → Level {N}"

LOCALSTORAGE CONTRACT (must match exactly across all 13 pages):
- Use the course slug provided in the per-page prompt as <COURSE_SLUG>.
- Required keys:
    ots_skills_<COURSE_SLUG>_xp_total            (integer, total XP earned)
    ots_skills_<COURSE_SLUG>_level_<N>_complete  (boolean "true"/"false")
    ots_skills_<COURSE_SLUG>_level_<N>_xp        (integer, XP earned at this level)
    ots_skills_<COURSE_SLUG>_portfolio_level_<N> (JSON string — level's saved artifact)
    ots_skills_<COURSE_SLUG>_started_at          (ISO date of first visit)
- The XP counter in the sticky top nav reads ots_skills_<COURSE_SLUG>_xp_total
  on every page load.
- On level completion, the page MUST:
    1. Set ots_skills_<COURSE_SLUG>_level_<N>_complete = "true"
    2. Set ots_skills_<COURSE_SLUG>_level_<N>_xp = <level's XP reward>
    3. Recompute and write ots_skills_<COURSE_SLUG>_xp_total from all completed levels
    4. Trigger the confetti burst + badge reveal described in the PDF
- All localStorage writes wrapped in try-catch (private browsing may block).

STICKY TOP NAVIGATION (every page):
- OTS Skills Academy logo/wordmark on the left → index.html
- Course title in the center
- XP counter on the right: "⚡ {total_xp} XP" — live from localStorage
- Must remain visible on scroll. Background uses the level's identity color
  at low opacity, or a course-neutral dark on index.html.

PROGRESS BAR:
- index.html shows a course-wide progress bar (count of completed levels / 12).
- Each level page shows a thin progress bar under the sticky nav reflecting
  level N of 12 (just position, not completion).

URDU LABEL TOGGLE (Logic Building only — see PDF):
- If the PDF specifies Urdu labels, add a toggle in the top nav.
- Toggle state persisted in localStorage as ots_skills_<COURSE_SLUG>_urdu_on.

LEVEL IDENTITY COLOR — CRITICAL:
- Each level has a specific color from the PDF's Quick Reference table.
- That color is the page's accent. The page's aesthetic must match the
  "Page Design Direction" for THAT level — do NOT impose a generic dark theme
  on every level. Level 4 of Basic Design Theory (cream #F8F4EF) is supposed
  to feel SPACIOUS AND LIGHT. Level 5 (pure black #111111) is supposed to feel
  HIGH-CONTRAST. Honor the level's stated aesthetic.
"""


# ════════════════════════════════════════════════════════════════════════════════
#  PROMPT BUILDERS
# ════════════════════════════════════════════════════════════════════════════════

def build_level_prompt(course_slug: str, course_name: str, level_num: int) -> str:
    """Prompt that tells Claude to build ONE specific level page from the PDF."""
    return f"""You are building Level {level_num} of the "{course_name}" course for the OTS Skills Academy EdTech platform (edu.offtheschool.io).

The PDF attached contains the complete design specification for ALL 12 levels of this course. You must:

1. READ THE GLOBAL DESIGN SYSTEM section (typography, color philosophy, animation principles, layout rules) and apply it to this page.

2. READ THE LEVEL ARCHITECTURE section and produce a page with EVERY mandatory section listed there, in the exact order specified. Do not skip sections. Do not invent new ones.

3. FOCUS ON LEVEL {level_num} SPECIFICALLY. The PDF contains specs for all 12 levels — extract the spec for Level {level_num} only:
   - Level name and tagline
   - Difficulty badge
   - XP reward (from the Quick Reference table)
   - Identity color (from the Quick Reference table — this is the page's accent color)
   - Content & interactions described for THIS level
   - Page Design Direction described for THIS level (this defines the visual style — follow it literally, do not impose a generic dark theme)

4. APPLY THE PAGE DESIGN DIRECTION LITERALLY. If the PDF says "cream/off-white, generous margins, minimalist", build a light spacious page — not a dark one. If it says "pure black background with yellow accents", build that. Each level's aesthetic is a teaching tool in itself.

5. BUILD ALL INTERACTIVE ACTIVITIES described for this level — drag-and-drop, builders, validators, simulators, etc. They must actually work, not be placeholders.

6. CROSS-PAGE CONTRACT:
   - Course slug for localStorage keys: "{course_slug}"
   - Previous link: {"index.html" if level_num == 1 else f"level-{level_num - 1:02d}.html"}
   - Next link: {"index.html?completed=1" if level_num == TOTAL_LEVELS else f"level-{level_num + 1:02d}.html"}
   - Home link: index.html
   - Output filename will be: level-{level_num:02d}.html

7. INCLUDE THE OTS BRANDING in the sticky top nav: "OTS Skills Academy" wordmark + course name + XP counter.

8. ADD HTML COMMENT AT TOP: <!-- COURSE: {course_name} | LEVEL: {level_num} | OTS Skills Academy | v1.0 -->

Return ONLY the raw HTML for level-{level_num:02d}.html. No markdown fences. No explanation. No commentary.
"""


def build_index_prompt(course_slug: str, course_name: str) -> str:
    """Prompt for the course landing / level selector page."""
    return f"""You are building the course landing page (index.html) for the "{course_name}" course on the OTS Skills Academy EdTech platform (edu.offtheschool.io).

The PDF attached contains the complete design specification for the course. You must:

1. CREATE A COURSE LANDING PAGE that serves as both:
   (a) An introduction to the course — its philosophy, the gaps it solves, the taglines and identity from the PDF.
   (b) A LEVEL SELECTOR with all 12 levels displayed as interactive cards.

2. EACH LEVEL CARD must show:
   - Level number (01–12)
   - Level name (from the PDF)
   - Difficulty badge (Starter / Explorer / Challenger / Advanced / MASTER)
   - XP reward (from the Quick Reference table)
   - The level's identity color (from the Quick Reference table) as the card's accent
   - The level's tagline (one-line italic quote from the PDF) as a hover-reveal or subtitle
   - A "completed" checkmark/badge if localStorage shows that level as complete
   - A click action that navigates to level-{{NN}}.html (e.g., level-03.html)

3. APPLY THE COURSE'S GLOBAL DESIGN SYSTEM (typography, color philosophy, animation principles) from the PDF. The landing page is the user's first impression — make it feel premium and on-brand.

4. INCLUDE A COURSE-WIDE PROGRESS BAR:
   - Reads ots_skills_{course_slug}_level_<N>_complete for N in 1..12 from localStorage
   - Shows "X / 12 levels complete" + total XP
   - On completion of all 12 levels (or when ?completed=1 in URL), show a celebration overlay with confetti and a "View Certificate" button (link to "#" — placeholder).

5. INCLUDE THE FOUR GAPS SECTION from the PDF (the four problems the course solves), the course tagline, and any other meaningful framing content from the PDF's Course Overview.

6. STICKY TOP NAV: "OTS Skills Academy" wordmark on the left, course title centered, XP counter on the right. Same convention as level pages.

7. ADD HTML COMMENT AT TOP: <!-- COURSE: {course_name} | INDEX | OTS Skills Academy | v1.0 -->

8. Course slug for localStorage: "{course_slug}"
9. Output filename: index.html

Return ONLY the raw HTML. No markdown fences. No explanation. No commentary.
"""


# ════════════════════════════════════════════════════════════════════════════════
#  UTILITIES
# ════════════════════════════════════════════════════════════════════════════════

def get_api_key() -> str:
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        key = input("Enter your Anthropic API key: ").strip()
    if not key:
        sys.exit("No API key provided. Set ANTHROPIC_API_KEY in .env")
    return key


def load_cache(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_cache(path: Path, cache: dict):
    path.write_text(json.dumps(cache, indent=2), encoding="utf-8")


def file_hash(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def log(msg: str, log_path: Path = None):
    line = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line)
    if log_path:
        try:
            with open(log_path, "a", encoding="utf-8", errors="replace") as f:
                f.write(line + "\n")
        except Exception:
            pass


def slugify(name: str) -> str:
    """'Logic Building' → 'logic-building'. Used for localStorage keys."""
    s = name.lower().strip()
    out = []
    for ch in s:
        if ch.isalnum():
            out.append(ch)
        elif ch in (" ", "_", "-"):
            out.append("-")
    slug = "".join(out)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-")


def humanize_course_name(folder_name: str) -> str:
    """'logic-building' → 'Logic Building'."""
    return " ".join(w.capitalize() for w in folder_name.replace("_", "-").split("-") if w)


# ════════════════════════════════════════════════════════════════════════════════
#  COURSE DISCOVERY
# ════════════════════════════════════════════════════════════════════════════════

def discover_courses(input_dir: Path, course_filter: str = None) -> list:
    """Find each subdirectory of input_dir that contains a prompt.pdf."""
    courses = []
    if not input_dir.exists():
        return courses

    for course_dir in sorted(input_dir.iterdir()):
        if not course_dir.is_dir():
            continue
        if course_filter and course_filter.lower() not in course_dir.name.lower():
            continue

        pdf_path = course_dir / COURSE_PDF_NAME
        if not pdf_path.exists():
            # Allow any single PDF in the folder as a fallback
            pdfs = list(course_dir.glob("*.pdf"))
            if len(pdfs) == 1:
                pdf_path = pdfs[0]
            else:
                continue

        slug = slugify(course_dir.name)
        courses.append({
            "folder": course_dir.name,
            "slug":   slug,
            "name":   humanize_course_name(course_dir.name),
            "pdf":    pdf_path,
        })
    return courses


def build_output_path(course: dict, output_dir: Path, page_name: str) -> Path:
    out_dir = output_dir / course["slug"]
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / page_name


# ════════════════════════════════════════════════════════════════════════════════
#  CORE: PDF + LEVEL → HTML via Claude (with prompt caching)
# ════════════════════════════════════════════════════════════════════════════════

def generate_html(client: anthropic.Anthropic,
                  pdf_b64: str,
                  prompt_text: str) -> tuple:
    """
    Send one API call with the cached PDF + per-page instruction.
    Returns: (html, input_tokens, output_tokens, cache_read_tokens,
              cache_creation_tokens, cost_usd)
    """
    last_err = None
    for attempt in range(1, RETRY_ATTEMPTS + 1):
        try:
            html_chunks = []

            with client.messages.stream(
                model=CLAUDE_MODEL,
                max_tokens=MAX_TOKENS,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "document",
                            "source": {
                                "type":       "base64",
                                "media_type": "application/pdf",
                                "data":       pdf_b64,
                            },
                            "cache_control": {"type": "ephemeral"},
                        },
                        {
                            "type": "text",
                            "text": prompt_text,
                        },
                    ],
                }],
            ) as stream:
                for text in stream.text_stream:
                    html_chunks.append(text)

                final_msg = stream.get_final_message()
                usage = final_msg.usage
                in_tok    = getattr(usage, "input_tokens", 0) or 0
                out_tok   = getattr(usage, "output_tokens", 0) or 0
                cache_rd  = getattr(usage, "cache_read_input_tokens", 0) or 0
                cache_wr  = getattr(usage, "cache_creation_input_tokens", 0) or 0

            html = "".join(html_chunks).strip()
            if html.startswith("```"):
                lines = html.split("\n")
                html = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

            # Pricing (Claude Sonnet 4.6 standard rates):
            #   input base:        $3.00 / 1M
            #   output:           $15.00 / 1M
            #   cache write (5m): $3.75 / 1M  (1.25x base)
            #   cache read:       $0.30 / 1M  (0.10x base)
            cost = (
                (in_tok    / 1_000_000) * 3.00  +
                (out_tok   / 1_000_000) * 15.00 +
                (cache_wr  / 1_000_000) * 3.75  +
                (cache_rd  / 1_000_000) * 0.30
            )
            return html, in_tok, out_tok, cache_rd, cache_wr, cost

        except Exception as e:
            last_err = e
            if attempt < RETRY_ATTEMPTS:
                time.sleep(RETRY_DELAY_SEC)

    raise RuntimeError(f"Claude API failed after {RETRY_ATTEMPTS} attempts: {last_err}")


def process_page(client, course, page_kind, output_dir, cache, cache_path,
                 log_path, pdf_b64, pdf_hash, dry_run=False) -> bool:
    """
    page_kind is either "index" or an int 1..12.
    """
    if page_kind == "index":
        page_name = "index.html"
        prompt_text = build_index_prompt(course["slug"], course["name"]) + UNIVERSAL_SCRIPT_RULES
        label = f"{course['name']} / index"
    else:
        level_num = int(page_kind)
        page_name = f"level-{level_num:02d}.html"
        prompt_text = build_level_prompt(course["slug"], course["name"], level_num) + UNIVERSAL_SCRIPT_RULES
        label = f"{course['name']} / Level {level_num}"

    output_file = build_output_path(course, output_dir, page_name)
    cache_key   = f"{course['slug']}::{page_name}"

    if dry_run:
        log(f"   [DRY RUN] → {output_file}", log_path)
        return True

    try:
        log(f"   🤖 Sending to Claude ({CLAUDE_MODEL}) — {label}…", log_path)
        html, in_tok, out_tok, cache_rd, cache_wr, cost = generate_html(
            client, pdf_b64, prompt_text
        )

        output_file.write_text(html, encoding="utf-8")
        log(f"   ✅ Saved → {output_file}", log_path)
        log(f"   📊 in:{in_tok:,} out:{out_tok:,} "
            f"cache_read:{cache_rd:,} cache_write:{cache_wr:,} "
            f"| ${cost:.4f}", log_path)

        # Cache key encodes both the source PDF hash AND the page identity.
        # If the PDF changes, all 13 pages regenerate.
        cache[cache_key] = pdf_hash
        save_cache(cache_path, cache)
        return True

    except Exception as e:
        log(f"   ❌ Failed: {e}", log_path)
        return False


# ════════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ════════════════════════════════════════════════════════════════════════════════

def main():
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    parser = argparse.ArgumentParser(
        description="Generate OTS Skills Academy course pages from prompt PDFs"
    )
    parser.add_argument("--input",       default=DEFAULT_INPUT_DIR,
                        help="Root folder containing course subfolders")
    parser.add_argument("--output",      default=DEFAULT_OUTPUT_DIR,
                        help="Output folder")
    parser.add_argument("--course",      default=None,
                        help="Process only this course (substring match on folder name)")
    parser.add_argument("--level",       type=int, default=None,
                        help="Process only this level (1-12). Implies one course.")
    parser.add_argument("--skip-index",  action="store_true",
                        help="Skip generating the course index.html landing page")
    parser.add_argument("--only-index",  action="store_true",
                        help="Only generate the course index.html; skip all levels")
    parser.add_argument("--dry-run",     action="store_true")
    parser.add_argument("--force",       action="store_true",
                        help="Ignore cache, regenerate everything")
    args = parser.parse_args()

    input_dir  = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path   = output_dir / LOG_FILE
    cache_path = output_dir / CACHE_FILE

    log("=" * 64, log_path)
    log(f"  OTS SKILLS ACADEMY PIPELINE  —  {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        log_path)
    log("=" * 64, log_path)

    client = anthropic.Anthropic(api_key=get_api_key())
    cache  = {} if args.force else load_cache(cache_path)

    courses = discover_courses(input_dir, args.course)
    if not courses:
        log(f"No courses found in {input_dir}. Expected structure:", log_path)
        log("  skills-academy/<course-name>/prompt.pdf", log_path)
        return

    log(f"📚 Found {len(courses)} course(s)", log_path)
    for c in courses:
        log(f"   • {c['name']}  ({c['folder']} → slug: {c['slug']})", log_path)
    log("", log_path)

    if args.level is not None:
        if args.level < 1 or args.level > TOTAL_LEVELS:
            sys.exit(f"--level must be between 1 and {TOTAL_LEVELS}")

    grand_success = grand_fail = grand_skip = 0

    for course in courses:
        log("─" * 64, log_path)
        log(f"📖 COURSE: {course['name']}", log_path)
        log(f"   PDF:  {course['pdf']}", log_path)
        log(f"   Out:  {output_dir / course['slug']}", log_path)
        log("─" * 64, log_path)

        # Read PDF once per course (cached server-side across the 13 calls)
        pdf_b64  = base64.b64encode(course["pdf"].read_bytes()).decode()
        pdf_hash = file_hash(course["pdf"])

        # Decide which pages to generate
        if args.level is not None:
            pages = [args.level]
        elif args.only_index:
            pages = ["index"]
        elif args.skip_index:
            pages = list(range(1, TOTAL_LEVELS + 1))
        else:
            pages = ["index"] + list(range(1, TOTAL_LEVELS + 1))

        for i, page_kind in enumerate(pages, 1):
            page_name = "index.html" if page_kind == "index" else f"level-{int(page_kind):02d}.html"
            cache_key = f"{course['slug']}::{page_name}"
            output_file = build_output_path(course, output_dir, page_name)

            log(f"[{i}/{len(pages)}] {course['slug']}/{page_name}", log_path)

            if (not args.force
                    and cache_key in cache
                    and cache[cache_key] == pdf_hash
                    and output_file.exists()):
                log("   ⏭  Already up-to-date, skipping.", log_path)
                grand_skip += 1
                continue

            ok = process_page(
                client, course, page_kind, output_dir, cache, cache_path,
                log_path, pdf_b64, pdf_hash, args.dry_run
            )
            if ok:
                grand_success += 1
            else:
                grand_fail += 1

            # Small pause so the 5-minute TTL clearly covers all 13 calls,
            # and so we don't slam the API.
            if i < len(pages):
                time.sleep(1)

    log("", log_path)
    log("=" * 64, log_path)
    log(f"  DONE  ✅ {grand_success} generated  ⏭ {grand_skip} skipped  ❌ {grand_fail} failed",
        log_path)
    log(f"  Output → {output_dir.resolve()}", log_path)
    log("=" * 64, log_path)


if __name__ == "__main__":
    main()
