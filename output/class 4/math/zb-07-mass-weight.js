/**
 * Zero-button interaction layer — Class 4 Math Ch.7 Mass and Weight
 * Does not modify existing script tags; wraps enhancements around existing DOM.
 */
(function () {
  'use strict';

  const ZB = {
    gazeX: 0,
    gazeY: 0,
    useWebGazer: false,
    useCursorGaze: true,
    camStream: null,
    lastGesture: 0,
    gestureCooldown: 800,
    camDenied: false,
    calibrationActive: false,
    cursorGazeListener: false,
    readingPct: 0,
    xp: 0,
    hands: null,
    handsCamera: null,
    handVideo: null,
    lastHandLandmarks: null,
    swipeHist: [],
    tiltBeta: 0,
    tiltGamma: 0,
    quizTiltFocus: null,
    pickedDragItem: null,
    voiceActive: false
  };

  function injectStyles() {
    if (document.getElementById('zb-styles')) return;
    const st = document.createElement('style');
    st.id = 'zb-styles';
    st.textContent = [
      'html.zb-no-scroll, html.zb-no-scroll body { overflow: hidden; }',
      '#zb-intro { position: fixed; inset: 0; z-index: 200000;',
      'background: radial-gradient(ellipse at center, #0d0221 0%, #07090f 100%);',
      'display: flex; flex-direction: column; align-items: center; justify-content: center;',
      'font-family: Poppins, Inter, sans-serif; transition: transform 0.6s ease, opacity 0.5s ease; }',
      '#zb-intro.zb-out { transform: translateY(-100vh); opacity: 0; pointer-events: none; }',
      '#zb-intro.zb-deny-shrink { transform: scale(0.15); transform-origin: bottom left; bottom: 8px; left: 8px; top: auto; right: auto; width: 32px; height: 32px; border-radius: 8px; opacity: 0.9; }',
      '.zb-particle-field { position: absolute; inset: 0; overflow: hidden; pointer-events: none; }',
      '.zb-particle { position: absolute; width: 4px; height: 4px; border-radius: 50%; background: rgba(200,220,255,0.6); animation: zb-drift 12s linear infinite; }',
      '@keyframes zb-drift { from { transform: translateY(100vh) translateX(0); opacity: 0; } 10% { opacity: 0.8; } to { transform: translateY(-20vh) translateX(20px); opacity: 0; } }',
      '.zb-eye-wrap { position: relative; width: 140px; height: 140px; margin-bottom: 24px; }',
      '.zb-eye-ring { position: absolute; inset: 0; border: 3px solid rgba(106,176,76,0.5); border-radius: 50%; animation: zb-spin 8s linear infinite; }',
      '@keyframes zb-spin { to { transform: rotate(360deg); } }',
      '.zb-eye-svg { width: 140px; height: 140px; animation: zb-breathe 2s ease-in-out infinite; filter: drop-shadow(0 0 12px rgba(100,200,255,0.5)); }',
      '@keyframes zb-breathe { 0%,100% { transform: scale(0.95); } 50% { transform: scale(1.05); } }',
      '.zb-intro-title { color: #fff; font-size: clamp(1.2rem, 4vw, 1.8rem); letter-spacing: 0.35em; text-transform: uppercase; opacity: 0; transform: translateY(20px); transition: all 0.8s ease; }',
      '.zb-intro-title.zb-show { opacity: 1; transform: translateY(0); }',
      '.zb-intro-tag { color: rgba(255,255,255,0.75); font-size: 1rem; margin-top: 12px; opacity: 0; transition: opacity 0.6s; }',
      '.zb-intro-tag.zb-show { opacity: 1; }',
      '.zb-type-text { color: #6AB04C; font-size: 0.95rem; margin-top: 20px; min-height: 2.6em; max-width: 90vw; text-align: center; padding: 0 12px; }',
      '.zb-calib-dot { position: fixed; width: 28px; height: 28px; border-radius: 50%; background: #6AB04C;',
      'box-shadow: 0 0 20px #6AB04C; z-index: 200002; transition: transform 0.3s; }',
      '.zb-calib-dot.zb-hot { transform: scale(1.3); }',
      '.zb-calib-bar { position: fixed; bottom: 48px; left: 10%; width: 80%; height: 6px; background: #333; border-radius: 3px; overflow: hidden; z-index: 200002; }',
      '.zb-calib-fill { height: 100%; width: 0%; background: linear-gradient(90deg, #6AB04C, #F0932B); transition: width 0.4s; }',
      '#zb-hud-wrap { position: fixed; z-index: 95000; pointer-events: none; }',
      '.zb-hud-video { position: fixed; bottom: 96px; right: 10px; width: 120px; height: 90px; border-radius: 8px; overflow: hidden; opacity: 0.85; border: 2px solid rgba(106,176,76,0.5); display: none; }',
      '.zb-hud-video video { width: 100%; height: 100%; object-fit: cover; transform: scaleX(-1); }',
      '.zb-gesture-hud { position: fixed; top: 72px; right: 10px; padding: 8px 14px; background: rgba(44,62,80,0.92); color: #fff; border-radius: 8px; font-size: 0.85rem; opacity: 0; transition: opacity 0.3s; max-width: 200px; }',
      '.zb-gesture-hud.zb-on { opacity: 1; }',
      '.zb-voice-bar { position: fixed; bottom: 0; left: 0; right: 0; height: 36px; background: rgba(13,2,33,0.85); display: flex; align-items: center; justify-content: center; gap: 10px; z-index: 94999; font-size: 0.8rem; color: rgba(255,255,255,0.85); }',
      '.zb-mic-pulse { width: 12px; height: 12px; border-radius: 50%; background: #6AB04C; animation: zb-mic 1.2s ease-in-out infinite; }',
      '@keyframes zb-mic { 0%,100% { transform: scale(1); opacity: 0.6; } 50% { transform: scale(1.4); opacity: 1; } }',
      '.zb-reading-orb { position: fixed; top: 72px; left: 12px; width: 48px; height: 48px; border-radius: 50%;',
      'background: conic-gradient(#6AB04C calc(var(--zb-read, 0) * 3.6deg), #2a3a4a 0deg); display: flex; align-items: center; justify-content: center; font-size: 10px; color: #fff; font-weight: 700;',
      'box-shadow: 0 0 16px rgba(106,176,76,0.35); }',
      '.zb-reading-orb::after { content: ""; position: absolute; inset: 6px; background: #2C3E50; border-radius: 50%; }',
      '.zb-reading-orb span { position: relative; z-index: 1; font-size: 9px; }',
      '.zb-xp-bar { position: fixed; top: 0; left: 0; right: 0; height: 4px; background: #1a2530; z-index: 94998; }',
      '.zb-xp-fill { height: 100%; width: var(--zb-xp-pct, 0%); background: linear-gradient(90deg, #6AB04C, #F0932B); transition: width 0.5s; }',
      '.zb-prox-section { transition: opacity 0.35s ease, filter 0.35s ease, box-shadow 0.35s; }',
      '.zb-card-blur { filter: blur(4px); opacity: 0.55; transition: filter 0.4s, opacity 0.4s, transform 0.4s; }',
      '.zb-card-blur.zb-lit { filter: none; opacity: 1; transform: scale(1.02); }',
      '.zb-mini-tooltip { position: absolute; bottom: 100%; left: 0; right: 0; margin-bottom: 8px; padding: 10px; background: rgba(44,62,80,0.95); color: #fff; border-radius: 8px; font-size: 0.85rem; opacity: 0; pointer-events: none; transition: opacity 0.3s; z-index: 5; }',
      '.zb-mini-tooltip.zb-show { opacity: 1; }',
      '.zb-expand-panel { max-height: 0; overflow: hidden; transition: max-height 0.4s; background: var(--lightgreen); border-radius: 0 0 8px 8px; margin-top: 0; padding: 0 12px; font-size: 0.9rem; }',
      '.zb-expand-panel.zb-open { max-height: 120px; padding: 12px; margin-top: 8px; }',
      '.zb-practice-item-enh { transition: opacity 0.3s, filter 0.3s, box-shadow 0.3s; }',
      '.zb-dwell-ring { position: absolute; inset: -4px; border-radius: 12px; pointer-events: none; border: 3px solid transparent; }',
      '.zb-dwell-ring svg { position: absolute; inset: 0; width: 100%; height: 100%; }',
      '.zb-quiz-opt-wrap { position: relative; display: block; }',
      '.zb-compare-chips { display: flex; gap: 6px; margin-top: 6px; flex-wrap: wrap; }',
      '.zb-sym-chip { min-width: 44px; min-height: 44px; display: inline-flex; align-items: center; justify-content: center; background: rgba(44,62,80,0.12); border-radius: 8px; font-weight: 700; font-family: Poppins,sans-serif;',
      'border: 2px dashed rgba(106,176,76,0.4); }',
      '.zb-sym-chip.zb-active { border-color: #6AB04C; background: rgba(106,176,76,0.2); }',
      '.zb-reading-track { height: 4px; background: #e0e0e0; border-radius: 2px; margin-top: 8px; overflow: hidden; }',
      '.zb-reading-track-fill { height: 100%; width: 0%; background: linear-gradient(90deg, #6AB04C, #F0932B); transition: width 0.3s; }',
      '.zb-wp-particles { position: absolute; inset: 0; pointer-events: none; overflow: hidden; border-radius: 14px; opacity: 0; }',
      '.zb-wp-particles.zb-on { opacity: 1; }',
      '.zb-wp-particles span { position: absolute; width: 6px; height: 6px; background: rgba(106,176,76,0.45); border-radius: 50%; animation: zb-wp-float 4s linear infinite; }',
      '@keyframes zb-wp-float { 0% { transform: translate(0,0); } 100% { transform: translate(30px,-40px); opacity: 0; } }',
      '.zb-hint-overlay { position: fixed; inset: 0; z-index: 94000; background: rgba(0,0,0,0.5); display: none; align-items: center; justify-content: center; pointer-events: none; }',
      '.zb-hint-overlay.zb-show { display: flex; }',
      '.zb-hint-box { background: #fff; padding: 24px; border-radius: 16px; max-width: 90vw; font-size: 0.95rem; box-shadow: 0 8px 32px rgba(0,0,0,0.2); }',
      '.zb-scroll-slow-msg { position: fixed; bottom: 120px; left: 50%; transform: translateX(-50%); background: rgba(240,147,43,0.95); color: #fff; padding: 10px 20px; border-radius: 999px; font-size: 0.9rem; opacity: 0; transition: opacity 0.3s; z-index: 94800; pointer-events: none; }',
      '.zb-scroll-slow-msg.zb-on { opacity: 1; }',
      '.zb-gesture-intro { position: fixed; top: 80px; right: 10px; width: 220px; background: rgba(44,62,80,0.92); color: #fff; padding: 12px; border-radius: 10px;',
      'font-size: 0.75rem; z-index: 94990; transform: translateX(120%); transition: transform 0.5s; }',
      '.zb-gesture-intro.zb-in { transform: translateX(0); }',
      '@media (max-width: 768px) { .zb-hud-video { bottom: 88px; } .zb-reading-orb { top: 64px; } }',
      '@keyframes zb-shake { 0%,100% { transform: translateX(0); } 25% { transform: translateX(-6px); } 75% { transform: translateX(6px); } }',
      '.zb-shake { animation: zb-shake 0.4s ease; }',
      '@keyframes zb-ripple { from { box-shadow: 0 0 0 0 rgba(106,176,76,0.6); } to { box-shadow: 0 0 0 20px rgba(106,176,76,0); } }',
      '.zb-ripple { animation: zb-ripple 0.6s ease; }'
    ].join('');
    document.head.appendChild(st);
  }

  function showGestureHud(name) {
    const el = document.getElementById('zb-gesture-name');
    if (!el) return;
    el.textContent = name;
    el.parentElement.classList.add('zb-on');
    clearTimeout(showGestureHud._t);
    showGestureHud._t = setTimeout(() => {
      el.parentElement.classList.remove('zb-on');
    }, 1500);
  }

  function gestureDebounce() {
    const t = performance.now();
    if (t - ZB.lastGesture < ZB.gestureCooldown) return false;
    ZB.lastGesture = t;
    return true;
  }

  function getPointer() {
    return { x: ZB.gazeX, y: ZB.gazeY };
  }

  function onGazeMove(x, y) {
    ZB.gazeX = x;
    ZB.gazeY = y;
    if (document.body.classList.contains('zb-cursor-gaze')) {
      ZB.gazeX = x;
      ZB.gazeY = y;
    }
  }

  function createIntroOverlay() {
    const root = document.createElement('div');
    root.id = 'zb-intro';

    const field = document.createElement('div');
    field.className = 'zb-particle-field';
    for (let i = 0; i < 40; i++) {
      const p = document.createElement('div');
      p.className = 'zb-particle';
      p.style.left = Math.random() * 100 + '%';
      p.style.animationDelay = Math.random() * 10 + 's';
      p.style.animationDuration = 10 + Math.random() * 15 + 's';
      field.appendChild(p);
    }
    root.appendChild(field);

    const eyeWrap = document.createElement('div');
    eyeWrap.className = 'zb-eye-wrap';
    eyeWrap.innerHTML =
      '<div class="zb-eye-ring"></div>' +
      '<svg class="zb-eye-svg zb-eye-main" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">' +
      '<ellipse cx="50" cy="50" rx="48" ry="30" fill="#1a2530" stroke="#6AB04C" stroke-width="2"/>' +
      '<circle class="zb-pupil" cx="50" cy="50" r="12" fill="#F0932B"/>' +
      '</svg>';
    root.appendChild(eyeWrap);

    const title = document.createElement('div');
    title.className = 'zb-intro-title';
    title.textContent = 'Mass and Weight';
    root.appendChild(title);

    const tag = document.createElement('div');
    tag.className = 'zb-intro-tag';
    tag.textContent = 'No tapping. No clicking. Just you.';
    root.appendChild(tag);

    const typeEl = document.createElement('div');
    typeEl.className = 'zb-type-text';
    typeEl.id = 'zb-type-text';
    root.appendChild(typeEl);

    const sub = document.createElement('div');
    sub.id = 'zb-intro-status';
    sub.style.cssText = 'color:#aaa;font-size:0.9rem;margin-top:12px;min-height:1.2em;text-align:center;padding:0 16px;';
    root.appendChild(sub);

    document.body.insertBefore(root, document.body.firstChild);
    document.documentElement.classList.add('zb-no-scroll');

    return { root, title, tag, typeEl, sub, eyeWrap };
  }

  function typeWriter(el, text, startDelay) {
    return new Promise((resolve) => {
      setTimeout(() => {
        let i = 0;
        const tick = () => {
          if (i <= text.length) {
            el.textContent = text.slice(0, i);
            i++;
            setTimeout(tick, 38);
          } else resolve();
        };
        tick();
      }, startDelay);
    });
  }

  function runCalibrationSequence(resolve) {
    ZB.calibrationActive = true;
    ZB.useCursorGaze = true;
    const stEl = document.getElementById('zb-intro-status');
    if (stEl) {
      stEl.innerHTML =
        '<strong style="color:#6AB04C">Move your mouse pointer</strong> onto each green dot and keep it there for about 1.5 seconds. ' +
        '(<kbd>Esc</kbd> skips calibration — cursor will stand in for gaze.)';
    }
    const dots = [
      { x: '12%', y: '25%' },
      { x: '88%', y: '30%' },
      { x: '50%', y: '18%' },
      { x: '20%', y: '75%' },
      { x: '80%', y: '72%' }
    ];
    let idx = 0;
    const bar = document.createElement('div');
    bar.className = 'zb-calib-bar';
    bar.innerHTML = '<div class="zb-calib-fill" id="zb-calib-fill"></div>';
    document.getElementById('zb-intro').appendChild(bar);

    let dwellStart = 0;
    const dwellMs = 1500;
    const radius = 56;
    let calibDone = false;

    function currentDotEl() {
      return document.getElementById('zb-cal-dot');
    }

    function placeDot() {
      const old = currentDotEl();
      if (old) old.remove();
      if (idx >= dots.length) return;
      const d = document.createElement('div');
      d.id = 'zb-cal-dot';
      d.className = 'zb-calib-dot';
      d.style.left = dots[idx].x;
      d.style.top = dots[idx].y;
      d.style.marginLeft = '-14px';
      d.style.marginTop = '-14px';
      document.getElementById('zb-intro').appendChild(d);
    }

    placeDot();
    dwellStart = 0;

    const tick = () => {
      if (idx >= dots.length) {
        finishCalib();
        return;
      }
      const dot = currentDotEl();
      if (!dot) return;
      const rect = dot.getBoundingClientRect();
      const cx = rect.left + rect.width / 2;
      const cy = rect.top + rect.height / 2;
      const px = ZB.gazeX;
      const py = ZB.gazeY;
      const dist = Math.hypot(px - cx, py - cy);
      if (dist < radius) {
        if (!dwellStart) dwellStart = performance.now();
        dot.classList.add('zb-hot');
        const prog = Math.min(1, (performance.now() - dwellStart) / dwellMs);
        const fill = document.getElementById('zb-calib-fill');
        if (fill) fill.style.width = ((idx + prog) / dots.length) * 100 + '%';
        if (performance.now() - dwellStart >= dwellMs) {
          idx++;
          dwellStart = 0;
          const fill2 = document.getElementById('zb-calib-fill');
          if (fill2) fill2.style.width = (idx / dots.length) * 100 + '%';
          if (idx >= dots.length) {
            finishCalib();
            return;
          }
          placeDot();
        }
      } else {
        dwellStart = 0;
        dot.classList.remove('zb-hot');
      }
      if (ZB.calibRaf) cancelAnimationFrame(ZB.calibRaf);
      ZB.calibRaf = requestAnimationFrame(tick);
    };

    function finishCalib() {
      if (calibDone) return;
      calibDone = true;
      if (ZB.calibRaf) cancelAnimationFrame(ZB.calibRaf);
      ZB.calibrationActive = false;
      document.removeEventListener('keydown', onCalibKey);
      document.removeEventListener('touchstart', onCalibTouch);
      document.removeEventListener('touchmove', onCalibTouch);
      const d = currentDotEl();
      if (d) d.remove();
      bar.remove();
      resolve();
    }

    function skipCalib() {
      idx = dots.length;
      finishCalib();
    }

    function onCalibKey(ev) {
      if (ev.key === 'Escape') {
        ev.preventDefault();
        skipCalib();
      }
    }
    function onCalibTouch(ev) {
      const t = ev.touches && ev.touches[0];
      if (t) {
        ZB.gazeX = t.clientX;
        ZB.gazeY = t.clientY;
      }
    }
    document.addEventListener('touchstart', onCalibTouch, { passive: true });
    document.addEventListener('touchmove', onCalibTouch, { passive: true });

    document.addEventListener('keydown', onCalibKey);

    ZB.calibRaf = requestAnimationFrame(tick);
  }

  function dismissIntroGood() {
    const intro = document.getElementById('zb-intro');
    if (!intro) return;
    intro.classList.add('zb-out');
    document.documentElement.classList.remove('zb-no-scroll');
    setTimeout(() => {
      intro.style.display = 'none';
    }, 650);
  }

  function denyIntroSequence() {
    const intro = document.getElementById('zb-intro');
    if (!intro) return;
    const st = document.getElementById('zb-intro-status');
    if (st) st.textContent = 'Switching to touch mode…';
    const svg = intro.querySelector('.zb-eye-main');
    if (svg) svg.style.filter = 'grayscale(1) brightness(0.5)';
    ZB.useCursorGaze = true;
    document.body.classList.add('zb-cursor-gaze');
    setTimeout(() => {
      intro.classList.add('zb-deny-shrink');
      document.documentElement.classList.remove('zb-no-scroll');
      setTimeout(() => {
        intro.style.pointerEvents = 'none';
      }, 600);
    }, 1500);
  }

  function bootHud() {
    if (document.getElementById('zb-hud-wrap')) return;
    const wrap = document.createElement('div');
    wrap.id = 'zb-hud-wrap';
    const xp = document.createElement('div');
    xp.className = 'zb-xp-bar';
    xp.innerHTML = '<div class="zb-xp-fill" id="zb-xp-fill"></div>';
    const orb = document.createElement('div');
    orb.className = 'zb-reading-orb';
    orb.style.setProperty('--zb-read', '0');
    orb.innerHTML = '<span id="zb-orb-label">0%</span>';
    const gh = document.createElement('div');
    gh.className = 'zb-gesture-hud';
    gh.innerHTML = '<span id="zb-gesture-name"></span>';
    const vb = document.createElement('div');
    vb.className = 'zb-voice-bar';
    vb.innerHTML =
      '<div class="zb-mic-pulse" id="zb-mic-dot"></div>' +
      '<span>Say: next · back · quiz me · explain · hint · check · submit</span>';
    const vid = document.createElement('div');
    vid.className = 'zb-hud-video';
    vid.id = 'zb-hud-video';
    vid.innerHTML = '<video id="zb-hud-v" playsinline muted autoplay></video>';
    wrap.appendChild(xp);
    wrap.appendChild(orb);
    wrap.appendChild(gh);
    document.body.appendChild(wrap);
    document.body.appendChild(vb);
    document.body.appendChild(vid);
    if (ZB.camStream) {
      const v = document.getElementById('zb-hud-v');
      if (v) {
        v.srcObject = ZB.camStream;
        vid.style.display = 'block';
      }
    }

    const gi = document.createElement('div');
    gi.className = 'zb-gesture-intro';
    gi.innerHTML =
      '<strong>Hand cues</strong><br>✋ Open · ✊ Fist · 🤏 Pinch<br>☝️ Point · 👍 Up · ✌️ Peace<br>◀▶ Swipe';
    document.body.appendChild(gi);
    setTimeout(() => gi.classList.add('zb-in'), 2000);
    setTimeout(() => gi.classList.remove('zb-in'), 6000);
  }

  function addXp(n) {
    ZB.xp = Math.min(100, ZB.xp + n);
    const f = document.getElementById('zb-xp-fill');
    if (f) f.style.setProperty('--zb-xp-pct', ZB.xp + '%');
    if (f) f.style.width = ZB.xp + '%';
  }

  function cursorAsGaze() {
    if (ZB.cursorGazeListener) return;
    ZB.cursorGazeListener = true;
    ZB.gazeX = window.innerWidth / 2;
    ZB.gazeY = window.innerHeight / 2;
    document.addEventListener(
      'mousemove',
      (e) => {
        if (
          ZB.calibrationActive ||
          !ZB.useWebGazer ||
          ZB.useCursorGaze ||
          ZB.camDenied
        ) {
          ZB.gazeX = e.clientX;
          ZB.gazeY = e.clientY;
        }
      },
      { passive: true }
    );
    document.body.classList.add('zb-cursor-gaze');
  }

  function bootVoice() {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) {
      const vb = document.querySelector('.zb-voice-bar span');
      if (vb) vb.textContent = 'Keys: n next · b back · e explain · q quiz · h hint · c check';
      document.addEventListener('keydown', onKeyShortcut);
      return;
    }
    try {
      const rec = new SR();
      rec.continuous = true;
      rec.interimResults = false;
      rec.lang = 'en-US';
      rec.onresult = (ev) => {
        const t = (ev.results[ev.results.length - 1][0].transcript || '').toLowerCase().trim();
        showFloatingText(t);
        handleVoiceCmd(t);
      };
      rec.onend = () => {
        if (!ZB.voiceActive) return;
        try {
          rec.start();
        } catch (e) {}
      };
      rec.onerror = () => {};
      rec.start();
      ZB.voiceActive = true;
      const md = document.getElementById('zb-mic-dot');
      if (md) md.style.background = '#6AB04C';
    } catch (e) {
      document.addEventListener('keydown', onKeyShortcut);
    }
  }

  function showFloatingText(t) {
    const el = document.createElement('div');
    el.style.cssText =
      'position:fixed;bottom:48px;left:50%;transform:translateX(-50%);background:rgba(44,62,80,0.95);color:#fff;padding:8px 16px;border-radius:8px;z-index:96000;font-size:0.85rem;pointer-events:none;transition:opacity 1.5s';
    el.textContent = t;
    document.body.appendChild(el);
    setTimeout(() => {
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 1500);
    }, 1500);
  }

  const sections = ['hero', 'concepts', 'conversion', 'addition', 'subtraction', 'comparison', 'worded', 'quiz'];

  function scrollToSection(id) {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function sectionIndex() {
    let best = 0;
    let bestY = -Infinity;
    sections.forEach((id, i) => {
      const el = document.getElementById(id);
      if (!el) return;
      const r = el.getBoundingClientRect();
      if (r.top < 200 && r.top > bestY) {
        bestY = r.top;
        best = i;
      }
    });
    return best;
  }

  function tryVoiceClozeFill(t) {
    const inputs = document.querySelectorAll('.cloze-input');
    let hit = false;
    inputs.forEach((inp) => {
      const a = (inp.dataset.ans || '').toLowerCase();
      if (a && t.includes(a)) {
        inp.value = inp.dataset.ans;
        inp.dispatchEvent(new Event('input', { bubbles: true }));
        hit = true;
      }
    });
    if (hit && typeof checkCloze === 'function') checkCloze();
    const md = document.getElementById('zb-mic-dot');
    if (hit && md) {
      md.style.background = '#27ae60';
      setTimeout(() => {
        if (md) md.style.background = '#6AB04C';
      }, 500);
    }
  }

  function handleVoiceCmd(t) {
    tryVoiceClozeFill(t);
    if (t.includes('next')) scrollToSection(sections[Math.min(sections.length - 1, sectionIndex() + 1)]);
    else if (t.includes('back')) scrollToSection(sections[Math.max(0, sectionIndex() - 1)]);
    else if (t.includes('quiz') || t.includes('quiz me')) scrollToSection('quiz');
    else if (t.includes('explain')) document.querySelectorAll('.zb-expand-panel').forEach((p) => p.classList.add('zb-open'));
    else if (t.includes('hint')) showHintOverlay('Try converting to grams first, then compare.');
    else if (t.includes('submit') && typeof submitQuiz === 'function') submitQuiz();
    else if (t.includes('try again') && typeof resetQuiz === 'function') resetQuiz();
    else if (t.includes('check')) runProximityCheck();
  }

  function onKeyShortcut(e) {
    const k = e.key.toLowerCase();
    if (k === 'n') scrollToSection(sections[Math.min(sections.length - 1, sectionIndex() + 1)]);
    if (k === 'b') scrollToSection(sections[Math.max(0, sectionIndex() - 1)]);
    if (k === 'e') document.querySelectorAll('.zb-expand-panel').forEach((p) => p.classList.add('zb-open'));
    if (k === 'q') scrollToSection('quiz');
    if (k === 'h') showHintOverlay('Convert units before adding or subtracting.');
    if (k === 'c') runProximityCheck();
    if (k === 's' && typeof submitQuiz === 'function') submitQuiz();
  }

  function runProximityCheck() {
    const el = document.elementFromPoint(ZB.gazeX, ZB.gazeY);
    const grid = el && el.closest('.practice-grid');
    if (!grid || !grid.id) return;
    if (grid.id === 'gToKg' || grid.id === 'kgToG' || grid.id === 'quickConv') {
      if (typeof checkPractice === 'function') checkPractice(grid.id);
    } else if (grid.id === 'addPractice' || grid.id === 'subPractice') {
      if (typeof checkAddSub === 'function') checkAddSub(grid.id);
    }
    const cloze = el && el.closest('.cloze-wrap');
    if (cloze && typeof checkCloze === 'function') checkCloze();
    if (el && el.closest('#compareGrid') && typeof checkComparisons === 'function') checkComparisons();
  }

  function showHintOverlay(msg) {
    let o = document.getElementById('zb-hint-overlay');
    if (!o) {
      o = document.createElement('div');
      o.id = 'zb-hint-overlay';
      o.className = 'zb-hint-overlay';
      o.innerHTML = '<div class="zb-hint-box" id="zb-hint-txt"></div>';
      document.body.appendChild(o);
    }
    const t = document.getElementById('zb-hint-txt');
    if (t) t.textContent = msg;
    o.classList.add('zb-show');
    setTimeout(() => o.classList.remove('zb-show'), 3200);
  }

  function proximitySections() {
    const secs = document.querySelectorAll('main .section, #hero, section.section');
    const set = new Set();
    document.querySelectorAll('.section, #hero').forEach((sec) => {
      if (!sec.classList.contains('zb-prox-section')) sec.classList.add('zb-prox-section');
    });
    document.addEventListener(
      'mousemove',
      (e) => {
        document.querySelectorAll('.section, #hero').forEach((sec) => {
          const r = sec.getBoundingClientRect();
          const cx = r.left + r.width / 2;
          const cy = r.top + r.height / 2;
          const d = Math.hypot(e.clientX - cx, e.clientY - cy);
          const max = Math.hypot(r.width, r.height) / 2 + 150;
          const t = Math.max(0, 1 - d / max);
          sec.style.opacity = String(0.15 + t * 0.85);
          sec.style.filter = 'blur(' + (1 - t) * 4 + 'px)';
          if (t > 0.85) sec.style.boxShadow = '0 0 0 2px rgba(106,176,76,0.35)';
          else sec.style.boxShadow = 'none';
        });
      },
      { passive: true }
    );
  }

  function heroMagnetic() {
    const icons = document.querySelector('#hero .hero-icons');
    const desc = document.querySelector('#hero .hero-desc');
    if (!icons || !desc) return;
    desc.classList.add('zb-prox-section');
    document.addEventListener(
      'mousemove',
      (e) => {
        const r = icons.getBoundingClientRect();
        const mx = r.left + r.width / 2;
        const my = r.top + r.height / 2;
        const dx = (e.clientX - mx) * 0.15;
        const dy = (e.clientY - my) * 0.15;
        icons.style.transform = 'translate(' + dx + 'px,' + dy + 'px)';
        const dr = desc.getBoundingClientRect();
        const dcx = dr.left + dr.width / 2;
        const dcy = dr.top + dr.height / 2;
        const dist = Math.hypot(e.clientX - dcx, e.clientY - dcy);
        const cl = Math.max(0, 1 - dist / 220);
        desc.style.filter = 'blur(' + (1 - cl) * 4 + 'px)';
        desc.style.opacity = String(0.35 + cl * 0.65);
      },
      { passive: true }
    );
  }

  function setupConceptCards() {
    const cards = document.querySelectorAll('#concepts .card');
    cards.forEach((card, i) => {
      card.style.position = 'relative';
      card.classList.add('zb-card-blur');
      const tip = document.createElement('div');
      tip.className = 'zb-mini-tooltip';
      const hints = [
        'Kilogram: about the mass of a small bag of sugar or a litre of milk.',
        'Gram: great for tiny things — a paperclip is only a few grams.',
        'Balance: compare unknown mass with known standard masses until level.',
        'Weighing machine: the dial shows total mass directly in kg or g.'
      ];
      tip.textContent = hints[i] || '';
      card.appendChild(tip);
      const panel = document.createElement('div');
      panel.className = 'zb-expand-panel';
      panel.textContent = 'Tip: always check whether the scale reads in kg or g before you record an answer.';
      card.appendChild(panel);
    });

    let dwellCard = null;
    let dwellT0 = 0;

    function tick() {
      const el = document.elementFromPoint(ZB.gazeX, ZB.gazeY);
      const card = el && el.closest('#concepts .card');
      cards.forEach((c) => {
        c.classList.remove('zb-lit');
        c.querySelector('.zb-mini-tooltip') && c.querySelector('.zb-mini-tooltip').classList.remove('zb-show');
      });
      if (card) {
        card.classList.add('zb-lit');
        if (dwellCard !== card) {
          dwellCard = card;
          dwellT0 = performance.now();
        }
        if (performance.now() - dwellT0 > 1000) {
          const tip = card.querySelector('.zb-mini-tooltip');
          if (tip) tip.classList.add('zb-show');
        }
      } else {
        dwellCard = null;
      }
      requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  function setupHandExpand() {
    function loop() {
      const lm = ZB.lastHandLandmarks;
      if (!lm || !lm.length) {
        requestAnimationFrame(loop);
        return;
      }
      const el = document.elementFromPoint(ZB.gazeX, ZB.gazeY);
      const card = el && el.closest('#concepts .card');
      if (card && gestureDebounce()) {
        const open = isOpenPalm(lm[0]);
        const fist = isFist(lm[0]);
        const peace = isPeace(lm[0]);
        if (open) {
          const p = card.querySelector('.zb-expand-panel');
          if (p) {
            p.classList.add('zb-open');
            showGestureHud('Open palm — expand');
          }
        }
        if (fist) {
          const p = card.querySelector('.zb-expand-panel');
          if (p) {
            p.classList.remove('zb-open');
            showGestureHud('Fist — collapse');
          }
        }
        if (peace) {
          showHintOverlay(card.querySelector('h4') ? card.querySelector('h4').textContent : 'Hint');
          showGestureHud('Peace — hint');
        }
      }
      requestAnimationFrame(loop);
    }
    requestAnimationFrame(loop);
  }

  function isOpenPalm(lm) {
    const tips = [8, 12, 16, 20];
    const wrist = lm[0];
    let ext = 0;
    tips.forEach((idx) => {
      const d = Math.hypot(lm[idx].x - wrist.x, lm[idx].y - wrist.y);
      if (d > 0.12) ext++;
    });
    return ext >= 4;
  }

  function isFist(lm) {
    const tips = [8, 12, 16, 20];
    const wrist = lm[0];
    let curled = 0;
    tips.forEach((idx) => {
      const d = Math.hypot(lm[idx].x - wrist.x, lm[idx].y - wrist.y);
      if (d < 0.08) curled++;
    });
    return curled >= 4;
  }

  function isPeace(lm) {
    const up = lm[8].y < lm[6].y && lm[12].y < lm[10].y;
    const down = lm[16].y > lm[14].y && lm[20].y > lm[18].y;
    return up && down;
  }

  function isPinch(lm) {
    const d = Math.hypot(lm[4].x - lm[8].x, lm[4].y - lm[8].y);
    return d < 0.04;
  }

  function isThumbsUp(lm) {
    return lm[4].y < lm[3].y && lm[8].y > lm[6].y;
  }

  function initMediaPipeHands() {
    if (typeof Hands === 'undefined' || typeof Camera === 'undefined') return;
    if (!ZB.camStream) return;
    ZB.handVideo = document.createElement('video');
    ZB.handVideo.srcObject = ZB.camStream;
    ZB.handVideo.playsInline = true;
    ZB.handVideo.muted = true;
    ZB.handVideo.play().catch(() => {});

    const hands = new Hands({
      locateFile: (f) =>
        'https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4.1675469240/' + f
    });
    hands.setOptions({ maxNumHands: 1, modelComplexity: 1, minDetectionConfidence: 0.6 });
    hands.onResults((res) => {
      if (res.multiHandLandmarks && res.multiHandLandmarks[0]) {
        ZB.lastHandLandmarks = res.multiHandLandmarks;
        const lm = res.multiHandLandmarks[0];
        const wrist = lm[0];
        ZB.swipeHist.push({ x: wrist.x, y: wrist.y, t: performance.now() });
        if (ZB.swipeHist.length > 12) ZB.swipeHist.shift();
        detectSwipe();
        handleGestureNavigation(lm);
        if (isPinch(lm) && gestureDebounce()) {
          const c = document.getElementById('balanceCanvas');
          if (c) {
            c.style.transform = 'scale(1.35)';
            c.style.transition = 'transform 0.3s';
            showGestureHud('Pinch zoom');
            setTimeout(() => {
              c.style.transform = 'scale(1)';
            }, 1200);
          }
        }
        if (isThumbsUp(lm) && gestureDebounce()) {
          addXp(4);
          showGestureHud('Thumbs up +XP');
        }
      }
    });

    try {
      const camera = new Camera(ZB.handVideo, {
        onFrame: async () => {
          await hands.send({ image: ZB.handVideo });
        },
        width: 320,
        height: 240
      });
      camera.start();
      ZB.handsCamera = camera;
    } catch (e) {}
  }

  function detectSwipe() {
    const h = ZB.swipeHist;
    if (h.length < 8) return;
    const a = h[0];
    const b = h[h.length - 1];
    const dt = b.t - a.t;
    if (dt > 300) return;
    const vx = (b.x - a.x) / dt;
    if (Math.abs(vx) > 0.0012 && gestureDebounce()) {
      if (vx > 0) {
        runNavGesture('swipe-right');
        showGestureHud('Swipe right');
      } else {
        runNavGesture('swipe-left');
        showGestureHud('Swipe left');
      }
      ZB.swipeHist = [];
    }
  }

  function runNavGesture(dir) {
    const n = activeStepContainerId();
    if (!n) return;
    if (dir === 'swipe-right' || dir === 'point-down') {
      if (n && typeof nextStep === 'function') nextStep(n);
    } else if (dir === 'swipe-left' || dir === 'point-up') {
      if (n && typeof prevStep === 'function') prevStep(n);
    }
  }

  function isInView(el) {
    if (!el) return false;
    const r = el.getBoundingClientRect();
    return r.top < innerHeight && r.bottom > 0;
  }

  function activeStepContainerId() {
    const triple = [
      { id: 'conversion', n: 1 },
      { id: 'addition', n: 2 },
      { id: 'subtraction', n: 3 }
    ];
    let best = 0;
    let bestArea = 0;
    for (let i = 0; i < triple.length; i++) {
      const sec = document.getElementById(triple[i].id);
      if (!sec || !isInView(sec)) continue;
      const r = sec.getBoundingClientRect();
      const vis = Math.max(0, Math.min(r.bottom, innerHeight) - Math.max(r.top, 0));
      if (vis > bestArea) {
        bestArea = vis;
        best = triple[i].n;
      }
    }
    return best;
  }

  function handleGestureNavigation(lm) {
    const idxTip = lm[8];
    const idxPIP = lm[6];
    const up = idxTip.y < idxPIP.y - 0.02;
    const down = idxTip.y > idxPIP.y + 0.02;
    const otherDown = lm[12].y > lm[10].y && lm[16].y > lm[14].y;
    const stepN = activeStepContainerId();
    if (otherDown && up && gestureDebounce()) {
      if (stepN && typeof prevStep === 'function') {
        prevStep(stepN);
        showGestureHud('Point up — previous step');
      } else {
        window.scrollBy({ top: -80, behavior: 'smooth' });
        showGestureHud('Point up');
      }
    }
    if (otherDown && down && gestureDebounce()) {
      if (stepN && typeof nextStep === 'function') {
        nextStep(stepN);
        showGestureHud('Point down — next step');
      } else {
        window.scrollBy({ top: 80, behavior: 'smooth' });
        showGestureHud('Point down');
      }
    }
  }

  function initTilt() {
    window.addEventListener(
      'deviceorientation',
      (e) => {
        if (e.beta != null) ZB.tiltBeta = e.beta;
        if (e.gamma != null) ZB.tiltGamma = e.gamma;
        const slider = document.getElementById('balanceSlider');
        const demo = document.querySelector('.scale-demo');
        if (slider && demo && isInView(demo)) {
          const g = Math.max(-40, Math.min(40, ZB.tiltGamma || 0));
          const val = 1000 + (g / 40) * 1000;
          slider.value = String(Math.round(Math.max(0, Math.min(2000, val))));
          slider.dispatchEvent(new Event('input', { bubbles: true }));
        }
        const quiz = document.getElementById('quiz');
        if (quiz && isInView(quiz)) {
          tiltQuizSelect(e);
        }
      },
      { passive: true }
    );
  }

  let quizTiltPrevIdx = null;
  function tiltQuizSelect(e) {
    const q = document.elementFromPoint(innerWidth / 2, innerHeight / 2);
    const quizQ = q && q.closest('.quiz-q');
    if (!quizQ) return;
    const beta = e.beta != null ? e.beta : 55;
    const gamma = e.gamma != null ? e.gamma : 0;
    const opts = quizQ.querySelectorAll('.quiz-opt');
    if (opts.length < 4) return;
    let idx = 0;
    if (gamma < -15) idx = 0;
    else if (gamma > 15) idx = 1;
    else if (beta < 35) idx = 2;
    else idx = 3;
    if (quizTiltPrevIdx !== idx) {
      quizTiltPrevIdx = idx;
      ZB.tiltDwell = performance.now();
      return;
    }
    if (performance.now() - (ZB.tiltDwell || 0) >= 1500) {
      const b = opts[idx];
      if (b && typeof b.click === 'function') b.click();
      ZB.tiltDwell = performance.now();
      quizTiltPrevIdx = null;
    }
  }

  function setupBalanceHover() {
    const demo = document.querySelector('.scale-demo');
    const slider = document.getElementById('balanceSlider');
    if (!demo || !slider) return;
    demo.addEventListener(
      'mousemove',
      (e) => {
        const r = demo.getBoundingClientRect();
        const t = (e.clientX - r.left) / r.width;
        const val = Math.round(t * 2000);
        slider.value = String(val);
        slider.dispatchEvent(new Event('input', { bubbles: true }));
      },
      { passive: true }
    );
  }

  function setupConversionSteps() {
    const dwellMs = 1500;
    const map = [
      { cid: 'step-container-1', n: 1 },
      { cid: 'step-container-2', n: 2 },
      { cid: 'step-container-3', n: 3 }
    ];
    let dwell = 0;
    function stepTick() {
      const el = document.elementFromPoint(ZB.gazeX, ZB.gazeY);
      const step = el && el.closest('.step.visible');
      let n = 0;
      if (step) {
        for (let i = 0; i < map.length; i++) {
          const root = document.getElementById(map[i].cid);
          if (root && root.contains(step)) {
            n = map[i].n;
            break;
          }
        }
      }
      if (n) {
        if (!dwell) dwell = performance.now();
        if (performance.now() - dwell > dwellMs && typeof nextStep === 'function') {
          nextStep(n);
          dwell = 0;
        }
      } else {
        dwell = 0;
      }
      requestAnimationFrame(stepTick);
    }
    requestAnimationFrame(stepTick);
  }

  function practiceProximity() {
    document.querySelectorAll('.practice-grid .practice-item').forEach((item) => {
      item.classList.add('zb-practice-item-enh');
      item.style.opacity = '0.45';
      item.style.filter = 'blur(3px)';
    });
    document.addEventListener(
      'mousemove',
      (e) => {
        document.querySelectorAll('.practice-grid .practice-item').forEach((item) => {
          const r = item.getBoundingClientRect();
          const cx = r.left + r.width / 2;
          const cy = r.top + r.height / 2;
          const d = Math.hypot(e.clientX - cx, e.clientY - cy);
          if (d < 150) {
            item.style.opacity = '1';
            item.style.filter = 'none';
            item.style.boxShadow = '0 0 0 2px rgba(106,176,76,0.25)';
          } else {
            item.style.opacity = '0.45';
            item.style.filter = 'blur(3px)';
            item.style.boxShadow = 'none';
          }
        });
      },
      { passive: true }
    );
  }

  function borrowPulse() {
    const s = document.getElementById('step3-2');
    if (!s) return;
    const obs = new MutationObserver(() => {
      if (s.classList.contains('visible')) {
        s.style.outline = '3px solid #F0932B';
        s.style.transition = 'outline 0.3s';
        setTimeout(() => {
          s.style.outline = 'none';
        }, 2000);
      }
    });
    obs.observe(s, { attributes: true, attributeFilter: ['class'] });
  }

  function comparisonTableGlow() {
    document.querySelectorAll('.comparison-table tbody tr').forEach((tr) => {
      tr.style.transition = 'background 0.3s';
    });
    function tick() {
      const el = document.elementFromPoint(ZB.gazeX, ZB.gazeY);
      const row = el && el.closest('.comparison-table tbody tr');
      document.querySelectorAll('.comparison-table tbody tr').forEach((tr) => {
        tr.style.background = '';
      });
      if (row) row.style.background = 'rgba(106,176,76,0.2)';
      requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  function setupCompareChips() {
    document.querySelectorAll('#compareGrid .compare-item').forEach((item) => {
      const wrap = document.createElement('div');
      wrap.className = 'zb-compare-chips';
      ['<', '=', '>'].forEach((sym) => {
        const chip = document.createElement('div');
        chip.className = 'zb-sym-chip';
        chip.textContent = sym;
        chip.dataset.sym = sym;
        wrap.appendChild(chip);
      });
      item.appendChild(wrap);
    });

    let dwellEl = null;
    let t0 = 0;
    function tick() {
      const el = document.elementFromPoint(ZB.gazeX, ZB.gazeY);
      const chip = el && el.closest('.zb-sym-chip');
      if (chip) {
        if (dwellEl !== chip) {
          dwellEl = chip;
          t0 = performance.now();
        }
        chip.classList.add('zb-active');
        if (performance.now() - t0 > 2000) {
          const item = chip.closest('.compare-item');
          const sel = item && item.querySelector('select');
          if (sel) {
            const sym = chip.dataset.sym;
            let found = false;
            for (let i = 0; i < sel.options.length; i++) {
              const o = sel.options[i];
              const label = o.textContent.replace(/\s+/g, '');
              if (label === sym) {
                sel.selectedIndex = i;
                found = true;
                break;
              }
            }
            if (!found) {
              const entity = sym === '<' ? '&lt;' : sym === '>' ? '&gt;' : '=';
              sel.value = entity;
            }
            sel.dispatchEvent(new Event('change', { bubbles: true }));
            if (typeof checkComparisons === 'function') checkComparisons();
          }
          t0 = performance.now();
        }
      } else {
        dwellEl = null;
        document.querySelectorAll('.zb-sym-chip').forEach((c) => c.classList.remove('zb-active'));
      }
      requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  function setupDragGaze() {
    let lifted = null;
    let liftT = 0;
    function tick() {
      const el = document.elementFromPoint(ZB.gazeX, ZB.gazeY);
      const di = el && el.closest('.drag-item');
      const dt = el && el.closest('.drag-target');
      if (di && !di.classList.contains('placed')) {
        if (lifted !== di) {
          lifted = di;
          liftT = performance.now();
        }
        di.style.transform = 'scale(1.08)';
        di.style.boxShadow = '0 8px 20px rgba(0,0,0,0.2)';
        if (performance.now() - liftT > 1500) {
          ZB.pickedDragItem = di;
        }
      } else if (dt && ZB.pickedDragItem) {
        dt.appendChild(ZB.pickedDragItem);
        ZB.pickedDragItem.classList.add('placed');
        ZB.pickedDragItem = null;
        lifted = null;
      } else if (di) {
        di.style.transform = '';
        di.style.boxShadow = '';
      }
      requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  function setupWordProblems() {
    document.querySelectorAll('#worded .word-problem').forEach((wp) => {
      const q = wp.querySelector('.wp-q');
      if (!q) return;
      const track = document.createElement('div');
      track.className = 'zb-reading-track';
      track.innerHTML = '<div class="zb-reading-track-fill"></div>';
      q.after(track);
      const fill = track.querySelector('.zb-reading-track-fill');
      const particles = document.createElement('div');
      particles.className = 'zb-wp-particles';
      wp.style.position = 'relative';
      for (let i = 0; i < 12; i++) {
        const s = document.createElement('span');
        s.style.left = Math.random() * 100 + '%';
        s.style.top = Math.random() * 100 + '%';
        s.style.animationDelay = Math.random() * 3 + 's';
        particles.appendChild(s);
      }
      wp.appendChild(particles);
      let stopT = 0;
      let readProg = 0;
      function upd() {
        const wr = wp.getBoundingClientRect();
        const rel = (ZB.gazeY - wr.top) / wr.height;
        readProg = Math.max(readProg, Math.min(1, Math.max(0, rel)));
        if (fill) fill.style.width = readProg * 100 + '%';
        if (readProg > 0.92) {
          const ans = wp.querySelector('.wp-answer');
          if (ans) {
            ans.style.display = 'block';
            ans.style.opacity = '0';
            ans.style.transition = 'opacity 0.6s';
            requestAnimationFrame(() => {
              ans.style.opacity = '1';
            });
          }
        }
        requestAnimationFrame(upd);
      }
      requestAnimationFrame(upd);
      let lastScroll = performance.now();
      window.addEventListener(
        'scroll',
        () => {
          lastScroll = performance.now();
        },
        { passive: true }
      );
      setInterval(() => {
        if (performance.now() - lastScroll > 3000 && isInView(wp)) {
          particles.classList.add('zb-on');
          setTimeout(() => particles.classList.remove('zb-on'), 4000);
        }
      }, 500);
    });
  }

  function setupQuizDwell() {
    document.querySelectorAll('.quiz-opt').forEach((opt) => {
      const wrap = document.createElement('div');
      wrap.className = 'zb-quiz-opt-wrap';
      opt.parentNode.insertBefore(wrap, opt);
      wrap.appendChild(opt);
      const ring = document.createElement('div');
      ring.className = 'zb-dwell-ring';
      ring.innerHTML =
        '<svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="46" stroke="#6AB04C" stroke-width="4" fill="none" stroke-dasharray="290" stroke-dashoffset="290" id="arc"/></svg>';
      wrap.appendChild(ring);
      const arc = ring.querySelector('circle');
    });

    let activeOpt = null;
    let t0 = 0;
    function tick() {
      const el = document.elementFromPoint(ZB.gazeX, ZB.gazeY);
      const opt = el && el.closest('.quiz-opt');
      document.querySelectorAll('.zb-dwell-ring circle').forEach((c) => {
        c.style.strokeDashoffset = '290';
      });
      if (opt) {
        if (activeOpt !== opt) {
          activeOpt = opt;
          t0 = performance.now();
        }
        const ring = opt.parentElement.querySelector('.zb-dwell-ring circle');
        const p = Math.min(1, (performance.now() - t0) / 2000);
        if (ring) ring.style.strokeDashoffset = String(290 * (1 - p));
        if (p >= 1 && typeof opt.click === 'function') {
          opt.click();
          t0 = performance.now();
          activeOpt = null;
        }
      } else activeOpt = null;
      requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  function setupFooterXp() {
    const foot = document.querySelector('footer');
    if (!foot) return;
    const obs = new IntersectionObserver(
      (ents) => {
        ents.forEach((en) => {
          if (en.isIntersecting) {
            addXp(20);
            document.querySelector('.zb-reading-orb') && document.body.classList.add('zb-footer-reward');
          }
        });
      },
      { threshold: 0.2 }
    );
    obs.observe(foot);
  }

  function scrollVelocityFx() {
    let lastY = window.scrollY;
    let lastT = performance.now();
    let vel = 0;
    const msg = document.createElement('div');
    msg.className = 'zb-scroll-slow-msg';
    msg.textContent = 'Slow down — read carefully';
    document.body.appendChild(msg);
    window.addEventListener(
      'scroll',
      () => {
        const t = performance.now();
        const dy = window.scrollY - lastY;
        vel = dy / (t - lastT || 1);
        lastY = window.scrollY;
        lastT = t;
        document.querySelectorAll('.section').forEach((s) => {
          if (Math.abs(vel) > 2) s.style.filter = 'blur(2px)';
          else s.style.filter = '';
        });
        if (Math.abs(vel) > 3) msg.classList.add('zb-on');
        else msg.classList.remove('zb-on');
      },
      { passive: true }
    );
  }

  function readingOrbSync() {
    function tick() {
      const pct = Math.min(1, window.scrollY / (document.body.scrollHeight - innerHeight || 1));
      const orb = document.querySelector('.zb-reading-orb');
      if (orb) {
        orb.style.setProperty('--zb-read', String(pct * 100));
        const lbl = document.getElementById('zb-orb-label');
        if (lbl) lbl.textContent = Math.round(pct * 100) + '%';
      }
      requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  function startAfterIntro() {
    injectStyles();
    if (!document.getElementById('zb-hud-wrap')) bootHud();
    bootVoice();
    if (ZB.camStream) {
      const vid = document.getElementById('zb-hud-video');
      const v = document.getElementById('zb-hud-v');
      if (v && !v.srcObject) v.srcObject = ZB.camStream;
      if (v) v.play().catch(() => {});
      if (vid) vid.style.display = 'block';
    }
    proximitySections();
    heroMagnetic();
    setupConceptCards();
    setupHandExpand();
    initMediaPipeHands();
    initTilt();
    setupBalanceHover();
    setupConversionSteps();
    practiceProximity();
    borrowPulse();
    comparisonTableGlow();
    setupCompareChips();
    setupDragGaze();
    setupWordProblems();
    setupQuizDwell();
    setupFooterXp();
    scrollVelocityFx();
    readingOrbSync();
  }

  /** Camera preview to HUD only. Gaze is pointer/touch (no WebGazer — avoids HTTPS/localhost alert + IP quirks). */
  function startWebGazerPipeline(stream) {
    ZB.useWebGazer = false;
    ZB.useCursorGaze = true;
    document.body.classList.add('zb-cursor-gaze');
    const v = document.getElementById('zb-hud-v');
    if (v && stream) {
      v.srcObject = stream;
      v.play().catch(() => {});
    }
  }

  function boot() {
    injectStyles();
    cursorAsGaze();
    createIntroOverlay();

    setTimeout(() => {
      const el = document.getElementById('zb-intro');
      const refs = {
        title: el.querySelector('.zb-intro-title'),
        tag: el.querySelector('.zb-intro-tag'),
        typeEl: document.getElementById('zb-type-text'),
        sub: document.getElementById('zb-intro-status')
      };
      setTimeout(() => refs.title.classList.add('zb-show'), 1200);
      setTimeout(() => refs.tag.classList.add('zb-show'), 2000);
      typeWriter(
        refs.typeEl,
        'Follow each dot with your mouse or finger — then you can scroll and use hand gestures.',
        2800
      );
    }, 0);

    setTimeout(() => {
      const sub = document.getElementById('zb-intro-status');
      if (sub) sub.textContent = 'Requesting camera…';
      navigator.mediaDevices
        .getUserMedia({ video: true, audio: false })
        .then((stream) => {
          ZB.camStream = stream;
          ZB.calibrationActive = true;
          ZB.useCursorGaze = true;
          bootHud();
          const vid = document.getElementById('zb-hud-video');
          const v = document.getElementById('zb-hud-v');
          if (v) {
            v.srcObject = stream;
            v.play().catch(() => {});
          }
          if (vid) {
            vid.style.display = 'block';
          }
          const pupil = document.querySelector('.zb-pupil');
          if (pupil) pupil.setAttribute('fill', '#6AB04C');
          if (sub) sub.textContent = 'Calibrating…';
          startWebGazerPipeline(stream);
          return new Promise((resolve) => {
            setTimeout(() => runCalibrationSequence(resolve), 500);
          });
        })
        .then(() => {
          dismissIntroGood();
          startAfterIntro();
        })
        .catch(() => {
          ZB.camDenied = true;
          ZB.useCursorGaze = true;
          document.body.classList.add('zb-cursor-gaze');
          denyIntroSequence();
          setTimeout(startAfterIntro, 2000);
        });
    }, 3500);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
