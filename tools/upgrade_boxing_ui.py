# -*- coding: utf-8 -*-
from pathlib import Path

HTML = Path(__file__).resolve().parents[1] / "output" / "class 4" / "math" / "03.html"
text = HTML.read_text(encoding="utf-8")

intro_start = text.find('  <motion.div id="boxingIntro"')
if intro_start == -1:
    intro_start = text.find('  <div id="boxingIntro"')
intro_end = text.find('  </div>\n\n  <div id="boxingArena"', intro_start)
INTRO_OLD = text[intro_start:intro_end + len('  </div>')]

INTRO_NEW = """  <div id="boxingIntro" class="boxing-intro">
    <div class="boxing-intro-icon">🥊</div>
    <h3>Multiplication Boxing</h3>
    <p>You're in the ring! <span class="accent">Jab LEFT</span> or <span class="accent">jab RIGHT</span> to pick your answer. Win by landing more hits than your opponent.</p>
    <motion.div class="boxing-intro-actions">
      <button type="button" class="boxing-launch-btn" id="boxingBtnCam">📷 Fight with camera</button>
      <button type="button" class="boxing-launch-btn secondary" id="boxingBtnTap">👆 Tap only</button>
    </div>
  </div>"""

INTRO_NEW = INTRO_NEW.replace('<motion.div class="boxing-intro-actions">', '<div class="boxing-intro-actions">')

start = text.find('    <div class="boxing-ring" id="boxingRing">')
end = text.find('    </div>\n    <div class="boxing-cam-pip"', start)
RING_OLD = text[start:end + len('    </div>')]

RING_NEW = """    <div class="boxing-ring" id="boxingRing">
      <div class="boxing-ring-spotlight"></div>
      <div class="boxing-ring-floor"></div>
      <div class="boxing-ropes"></div>
      <div id="boxingFxLayer" class="boxing-fx-layer" aria-hidden="true"></div>
      <div class="boxing-opponent" id="boxingOpponent">
        <svg viewBox="0 0 200 260" xmlns="http://www.w3.org/2000/svg" aria-label="Boxing opponent">
          <defs>
            <linearGradient id="oppSkin" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#f0c9a0"/><stop offset="100%" stop-color="#d4a574"/></linearGradient>
            <linearGradient id="oppShorts" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#2C3E50"/><stop offset="100%" stop-color="#1a2838"/></linearGradient>
            <linearGradient id="oppGlove" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#e74c3c"/><stop offset="100%" stop-color="#c0392b"/></linearGradient>
          </defs>
          <ellipse cx="100" cy="248" rx="52" ry="10" fill="rgba(44,62,80,0.12)"/>
          <rect x="72" y="195" width="22" height="48" rx="10" fill="#2C3E50"/>
          <rect x="106" y="195" width="22" height="48" rx="10" fill="#2C3E50"/>
          <path d="M68 118 Q100 108 132 118 L128 198 Q100 208 72 198 Z" fill="url(#oppShorts)"/>
          <path d="M78 118 Q100 100 122 118 L118 155 Q100 162 82 155 Z" fill="#e8b89a"/>
          <path d="M68 125 Q42 145 38 175 Q36 188 48 192 Q58 194 62 180 Q66 158 72 140 Z" fill="url(#oppSkin)" stroke="#c49a6c" stroke-width="1.5"/>
          <path d="M132 125 Q158 145 162 175 Q164 188 152 192 Q142 194 138 180 Q134 158 128 140 Z" fill="url(#oppSkin)" stroke="#c49a6c" stroke-width="1.5"/>
          <ellipse cx="50" cy="188" rx="22" ry="20" fill="url(#oppGlove)" stroke="#922b21" stroke-width="2"/>
          <ellipse cx="150" cy="188" rx="22" ry="20" fill="url(#oppGlove)" stroke="#922b21" stroke-width="2"/>
          <circle cx="100" cy="72" r="38" fill="url(#oppSkin)" stroke="#c49a6c" stroke-width="1.5"/>
          <path d="M62 72 Q62 38 100 32 Q138 38 138 72 Q138 88 100 92 Q62 88 62 72 Z" fill="#2C3E50" opacity="0.9"/>
          <rect x="78" y="62" width="44" height="12" rx="4" fill="#fff" opacity="0.25"/>
          <ellipse cx="86" cy="74" rx="5" ry="6" fill="#2C3E50"/>
          <ellipse cx="114" cy="74" rx="5" ry="6" fill="#2C3E50"/>
          <circle cx="88" cy="72" r="1.5" fill="#fff"/>
          <circle cx="116" cy="72" r="1.5" fill="#fff"/>
          <rect x="58" y="218" width="84" height="22" rx="11" fill="#fff" stroke="#e8ecf1" stroke-width="1"/>
          <text x="100" y="233" text-anchor="middle" font-family="Poppins,sans-serif" font-size="11" font-weight="700" fill="#2C3E50">CHAMP</text>
        </svg>
      </div>
      <div class="boxing-question-panel">
        <div class="boxing-question-card">
          <div class="boxing-question-text" id="boxingQuestion">6 × 7 = ?</div>
          <div class="boxing-options-row">
            <button type="button" class="boxing-option left" id="boxingOptL"><small>← Jab left</small><span id="boxingValL">42</span></button>
            <button type="button" class="boxing-option right" id="boxingOptR"><small>Jab right →</small><span id="boxingValR">48</span></button>
          </div>
        </div>
      </div>
      <p class="boxing-punch-hint" id="boxingPunchHint">Put hands up — calibrating…</p>
      <div class="boxing-player-gloves">
        <motion.div class="boxing-p-glove left" id="boxingPGloveL"><span class="bx-glove-trail"></span></div>
        <div class="boxing-p-glove right" id="boxingPGloveR"><span class="bx-glove-trail"></span></motion.div>
      </div>
      <div class="boxing-flash-msg" id="boxingFlash" role="status"></div>
    </div>"""

