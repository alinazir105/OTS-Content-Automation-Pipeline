# -*- coding: utf-8 -*-
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "output" / "class 4" / "math" / "03.html"
text = HTML.read_text(encoding="utf-8")
shell = (ROOT / "tools" / "boxing_shell.html").read_text(encoding="utf-8").strip()
js = (ROOT / "tools" / "boxing_js.txt").read_text(encoding="utf-8").strip()

start = text.find("<!-- BOXING MATCH FULLSCREEN -->")
if start == -1:
    anchor = "</main>\n\n"
    idx = text.find(anchor)
    if idx == -1:
        raise SystemExit("Could not find </main>")
    start = idx + len(anchor)
    before = text[:start]
    after = text[start:]
else:
    nav = text.find("<nav id=\"mobile-bottom-nav\">")
    if nav == -1:
        raise SystemExit("Could not find mobile nav")
    before = text[:start]
    after = text[nav:]

text = before + shell + "\n\n<!-- MOBILE BOTTOM NAV -->\n" + after

if "function initBoxingGame" not in text:
    text = text.replace("</script>\n</body>", js + "\n</script>\n</body>", 1)

HTML.write_text(text, encoding="utf-8")
print("OK", "initBoxingGame" in text, "boxingArena" in text)
