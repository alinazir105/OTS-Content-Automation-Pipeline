# -*- coding: utf-8 -*-
import re
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "output" / "class 4" / "english" / "01.html"
t = p.read_text(encoding="utf-8")

t = re.sub(
    r'\n\s*<div class="headgame-tilt-meter" id="headgameTiltMeter"[^>]*>[\s\S]*?</div>\n',
    "\n",
    t,
    count=1,
)

cam_marker = '<div class="headgame-bento-cell headgame-cell-cam">'
q_marker = '<div class="headgame-bento-cell headgame-cell-q">'
cam_start = t.index(cam_marker)
cam_end = t.index(q_marker)
cam_block = t[cam_start:cam_end]
t = t[:cam_start] + t[cam_end:]

old = '      </div>\n    </div>\n    <p id="headgameCamHint"'
new = cam_block.rstrip() + '\n    </div>\n    <p id="headgameCamHint"'
if old not in t:
    raise SystemExit('insert anchor not found')
t = t.replace(old, new, 1)

p.write_text(t, encoding="utf-8")
print("OK")
