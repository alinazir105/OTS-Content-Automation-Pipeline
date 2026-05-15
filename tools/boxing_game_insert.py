# -*- coding: utf-8 -*-
"""Insert Multiplication Boxing game into class 4 math 03.html"""
from pathlib import Path

HTML = Path(__file__).resolve().parents[1] / "output" / "class 4" / "math" / "03.html"
text = HTML.read_text(encoding="utf-8")

POSE_SCRIPTS = '''
<script defer src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils@0.3.1675466862/camera_utils.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/@mediapipe/pose@0.5.1675469404/pose.js"></script>
'''

BOXING_CSS = r'''
/* ===== MULTIPLICATION BOXING ARENA ===== */
.boxing-teaser-section { background: linear-gradient(180deg, #1a2330 0%, #2c3e50 45%, #1e2d40 100%); color: #fff; }
.boxing-teaser-section .section-label { background: var(--amber); }
.boxing-teaser-section h2 { color: #fff; }
.boxing-teaser-section p { color: rgba(255,255,255,0.88); }
.boxing-teaser-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 20px; margin-top: 24px; }
.boxing-teaser-card { background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.12); border-radius: 18px; padding: 24px; }
.boxing-teaser-card h3 { font-family: 'Poppins', sans-serif; color: #fff; margin-bottom: 10px; font-size: 1.15rem; }
.boxing-teaser-card p { font-size: 0.95rem; line-height: 1.55; }
.boxing-launch-btn { margin-top: 20px; background: var(--amber); color: #fff; border: none; padding: 16px 36px; border-radius: 999px; font-family: 'Poppins', sans-serif; font-weight: 800; font-size: 1.05rem; cursor: pointer; box-shadow: 0 8px 28px rgba(240,147,43,0.45); transition: transform 0.2s, box-shadow 0.2s; }
.boxing-launch-btn:hover { transform: translateY(-2px) scale(1.02); box-shadow: 0 12px 36px rgba(240,147,43,0.55); }

body.boxing-no-scroll { overflow: hidden; }
.boxing-shell {
  position: fixed; inset: 0; z-index: 10050;
  background: #0a0e14;
  display: none; flex-direction: column;
  opacity: 0; transition: opacity 0.35s ease;
}
.boxing-shell.is-open { display: flex; opacity: 1; }
.boxing-shell[hidden] { display: none !important; }
.boxing-close {
  position: absolute; top: 14px; right: 14px; z-index: 30;
  background: rgba(255,255,255,0.12); color: #fff; border: 1px solid rgba(255,255,255,0.2);
  padding: 10px 18px; border-radius: 999px; font-family: 'Poppins', sans-serif; font-weight: 700;
  cursor: pointer; backdrop-filter: blur(8px);
}
.boxing-intro, .boxing-end {
  margin: auto; max-width: 480px; text-align: center; padding: 32px 28px;
  background: rgba(255,255,255,0.06); border-radius: 22px; border: 1px solid rgba(255,255,255,0.12);
  color: #fff;
}
.boxing-intro h3, .boxing-end h3 { font-family: 'Poppins', sans-serif; font-size: 1.6rem; margin-bottom: 12px; }
.boxing-intro p, .boxing-end p { color: rgba(255,255,255,0.85); line-height: 1.6; margin-bottom: 20px; }
.boxing-intro .accent { color: var(--amber); font-weight: 800; }

.boxing-arena {
  flex: 1; display: none; flex-direction: column; min-height: 0;
  position: relative; overflow: hidden;
}
.boxing-arena.is-active { display: flex; }
.boxing-ring {
  flex: 1; position: relative; perspective: 900px;
  background:
    radial-gradient(ellipse 80% 40% at 50% 100%, rgba(106,176,76,0.15), transparent 60%),
    radial-gradient(ellipse 120% 80% at 50% 30%, #1a2838, #0a0e14 70%);
}
.boxing-ring-floor {
  position: absolute; bottom: 0; left: -20%; right: -20%; height: 38%;
  background: linear-gradient(180deg, #2c3e50 0%, #1a2330 100%);
  transform: rotateX(58deg); transform-origin: bottom center;
  border-top: 4px solid rgba(240,147,43,0.6);
  box-shadow: 0 -20px 60px rgba(0,0,0,0.5);
}
.boxing-ropes {
  position: absolute; inset: 12% 8% 28% 8%; pointer-events: none;
  border: 3px solid rgba(255,255,255,0.08);
  border-radius: 8px;
  box-shadow: inset 0 0 80px rgba(0,0,0,0.4);
}
.boxing-opponent {
  position: absolute; left: 50%; top: 18%; transform: translateX(-50%);
  width: min(280px, 42vw); height: min(380px, 50vh);
  display: flex; flex-direction: column; align-items: center;
  transition: transform 0.35s ease, filter 0.3s;
}
.opp-head {
  width: 88px; height: 96px; border-radius: 50% 50% 46% 46%;
  background: linear-gradient(180deg, #d4a574 0%, #a67c52 100%);
  border: 3px solid rgba(0,0,0,0.2);
  box-shadow: 0 8px 24px rgba(0,0,0,0.35);
  position: relative; z-index: 3;
}
.opp-head::after {
  content: ''; position: absolute; inset: 18% 20% 45% 20%;
  background: #2c3e50; border-radius: 50%; opacity: 0.85;
}
.opp-body {
  width: 140px; height: 160px; margin-top: -12px;
  background: linear-gradient(180deg, #c0392b 0%, #922b21 100%);
  border-radius: 24px 24px 40px 40px;
  border: 3px solid rgba(0,0,0,0.25);
  box-shadow: 0 12px 32px rgba(0,0,0,0.4);
  z-index: 2;
}
.opp-gloves-row {
  display: flex; gap: 100px; margin-top: -28px; z-index: 4;
}
.opp-glove {
  width: 56px; height: 56px; border-radius: 50%;
  background: linear-gradient(145deg, #e74c3c, #c0392b);
  border: 3px solid #922b21;
  box-shadow: 0 6px 16px rgba(0,0,0,0.35);
}
.boxing-opponent.hit { animation: opp-hit 0.45s ease; }
.boxing-opponent.dodge { animation: opp-dodge 0.5s ease; }
@keyframes opp-hit {
  0%, 100% { transform: translateX(-50%); }
  25% { transform: translateX(-50%) rotate(-6deg) scale(0.96); filter: brightness(1.3); }
  50% { transform: translateX(-48%) translateY(8px); }
}
@keyframes opp-dodge {
  0%, 100% { transform: translateX(-50%); }
  40% { transform: translateX(-42%); }
}
.boxing-screen-shake { animation: screen-shake 0.4s ease; }
@keyframes screen-shake {
  0%, 100% { transform: translate(0); }
  20% { transform: translate(-8px, 4px); }
  40% { transform: translate(8px, -4px); }
  60% { transform: translate(-6px, -2px); }
  80% { transform: translate(6px, 2px); }
}

.boxing-hud-top {
  position: absolute; top: 0; left: 0; right: 0; z-index: 20;
  padding: 56px 20px 12px;
  display: flex; justify-content: space-between; align-items: flex-start;
  pointer-events: none;
}
.boxing-health-bar {
  flex: 1; max-width: 200px;
}
.boxing-health-bar label {
  font-family: 'Poppins', sans-serif; font-size: 0.7rem; font-weight: 700;
  color: rgba(255,255,255,0.7); text-transform: uppercase; letter-spacing: 0.08em;
}
.boxing-health-track {
  height: 12px; background: rgba(0,0,0,0.4); border-radius: 999px; overflow: hidden; margin-top: 4px;
  border: 1px solid rgba(255,255,255,0.15);
}
.boxing-health-fill {
  height: 100%; border-radius: 999px; transition: width 0.4s ease;
}
.boxing-health-fill.you { background: linear-gradient(90deg, #6ab04c, #4e8a34); width: 100%; }
.boxing-health-fill.opp { background: linear-gradient(90deg, #e74c3c, #c0392b); width: 100%; }
.boxing-round-badge {
  font-family: 'Poppins', sans-serif; font-weight: 800; font-size: 0.9rem;
  background: rgba(0,0,0,0.45); color: var(--amber); padding: 8px 16px; border-radius: 999px;
  border: 1px solid rgba(240,147,43,0.4);
}

.boxing-question-panel {
  position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
  z-index: 15; width: min(92%, 720px); text-align: center; pointer-events: none;
}
.boxing-question-text {
  font-family: 'Poppins', sans-serif; font-weight: 800;
  font-size: clamp(1.8rem, 5vw, 2.8rem); color: #fff;
  text-shadow: 0 4px 24px rgba(0,0,0,0.8);
  margin-bottom: 20px;
}
.boxing-options-row {
  display: grid; grid-template-columns: 1fr 1fr; gap: 16px;
  pointer-events: auto;
}
.boxing-option {
  background: rgba(255,255,255,0.1); border: 3px solid rgba(255,255,255,0.25);
  border-radius: 18px; padding: 20px 16px; cursor: pointer;
  font-family: 'Poppins', sans-serif; font-weight: 800; font-size: clamp(1.4rem, 4vw, 2rem);
  color: #fff; transition: transform 0.2s, border-color 0.2s, background 0.2s;
  backdrop-filter: blur(6px);
}
.boxing-option.left { border-color: rgba(106,176,76,0.5); }
.boxing-option.right { border-color: rgba(52,152,219,0.5); }
.boxing-option.hot { transform: scale(1.05); border-color: var(--amber); background: rgba(240,147,43,0.25); }
.boxing-option.locked { border-color: var(--amber); box-shadow: 0 0 24px rgba(240,147,43,0.5); }
.boxing-option.correct { border-color: #6ab04c; background: rgba(106,176,76,0.35); }
.boxing-option.wrong { border-color: #e74c3c; background: rgba(231,76,60,0.3); }
.boxing-option small {
  display: block; font-size: 0.65rem; font-weight: 700; letter-spacing: 0.1em;
  opacity: 0.85; margin-bottom: 6px; text-transform: uppercase;
}
.boxing-option:disabled { cursor: default; }

.boxing-punch-hint {
  position: absolute; bottom: 22%; left: 50%; transform: translateX(-50%);
  z-index: 12; font-family: 'Poppins', sans-serif; font-weight: 700;
  font-size: 0.9rem; color: rgba(255,255,255,0.75);
  text-align: center; padding: 8px 20px; border-radius: 999px;
  background: rgba(0,0,0,0.45);
}
.boxing-player-gloves {
  position: absolute; bottom: 8%; left: 0; right: 0; z-index: 10;
  display: flex; justify-content: space-between; padding: 0 8%;
  pointer-events: none;
}
.boxing-p-glove {
  width: 80px; height: 80px; border-radius: 50%;
  background: linear-gradient(145deg, #3498db, #2980b9);
  border: 4px solid #1a5276;
  box-shadow: 0 10px 30px rgba(0,0,0,0.5);
  opacity: 0.9;
}
.boxing-p-glove.punch-l { animation: p-punch-l 0.35s ease; }
.boxing-p-glove.punch-r { animation: p-punch-r 0.35s ease; }
@keyframes p-punch-l {
  0% { transform: translate(0,0) scale(1); }
  50% { transform: translate(60px, -40px) scale(1.15); }
  100% { transform: translate(0,0) scale(1); }
}
@keyframes p-punch-r {
  0% { transform: translate(0,0) scale(1); }
  50% { transform: translate(-60px, -40px) scale(1.15); }
  100% { transform: translate(0,0) scale(1); }
}

.boxing-cam-pip {
  position: absolute; bottom: 14px; right: 14px; z-index: 25;
  width: 140px; height: 105px; border-radius: 12px; overflow: hidden;
  border: 2px solid rgba(255,255,255,0.25);
  box-shadow: 0 8px 24px rgba(0,0,0,0.5);
  background: #111;
}
.boxing-cam-pip video { width: 100%; height: 100%; object-fit: cover; transform: scaleX(-1); }
.boxing-cal {
  position: absolute; bottom: 6px; left: 50%; transform: translateX(-50%);
  font-size: 0.72rem; font-weight: 700; color: var(--amber);
  background: rgba(0,0,0,0.7); padding: 4px 10px; border-radius: 999px;
  white-space: nowrap; opacity: 0; transition: opacity 0.2s;
}
.boxing-cal.show { opacity: 1; }
.boxing-flash-msg {
  position: absolute; top: 42%; left: 50%; transform: translate(-50%, -50%);
  z-index: 22; font-family: 'Poppins', sans-serif; font-weight: 800;
  font-size: clamp(1.2rem, 4vw, 1.8rem); color: #fff;
  padding: 12px 28px; border-radius: 999px; background: rgba(0,0,0,0.75);
  opacity: 0; pointer-events: none; transition: opacity 0.2s;
}
.boxing-flash-msg.show { opacity: 1; }
@media (max-width: 600px) {
  .boxing-cam-pip { width: 110px; height: 82px; }
  .boxing-options-row { gap: 10px; }
  .opp-gloves-row { gap: 60px; }
}
'''

