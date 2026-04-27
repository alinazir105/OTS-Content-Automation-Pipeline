#!/usr/bin/env python3
"""
Educational HTML Generator Pipeline
=====================================
Reads PDFs from a classes/ folder tree and generates interactive HTML
lesson pages by sending each PDF directly to Claude with the appropriate
class-level design prompt.

Folder structure:
    classes/
      class 1/
        computer/
          lesson_1.pdf
      class 2/
        math/
          unit_1.pdf

Each PDF → one self-contained HTML file under output/ (same tree).

Usage:
    python generate.py                           # process all PDFs
    python generate.py --input ./classes         # custom input folder
    python generate.py --file path/to/pdf        # single PDF
    python generate.py --class-filter "class 1"  # only one class
    python generate.py --dry-run                 # preview without generating
    python generate.py --force                   # regenerate even if cached
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
DEFAULT_INPUT_DIR  = "./classes"
DEFAULT_OUTPUT_DIR = "./output"
CLAUDE_MODEL       = "claude-sonnet-4-6"
MAX_TOKENS         = 64000
CACHE_FILE         = ".pipeline_cache.json"
LOG_FILE           = "pipeline.log"
RETRY_ATTEMPTS     = 3
RETRY_DELAY_SEC    = 5
# ──────────────────────────────────────────────────────────────────────────────


# ════════════════════════════════════════════════════════════════════════════════
#  CLASS DESIGN PROMPTS
#  Sourced from: EdTech_Cursor_Prompts.pdf
#  Each prompt tells Claude exactly how to design the HTML for that class level.
# ════════════════════════════════════════════════════════════════════════════════

CLASS_PROMPTS = {

    1: """You are building a lesson HTML page for Class 1 (ages 5–6) for an EdTech platform called Digital School. This is the lowest difficulty level. Every design and interactivity decision must be optimized for a young child who cannot read well yet.

DESIGN SYSTEM:
- Font: 'Bubblegum Sans' (Google Fonts) for headings, 'Nunito' for body text, minimum 20px body size, minimum 36px headings.
- Color palette: Bright primaries — Red #FF6B6B, Yellow #FFD93D, Blue #6BCB77, White #FFFFFF. Never use dark or muted colors.
- Rounded corners everywhere (border-radius: 24px minimum).
- Thick colored borders (4px+) on all interactive cards and buttons.
- Background: Soft pastel gradient or animated sky/grass SVG background.

LAYOUT:
- Single column layout only. No sidebars.
- Each lesson section = one large "fun card" taking full width, with a big illustration at the top.
- Cards must be spaced 40px apart. Breathing room is critical.
- Section icons: Use emoji or inline SVG for section icons (animals, stars, pencils etc.).

ANIMATIONS (GSAP Required):
- Load GSAP from: https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js
- Load ScrollTrigger from: https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js
- On page load: cards bounce in using GSAP stagger from 0.1s.
- Each card entrance: GSAP ScrollTrigger fade-up + scale from 0.85 to 1.
- Correct answer: GSAP confetti burst using canvas-confetti CDN.
- Wrong answer: GSAP shake animation (x: [-10,10,-10,10,0]).
- Never use animation durations longer than 0.6s.

SMOOTH SCROLLING (Lenis Required):
- Load Lenis from: https://cdn.jsdelivr.net/npm/@studio-freight/lenis@1.0.29/dist/lenis.min.js
- Initialize with lerp: 0.08
- Sync with GSAP: gsap.ticker.add(time => lenis.raf(time * 1000))
- Disable on mobile if navigator.deviceMemory < 2

THREE.JS (Required):
- Load from: https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js
- Add one simple rotating 3D object relevant to the lesson topic.
- WebGL canvas max 300x300px on mobile.
- Always include a fallback static illustration if WebGL unsupported.
- OrbitControls disabled for Class 1.

INTERACTIVITY:
- Drag-and-drop matching activity (drag word to picture).
- Tap-to-reveal: tap any image to see a fun animation.
- A simple quiz at lesson end: each question shows a picture and 2-3 large image-based answer buttons.
- Correct answers: confetti. Wrong answers: friendly shake + try again.
- All quizzes must be answerable without reading.

PERFORMANCE:
- Lazy-load images with loading="lazy".
- Defer all scripts.
- Use IntersectionObserver for animating only visible elements.

MOBILE:
- Touch targets minimum 56px height.
- No horizontal scroll allowed.

SELF-HEALING:
- All CDN imports must have try-catch fallback.
- If GSAP fails, fall back to CSS transitions.
- If Three.js fails, show a static illustrated placeholder.
- Validate all querySelector calls with null checks.