RING_NEW = RING_NEW.replace('<motion.div class="boxing-p-glove left"', '<div class="boxing-p-glove left"')
RING_NEW = RING_NEW.replace('</motion.div>\n      </div>', '</div>\n      </div>', 1)

text = text.replace(INTRO_OLD, INTRO_NEW, 1)
text = text.replace(RING_OLD, RING_NEW, 1)

FX_JS = """
function bxSpawnPunchFx(kind, side) {
  var layer = document.getElementById('boxingFxLayer');
  var ring = document.getElementById('boxingRing');
  if (!layer) return;
  if (kind === 'hit') {
    var impact = document.createElement('div');
    impact.className = 'bx-impact';
    layer.appendChild(impact);
    setTimeout(function() { impact.remove(); }, 600);
    var pow = document.createElement('div');
    pow.className = 'bx-pow';
    pow.textContent = 'POW!';
    layer.appendChild(pow);
    setTimeout(function() { pow.remove(); }, 700);
    var flash = document.createElement('div');
    flash.className = 'bx-hit-flash';
    if (ring) { ring.appendChild(flash); setTimeout(function() { flash.remove(); }, 400); }
    for (var i = 0; i < 4; i++) {
      (function(idx) {
        var line = document.createElement('div');
        line.className = 'bx-speed-line';
        line.style.left = (35 + idx * 12) + '%';
        line.style.top = (55 + (idx % 2) * 8) + '%';
        line.style.transform = 'rotate(' + (-30 + idx * 20) + 'deg)';
        layer.appendChild(line);
        setTimeout(function() { line.remove(); }, 450);
      })(i);
    }
  }
  if (kind === 'counter') {
    var spin = document.createElement('motion.div');
    spin.className = 'bx-counter-lines';
    layer.appendChild(spin);
    setTimeout(function() { spin.remove(); }, 550);
    var pow = document.createElement('div');
    pow.className = 'bx-pow';
    pow.textContent = 'WHAM!';
    pow.style.color = '#e74c3c';
    pow.style.textShadow = '3px 3px 0 #fff, -1px -1px 0 #2C3E50';
    layer.appendChild(pow);
    setTimeout(function() { pow.remove(); }, 700);
  }
  if (kind === 'jab' && side !== undefined) {
    var line = document.createElement('div');
    line.className = 'bx-speed-line';
    line.style.top = '62%';
    if (side === 0) { line.style.left = '18%'; line.style.transform = 'rotate(-15deg)'; }
    else { line.style.right = '18%'; line.style.transform = 'rotate(15deg)'; }
    layer.appendChild(line);
    setTimeout(function() { line.remove(); }, 450);
  }
}

"""