TEASER_HTML = '''
<hr class="section-divider"/>

<!-- MULTIPLICATION BOXING -->
<section class="section-wrap boxing-teaser-section" id="sec-boxing" data-section="boxing">
  <motion.div style="max-width:1100px;margin:0 auto;">
    <div class="section-label">🥊 Arena</motion.div>
    <h2>Multiplication Boxing Match</h2>
    <p>Face your opponent in a first-person ring! Punch <strong>left</strong> or <strong>right</strong> to pick the product. Correct answers land hits — wrong answers mean a counter-punch. Win by landing more hits than you take.</p>
    <div class="boxing-teaser-grid">
      <div class="boxing-teaser-card">
        <h3>🎥 Camera punches</h3>
        <p>MediaPipe tracks your arms. Jab left for the left answer, jab right for the right answer — or tap on screen.</p>
      </div>
      <div class="boxing-teaser-card">
        <h3>🧠 Class 4 multiplication</h3>
        <p>Times tables and multi-digit problems. Every round is a new matchup with two choices — only one is correct.</p>
      </div>
      <div class="boxing-teaser-card">
        <h3>🏆 Win the belt</h3>
        <p>Beat the opponent when your correct hits outnumber your misses. Health bars show who is winning the fight.</p>
      </div>
    </div>
    <button type="button" class="boxing-launch-btn" id="btnBoxingOpen">🥊 Enter the Ring</button>
  </div>
</section>
'''.replace('<motion.div', '<div').replace('</motion.div>', '</div>')

