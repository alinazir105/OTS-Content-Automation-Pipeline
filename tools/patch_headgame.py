# -*- coding: utf-8 -*-
from pathlib import Path
import re

p = Path(r'c:\Users\HP\Desktop\OTS-Content-Automation-Pipeline\output\class 4\english\01.html')
text = p.read_text(encoding='utf-8')

# Teaser CSS
old_pill_end = """  .headgame-pill {
    font-family: 'Poppins', sans-serif; font-weight: 700; font-size: 0.82rem;
    padding: 8px 14px; border-radius: 999px;
    background: var(--light-green); color: var(--navy);
    border: 1px solid rgba(106, 176, 76, 0.35);
  }

  .headgame-shell {"""

new_pill_end = """  .headgame-pill {
    font-family: 'Poppins', sans-serif; font-weight: 700; font-size: 0.82rem;
    padding: 8px 14px; border-radius: 999px;
    background: var(--light-green); color: var(--navy);
    border: 1px solid rgba(106, 176, 76, 0.35);
  }
  .headgame-teaser-section { background: var(--light-green); }
  .headgame-teaser-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 20px;
    margin-top: 8px;
  }
  .headgame-teaser-card {
    background: #fff;
    border-radius: var(--border-radius);
    box-shadow: var(--shadow);
    padding: 24px 22px;
    border: 1px solid rgba(44, 62, 80, 0.08);
  }
  .headgame-teaser-card-label {
    display: block;
    font-family: 'Poppins', sans-serif;
    font-weight: 700;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--green);
    margin-bottom: 10px;
  }
  .headgame-teaser-card p { font-size: 0.98rem; line-height: 1.55; color: #444; }
  .headgame-teaser-card .headgame-feature-row { margin: 14px 0 0; }
  .headgame-teaser-launch {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: center;
  }

  .headgame-shell {"""

if old_pill_end in text:
    text = text.replace(old_pill_end, new_pill_end, 1)

old_stage_css = """  .headgame-stage-wrap-inner {
    width: 100%;
    max-width: 480px;
    display: flex;
    flex-direction: column;
    align-items: stretch;
    gap: 14px;
  }

  .headgame-stage {
    position: relative;
    display: flex;
    flex-direction: column;
    width: 100%;
    max-height: min(92vh, 820px);
    min-height: 520px;
    border-radius: 22px;
    overflow: hidden;
    background: #0d141c;
    box-shadow:
      0 0 0 1px rgba(255,255,255,0.08),
      0 24px 64px rgba(0,0,0,0.45),
      0 0 100px rgba(106, 176, 76, 0.08);
    perspective: 900px;
  }

  .headgame-rail {
    flex-shrink: 0;
    height: 10px;
    background: repeating-linear-gradient(90deg, var(--amber) 0 14px, rgba(44,62,80,0.9) 14px 28px);
    opacity: 0.9;
    animation: headgame-rail-move 1.4s linear infinite;
  }
  @keyframes headgame-rail-move { to { background-position: 28px 0; } }

  .headgame-video-wrap {
    position: relative;
    flex: 1 1 44%;
    min-height: 220px;
    max-height: min(44vh, 360px);
    background: #0a0e12;
  }"""

new_stage_css = """  .headgame-stage-wrap-inner {
    width: 100%;
    max-width: 520px;
    display: flex;
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
  .headgame-play-grid {
    display: flex;
    flex-direction: column;
    gap: 16px;
    width: 100%;
  }
  .headgame-box {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 18px;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  }
  .headgame-box-label {
    font-family: 'Poppins', sans-serif;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: rgba(255, 255, 255, 0.55);
    padding: 12px 16px 0;
  }
  .headgame-rail {
    height: 8px;
    background: repeating-linear-gradient(90deg, var(--amber) 0 14px, rgba(44,62,80,0.9) 14px 28px);
    opacity: 0.9;
    animation: headgame-rail-move 1.4s linear infinite;
  }
  @keyframes headgame-rail-move { to { background-position: 28px 0; } }
  .headgame-video-wrap {
    position: relative;
    min-height: 240px;
    max-height: min(42vh, 340px);
    background: #0a0e12;
  }"""