OUTPUT:
- Single self-contained HTML file. All CSS in <style>. All JS in <script> at bottom of body.
- Add comment at top: <!-- CLASS: 1 | SUBJECT: {subject} | VERSION: 1.0 -->""",

    2: """You are building a lesson HTML page for Class 2 (ages 6–7) for Digital School, an EdTech platform. Children at this level are beginning to read short sentences and can handle simple structured activities.

DESIGN SYSTEM:
- Fonts: 'Nunito' (headings 28px+, body 18px+). Avoid all-caps text blocks.
- Color palette: Warm and inviting — Orange #FF9F43, Teal #1DD1A1, Purple #A29BFE, off-white #FAFAFA.
- Cards with subtle box-shadow (0 8px 32px rgba(0,0,0,0.08)).
- Rounded corners (border-radius: 20px).
- Each section has a colored left-border accent (4px solid [section color]).

LAYOUT:
- Mostly single-column with optional 2-column layout for comparison activities.
- Section structure: Icon + Title → Illustration → Short explanation text → Mini activity.
- Sticky progress bar at the top showing lesson completion %.

ANIMATIONS (GSAP Required):
- Load GSAP from: https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js
- Load ScrollTrigger from: https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js
- Hero section: Title words animate in one-by-one using manual span splitting.
- Section cards: ScrollTrigger fade-up from bottom (y: 40 → 0, opacity 0 → 1).
- Activity correct: Scale-up + color burst.
- Activity wrong: Gentle wobble (rotation: [-5,5,-5,5,0]).

SMOOTH SCROLLING (Lenis Required):
- Load Lenis from: https://cdn.jsdelivr.net/npm/@studio-freight/lenis@1.0.29/dist/lenis.min.js
- lerp: 0.1. Sync with GSAP ticker.

THREE.JS:
- Load from: https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js
- Add one 3D scene per major concept.
- Allow OrbitControls on desktop only.
- Mobile: static render after first frame.

INTERACTIVITY:
- Fill-in-the-blank: click on a blank, word-bank appears.
- Sorting activity: drag items into two labeled buckets.
- End quiz: 5-6 questions with text + image options (2 choices per question).
- "Read Aloud" button using Web Speech API.

SELF-HEALING:
- Speech synthesis in try-catch. Fallback to text tooltip.
- All GSAP animations check prefers-reduced-motion.

OUTPUT: Single self-contained HTML file. Comment: <!-- CLASS: 2 | SUBJECT: {subject} | VERSION: 1.0 -->""",

    3: """You are building a lesson HTML page for Class 3 (ages 7–8) for Digital School. Students can read paragraphs and follow multi-step instructions.

DESIGN SYSTEM:
- Fonts: 'Poppins' headings (bold, 26px+), 'Inter' body (18px).
- Color palette: Energetic — Sunshine #F9CA24, Sky #48DBFB, Coral #FF6B6B, Light Gray #F8F9FA.
- Cards: white background, 12px radius, soft shadow.
- Section headers: colored band (full-width strip) with white text.
- CSS Grid for activity layouts.

LAYOUT:
- Introduction → Concept → Visual Explanation → Guided Practice → Activity → Quiz.
- Sidebar table-of-contents on desktop (sticky, highlights active section via IntersectionObserver).
- Progress tracker (breadcrumb style) at top.

ANIMATIONS (GSAP Required):
- Load GSAP from: https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js
- Load ScrollTrigger from: https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js
- Hero: SVG path drawing animation (stroke-dashoffset trick).
- ScrollTrigger pin + scrub for concept reveals.
- Parallax on section backgrounds (y: -30 to +30).
- Number counters: GSAP countTo on statistics.

SMOOTH SCROLLING (Lenis):
- Load from: https://cdn.jsdelivr.net/npm/@studio-freight/lenis@1.0.29/dist/lenis.min.js
- lerp: 0.1, duration: 1.2

THREE.JS:
- Load from: https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js
- Geometry scene for math/science concepts.
- Click-to-rotate via OrbitControls.
- Fallback: 2D SVG diagram.

INTERACTIVITY:
- Drag-and-drop labeling (drag labels onto diagram).
- Timeline activity: arrange events in order.
- Quiz: 8 questions, mix of MCQ and true/false.
- Score card with animated progress circle.

OUTPUT: Single HTML. Comment: <!-- CLASS: 3 | SUBJECT: {subject} | VERSION: 1.0 -->""",

    4: """You are building a lesson HTML page for Class 4 (ages 8–9) for Digital School. Students handle multi-step problems and appreciate structured content with clear visual hierarchy.

DESIGN SYSTEM:
- Fonts: 'Poppins' (headings), 'Inter' (body 17px). Line height 1.7.
- Palette: Forest Green #6AB04C, Deep Navy #2C3E50, Amber #F0932B, White.
- Alternating white and light-green section backgrounds.
- Highlight boxes (colored bg with left border) for key definitions.
- Code-style boxes (monospace, dark bg) for step-by-step processes.