SHELL_HTML = '''
<!-- BOXING MATCH FULLSCREEN -->
<div id="boxing-shell" class="boxing-shell" hidden aria-modal="true">
  <button type="button" class="boxing-close" id="boxingClose">✕ Exit</button>

  <div id="boxingIntro" class="boxing-intro">
    <div style="font-size:3rem;margin-bottom:8px;">🥊</motion.div>
    <h3>Multiplication Boxing</h3>
    <p>You're in the ring! See the problem, then <span class="accent">jab LEFT</span> or <span class="accent">jab RIGHT</span> for your answer. Your camera detects your punches. Win by scoring more hits than your opponent.</p>
    <button type="button" class="boxing-launch-btn" id="boxingBtnCam">📷 Fight with camera</button>
    <div style="margin-top:12px;"><button type="button" class="boxing-launch-btn" id="boxingBtnTap" style="background:transparent;border:2px solid rgba(255,255,255,0.4);box-shadow:none;">👆 Tap only (no camera)</button></div>
  </div>

  <div id="boxingArena" class="boxing-arena">
    <div class="boxing-hud-top">
      <div class="boxing-health-bar">
        <label>You</label>
        <div class="boxing-health-track"><div class="boxing-health-fill you" id="boxingHealthYou"></div></div>
      </div>
      <span class="boxing-round-badge" id="boxingRoundBadge">Round 1 / 8</span>
      <div class="boxing-health-bar" style="text-align:right;">
        <label>Opponent</label>
        <div class="boxing-health-track"><div class="boxing-health-fill opp" id="boxingHealthOpp"></motion.div></div>
      </div>
    </div>

    <div class="boxing-ring" id="boxingRing">
      <div class="boxing-ring-floor"></div>
      <div class="boxing-ropes"></div>
      <div class="boxing-opponent" id="boxingOpponent">
        <div class="opp-head"></div>
        <div class="opp-body"></div>
        <div class="opp-gloves-row">
          <div class="opp-glove"></div>
          <div class="opp-glove"></div>
        </div>
      </div>
      <div class="boxing-question-panel">
        <div class="boxing-question-text" id="boxingQuestion">6 × 7 = ?</div>
        <div class="boxing-options-row">
          <button type="button" class="boxing-option left" id="boxingOptL" disabled>
            <small>← Jab left</small><span id="boxingValL">42</span>
          </button>
          <button type="button" class="boxing-option right" id="boxingOptR" disabled>
            <small>Jab right →</small><span id="boxingValR">48</span>
          </button>
        </div>
      </div>
      <p class="boxing-punch-hint" id="boxingPunchHint">Put hands up — calibrating…</p>
      <div class="boxing-player-gloves">
        <div class="boxing-p-glove" id="boxingPGloveL"></div>
        <div class="boxing-p-glove" id="boxingPGloveR"></motion.div>
      </div>
      <div class="boxing-flash-msg" id="boxingFlash" role="status"></div>
    </div>

    <div class="boxing-cam-pip" id="boxingCamPip">
      <video id="boxingVideo" playsinline muted autoplay></video>
      <span class="boxing-cal" id="boxingCal">Hands up — calibrating…</span>
    </div>
  </div>

  <div id="boxingEnd" class="boxing-end" style="display:none;">
    <div style="font-size:2.5rem;">🏆</motion.div>
    <h3 id="boxingEndTitle">Victory!</h3>
    <p id="boxingEndStats"></p>
    <button type="button" class="boxing-launch-btn" id="boxingBtnAgain">🔄 Rematch</button>
  </div>
</div>
'''.replace('<motion.div', '<div').replace('</motion.div>', '</motion.div>')
# fix broken replacements
SHELL_HTML = SHELL_HTML.replace('</motion.div>', '</motion.div>')
while '<motion.div' in SHELL_HTML or '</motion.div>' in SHELL_HTML:
    SHELL_HTML = SHELL_HTML.replace('<motion.div', '<div').replace('</motion.div>', '</div>')

