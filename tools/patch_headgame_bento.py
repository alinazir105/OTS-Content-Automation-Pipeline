# -*- coding: utf-8 -*-
from pathlib import Path

HTML = Path(__file__).resolve().parents[1] / "output" / "class 4" / "english" / "01.html"
text = HTML.read_text(encoding="utf-8")

# Intro tweaks
text = text.replace(
    "font-weight:800;color:#fff;margin-bottom:14px;letter-spacing:-0.02em;\">Express Lane</h3>",
    "font-weight:800;margin-bottom:14px;letter-spacing:-0.02em;\">Express Lane</h3>",
)
text = text.replace(
    "<p>Questions roll in under your camera. <span class=\"headgame-intro-accent\">Tilt toward the green (left) or navy (right) track</span> and hold briefly to lock your answer. You have <strong>7 seconds</strong> each round.</p>",
    "<p>Your camera fills the left panel. <span class=\"headgame-intro-accent\">Tilt toward the green (left) or navy (right) track</span> — the amber dot shows your tilt. Hold briefly to lock in. <strong>7 seconds</strong> per question.</p>",
)
text = text.replace(
    'id="headgameBtnNoCam" style="border-color:rgba(255,255,255,0.45);color:#fff;background:transparent;"',
    'id="headgameBtnNoCam"',
)

start = text.index('  <div id="headgameStageWrap"')
end = text.index('  <div id="headgameEndCard"')

new_stage = r'''  <div id="headgameStageWrap" class="headgame-stage-wrap">
    <div class="headgame-bento" id="headgameStage">
      <div class="headgame-bento-cell headgame-cell-cam">
        <div class="headgame-rail" aria-hidden="true"></div>
        <div class="headgame-video-wrap" id="headgameVideoWrap">
          <video id="headgameVideo" playsinline muted autoplay></video>
          <div class="headgame-face-guide" aria-hidden="true"></div>
          <div class="headgame-vignette" aria-hidden="true"></div>
          <div class="headgame-tilt-meter" id="headgameTiltMeter" aria-hidden="true">
            <div class="headgame-tilt-meter-labels"><span>← Left</span><span>Center</span><span>Right →</span></div>
            <div class="headgame-tilt-bar"><div class="headgame-tilt-needle" id="headgameTiltNeedle"></div></div>
          </div>
          <div id="headgameNoCamFill" aria-hidden="true"><span style="font-size:2.25rem;">📵</span><span>Camera off — tap a track below</span></div>
          <div class="headgame-cal-label" id="headgameCalLabel">Look straight ahead — calibrating…</div>
          <div class="headgame-msg" id="headgameMsg" role="status"></div>
        </div>
      </div>

      <div class="headgame-bento-cell headgame-cell-q">
        <div class="headgame-cell-head">
          <span class="headgame-cell-label">Question</span>
          <span class="headgame-round-pill" id="headgameRoundPill">1 / 8</span>
        </div>
        <div class="headgame-train-host">
          <div id="headgameTrainCard" class="headgame-train-card">Loading…</div>
        </div>
      </div>

      <div class="headgame-bento-cell headgame-cell-stats">
        <span class="headgame-cell-label">Timer &amp; score</span>
        <div class="headgame-timer-row">
          <div class="headgame-timer-ring" id="headgameTimerRing" style="--p:1"><span id="headgameTimerNum">7</span></div>
          <div class="headgame-score-pill"><span id="headgameScoreTxt">0</span> pts · streak <span id="headgameStreakTxt">0</span></div>
        </div>
      </div>

      <div class="headgame-bento-cell headgame-cell-tracks">
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
    </div>
    <p id="headgameCamHint" class="headgame-cam-hint">Match the amber dot to the side you mean — green = tilt left, navy = tilt right. Hold half a second.</p>
  </div>

'''
new_stage = new_stage.replace("<motion.div", "<div").replace("</motion.div>", "</div>")

text = text[:start] + new_stage + text[end:]

text = text.replace(
    "font-weight:800;color:#fff;margin-bottom:10px;\">Station reached</h3>",
    "font-weight:800;margin-bottom:10px;\">Station reached</h3>",
)

# JS: thresholds and tilt
text = text.replace("  THRESH: 0.022,\n  DWELL_MS: 450,\n  CAL_MIN: 18", "  THRESH: 0.014,\n  DWELL_MS: 400,\n  CAL_MIN: 14")