LAYOUT:
- Desktop: main content (65%) + concept sidebar (35%).
- Mobile: single column, sidebar collapses to accordion.
- Sticky header with lesson title + progress dots.

ANIMATIONS (GSAP Required):
- Load GSAP from: https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js
- Load ScrollTrigger from: https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js
- Each paragraph fades in with stagger on scroll.
- Sidebar slides in from right on desktop.
- Formula underline draw effect on key formulas.
- Math step reveal: "Show Step" buttons with GSAP timeline.

SMOOTH SCROLLING (Lenis):
- Load from: https://cdn.jsdelivr.net/npm/@studio-freight/lenis@1.0.29/dist/lenis.min.js
- lerp: 0.12

THREE.JS:
- Load from: https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js
- One 3D scene per lesson for a major concept.
- ScrollTrigger controls 3D rotation.
- Mobile: reduce geometry complexity.

INTERACTIVITY:
- Guided worked example with "Next Step" button.
- Cloze passage fill-in-the-blank.
- Diagram labeling with snap-to-target drag and drop.
- 8-10 question quiz.

OUTPUT: Single HTML. Comment: <!-- CLASS: 4 | SUBJECT: {subject} | VERSION: 1.0 -->""",

    5: """You are building a lesson HTML page for Class 5 (ages 9–10) for Digital School. Students engage with abstract ideas, data interpretation, and multi-step reasoning.

DESIGN SYSTEM:
- Fonts: 'Poppins' (headings), 'Inter' (body 16px, clamp(15px,2.5vw,18px)).
- Palette: Teal #22A6B3, Indigo #4834D4, Warm White #FEFEFE, Slate #636E72.
- "Discovery zones": sections with dashed border and magnifying glass icon.
- Data tables: alternating row colors, sortable columns.
- Formula callout: dark background with monospace font.

LAYOUT:
- Introduction → Background → Core Concept → Worked Examples → Practice → Challenge → Quiz.
- Sticky TOC on desktop (IntersectionObserver scrollspy).
- Collapsible hint panels.

ANIMATIONS (GSAP Required):
- Load GSAP from: https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js
- Load ScrollTrigger from: https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js
- Headline: character-by-character entrance.
- SVG bar/line charts animated on scroll.
- Flip card reveal for "Did You Know?" boxes (rotationY).

SMOOTH SCROLLING (Lenis):
- Load from: https://cdn.jsdelivr.net/npm/@studio-freight/lenis@1.0.29/dist/lenis.min.js
- lerp: 0.1, wheelMultiplier: 0.8

THREE.JS:
- Load from: https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js
- 3D data visualization or concept model.
- Click a 3D object to show a modal with details.
- Mobile: canvas pauses when off-screen.

INTERACTIVITY:
- Drag-and-drop classification (2-3 categories).
- Interactive data table (click row to expand).
- 10-question quiz: MCQ + numerical answer.

OUTPUT: Single HTML. Comment: <!-- CLASS: 5 | SUBJECT: {subject} | VERSION: 1.0 -->""",

    6: """You are building a lesson HTML page for Class 6 (ages 10–11) for Digital School. Design must feel mature but approachable, with deep interactivity that rewards exploration.

DESIGN SYSTEM:
- Fonts: 'Poppins' (display 700), 'Inter' (body 16px), 'JetBrains Mono' (code/math).
- Palette: Deep Violet #8C7AE6, Cyan #00B5CC, Charcoal #2D3436, White, Light Gray #F5F6FA.
- Glassmorphism cards: background rgba(255,255,255,0.7), backdrop-filter blur(12px).
- Dark mode toggle (CSS custom properties swap).
- Animated SVG wave section dividers.

LAYOUT:
- Sticky chapter navigation (left sidebar desktop, bottom sheet mobile).
- "Concept Map" section: SVG nodes + edges, click to expand.
- Collapsible deeper-reading panels.

ANIMATIONS (GSAP Required):
- Load GSAP from: https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js
- Load ScrollTrigger from: https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js
- GSAP curtain wipe on initial load.
- Parallax hero with layered SVG elements.
- Concept map: animated SVG path drawing between nodes.
- Micro-interactions: hover states with GSAP quickTo.

SMOOTH SCROLLING (Lenis):
- Load from: https://cdn.jsdelivr.net/npm/@studio-freight/lenis@1.0.29/dist/lenis.min.js
- lerp: 0.1, smoothWheel: true

THREE.JS:
- Load from: https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js
- Immersive 3D model as lesson centerpiece.
- Raycasting: click objects to open info panel.
- Responsive canvas: full-width on desktop.

INTERACTIVITY:
- Interactive concept map (click nodes, draw connections).
- Cause-and-effect chain builder.
- 12-question quiz: MCQ + matching + sequence-ordering.
- Timed challenge mode toggle.