BOXING_JS = r'''
// ===== MULTIPLICATION BOXING =====
const BX = {
  useCam: false,
  lastMode: 'cam',
  running: false,
  round: 0,
  totalRounds: 8,
  questions: [],
  lockedSide: null,
  resolving: false,
  youHits: 0,
  oppHits: 0,
  playerHp: 100,
  oppHp: 100,
  stream: null,
  mpCamera: null,
  pose: null,
  calibrating: true,
  calFrames: 0,
  baselineL: 0,
  baselineR: 0,
  smoothL: 0,
  smoothR: 0,
  dwellDir: 0,
  dwellSince: 0,
  PUNCH_THRESH: 0.11,
  DWELL_MS: 520,
  CAL_FRAMES: 20
};

function bxGenQuestions(n) {
  const qs = [];
  const used = new Set();
  while (qs.length < n) {
    const a = 2 + Math.floor(Math.random() * 11);
    const b = 2 + Math.floor(Math.random() * 11);
    const key = a + 'x' + b;
    if (used.has(key)) continue;
    used.add(key);
    const correct = a * b;
    let wrong = correct + (Math.random() < 0.5 ? -1 : 1) * (2 + Math.floor(Math.random() * 6));
    if (wrong <= 0 || wrong === correct) wrong = correct + 5;
    const leftCorrect = Math.random() < 0.5;
    qs.push({
      a, b, correct,
      left: leftCorrect ? correct : wrong,
      right: leftCorrect ? wrong : correct,
      correctSide: leftCorrect ? 0 : 1
    });
  }
  return qs;
}

function bxStopPipeline() {
  try { if (BX.pose) BX.pose.onResults(() => {}); } catch (e) {}
  try { if (BX.mpCamera) { BX.mpCamera.stop(); BX.mpCamera = null; } } catch (e) {}
  try { if (BX.pose && BX.pose.close) BX.pose.close(); } catch (e) {}
  BX.pose = null;
  if (BX.stream) {
    BX.stream.getTracks().forEach(t => { try { t.stop(); } catch (e2) {} });
    BX.stream = null;
  }
  const v = document.getElementById('boxingVideo');
  if (v) try { v.srcObject = null; } catch (e3) {}
  BX.running = false;
}

function bxOpen() {
  const shell = document.getElementById('boxing-shell');
  if (!shell) return;
  shell.removeAttribute('hidden');
  requestAnimationFrame(() => shell.classList.add('is-open'));
  document.body.classList.add('boxing-no-scroll');
  document.getElementById('boxingIntro').style.display = '';
  document.getElementById('boxingArena').classList.remove('is-active');
  document.getElementById('boxingEnd').style.display = 'none';
}

function bxClose() {
  bxStopPipeline();
  const shell = document.getElementById('boxing-shell');
  if (shell) { shell.classList.remove('is-open'); shell.setAttribute('hidden', ''); }
  document.body.classList.remove('boxing-no-scroll');
}

function bxFlash(text, ms) {
  const el = document.getElementById('boxingFlash');
  if (!el) return;
  el.textContent = text;
  el.classList.add('show');
  setTimeout(() => el.classList.remove('show'), ms || 900);
}

function bxSetHealth() {
  const y = document.getElementById('boxingHealthYou');
  const o = document.getElementById('boxingHealthOpp');
  if (y) y.style.width = Math.max(0, BX.playerHp) + '%';
  if (o) o.style.width = Math.max(0, BX.oppHp) + '%';
}

function bxClearOpts() {
  ['boxingOptL', 'boxingOptR'].forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    el.classList.remove('hot', 'locked', 'correct', 'wrong');
    el.disabled = false;
  });
}

function bxLockPick(side) {
  if (!BX.running || BX.resolving || BX.lockedSide !== null) return;
  if (side !== 0 && side !== 1) return;
  BX.lockedSide = side;
  bxClearOpts();
  const L = document.getElementById('boxingOptL');
  const R = document.getElementById('boxingOptR');
  if (L) { L.classList.toggle('locked', side === 0); L.disabled = true; }
  if (R) { R.classList.toggle('locked', side === 1); R.disabled = true; }
  bxFlash('🔒 Locked!', 500);
}

function bxResolveRound() {
  if (!BX.running || BX.resolving) return;
  BX.resolving = true;
  const q = BX.questions[BX.round];
  const pick = BX.lockedSide;
  const correct = pick !== null && pick === q.correctSide;
  const opp = document.getElementById('boxingOpponent');
  const ring = document.getElementById('boxingRing');
  const gL = document.getElementById('boxingPGloveL');
  const gR = document.getElementById('boxingPGloveR');
  const L = document.getElementById('boxingOptL');
  const R = document.getElementById('boxingOptR');

  if (pick === 0 && gL) { gL.classList.add('punch-l'); setTimeout(() => gL.classList.remove('punch-l'), 400); }
  if (pick === 1 && gR) { gR.classList.add('punch-r'); setTimeout(() => gR.classList.remove('punch-r'), 400); }

  if (correct) {
    BX.youHits++;
    BX.oppHp = Math.max(0, BX.oppHp - 14);
    if (opp) { opp.classList.remove('dodge'); opp.classList.add('hit'); setTimeout(() => opp.classList.remove('hit'), 500); }
    bxFlash('💥 Solid hit!', 800);
    if (L && R) {
      if (q.correctSide === 0) L.classList.add('correct'); else R.classList.add('correct');
    }
  } else {
    BX.oppHits++;
    BX.playerHp = Math.max(0, BX.playerHp - 14);
    if (opp) { opp.classList.remove('hit'); opp.classList.add('dodge'); setTimeout(() => opp.classList.remove('dodge'), 500); }
    if (ring) { ring.classList.add('boxing-screen-shake'); setTimeout(() => ring.classList.remove('boxing-screen-shake'), 450); }
    bxFlash(pick === null ? '⏰ No punch — countered!' : '😵 Counter punch!', 900);
    if (L && R) {
      if (q.correctSide === 0) L.classList.add('correct');
      else R.classList.add('correct');
      if (pick !== null) (pick === 0 ? L : R).classList.add('wrong');
    }
  }
  bxSetHealth();

  setTimeout(() => {
    BX.round++;
  BX.lockedSide = null;
    BX.resolving = false;
    if (BX.round >= BX.totalRounds || BX.playerHp <= 0 || BX.oppHp <= 0) bxFinish();
    else bxBeginRound();
  }, 1600);
}

function bxBeginRound() {
  const q = BX.questions[BX.round];
  if (!q) return;
  BX.lockedSide = null;
  BX.resolving = false;
  BX.calibrating = BX.useCam;
  BX.calFrames = 0;
  BX.baselineL = 0;
  BX.baselineR = 0;
  BX.dwellDir = 0;
  bxClearOpts();

  const badge = document.getElementById('boxingRoundBadge');
  if (badge) badge.textContent = 'Round ' + (BX.round + 1) + ' / ' + BX.totalRounds;
  document.getElementById('boxingQuestion').textContent = q.a + ' × ' + q.b + ' = ?';
  document.getElementById('boxingValL').textContent = String(q.left);
  document.getElementById('boxingValR').textContent = String(q.right);

  const hint = document.getElementById('boxingPunchHint');
  const cal = document.getElementById('boxingCal');
  if (BX.useCam) {
    if (hint) hint.textContent = 'Hands up — then jab toward an answer';
    if (cal) cal.classList.add('show');
  } else {
    if (hint) hint.textContent = 'Tap left or right to punch';
    if (cal) cal.classList.remove('show');
    BX.calibrating = false;
  }

  try {
    if (typeof gsap !== 'undefined') {
      gsap.fromTo('#boxingQuestion', { scale: 0.85, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.5, ease: 'back.out(1.4)' });
    }
  } catch (e) {}
}

function bxFinish() {
  bxStopPipeline();
  document.getElementById('boxingArena').classList.remove('is-active');
  const end = document.getElementById('boxingEnd');
  end.style.display = 'block';
  const won = BX.youHits > BX.oppHits && BX.playerHp > 0;
  const draw = BX.youHits === BX.oppHits;
  document.getElementById('boxingEndTitle').textContent = won ? '🏆 You Win!' : (draw ? '🤝 Draw!' : '😵 Knockout!');
  document.getElementById('boxingEndStats').innerHTML =
    'Your hits: <strong>' + BX.youHits + '</strong> · Opponent hits: <strong>' + BX.oppHits + '</strong><br>' +
    (won ? 'Great multiplication — and great jabs!' : 'Keep practicing your times tables and come back!');
}

function bxComputePunchSignals(lm) {
  const ls = lm[11], rs = lm[12], lw = lm[15], rw = lm[16];
  const mx = x => 1 - x;
  const leftExt = mx(ls.x) - mx(lw.x);
  const rightExt = mx(rw.x) - mx(rs.x);
  return { leftExt, rightExt };
}

function bxOnPoseResults(results) {
  if (!BX.running || BX.resolving || BX.lockedSide !== null || !BX.useCam) return;
  const lm = results.poseLandmarks;
  if (!lm) return;
  const { leftExt, rightExt } = bxComputePunchSignals(lm);
  BX.smoothL = BX.smoothL * 0.55 + leftExt * 0.45;
  BX.smoothR = BX.smoothR * 0.55 + rightExt * 0.45;

  if (BX.calibrating) {
    BX.baselineL = (BX.baselineL * BX.calFrames + BX.smoothL) / (BX.calFrames + 1);
    BX.baselineR = (BX.baselineR * BX.calFrames + BX.smoothR) / (BX.calFrames + 1);
    BX.calFrames++;
    if (BX.calFrames >= BX.CAL_FRAMES) {
      BX.calibrating = false;
      const cal = document.getElementById('boxingCal');
      if (cal) cal.classList.remove('show');
      document.getElementById('boxingPunchHint').textContent = 'Jab LEFT or RIGHT toward an answer!';
    }
    return;
  }

  const dL = BX.smoothL - BX.baselineL;
  const dR = BX.smoothR - BX.baselineR;
  let dir = 0;
  if (dL > BX.PUNCH_THRESH && dL > dR) dir = -1;
  else if (dR > BX.PUNCH_THRESH && dR > dL) dir = 1;

  const L = document.getElementById('boxingOptL');
  const R = document.getElementById('boxingOptR');
  const now = performance.now();

  if (dir === 0) {
    BX.dwellDir = 0;
    BX.dwellSince = 0;
    if (L) L.classList.remove('hot');
    if (R) R.classList.remove('hot');
  } else {
    if (dir !== BX.dwellDir) { BX.dwellDir = dir; BX.dwellSince = now; }
    else if (now - BX.dwellSince > BX.DWELL_MS) {
      bxLockPick(dir === -1 ? 0 : 1);
      setTimeout(() => { if (BX.lockedSide !== null && !BX.resolving) bxResolveRound(); }, 400);
      return;
    }
    if (L) L.classList.toggle('hot', dir === -1);
    if (R) R.classList.toggle('hot', dir === 1);
  }
}

async function bxStartCam() {
  bxStopPipeline();
  await new Promise(r => setTimeout(r, 300));
  BX.lastMode = 'cam';
  BX.useCam = true;
  document.getElementById('boxingIntro').style.display = 'none';
  document.getElementById('boxingEnd').style.display = 'none';
  document.getElementById('boxingArena').classList.add('is-active');
  document.getElementById('boxingCamPip').style.display = '';

  const video = document.getElementById('boxingVideo');
  try {
    BX.stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user', width: { ideal: 640 }, height: { ideal: 480 } }, audio: false });
    video.srcObject = BX.stream;
    await video.play().catch(() => {});
  } catch (e) {
    BX.useCam = false;
    return bxStartTap();
  }

  if (typeof Pose === 'undefined' || typeof Camera === 'undefined') {
    BX.useCam = false;
    document.getElementById('boxingCamPip').style.display = 'none';
    return bxStartTap();
  }

  const PV = '0.5.1675469404';
  try {
    BX.pose = new Pose({ locateFile: f => 'https://cdn.jsdelivr.net/npm/@mediapipe/pose@' + PV + '/' + f });
    BX.pose.setOptions({ modelComplexity: 1, smoothLandmarks: true, minDetectionConfidence: 0.5, minTrackingConfidence: 0.5 });
    BX.pose.onResults(bxOnPoseResults);
    BX.mpCamera = new Camera(video, {
      onFrame: async () => { if (BX.pose) await BX.pose.send({ image: video }); },
      width: 640, height: 480
    });
    BX.mpCamera.start();
  } catch (e2) {
    console.warn('Pose init', e2);
    BX.useCam = false;
    document.getElementById('boxingCamPip').style.display = 'none';
  }
  bxStartMatch();
}

function bxStartTap() {
  bxStopPipeline();
  BX.lastMode = 'tap';
  BX.useCam = false;
  BX.calibrating = false;
  document.getElementById('boxingIntro').style.display = 'none';
  document.getElementById('boxingEnd').style.display = 'none';
  document.getElementById('boxingArena').classList.add('is-active');
  document.getElementById('boxingCamPip').style.display = 'none';
  bxStartMatch();
}

function bxStartMatch() {
  BX.questions = bxGenQuestions(BX.totalRounds);
  BX.round = 0;
  BX.youHits = 0;
  BX.oppHits = 0;
  BX.playerHp = 100;
  BX.oppHp = 100;
  BX.running = true;
  bxSetHealth();
  bxBeginRound();
}

function initBoxingGame() {
  const open = document.getElementById('btnBoxingOpen');
  const close = document.getElementById('boxingClose');
  const cam = document.getElementById('boxingBtnCam');
  const tap = document.getElementById('boxingBtnTap');
  const again = document.getElementById('boxingBtnAgain');
  const optL = document.getElementById('boxingOptL');
  const optR = document.getElementById('boxingOptR');

  if (open) open.addEventListener('click', bxOpen);
  if (close) close.addEventListener('click', bxClose);
  if (cam) cam.addEventListener('click', () => bxStartCam());
  if (tap) tap.addEventListener('click', () => bxStartTap());
  if (again) again.addEventListener('click', async () => {
    document.getElementById('boxingEnd').style.display = 'none';
    bxStopPipeline();
    await new Promise(r => setTimeout(r, 320));
    if (BX.lastMode === 'tap') bxStartTap(); else bxStartCam();
  });
  if (optL) optL.addEventListener('click', () => {
    if (BX.lockedSide !== null || BX.resolving) return;
    bxLockPick(0);
    setTimeout(() => bxResolveRound(), 400);
  });
  if (optR) optR.addEventListener('click', () => {
    if (BX.lockedSide !== null || BX.resolving) return;
    bxLockPick(1);
    setTimeout(() => bxResolveRound(), 400);
  });
  document.addEventListener('keydown', ev => {
    const shell = document.getElementById('boxing-shell');
    if (!shell || shell.hasAttribute('hidden')) return;
    if (ev.key === 'Escape') bxClose();
  });
}
'''