if old_stage_css in text:
    text = text.replace(old_stage_css, new_stage_css, 1)

old_lower = """  .headgame-lower {
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
    gap: 18px;
    padding: 20px 18px 22px;
    background: linear-gradient(180deg, #152028 0%, #101820 100%);
    border-top: 1px solid rgba(255,255,255,0.06);
  }

  .headgame-train-host {"""

new_lower = """  .headgame-box-question { padding-bottom: 4px; }
  .headgame-box-stats { padding: 16px 18px; }
  .headgame-box-tracks { padding: 16px; background: rgba(0,0,0,0.15); }
  .headgame-tilt-hud {
    text-align: center;
    font-family: 'Poppins', sans-serif;
    font-weight: 700;
    font-size: 0.88rem;
    color: rgba(255,255,255,0.65);
    padding: 0 8px 12px;
    min-height: 1.4em;
  }
  .headgame-tilt-hud.active-left { color: #9fd48a; }
  .headgame-tilt-hud.active-right { color: #90caf9; }
  .headgame-lane .lane-tag {
    display: block;
    font-size: 0.65rem;
    letter-spacing: 0.12em;
    opacity: 0.85;
    margin-bottom: 6px;
  }

  .headgame-train-host {"""

if old_lower in text:
    text = text.replace(old_lower, new_lower, 1)

text = text.replace(
    """  .headgame-train-card {
    background: #fff;
    border-radius: 14px;
    padding: 18px 20px;
    border-left: 5px solid var(--green);
    box-shadow: 0 8px 28px rgba(0,0,0,0.22);""",
    """  .headgame-train-card {
    background: #fff;
    border-radius: 12px;
    margin: 0 16px 16px;
    padding: 20px 22px;
    border-left: 5px solid var(--green);
    box-shadow: 0 4px 16px rgba(0,0,0,0.12);""",
    1,
)

text = text.replace(
    """  .headgame-timer-row {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 20px;
    padding: 4px 0;
  }""",
    """  .headgame-timer-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
    padding: 0;
  }""",
    1,
)

text = text.replace(
    """  .headgame-lanes {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
    padding: 0 2px 4px;
  }""",
    """  .headgame-lanes {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    padding: 0;
  }""",
    1,
)

text = text.replace(
    """  @media (max-width: 480px) {
    .headgame-stage { min-height: 0; border-radius: 18px; }
    .headgame-video-wrap { min-height: 200px; max-height: 40vh; }
    .headgame-lower { padding: 16px 14px 18px; gap: 14px; }
    .headgame-lane { min-height: 100px; padding: 18px 12px; }
  }""",
    """  @media (max-width: 480px) {
    .headgame-teaser-grid { grid-template-columns: 1fr; }
    .headgame-video-wrap { min-height: 200px; max-height: 38vh; }
    .headgame-lane { min-height: 100px; padding: 18px 12px; }
  }""",
    1,
)