OUTPUT: Single HTML. Comment: <!-- CLASS: 6 | SUBJECT: {subject} | VERSION: 1.0 -->""",

    7: """You are building a lesson HTML page for Class 7 (ages 11–12) for Digital School. Design should feel like a professional, immersive research environment.

DESIGN SYSTEM:
- Fonts: 'Space Grotesk' (display), 'Inter' (body 16px), 'Fira Code' (code/math). Load from Google Fonts.
- Palette: Burnt Orange #E17055, Dark Slate #2D3436, Electric Blue #0984E3, Cream #FFEAA7.
- Bento grid layout for key concept sections.
- Colored sticky-note style callouts (info, warning, formula, example).
- Horizontal scrollable timeline component.

LAYOUT:
- Hook/Problem → Background Theory → Core Concept → Exploration → Application → Synthesis → Assessment.
- Bento grid for "Key Facts".
- Floating "Expert Tips" panel on hover of key terms.

ANIMATIONS (GSAP Required):
- Load GSAP from: https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js
- Load ScrollTrigger from: https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js
- Bento grid: stagger entrance with scale + blur removal.
- Timeline: GSAP horizontal scroll section (pinned, scrub).
- Loading screen before content appears.

SMOOTH SCROLLING (Lenis):
- Load from: https://cdn.jsdelivr.net/npm/@studio-freight/lenis@1.0.29/dist/lenis.min.js
- lerp: 0.08

THREE.JS:
- Load from: https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js
- Full-screen WebGL hero scene.
- Particle system background (THREE.Points).
- Mobile: particles disabled, lower poly models.

INTERACTIVITY:
- Hypothesis builder: choose variables → prediction → mini simulation.
- Evidence sorting: drag cards into "supports"/"contradicts".
- 15-question assessment: MCQ, true/false, short answer.

OUTPUT: Single HTML. Comment: <!-- CLASS: 7 | SUBJECT: {subject} | VERSION: 1.0 -->""",

    8: """You are building a lesson HTML page for Class 8 (ages 12–13) for Digital School. Students engage with abstract models, interpret data, and apply equations.

DESIGN SYSTEM:
- Fonts: 'DM Sans' (body 16px), 'Playfair Display' (section titles), 'JetBrains Mono' (equations). Load from Google Fonts.
- Palette: Emerald #00B894, Midnight #2D3436, Coral #FF7675, Ivory #FFF9F0.
- Magazine-style layout: large pullquotes, full-bleed sections, typographic hierarchy.
- Equation blocks: rendered in monospace with KaTeX-style formatting.
- Data cards: chart + caption arranged in CSS Grid.

LAYOUT:
- Long-form reading with floating chapter navigator.
- Data Dashboard section: 2-3 charts in responsive grid.
- "Model It" interactive section.

ANIMATIONS (GSAP Required):
- Load GSAP from: https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js
- Load ScrollTrigger from: https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js
- Magazine entrances: images slide in + text animates in.
- Pullquotes: scale entrance + background color morph.
- Scrub-based parallax on full-bleed images.

SMOOTH SCROLLING (Lenis):
- Load from: https://cdn.jsdelivr.net/npm/@studio-freight/lenis@1.0.29/dist/lenis.min.js
- lerp: 0.1

THREE.JS:
- Load from: https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js
- Physics-inspired simulation scene.
- Play/Pause controls. Real-time parameter sliders.
- Mobile: simplified static scene.

INTERACTIVITY:
- Data analysis task: view dataset → answer questions.
- Equation solver: student inputs variables → shows steps.
- 15-question test: MCQ + numerical + diagram-labeling.

OUTPUT: Single HTML. Comment: <!-- CLASS: 8 | SUBJECT: {subject} | VERSION: 1.0 -->""",

    9: """You are building a lesson HTML page for Class 9 (ages 13–14) for Digital School. Design must feel like a professional learning tool.

DESIGN SYSTEM:
- Fonts: 'Plus Jakarta Sans' (headings), 'Inter' (body 15px), 'Fira Code' (code/math). Load from Google Fonts.
- Palette: Deep Purple #6C5CE7, Graphite #2D3436, Electric Mint #00CEC9, Warm White #FDFDFD.
- Minimal editorial aesthetic: whitespace, strong typographic hierarchy, colored accents only.
- Proof/derivation blocks: numbered steps, collapsible detail, dark background.
- Case study cards: newspaper-style with headline and summary.

LAYOUT:
- Two-column reading view on desktop (content + margin notes).
- Margin notes system for key terms/formulas.
- Collapsible proof sections.

ANIMATIONS (GSAP Required):
- Load GSAP from: https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js
- Load ScrollTrigger from: https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js
- Editorial entrance: headline fades + scale, paragraphs stagger.
- Proof reveal: GSAP timeline sequentially reveals derivation steps.
- Margin notes slide in from right on scroll.

