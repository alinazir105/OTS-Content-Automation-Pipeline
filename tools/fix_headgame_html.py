# -*- coding: utf-8 -*-
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "output" / "class 4" / "english" / "01.html"
t = p.read_text(encoding="utf-8")

start = t.index('      <div class="headgame-bento-cell headgame-cell-tracks">')
end = t.index('    <p id="headgameCamHint"')

fixed = """      <motion.div class="headgame-bento-cell headgame-cell-tracks">
        <p id="headgameTiltHud" class="headgame-tilt-hud">Center your face in the oval, then tilt toward a track</p>
        <div class="headgame-lanes">
          <button type="button" class="headgame-lane lane-l" id="headgameLaneL" aria-label="Choose left answer">
            <span class="lane-tag">LEFT · TILT HERE</span>
            <span id="headgameLeftTxt">—</span><small>← or tap</small>
          </button>
          <button type="button" class="headgame-lane lane-r" id="headgameLaneR" aria-label="Choose right answer">
            <span class="lane-tag">RIGHT · TILT HERE</span>
            <span id="headgameRightTxt">—</span><small>tap or →</small>
          </button>
        </div>
      </div>

      <div class="headgame-bento-cell headgame-cell-cam">
        <div class="headgame-rail" aria-hidden="true"></div>
        <div class="headgame-video-wrap" id="headgameVideoWrap">
          <video id="headgameVideo" playsinline muted autoplay></video>
          <div class="headgame-face-guide" aria-hidden="true"></div>
          <div class="headgame-vignette" aria-hidden="true"></div>
          <div id="headgameNoCamFill" aria-hidden="true"><span style="font-size:2.25rem;">📵</span><span>Camera off — tap a track below</span></div>
          <motion.div class="headgame-cal-label" id="headgameCalLabel">Look straight ahead — calibrating…</div>
          <motion.div class="headgame-msg" id="headgameMsg" role="status"></div>
        </div>
      </div>
    </div>
    """
fixed = fixed.replace("motion.div", "div")

t = t[:start] + fixed + t[end:]
p.write_text(t, encoding="utf-8")
print("OK")