# Apply insertions
if '@mediapipe/pose' not in text:
    text = text.replace(
        '<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>',
        '<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>' + POSE_SCRIPTS
    )

if '.boxing-shell' not in text:
    text = text.replace('</style>', BOXING_CSS + '\n</style>', 1)

if 'sec-boxing' not in text:
    text = text.replace('<hr class="section-divider"/>\n\n<main>', '<hr class="section-divider"/>' + TEASER_HTML + '\n\n<main>', 1)

if 'boxing-shell' not in text:
    text = text.replace('<!-- MOBILE BOTTOM NAV -->', SHELL_HTML + '\n<!-- MOBILE BOTTOM NAV -->', 1)

if "const sections = ['sec-hero','sec-tens'" in text:
    text = text.replace(
        "const sections = ['sec-hero','sec-tens'",
        "const sections = ['sec-hero','sec-boxing','sec-tens'"
    )

if 'data-section="boxing"' not in text.split('progress-dots')[1][:800]:
    text = text.replace(
        '<motion.div class="progress-dot active" data-section="0" title="Introduction"></div>'.replace('motion.div','motion.div'),
        '<div class="progress-dot active" data-section="0" title="Introduction"></div>\n    <div class="progress-dot" data-section="boxing" title="Boxing"></div>'
    )
    # fix - use exact
    old_dots = '''    <motion.div class="progress-dot active" data-section="0" title="Introduction"></div>'''
    old_dots = '    <div class="progress-dot active" data-section="0" title="Introduction"></motion.div>'
    old_dots = '    <div class="progress-dot active" data-section="0" title="Introduction"></div>'
    if old_dots in text and 'title="Boxing"' not in text:
        text = text.replace(old_dots, old_dots + '\n    <div class="progress-dot" data-section="boxing" title="Boxing"></div>')

if 'initBoxingGame' not in text:
    text = text.replace(
        '  // PROGRESS DOTS',
        '  initBoxingGame();\n\n  // PROGRESS DOTS'
    )

if 'MULTIPLICATION BOXING' not in text:
    text = text.replace('</script>\n</body>', BOXING_JS + '\n</script>\n</body>', 1)

# mobile nav
if 'sec-boxing' in text and '#sec-boxing' not in text:
    text = text.replace(
        '<a href="#sec-tens"><span class="nav-icon">🔟</span>×10s</a>',
        '<a href="#sec-boxing"><span class="nav-icon">🥊</span>Boxing</a>\n    <a href="#sec-tens"><span class="nav-icon">🔟</span>×10s</a>'
    )

HTML.write_text(text, encoding='utf-8')
print('Inserted boxing game')