SMOOTH SCROLLING (Lenis):
- Load from: https://cdn.jsdelivr.net/npm/@studio-freight/lenis@1.0.29/dist/lenis.min.js
- lerp: 0.08, touchMultiplier: 1.5

THREE.JS:
- Load from: https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js
- Full conceptual 3D exploration model.
- OrbitControls with zoom and pan.
- Screenshot capture button.

INTERACTIVITY:
- Student margin annotations saved to localStorage.
- Proof builder: drag logical steps into sequence.
- 20-question formal test: MCQ, structured response, diagram completion.
- Timer, auto-save, review mode.

OUTPUT: Single HTML. Comment: <!-- CLASS: 9 | SUBJECT: {subject} | VERSION: 1.0 -->""",

    10: """You are building a lesson HTML page for Class 10 (ages 14–15) for Digital School. This is board exam preparation level.

DESIGN SYSTEM:
- Fonts: 'Inter' (body 15px, line-height 1.75), 'Bricolage Grotesque' (headings), 'Fira Code' (equations). Load from Google Fonts.
- Palette: Amber #FDCB6E, Dark Slate #1E1E2E, Accent Blue #4C6EF5, White.
- Exam-board aesthetic: clean borders, section numbering, clear hierarchy.
- Revision cards: flip-card design (3D CSS flip + GSAP).
- Floating formula sheet panel.

LAYOUT:
- Chapter overview → Objectives → Theory → Worked Exam Examples → Practice → Mind Map → Quick Revision.
- "Examiner's Tip" callout boxes.
- Quick revision flip cards at bottom.

ANIMATIONS (GSAP Required):
- Load GSAP from: https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js
- Load ScrollTrigger from: https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js
- Section numbers: count-up on viewport enter.
- Flip cards: GSAP rotateY 0→180 on click.
- Mind map: SVG radial expansion.
- Worked examples: step-by-step GSAP timeline.

SMOOTH SCROLLING (Lenis):
- Load from: https://cdn.jsdelivr.net/npm/@studio-freight/lenis@1.0.29/dist/lenis.min.js
- lerp: 0.1

THREE.JS:
- Load from: https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js
- Advanced 3D visualization for a key concept.
- Measurement tool. Reset button. Snapshot export.

INTERACTIVITY:
- 20-question practice bank, randomly ordered.
- 3-level hint system per question.
- Full mock test mode: timed, all question types, auto-scored.
- Revision flashcards with spaced repetition (localStorage).
- Performance tracker: Chart.js radar chart by topic.

OUTPUT: Single HTML. Comment: <!-- CLASS: 10 | SUBJECT: {subject} | VERSION: 1.0 -->""",

    11: """You are building a lesson HTML page for Class 11 (ages 15–16) for Digital School. University-preparation level content.

DESIGN SYSTEM:
- Fonts: 'Crimson Pro' (body 17px), 'Plus Jakarta Sans' (UI/headings). Load from Google Fonts.
- Palette: Oxford Blue #0984E3, Midnight Black #0D1117, Soft Gold #D4AC0D, White.
- Academic journal aesthetic: columns, pull-quotes, numbered theorems.
- Theorem/Proof blocks: formal boxed layout with QED symbol.
- Interactive knowledge graph section.

LAYOUT:
- Abstract → Prerequisites → Theory → Proof/Derivation → Examples → Advanced Applications → Assessment.
- Floating "Prerequisite check" widget.
- Multi-tab layout for parallel topic exploration.

ANIMATIONS (GSAP Required):
- Load GSAP from: https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js
- Load ScrollTrigger from: https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js
- Staggered text reveal with scholarly pacing.
- Proof steps type themselves in sequence.
- Tab switching: GSAP crossfade transitions.
- Theorem boxes: border-draw entrance.

SMOOTH SCROLLING (Lenis):
- Load from: https://cdn.jsdelivr.net/npm/@studio-freight/lenis@1.0.29/dist/lenis.min.js
- lerp: 0.07

THREE.JS:
- Load from: https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js
- Advanced 3D simulation with real-time parameter sliders.
- Camera auto-tour on load, then user takes over.

INTERACTIVITY:
- Prerequisite quiz: 5 quick questions, unlock lesson on pass.
- Proof builder: drag logical statements to construct valid proof.
- 25-question formal assessment: structured response + derivations.
- Bookmarking system (localStorage).

OUTPUT: Single HTML. Comment: <!-- CLASS: 11 | SUBJECT: {subject} | VERSION: 1.0 -->""",

    12: """You are building a lesson HTML page for Class 12 (ages 16–17) for Digital School. This is the pinnacle of the platform — match the quality of Khan Academy and Brilliant.org. Every pixel and interaction must serve learning.

