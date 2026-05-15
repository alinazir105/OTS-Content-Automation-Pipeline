#!/usr/bin/env python3
"""
Inline <script defer src="zb-*.js"></script> into the same directory's HTML.

Lesson pages are often delivered as a single HTML string from an API or
loadDataWithBaseURL without a folder of sibling assets. External zb-*.js then
404s; inlining restores self-contained behavior.

Usage (from repo root):
  python tools/inline_zb_scripts.py

Re-run after editing a zb-*.js file to push changes into the HTML.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUTPUT = REPO / "output"

# One defer zb script per file (current lesson convention).
PATTERN = re.compile(
    r'<script\s+defer\s+src="(zb-[^"]+\.js)"></script>',
    re.IGNORECASE,
)


def inline_one(html_path: Path) -> bool:
    text = html_path.read_text(encoding="utf-8")
    m = PATTERN.search(text)
    if not m:
        return False
    zb_name = m.group(1)
    zb_path = html_path.parent / zb_name
    if not zb_path.is_file():
        raise FileNotFoundError(f"{html_path}: expected {zb_path}")
    js = zb_path.read_text(encoding="utf-8")
    if "</script" in js.casefold():
        raise ValueError(f"{zb_path}: contains '</script' which breaks inline HTML")
    injected = "<script>\n" + js + "</script>"
    # Do not use re.sub(replacement=js): backslashes in JS are interpreted as re escapes.
    new_text = text[: m.start()] + injected + text[m.end() :]
    html_path.write_text(new_text, encoding="utf-8")
    print(f"Inlined {zb_name} -> {html_path.relative_to(REPO)}")
    return True


def main() -> int:
    if not OUTPUT.is_dir():
        print("No output/ directory.", file=sys.stderr)
        return 1
    n = 0
    for html_path in sorted(OUTPUT.rglob("*.html")):
        if inline_one(html_path):
            n += 1
    print(f"Done. Inlined zb scripts in {n} HTML file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
