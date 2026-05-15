# -*- coding: utf-8 -*-
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "output" / "class 4" / "math" / "03.html"
text = HTML.read_text(encoding="utf-8")

css = (ROOT / "tools" / "boxing_css.txt").read_text(encoding="utf-8")
teaser = (ROOT / "tools" / "boxing_teaser.html").read_text(encoding="utf-8")
shell = (ROOT / "tools" / "boxing_shell.html").read_text(encoding="utf-8")
js = (ROOT / "tools" / "boxing_js.txt").read_text(encoding="utf-8")

if "@mediapipe/pose" not in text:
    text = text.replace(
        '<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>',
        '<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>\n'
        '<script defer src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils@0.3.1675466862/camera_utils.js"></script>\n'
        '<script defer src="https://cdn.jsdelivr.net/npm/@mediapipe/pose@0.5.1675469404/pose.js"></script>',
    )

if ".boxing-shell" not in text:
    text = text.replace("</style>", css + "\n</style>", 1)

if "sec-boxing" not in text:
    text = text.replace(
        '<hr class="section-divider"/>\n\n<main>',
        '<hr class="section-divider"/>\n' + teaser + "\n\n<main>",
        1,
    )

if "boxing-shell" not in text:
    text = text.replace("<!-- MOBILE BOTTOM NAV -->", shell + "\n<!-- MOBILE BOTTOM NAV -->", 1)

if "'sec-boxing'" not in text and "'sec-boxing'" not in text:
    text = text.replace(
        "const sections = ['sec-hero','sec-tens'",
        "const sections = ['sec-hero','sec-boxing','sec-tens'",
    )

if 'title="Boxing"' not in text:
    text = text.replace(
        '<motion.div class="progress-dot active" data-section="0" title="Introduction"></div>',
        '<div class="progress-dot active" data-section="0" title="Introduction"></div>\n    <motion.div class="progress-dot" data-section="boxing" title="Boxing"></div>',
    )
    text = text.replace("<motion.div", "<div").replace("</motion.div>", "</div>")

if "#sec-boxing" not in text:
    text = text.replace(
        '<a href="#sec-tens"><span class="nav-icon">🔟</span>×10s</a>',
        '<a href="#sec-boxing"><span class="nav-icon">🥊</span>Boxing</a>\n    <a href="#sec-tens"><span class="nav-icon">🔟</span>×10s</a>',
    )

if "initBoxingGame" not in text:
    text = text.replace("  // PROGRESS DOTS", "  initBoxingGame();\n\n  // PROGRESS DOTS", 1)

if "MULTIPLICATION BOXING" not in text:
    text = text.replace("</script>\n</body>", js + "\n</script>\n</body>", 1)

HTML.write_text(text, encoding="utf-8")
print("Done")