new_game_html = """  <motion.div id="headgameStageWrap" style="display:none;width:100%;align-items:center;justify-content:center;flex-direction:column;">
    <div class="headgame-stage-wrap-inner">
      <div class="headgame-play-grid" id="headgameStage">
        <div class="headgame-box headgame-box-camera">
          <span class="headgame-box-label">Camera</span>
          <div class="headgame-rail" aria-hidden="true"></div>
          <div class="headgame-video-wrap" id="headgameVideoWrap">
            <video id="headgameVideo" playsinline muted autoplay></video>
            <motion.div class="headgame-vignette" aria-hidden="true"></div>
            <div class="headgame-scanlines" aria-hidden="true"></div>
            <div id="headgameNoCamFill" aria-hidden="true"><span style="font-size:2.25rem;">📵</span><span>Camera off — tap a track below</span></div>
            <div class="headgame-cal-label" id="headgameCalLabel">Look straight ahead — calibrating…</div>
            <div class="headgame-msg" id="headgameMsg" role="status"></div>
          </div>
        </div>

        <div class="headgame-box headgame-box-question">
          <span class="headgame-box-label">Question</span>
          <div class="headgame-train-host">
            <div id="headgameTrainCard" class="headgame-train-card">Loading…</div>
          </div>
        </div>

        <div class="headgame-box headgame-box-stats">
          <span class="headgame-box-label">Timer &amp; score</span>
          <div class="headgame-timer-row">
            <div class="headgame-timer-ring" id="headgameTimerRing" style="--p:1"><span id="headgameTimerNum">7</span></motion.div>
            <div class="headgame-score-pill"><span id="headgameScoreTxt">0</span> pts · streak <span id="headgameStreakTxt">0</span></div>
          </div>
        </div>

        <div class="headgame-box headgame-box-tracks">
          <span class="headgame-box-label">Your answer — tilt or tap</span>
          <p id="headgameTiltHud" class="headgame-tilt-hud">Center your face, then tilt toward a track</p>
          <div class="headgame-lanes">
            <button type="button" class="headgame-lane lane-l" id="headgameLaneL" aria-label="Choose left answer">
              <span class="lane-tag">LEFT</span>
              <span id="headgameLeftTxt">—</span>
              <small>← Tilt or tap</small>
            </button>
            <button type="button" class="headgame-lane lane-r" id="headgameLaneR" aria-label="Choose right answer">
              <span class="lane-tag">RIGHT</span>
              <span id="headgameRightTxt">—</span>
              <small>Tilt or tap →</small>
            </button>
          </div>
        </div>
      </div>
      <p id="headgameCamHint" class="headgame-cam-hint">Tip: good light, face the camera, then tilt clearly toward the green (left) or navy (right) panel. Hold for half a second.</p>
    </div>
  </div>

  <div id="headgameEndCard\""""

# Fix typos in new_game_html - remove motion.div
new_game_html = new_game_html.replace('motion.div', 'motion.div').replace('<motion.div', '<div').replace('</motion.div>', '</div>')

m = re.search(
    r'  <motion.div id="headgameStageWrap".*?  <div id="headgameEndCard"',
    text,
    re.DOTALL,
)
if not m:
    m = re.search(
        r'  <div id="headgameStageWrap".*?  <div id="headgameEndCard"',
        text,
        re.DOTALL,
    )
if m:
    text = text[: m.start()] + new_game_html + text[m.end() - len('  <div id="headgameEndCard"') :]
    print('Replaced game HTML')
else:
    print('Game HTML block not found')

text = text.replace(
    'You have <strong>5 seconds</strong> each round.',
    'You have <strong>7 seconds</strong> each round.',
)
text = text.replace('timeLeft: 5,', 'timeLeft: 7,')
text = text.replace('ROUND_SEC: 5,', 'ROUND_SEC: 7,')
text = text.replace('THRESH: 0.019,', 'THRESH: 0.022,')
text = text.replace('DWELL_MS: 300,', 'DWELL_MS: 450,')
text = text.replace(
    "const sections = ['section-nouns','section-plurals','section-articles','section-activities','section-headgame','section-quiz'];",
    "const sections = ['section-headgame','section-nouns','section-plurals','section-articles','section-activities','section-quiz'];",
)

# Replace headgameOnFaceResults and add compute function
old_face = """function headgameOnFaceResults(results) {
  if (!HG.running || HG.answered || !HG.useCam) return;
  const lm = results.multiFaceLandmarks && results.multiFaceLandmarks[0];
  const cal = document.getElementById('headgameCalLabel');

  if (!lm) {
    return;
  }
  const nose = lm[1];
  const le = lm[33];
  const re = lm[263];
  const midX = (le.x + re.x) * 0.5;
  const raw = nose.x - midX;
  HG.smoothOff = HG.smoothOff * 0.7 + raw * 0.3;

  if (HG.calibrating) {
    HG.calVals.push(HG.smoothOff);
    if (HG.calVals.length >= HG.CAL_MIN) {
      HG.baseline = HG.calVals.reduce((a, b) => a + b, 0) / HG.calVals.length;
      HG.calibrating = false;
      if (cal) cal.classList.remove('show');
      if (HG.calFailsafe) {
        clearTimeout(HG.calFailsafe);
        HG.calFailsafe = null;
      }
    }
    return;
  }

  const delta = HG.smoothOff - HG.baseline;
  let dir = 0;
  if (delta < -HG.THRESH) dir = -1;
  else if (delta > HG.THRESH) dir = 1;

  const now = performance.now();
  const L = document.getElementById('headgameLaneL');
  const R = document.getElementById('headgameLaneR');
  if (dir === 0) {
    HG.dwellDir = 0;
    HG.dwellSince = 0;
    if (L) L.classList.remove('hot');
    if (R) R.classList.remove('hot');
  } else {
    if (dir !== HG.dwellDir) {
      HG.dwellDir = dir;
      HG.dwellSince = now;
    } else if (now - HG.dwellSince > HG.DWELL_MS) {
      headgameCommitPick(dir === -1 ? 0 : 1);
      return;
    }
    if (L) L.classList.toggle('hot', dir === -1);
    if (R) R.classList.toggle('hot', dir === 1);
  }
}"""