old_compute = """function headgameComputeTilt(lm) {
  const nose = lm[1];
  const le = lm[33];
  const re = lm[263];
  const cheekL = lm[234];
  const cheekR = lm[454];
  const midX = (le.x + re.x) * 0.5;
  const faceMid = (cheekL.x + cheekR.x) * 0.5;
  const span = Math.max(0.08, cheekR.x - cheekL.x);
  const offset = (1 - nose.x) - (1 - midX);
  const yaw = ((1 - nose.x) - (1 - faceMid)) / span;
  return offset * 0.75 + yaw * 0.2;
}"""

new_compute = """function headgameComputeTilt(lm) {
  const nose = lm[1];
  const le = lm[33];
  const re = lm[263];
  const cx = (le.x + re.x) * 0.5;
  const span = Math.max(0.07, Math.abs(re.x - le.x));
  const raw = (nose.x - cx) / span;
  return -raw * 2.2;
}

function headgameUpdateTiltMeter(delta) {
  const needle = document.getElementById('headgameTiltNeedle');
  const meter = document.getElementById('headgameTiltMeter');
  if (!needle || !HG.useCam) return;
  if (meter) meter.removeAttribute('aria-hidden');
  const t = HG.calibrating ? 0 : Math.max(-1, Math.min(1, delta / (HG.THRESH * 2.2)));
  needle.style.left = `${50 + t * 44}%`;
}"""

if old_compute not in text:
    raise SystemExit("headgameComputeTilt block not found")
text = text.replace(old_compute, new_compute)

# Flip direction mapping
text = text.replace(
    "  if (delta > HG.THRESH) dir = -1;\n  else if (delta < -HG.THRESH) dir = 1;",
    "  if (delta < -HG.THRESH) dir = -1;\n  else if (delta > HG.THRESH) dir = 1;",
)

# Smoother + meter in onFaceResults
text = text.replace(
    "  HG.smoothTilt = (HG.smoothTilt || 0) * 0.65 + raw * 0.35;",
    "  HG.smoothTilt = (HG.smoothTilt || 0) * 0.5 + raw * 0.5;",
)

text = text.replace(
    """  const delta = HG.smoothTilt - HG.baseline;
  let dir = 0;
  if (delta < -HG.THRESH) dir = -1;
  else if (delta > HG.THRESH) dir = 1;

  const now = performance.now();""",
    """  const delta = HG.smoothTilt - HG.baseline;
  headgameUpdateTiltMeter(delta);
  let dir = 0;
  if (delta < -HG.THRESH) dir = -1;
  else if (delta > HG.THRESH) dir = 1;

  const now = performance.now();""",
)

# HUD text
text = text.replace(
    "    hud.textContent = 'Tilt toward green (left) or navy (right)';",
    "    hud.textContent = 'Tilt head toward green (left) or navy (right) panel';",
)

# stage wrap class toggle
text = text.replace(
    "  if (stageW) stageW.style.display = 'none';",
    "  if (stageW) { stageW.style.display = 'none'; stageW.classList.remove('is-active'); }",
)
text = text.replace(
    "  if (stageW) stageW.style.display = 'none';\n  if (endC) endC.style.display = 'none';",
    "  if (stageW) { stageW.style.display = 'none'; stageW.classList.remove('is-active'); }\n  if (endC) endC.style.display = 'none';",
    1,
)

# headgameStartWithCamera
text = text.replace(
    "  if (stageW) stageW.style.display = 'flex';",
    "  if (stageW) { stageW.style.display = 'flex'; stageW.classList.add('is-active'); }",
    2,
)

# Round pill in beginRound
needle = "  if (card) card.textContent = q.q;"
if needle in text and "headgameRoundPill" not in text[text.index(needle):text.index(needle)+400]:
    text = text.replace(
        needle,
        needle + "\n  const rp = document.getElementById('headgameRoundPill');\n  if (rp) rp.textContent = `${HG.qIndex + 1} / ${HG.questions.length}`;",
        1,
    )

# Hide meter when no cam
text = text.replace(
    "  if (fill) fill.classList.add('show');\n  HG.useCam = false;\n  headgameStartGameLoop();",
    "  if (fill) fill.classList.add('show');\n  const meter = document.getElementById('headgameTiltMeter');\n  if (meter) meter.setAttribute('aria-hidden', 'true');\n  HG.useCam = false;\n  headgameStartGameLoop();",
)

HTML.write_text(text, encoding="utf-8")
print("OK")