DESIGN SYSTEM:
- Fonts: System stack (-apple-system, BlinkMacSystemFont, 'Segoe UI'), 'Crimson Pro' (theorem text). Load Crimson Pro from Google Fonts.
- Palette: Deep Crimson #D63031, Carbon Black #0D0D0D, Platinum #E8E8E8, Electric Cyan #00FFF0 (accent only).
- Premium editorial design: maximum whitespace, precise typographic grid.
- DARK MODE as the DEFAULT. Light mode toggle available.
- Progress persistence: full lesson state saved to localStorage (IndexedDB preferred if available).

LAYOUT:
- Abstract → Introduction → Prerequisites → Core Theory → Derivations → Advanced Examples → Simulation → Research Context → Comprehensive Assessment → Further Reading.
- "Research Extension" section with external source links (target="_blank", rel="noopener").
- Floating annotation panel (student notes + highlights).

ANIMATIONS (GSAP Required):
- Load GSAP from: https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js
- Load ScrollTrigger from: https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js
- Cinematic page load: GSAP timeline orchestrates hero reveal with precision.
- Derivation steps: ScrollTrigger scrub — each step reveals as user scrolls.
- Background: Three.js particle field behind hero.

SMOOTH SCROLLING (Lenis):
- Load from: https://cdn.jsdelivr.net/npm/@studio-freight/lenis@1.0.29/dist/lenis.min.js
- lerp: 0.07

THREE.JS (Maximum sophistication):
- Load from: https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js
- Full custom WebGL experience relevant to the subject.
- Instanced mesh for complex systems.
- GUI controls for real-time parameter adjustment.
- Export rendered frame as PNG.
- Mobile: reduce complexity, single-pass rendering.

INTERACTIVITY:
- Full annotation system: highlight text, attach notes.
- Adaptive assessment: 30 questions, difficulty adjusts based on performance.
- Timed mock exam: tab-switch detection, auto-pause.
- Performance analytics dashboard (use Chart.js from CDN).
- Flashcard deck auto-generated from lesson key terms.

SELF-HEALING:
- FPS monitor: reduce Three.js quality if FPS < 30.
- All CDN imports: try primary CDN → fallback CDN → inline minimal implementation.
- Memory leak prevention: dispose() all Three.js resources on navigation.

OUTPUT: Single HTML file, dark mode default, fully self-contained.
Comment: <!-- CLASS: 12 | SUBJECT: {subject} | VERSION: 1.0 -->
Add a CHANGELOG comment block at the bottom.""",


}


UNIVERSAL_SCRIPT_RULES = """

---
CRITICAL TECHNICAL RULES (mandatory for all classes):

SCRIPT LOADING:
- Load ALL scripts (GSAP, ScrollTrigger, Lenis, Three.js) in <head> with NO defer and NO async.
- All custom JavaScript goes in a single <script> tag at the very bottom of <body>.
- Do NOT use window.addEventListener('load', ...) for initialization.
- Use: document.addEventListener('DOMContentLoaded', () => { init(); })

CONTENT VISIBILITY:
- ALL cards and sections must be fully visible (opacity:1, transform:none) by default in CSS.
- GSAP animations are progressive enhancement only — never the sole reason content becomes visible.
- If GSAP hasn't loaded, the page must still show all content normally.

SELF-HEALING:
- Wrap every CDN-dependent init block in try/catch.
- Check typeof gsap !== 'undefined' before using GSAP.
- Check typeof THREE !== 'undefined' before using Three.js.
- Check typeof Lenis !== 'undefined' before using Lenis.
- If Three.js fails or WebGL is unsupported, show a fallback emoji/illustration instead.

THREE.JS CANVAS RULES:
- Always set canvas width/height explicitly as attributes AND via renderer.setSize().
- After renderer.setSize(w, h), also set canvas.style.width and canvas.style.height in px.
- The Three.js canvas must have a visible background color set on the renderer: renderer.setClearColor(0xffffff, 1) or similar — never transparent for a main scene.
- Test WebGL support BEFORE creating renderer: use a try/catch around new THREE.WebGLRenderer(). If it throws or returns null, immediately show the fallback.
- The fallback element must have display:block and a minimum height of 200px with a large centered emoji, so it is always visible if Three.js fails.
- Never rely on CSS to size the Three.js canvas — set explicit pixel dimensions in JS.

LAYOUT RULES:
- html, body: width 100%, margin 0, padding 0, no max-width.
- The outermost page wrapper: width 100%, no max-width.
- Content containers inside sections: max-width 1500px, margin 0 auto, padding 0 40px.
- Individual cards and fun-cards: width 100%, max-width 100% — they must fill their container fully.
- NEVER set a card or section wrapper to a fixed pixel width like 500px, 600px, or 700px.
- The hero/header section must be 100vw wide with no side gaps.

