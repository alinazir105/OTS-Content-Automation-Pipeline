"""One-off: replace Express Lane stage markup with separated boxes."""
from pathlib import Path

HTML = Path(__file__).resolve().parents[1] / "output" / "class 4" / "english" / "01.html"
text = HTML.read_text(encoding="utf-8")

start_marker = '      <div class="headgame-stage" id="headgameStage">'
old_hint = (
    '      <p id="headgameCamHint" class="headgame-cam-hint">'
    "Tip: face the light, keep your head in frame, and use a clear side-to-side tilt. "
    "The amber ring shows time left.</p>"
)

start = text.index(start_marker)
end = text.index(old_hint) + len(old_hint)

new_block = "\n".join([
    '      <div class="headgame-play-grid" id="headgameStage">',
    '        <div class="headgame-box headgame-box-camera">',
    '          <span class="headgame-box-label">Camera</span>',
    '          <div class="headgame-rail" aria-hidden="true"></motion.div>',
    '          <div class="headgame-video-wrap" id="headgameVideoWrap">',
    '            <video id="headgameVideo" playsinline muted autoplay></video>',
    '            <div class="headgame-vignette" aria-hidden="true"></div>',
    '            <div class="headgame-scanlines" aria-hidden="true"></div>',
    '            <div id="headgameNoCamFill" aria-hidden="true"><span style="font-size:2.25rem;">📵</span><span>Camera off — tap a track below</span></div>',
    '            <div class="headgame-cal-label" id="headgameCalLabel">Look straight ahead — calibrating…</div>',
    '            <div class="headgame-msg" id="headgameMsg" role="status"></div>',
    '          </div>',
    '        </div>',
    '',
    '        <div class="headgame-box headgame-box-question">',
    '          <span class="headgame-box-label">Question</span>',
    '          <div class="headgame-train-host">',
    '            <div id="headgameTrainCard" class="headgame-train-card">Loading…</div>',
    '          </div>',
    '        </div>',
    '',
    '        <div class="headgame-box headgame-box-stats">',
    '          <span class="headgame-box-label">Timer &amp; score</span>',
    '          <div class="headgame-timer-row">',
    '            <div class="headgame-timer-ring" id="headgameTimerRing" style="--p:1"><span id="headgameTimerNum">7</span></motion.div>',
    '            <div class="headgame-score-pill"><span id="headgameScoreTxt">0</span> pts · streak <span id="headgameStreakTxt">0</span></div>',
    '          </div>',
    '        </div>',
    '',
    '        <div class="headgame-box headgame-box-tracks">',
    '          <span class="headgame-box-label">Your answer — tilt or tap</span>',
    '          <p id="headgameTiltHud" class="headgame-tilt-hud">Center your face, then tilt toward a track</p>',
    '          <motion.div class="headgame-lanes">',
    '            <button type="button" class="headgame-lane lane-l" id="headgameLaneL" aria-label="Choose left answer">',
    '              <span class="lane-tag">LEFT</span>',
    '              <span id="headgameLeftTxt">—</span><small>← Tilt or tap</small>',
    '            </button>',
    '            <button type="button" class="headgame-lane lane-r" id="headgameLaneR" aria-label="Choose right answer">',
    '              <span class="lane-tag">RIGHT</span>',
    '              <span id="headgameRightTxt">—</span><small>Tilt or tap →</small>',
    '            </button>',
    '          </div>',
    '        </div>',
    '      </div>',
    '      <p id="headgameCamHint" class="headgame-cam-hint">Tip: good light, face the camera, then tilt clearly toward the green (left) or navy (right) panel. Hold for half a second.</p>',
])
new_block = new_block.replace("</motion.div>", "</div>").replace("<motion.div", "<div")

text = text[:start] + new_block + text[end:]
HTML.write_text(text, encoding="utf-8")
print("Patched OK")