FX_JS = FX_JS.replace("document.createElement('motion.div')", "document.createElement('div')")

if 'function bxSpawnPunchFx' not in text:
    text = text.replace('function bxFlash(text, ms) {', FX_JS + 'function bxFlash(text, ms, isBad) {', 1)
    text = text.replace(
        "  el.classList.add('show');\n  setTimeout(function() { el.classList.remove('show'); }, ms || 850);",
        "  el.classList.toggle('bad', !!isBad);\n  el.classList.add('show');\n  setTimeout(function() { el.classList.remove('show', 'bad'); }, ms || 850);",
        1
    )
elif 'function bxFlash(text, ms, isBad)' not in text:
    pass

OLD_PUNCH = """  if (pick === 0 && gL) { gL.classList.add('punch-l'); setTimeout(function() { gL.classList.remove('punch-l'); }, 380); }
  if (pick === 1 && gR) { gR.classList.add('punch-r'); setTimeout(function() { gR.classList.remove('punch-r'); }, 380); }"""
NEW_PUNCH = """  if (pick === 0 && gL) { gL.classList.add('punch-l'); bxSpawnPunchFx('jab', 0); setTimeout(function() { gL.classList.remove('punch-l'); }, 420); }
  if (pick === 1 && gR) { gR.classList.add('punch-r'); bxSpawnPunchFx('jab', 1); setTimeout(function() { gR.classList.remove('punch-r'); }, 420); }"""
if OLD_PUNCH in text:
    text = text.replace(OLD_PUNCH, NEW_PUNCH, 1)

if "bxSpawnPunchFx('hit')" not in text:
    text = text.replace(
        "if (opp) { opp.classList.add('hit'); setTimeout(function() { opp.classList.remove('hit'); }, 480); }\n    if (q.correctSide === 0) L.classList.add('correct'); else R.classList.add('correct');\n    bxFlash('Direct hit!', 750);",
        "if (opp) { opp.classList.add('hit'); setTimeout(function() { opp.classList.remove('hit'); }, 480); }\n    if (q.correctSide === 0) L.classList.add('correct'); else R.classList.add('correct');\n    bxSpawnPunchFx('hit');\n    bxFlash('Direct hit! POW!', 750);",
        1
    )

if "bxSpawnPunchFx('counter')" not in text:
    text = text.replace(
        "bxFlash('Missing — counter punch!', 900);",
        "if (opp) { opp.classList.add('counter-punch'); setTimeout(function() { opp.classList.remove('counter-punch'); }, 480); }\n    bxSpawnPunchFx('counter');\n    bxFlash('Missing — counter punch!', 900, true);",
        1
    )
    text = text.replace(
        "(pick === 0 ? L : R).classList.add('wrong');\n    bxFlash('Counter punch!', 850);",
        "(pick === 0 ? L : R).classList.add('wrong');\n    if (opp) { opp.classList.add('counter-punch'); setTimeout(function() { opp.classList.remove('counter-punch'); }, 480); }\n    bxSpawnPunchFx('counter');\n    bxFlash('Counter punch!', 850, true);",
        1
    )

HTML.write_text(text, encoding="utf-8")
print('OK', 'boxingFxLayer' in text, 'bxSpawnPunchFx' in text, 'opp-head' not in text)