CURTAIN / LOADING SCREEN RULES:
- If you use a loading curtain/overlay, it MUST have a guaranteed fallback dismissal.
- Always add: setTimeout(() => { const c = document.getElementById('curtain'); if (c) c.style.display = 'none'; }, 3000);
- This goes as the very FIRST line inside DOMContentLoaded, before any other init calls.
- The curtain must NEVER depend solely on GSAP to dismiss — always include a pure JS fallback timeout.

FONT SIZE RULES:
- Base body font size must be minimum 18px, NOT 14px or 16px.
- All body text: minimum 18px.
- Section subtitles and descriptions: minimum 18px.
- Card body text: minimum 17px.
- Table cells (td): minimum 16px.
- Navigation items: minimum 15px.
- Small labels/badges: minimum 13px — nothing smaller.
- Headings (h1): clamp(2.5rem, 6vw, 4.5rem).
- Headings (h2): clamp(2rem, 4vw, 3rem).
- Headings (h3): clamp(1.4rem, 2.5vw, 1.8rem).
- ALL clamp() values must start 2-3px higher than you normally would.
- Never use font-size below 13px anywhere on the page.

MOBILE RESPONSIVENESS (mandatory for ALL classes):
- Every page MUST be fully usable on screens as narrow as 320px.
- At max-width: 768px breakpoint, ALL of the following are required:
  1. Any desktop sidebar must be hidden (display:none).
  2. A FIXED BOTTOM NAVIGATION BAR must appear instead, with the same section links, scrollable horizontally if needed.
  3. All multi-column grids (2-col, 3-col) must collapse to single column.
  4. Font sizes must use clamp() so they scale down gracefully — never overflow.
  5. No element may have a fixed width wider than 100vw.
  6. Touch targets (buttons, links, options) must be minimum 48px tall.
  7. Any fixed/floating widgets (prerequisite checker, bookmark panel, etc.) must be: max-width: calc(100vw - 32px), positioned so they don't cover main content permanently.
  8. Tables must be wrapped in overflow-x: auto containers.
  9. Hero sections must reduce min-height to 60vh on mobile.
  10. All padding/margin must use responsive values — never fixed px values above 20px on mobile.
- Test mentally at 375px width (iPhone SE) — if anything would overflow or be unreadable, fix it.
- The bottom nav bar on mobile must have: position:fixed, bottom:0, left:0, right:0, overflow-x:auto, with flex items that are touch-friendly.
- Add padding-bottom: 80px to the main content on mobile to prevent the bottom nav from covering content.
"""

# Fallback for any unrecognised class number
DEFAULT_PROMPT = CLASS_PROMPTS[6]


def get_class_prompt(class_num: int, subject: str) -> str:
    """Return the design prompt for this class, with subject injected."""
    template = CLASS_PROMPTS.get(class_num, DEFAULT_PROMPT)
    return template.replace("{subject}", subject) + UNIVERSAL_SCRIPT_RULES


# ════════════════════════════════════════════════════════════════════════════════
#  UTILITIES
# ════════════════════════════════════════════════════════════════════════════════

def get_class_number(folder_name: str) -> int:
    """Parse class number from folder name: 'class 1', 'Class 5', 'class10', '7'."""
    import re
    match = re.search(r"\d+", folder_name.lower())
    if match:
        return max(1, min(12, int(match.group())))
    return 1


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
        with open(log_path, "a", encoding="utf-8", errors="replace") as f:
            f.write(line + "\n")


# ════════════════════════════════════════════════════════════════════════════════
#  PDF DISCOVERY
# ════════════════════════════════════════════════════════════════════════════════

def discover_pdfs(input_dir: Path, class_filter: str = None) -> list:
    pdfs = []
    for pdf_path in sorted(input_dir.rglob("*.pdf")):
        parts = pdf_path.relative_to(input_dir).parts
        class_name   = parts[0] if len(parts) >= 3 else "class 1"
        subject_name = parts[1] if len(parts) >= 3 else (parts[0] if len(parts) >= 2 else "general")

        if class_filter and class_filter.lower() not in class_name.lower():
            continue

        pdfs.append({
            "path":      pdf_path,
            "class":     class_name,
            "class_num": get_class_number(class_name),
            "subject":   subject_name,
            "stem":      pdf_path.stem,
            "rel":       pdf_path.relative_to(input_dir),
        })
    return pdfs


def build_output_path(pdf_info: dict, output_dir: Path) -> Path:
    out = output_dir / pdf_info["class"] / pdf_info["subject"]
    out.mkdir(parents=True, exist_ok=True)
    return out / f"{pdf_info['stem']}.html"


# ════════════════════════════════════════════════════════════════════════════════
#  CORE: PDF → HTML via Claude
# ════════════════════════════════════════════════════════════════════════════════

def generate_html(client: anthropic.Anthropic, pdf_info: dict) -> str:
    pdf_b64       = base64.b64encode(pdf_info["path"].read_bytes()).decode()
    design_prompt = get_class_prompt(pdf_info["class_num"], pdf_info["subject"])

    prompt = f"""{design_prompt}