new_face = """function headgameComputeTilt(lm) {
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
}

function headgameUpdateTiltHud(dir) {
  const hud = document.getElementById('headgameTiltHud');
  if (!hud) return;
  hud.classList.remove('active-left', 'active-right');
  if (dir === -1) {
    hud.textContent = '← Tilting left — hold…';
    hud.classList.add('active-left');
  } else if (dir === 1) {
    hud.textContent = 'Tilting right → — hold…';
    hud.classList.add('active-right');
  } else if (HG.calibrating) {
    hud.textContent = 'Look straight at the camera…';
  } else {
    hud.textContent = 'Tilt toward green (left) or navy (right)';
  }
}

function headgameOnFaceResults(results) {
  if (!HG.running || HG.answered || !HG.useCam) return;
  const lm = results.multiFaceLandmarks && results.multiFaceLandmarks[0];
  const cal = document.getElementById('headgameCalLabel');

  if (!lm) {
    headgameUpdateTiltHud(0);
    return;
  }

  const raw = headgameComputeTilt(lm);
  HG.smoothTilt = (HG.smoothTilt || 0) * 0.65 + raw * 0.35;

  if (HG.calibrating) {
    HG.calVals.push(HG.smoothTilt);
    if (HG.calVals.length >= HG.CAL_MIN) {
      HG.baseline = HG.calVals.reduce((a, b) => a + b, 0) / HG.calVals.length;
      HG.calibrating = false;
      if (cal) cal.classList.remove('show');
      if (HG.calFailsafe) {
        clearTimeout(HG.calFailsafe);
        HG.calFailsafe = null;
      }
    }
    headgameUpdateTiltHud(0);
    return;
  }

  const delta = HG.smoothTilt - HG.baseline;
  let dir = 0;
  if (delta > HG.THRESH) dir = -1;
  else if (delta < -HG.THRESH) dir = 1;

  const now = performance.now();
  const L = document.getElementById('headgameLaneL');
  const R = document.getElementById('headgameLaneR');
  headgameUpdateTiltHud(dir);

  if (dir === 0) {
    HG.dwellDir = 0;
    HG.dwellSince = 0;
    if (L) L.classList.remove('hot');
    if (R) R.classList.remove('hot');
  } else {
    if (dir !== HG.dwellDir) {
      HG.dwellDir = dir;
      HG.dwellSince = now;
    } else if (now - HG.dwellSince > HG.DWELL_MS) {
      headgameCommitPick(dir === -1 ? 0 : 1);
      return;
    }
    if (L) L.classList.toggle('hot', dir === -1);
    if (R) R.classList.toggle('hot', dir === 1);
  }
}"""

if old_face in text:
    text = text.replace(old_face, new_face, 1)
    print('Replaced face handler')
else:
    print('Face handler not found')

# HG object: smoothOff -> smoothTilt in cal failsafe
text = text.replace('HG.smoothOff = 0;', 'HG.smoothTilt = 0;')
text = text.replace('HG.baseline = HG.smoothOff;', 'HG.baseline = HG.smoothTilt;')

# Add smoothTilt to HG if missing
if 'smoothTilt:' not in text:
    text = text.replace('smoothOff: 0,', 'smoothTilt: 0,')

p.write_text(text, encoding='utf-8')
print('Done')