---

The PDF attached is the lesson content. Read it thoroughly and build the complete, 
fully interactive HTML page following every design and technical requirement above.

The page must be entirely self-contained — all CSS, JavaScript, and content inline 
in a single .html file. Do not use placeholder content; extract everything from the PDF.

Return ONLY the raw HTML. No explanation, no markdown fences, no commentary."""

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
                        },
                        {
                            "type": "text",
                            "text": prompt,
                        },
                    ],
                }],
            ) as stream:
                for text in stream.text_stream:
                    html_chunks.append(text)

            html = "".join(html_chunks).strip()

            if html.startswith("```"):
                lines = html.split("\n")
                html  = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

            return html

        except Exception as e:
            last_err = e
            if attempt < RETRY_ATTEMPTS:
                time.sleep(RETRY_DELAY_SEC)

    raise RuntimeError(f"Claude API failed after {RETRY_ATTEMPTS} attempts: {last_err}")


def process_pdf(client, pdf_info, output_dir, cache, cache_path, log_path, dry_run=False) -> bool:
    output_file = build_output_path(pdf_info, output_dir)
    cache_key   = str(pdf_info["rel"])
    h           = file_hash(pdf_info["path"])

    if dry_run:
        log(f"   [DRY RUN] → {output_file}", log_path)
        return True

    try:
        log(f"   🤖 Sending to Claude ({CLAUDE_MODEL})…", log_path)
        html = generate_html(client, pdf_info)

        output_file.write_text(html, encoding="utf-8")
        log(f"   ✅ Saved → {output_file}", log_path)

        cache[cache_key] = h
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

    parser = argparse.ArgumentParser(description="Generate interactive HTML lesson pages from PDFs")
    parser.add_argument("--input",        default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output",       default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--file",         default=None,  help="Process a single PDF")
    parser.add_argument("--class-filter", default=None,  help="Only process this class, e.g. 'class 1'")
    parser.add_argument("--dry-run",      action="store_true")
    parser.add_argument("--force",        action="store_true", help="Ignore cache, regenerate all")
    args = parser.parse_args()

    input_dir  = Path(args.input)
    output_dir = Path(args.output)
    log_path   = output_dir / LOG_FILE
    cache_path = output_dir / CACHE_FILE
    output_dir.mkdir(parents=True, exist_ok=True)

    log("=" * 58, log_path)
    log(f"  EDU HTML PIPELINE  —  {datetime.now().strftime('%Y-%m-%d %H:%M')}", log_path)
    log("=" * 58, log_path)

    client = anthropic.Anthropic(api_key=get_api_key())
    cache  = {} if args.force else load_cache(cache_path)

    # Discover PDFs
    if args.file:
        p    = Path(args.file).resolve()
        pts  = p.parts
        cn   = pts[-3] if len(pts) >= 3 else "class 1"
        subj = pts[-2] if len(pts) >= 2 else "general"
        pdfs = [{
            "path": p, "class": cn, "class_num": get_class_number(cn),
            "subject": subj, "stem": p.stem, "rel": p,
        }]
    else:
        if not input_dir.exists():
            sys.exit(f"Input folder not found: {input_dir}")
        pdfs = discover_pdfs(input_dir, args.class_filter)

    if not pdfs:
        log("No PDFs found. Check folder structure: classes/<class name>/<subject>/<file>.pdf", log_path)
        return

    log(f"📚 Found {len(pdfs)} PDF(s)\n", log_path)

    success = fail = skip = 0

    for i, pdf_info in enumerate(pdfs, 1):
        log(f"[{i}/{len(pdfs)}] {pdf_info['rel']}  (Class {pdf_info['class_num']} · {pdf_info['subject']})", log_path)

        output_file = build_output_path(pdf_info, output_dir)
        cache_key   = str(pdf_info["rel"])
        h           = file_hash(pdf_info["path"])

        if (not args.force
                and cache_key in cache
                and cache[cache_key] == h
                and output_file.exists()):
            log("   ⏭  Already up-to-date, skipping.", log_path)
            skip += 1
            continue

        ok = process_pdf(client, pdf_info, output_dir, cache, cache_path, log_path, args.dry_run)
        if ok:
            success += 1
        else:
            fail += 1

        if i < len(pdfs):
            time.sleep(1)

    log("", log_path)
    log("=" * 58, log_path)
    log(f"  DONE  ✅ {success} generated  ⏭ {skip} skipped  ❌ {fail} failed", log_path)
    log(f"  Output → {output_dir.resolve()}", log_path)
    log("=" * 58, log_path)


if __name__ == "__main__":
    main()
