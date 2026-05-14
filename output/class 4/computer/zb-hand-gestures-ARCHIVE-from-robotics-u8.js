/**
 * ARCHIVE SNAPSHOT — full zb-08-robotics.js **with** MediaPipe hand gestures (palm scroll, swipe, pinch, etc.).
 * 08.html no longer loads this file. Use it to copy gesture logic into other lessons; wire camera_utils + hands
 * CDN scripts and call ensureHandsPipeline() after ZB.camStream is set (see boot() / startAfterIntro in this file).
 */
/**
 * Zero-button layer — Class 4 Computer Unit 8 Robotics (08.html)
 * Does not modify existing inline script; calls globals: nextStep, resetSteps, checkTF, checkFITB, resetFITB,
 * showFITBAnswers, selectLabel, checkLabels, checkQ, showQuizScore, toggleAccordion
 */
(function () {
  'use strict';

  const XP_STORAGE_KEY = 'gaze-xp-class4-computer-u8';
  const SECTION_IDS = [
    'hero',
    'what-is',
    'applications',
    'adv-dis',
    'tf-section',
    'fitb-section',
    'label-section',
    'quiz-section',
    'lab'
  ];

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
    xp: 0,
    xpLevel: 0,
    handsCamera: null,
    handVideo: null,
    lastHandLandmarks: null,
    swipeHist: [],
    tiltBeta: 0,
    tiltGamma: 0,
    voiceActive: false,
    calibRaf: 0,
    pickedLabelEl: null,
    labelLiftT: 0,
    fingerX: null,
    fingerY: null,
    fingerTs: 0,
    handsPipelineStarted: false,
    sectionDwellT: {},
    _palmYs: null,
    _palmYsLastT: 0,
    _lastPalmScroll: 0
  };

  function loadXp() {
    try {
      const n = parseInt(localStorage.getItem(XP_STORAGE_KEY) || '0', 10);
      if (!Number.isNaN(n) && n >= 0) ZB.xp = Math.min(100, n);
    } catch (e) {}
    ZB.xpLevel = Math.floor(ZB.xp / 25);
  }

  function saveXp() {
    try {
      localStorage.setItem(XP_STORAGE_KEY, String(Math.round(ZB.xp)));
    } catch (e) {}
  }

  function addXp(n, reason) {
    if (!n) return;
    const prevLevel = Math.floor(ZB.xp / 25);
    ZB.xp = Math.min(100, ZB.xp + n);
    const newLevel = Math.floor(ZB.xp / 25);
    const f = document.getElementById('zb-xp-fill');
    if (f) {
      f.style.setProperty('--zb-xp-pct', ZB.xp + '%');
      f.style.width = ZB.xp + '%';
    }
    if (newLevel > prevLevel) levelRipple();
    saveXp();
  }

  function levelRipple() {
    let el = document.getElementById('zb-level-ripple');
    if (!el) {
      el = document.createElement('div');
      el.id = 'zb-level-ripple';
      el.style.cssText =
        'position:fixed;inset:0;z-index:199000;pointer-events:none;background:rgba(106,176,76,0.35);opacity:0;transition:opacity 0.3s';
      document.body.appendChild(el);
    }
    el.style.opacity = '1';
    setTimeout(() => {
      el.style.opacity = '0';
    }, 600);
  }

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
      '.zb-particle { position: absolute; width: 4px; height: 4px; border-radius: 50%; background: rgba(106,176,76,0.45); animation: zb08-drift 14s linear infinite; }',
      '@keyframes zb08-drift { from { transform: translateY(100vh); opacity: 0; } 12% { opacity: 0.85; } to { transform: translateY(-15vh); opacity: 0; } }',
      '.zb-lens-wrap { position: relative; width: 140px; height: 140px; margin-bottom: 24px; }',
      '.zb-lens-ring { position: absolute; inset: 0; border: 3px solid rgba(106,176,76,0.55); border-radius: 50%; animation: zb08-spin 10s linear infinite; }',
      '@keyframes zb08-spin { to { transform: rotate(360deg); } }',
      '.zb-lens-svg { width: 140px; height: 140px; animation: zb08-breathe 2.2s ease-in-out infinite; filter: drop-shadow(0 0 14px rgba(106,176,76,0.45)); }',
      '@keyframes zb08-breathe { 0%,100% { transform: scale(0.94); } 50% { transform: scale(1.06); } }',
      '.zb-intro-title { color: #fff; font-size: clamp(1.1rem, 3.8vw, 1.65rem); letter-spacing: 0.28em; text-transform: uppercase; opacity: 0; transform: translateY(20px); transition: all 0.8s ease; }',
      '.zb-intro-title.zb-show { opacity: 1; transform: translateY(0); }',
      '.zb-intro-tag { color: rgba(255,255,255,0.78); font-size: 1rem; margin-top: 12px; opacity: 0; transition: opacity 0.6s; }',
      '.zb-intro-tag.zb-show { opacity: 1; }',
      '.zb-type-text { color: #6AB04C; font-size: 0.92rem; margin-top: 18px; min-height: 2.4em; max-width: 92vw; text-align: center; padding: 0 12px; }',
      '.zb-calib-dot { position: fixed; width: 28px; height: 28px; border-radius: 50%; background: #6AB04C; box-shadow: 0 0 22px #6AB04C; z-index: 200002; transition: transform 0.3s; }',
      '.zb-calib-dot.zb-hot { transform: scale(1.35); }',
      '.zb-calib-bar { position: fixed; bottom: 44px; left: 8%; width: 84%; height: 6px; background: #2a2a3a; border-radius: 3px; overflow: hidden; z-index: 200002; }',
      '.zb-calib-fill { height: 100%; width: 0%; background: linear-gradient(90deg, #6AB04C, #F0932B); transition: width 0.35s; }',
      '#zb-hud-wrap { position: fixed; z-index: 95000; pointer-events: none; }',
      '.zb-hud-video { position: fixed; bottom: 96px; right: 10px; width: 120px; height: 90px; border-radius: 8px; overflow: hidden; opacity: 0.88; border: 2px solid rgba(106,176,76,0.55); display: none; }',
      '.zb-hud-video video { width: 100%; height: 100%; object-fit: cover; transform: scaleX(-1); }',
      '.zb-gesture-hud { position: fixed; top: 72px; right: 10px; padding: 8px 14px; background: rgba(44,62,80,0.94); color: #fff; border-radius: 8px; font-size: 0.82rem; opacity: 0; transition: opacity 0.3s; max-width: 210px; z-index: 95001; }',
      '.zb-gesture-hud.zb-on { opacity: 1; }',
      '.zb-voice-bar { position: fixed; bottom: 0; left: 0; right: 0; height: 34px; background: rgba(13,2,33,0.88); display: flex; align-items: center; justify-content: center; gap: 8px; z-index: 94999; font-size: 0.75rem; color: rgba(255,255,255,0.88); }',
      '.zb-mic-pulse { width: 11px; height: 11px; border-radius: 50%; background: #6AB04C; animation: zb08-mic 1.15s ease-in-out infinite; }',
      '@keyframes zb08-mic { 0%,100% { transform: scale(1); opacity: 0.55; } 50% { transform: scale(1.35); opacity: 1; } }',
      '.zb-reading-orb { position: fixed; top: 72px; left: 10px; width: 46px; height: 46px; border-radius: 50%;',
      'background: conic-gradient(#6AB04C calc(var(--zb-read, 0) * 3.6deg), #2a3a4a 0deg); display: flex; align-items: center; justify-content: center;',
      'box-shadow: 0 0 14px rgba(106,176,76,0.35); z-index: 95001; }',
      '.zb-reading-orb::after { content: ""; position: absolute; inset: 6px; background: #2C3E50; border-radius: 50%; }',
      '.zb-reading-orb span { position: relative; z-index: 1; font-size: 8px; color: #fff; font-weight: 700; }',
      '.zb-xp-bar { position: fixed; top: 0; left: 0; right: 0; height: 5px; background: #1a2530; z-index: 94998; overflow: hidden; }',
      '.zb-xp-bar.zb-boot::after { content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 40%; background: linear-gradient(90deg, transparent, rgba(106,176,76,0.7), transparent); animation: zb08-circuit 1.4s ease-out forwards; }',
      '@keyframes zb08-circuit { from { transform: translateX(-100%); } to { transform: translateX(350%); } }',
      '.zb-xp-fill { height: 100%; width: 0%; background: linear-gradient(90deg, #6AB04C, #F0932B); transition: width 0.45s; }',
      '.zb-torch-target { transition: opacity 0.35s ease, filter 0.35s ease, box-shadow 0.35s; }',
      '.zb-term { display: inline; border-bottom: 1px dashed rgba(106,176,76,0.5); cursor: inherit; }',
      '.zb-term.zb-blur { filter: blur(5px); opacity: 0.45; transition: filter 0.35s, opacity 0.35s, transform 0.35s; }',
      '.zb-term.zb-lit { filter: none; opacity: 1; transform: scale(1.03); }',
      '.zb-term-tip { position: absolute; left: 0; right: 0; bottom: 100%; margin-bottom: 6px; padding: 8px 10px; background: rgba(44,62,80,0.95); color: #fff; border-radius: 8px; font-size: 0.82rem; opacity: 0; pointer-events: none; transition: opacity 0.25s; z-index: 20; max-width: 280px; }',
      '.zb-term-wrap { position: relative; display: inline; }',
      '.zb-term-tip.zb-show { opacity: 1; }',
      '.zb-expand-panel { max-height: 0; overflow: hidden; transition: max-height 0.45s ease; background: #f4faf0; border-radius: 0 0 10px 10px; font-size: 0.88rem; margin-top: 0; padding: 0 12px; }',
      '.zb-expand-panel.zb-open { max-height: 140px; padding: 12px; margin-top: 8px; }',
      '.zb-obj-li { position: relative; transition: box-shadow 0.3s, background 0.3s; border-radius: 8px; }',
      '.zb-obj-li.zb-scan { box-shadow: inset 0 0 0 2px rgba(106,176,76,0.75); background: rgba(255,255,255,0.12); }',
      '.zb-obj-li::after { content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 3px; background: #6AB04C; transform: scaleY(0); transform-origin: top; transition: transform 0.6s ease; }',
      '.zb-obj-li.zb-scan::after { transform: scaleY(1); }',
      '.zb-fitb-chips { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }',
      '.zb-fitb-chip { padding: 6px 10px; border-radius: 8px; background: rgba(44,62,80,0.08); border: 1px dashed rgba(106,176,76,0.45); font-size: 0.8rem; font-weight: 600; color: #2C3E50; }',
      '.zb-fitb-chip.zb-hot { border-color: #6AB04C; background: rgba(106,176,76,0.15); }',
      '.zb-dwell-timer { position: absolute; right: 6px; top: 50%; transform: translateY(-50%); width: 22px; height: 22px; border-radius: 50%; border: 2px solid rgba(106,176,76,0.35); pointer-events: none; }',
      '.zb-dwell-timer svg { width: 100%; height: 100%; transform: rotate(-90deg); }',
      '.zb-hint-overlay { position: fixed; inset: 0; z-index: 94000; background: rgba(0,0,0,0.48); display: none; align-items: center; justify-content: center; pointer-events: none; }',
      '.zb-hint-overlay.zb-show { display: flex; }',
      '.zb-hint-box { background: #fff; padding: 22px; border-radius: 14px; max-width: 90vw; font-size: 0.92rem; box-shadow: 0 8px 28px rgba(0,0,0,0.2); }',
      '.zb-scroll-slow-msg { position: fixed; bottom: 110px; left: 50%; transform: translateX(-50%); background: rgba(240,147,43,0.95); color: #fff; padding: 9px 18px; border-radius: 999px; font-size: 0.85rem; opacity: 0; transition: opacity 0.3s; z-index: 94800; pointer-events: none; }',
      '.zb-scroll-slow-msg.zb-on { opacity: 1; }',
      '.zb-gesture-intro { position: fixed; top: 78px; right: 8px; width: 224px; background: rgba(44,62,80,0.93); color: #fff; padding: 12px; border-radius: 10px; font-size: 0.72rem; z-index: 94990; transform: translateX(120%); transition: transform 0.45s; }',
      '.zb-gesture-intro.zb-in { transform: translateX(0); }',
      '.zb-lab-particles { position: absolute; inset: 0; pointer-events: none; overflow: hidden; border-radius: 12px; opacity: 0; transition: opacity 0.4s; }',
      '.zb-lab-particles.zb-on { opacity: 1; }',
      '.zb-lab-particles span { position: absolute; width: 5px; height: 5px; background: rgba(106,176,76,0.4); border-radius: 50%; animation: zb08-lp 3.5s linear infinite; }',
      '@keyframes zb08-lp { to { transform: translate(20px,-36px); opacity: 0; } }',
      '.lab-step { position: relative; }',
      '@media (max-width: 375px) { .zb-hud-video { width: 96px; height: 72px; bottom: 80px; right: 6px; } .zb-reading-orb { width: 40px; height: 40px; top: 62px; left: 6px; } .zb-gesture-hud { font-size: 0.72rem; max-width: 160px; top: 62px; } }'
    ].join('');
    document.head.appendChild(st);
  }

  function waitForCurtain(done) {
    const c = document.getElementById('curtain');
    if (!c) {
      done();
      return;
    }
    let finished = false;
    function finish() {
      if (finished) return;
      finished = true;
      done();
    }
    function probe() {
      const st = window.getComputedStyle(c);
      if (st.display === 'none' || parseFloat(st.opacity || '1') < 0.05) finish();
    }
    const mo = new MutationObserver(probe);
    mo.observe(c, { attributes: true, attributeFilter: ['style'] });
    probe();
    setTimeout(finish, 3200);
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

  function isInView(el) {
    if (!el) return false;
    const r = el.getBoundingClientRect();
    return r.top < innerHeight && r.bottom > 0;
  }

  function typeWriter(el, text, startDelay) {
    return new Promise((resolve) => {
      setTimeout(() => {
        let i = 0;
        const tick = () => {
          if (i <= text.length) {
            el.textContent = text.slice(0, i);
            i++;
            setTimeout(tick, 36);
          } else resolve();
        };
        tick();
      }, startDelay);
    });
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
      p.style.animationDelay = Math.random() * 12 + 's';
      p.style.animationDuration = 11 + Math.random() * 14 + 's';
      field.appendChild(p);
    }
    root.appendChild(field);
    const lens = document.createElement('div');
    lens.className = 'zb-lens-wrap';
    lens.innerHTML =
      '<div class="zb-lens-ring"></div>' +
      '<svg class="zb-lens-svg zb-lens-main" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">' +
      '<polygon points="50,8 88,28 88,72 50,92 12,72 12,28" fill="#1a2530" stroke="#6AB04C" stroke-width="2"/>' +
      '<circle class="zb-pupil" cx="50" cy="50" r="14" fill="#F0932B"/>' +
      '<circle cx="50" cy="50" r="22" fill="none" stroke="rgba(106,176,76,0.35)" stroke-width="1"/>' +
      '</svg>';
    root.appendChild(lens);
    const title = document.createElement('div');
    title.className = 'zb-intro-title';
    title.textContent = 'Robotics · Unit 8';
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
    sub.style.cssText =
      'color:#aaa;font-size:0.88rem;margin-top:12px;min-height:1.2em;text-align:center;padding:0 14px;';
    root.appendChild(sub);
    document.body.insertBefore(root, document.body.firstChild);
    document.documentElement.classList.add('zb-no-scroll');
    return { root, title, tag, typeEl, sub };
  }

  function runCalibrationSequence(resolve) {
    ZB.calibrationActive = true;
    ZB.useCursorGaze = true;
    const stEl = document.getElementById('zb-intro-status');
    if (stEl) {
      stEl.innerHTML =
        '<strong style="color:#6AB04C">Mouse / touch</strong> on each dot, or <strong style="color:#6AB04C">point your index finger</strong> at the dot (webcam). <kbd>Esc</kbd> skips.';
    }
    const dots = [
      { x: '12%', y: '26%' },
      { x: '88%', y: '28%' },
      { x: '50%', y: '16%' },
      { x: '18%', y: '74%' },
      { x: '82%', y: '72%' }
    ];
    let idx = 0;
    const bar = document.createElement('div');
    bar.className = 'zb-calib-bar';
    bar.innerHTML = '<div class="zb-calib-fill" id="zb-calib-fill"></div>';
    const introRoot = document.getElementById('zb-intro');
    if (introRoot) introRoot.appendChild(bar);
    let dwellStart = 0;
    const dwellMs = 1500;
    const radius = 52;
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
      if (introRoot) introRoot.appendChild(d);
    }
    placeDot();
    function finishCalib() {
      if (calibDone) return;
      calibDone = true;
      if (ZB.calibRaf) cancelAnimationFrame(ZB.calibRaf);
      ZB.calibrationActive = false;
      document.removeEventListener('keydown', onCalibKey);
      document.removeEventListener('touchstart', onCalibTouch);
      document.removeEventListener('touchmove', onCalibTouch);
      const dot = currentDotEl();
      if (dot) dot.remove();
      if (bar.parentNode) bar.remove();
      resolve();
    }
    function tick() {
      if (idx >= dots.length) {
        finishCalib();
        return;
      }
      const dotEl = currentDotEl();
      if (!dotEl) return;
      const rect = dotEl.getBoundingClientRect();
      const cx = rect.left + rect.width / 2;
      const cy = rect.top + rect.height / 2;
      const fingerFresh = ZB.fingerX != null && performance.now() - ZB.fingerTs < 400;
      const dGaze = Math.hypot(ZB.gazeX - cx, ZB.gazeY - cy);
      const dFinger =
        fingerFresh && ZB.fingerX != null ? Math.hypot(ZB.fingerX - cx, ZB.fingerY - cy) : Infinity;
      const dist = Math.min(dGaze, dFinger);
      const hitR = fingerFresh ? Math.max(radius, 78) : radius;
      if (dist < hitR) {
        if (!dwellStart) dwellStart = performance.now();
        dotEl.classList.add('zb-hot');
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
        dotEl.classList.remove('zb-hot');
      }
      ZB.calibRaf = requestAnimationFrame(tick);
    }
    function onCalibKey(ev) {
      if (ev.key === 'Escape') {
        ev.preventDefault();
        idx = dots.length;
        finishCalib();
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
    if (st) st.textContent = 'Switching to pointer mode…';
    const svg = intro.querySelector('.zb-lens-main');
    if (svg) svg.style.filter = 'grayscale(1) brightness(0.55)';
    ZB.useCursorGaze = true;
    document.body.classList.add('zb-cursor-gaze');
    setTimeout(() => {
      intro.classList.add('zb-deny-shrink');
      document.documentElement.classList.remove('zb-no-scroll');
      setTimeout(() => {
        intro.style.pointerEvents = 'none';
      }, 600);
    }, 1400);
  }

  function bootHud() {
    if (document.getElementById('zb-hud-wrap')) return;
    const wrap = document.createElement('div');
    wrap.id = 'zb-hud-wrap';
    const xp = document.createElement('div');
    xp.className = 'zb-xp-bar zb-boot';
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
      '<span>Say: next · back · quiz me · explain · hint · check · true · false · submit</span>';
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
    setTimeout(() => xp.classList.remove('zb-boot'), 1600);
    loadXp();
    const f = document.getElementById('zb-xp-fill');
    if (f) {
      f.style.width = ZB.xp + '%';
      f.style.setProperty('--zb-xp-pct', ZB.xp + '%');
    }
    const gi = document.createElement('div');
    gi.className = 'zb-gesture-intro';
    gi.innerHTML =
      '<strong>Hands</strong><br>✋ <strong>Open palm</strong> — move hand slowly <strong>up / down</strong> to scroll<br>◀ ▶ Swipe · 🤏 Pinch · ✊ Fist · 👍 XP · ✌️ Hint';
    document.body.appendChild(gi);
    setTimeout(() => gi.classList.add('zb-in'), 400);
    setTimeout(() => gi.classList.remove('zb-in'), 5200);
  }

  function cursorAsGaze() {
    if (ZB.cursorGazeListener) return;
    ZB.cursorGazeListener = true;
    ZB.gazeX = innerWidth / 2;
    ZB.gazeY = innerHeight / 2;
    document.addEventListener(
      'mousemove',
      (e) => {
        if (ZB.calibrationActive || !ZB.useWebGazer || ZB.useCursorGaze || ZB.camDenied) {
          ZB.gazeX = e.clientX;
          ZB.gazeY = e.clientY;
        }
      },
      { passive: true }
    );
    document.body.classList.add('zb-cursor-gaze');
  }

  function startWebGazerPipeline(stream) {
    const v = document.getElementById('zb-hud-v');
    if (v && stream) {
      v.srcObject = stream;
      v.play().catch(() => {});
    }
    const secure = window.isSecureContext === true || location.hostname === 'localhost' || location.hostname === '127.0.0.1';
    if (typeof webgazer === 'undefined' || !secure) {
      ZB.useWebGazer = false;
      ZB.useCursorGaze = true;
      document.body.classList.add('zb-cursor-gaze');
      return;
    }
    try {
      webgazer.setGazeListener((data) => {
        if (ZB.calibrationActive) return;
        if (data == null || data.x == null) return;
        ZB.gazeX = data.x;
        ZB.gazeY = data.y;
        ZB.useWebGazer = true;
        if (!ZB.camDenied) ZB.useCursorGaze = false;
      });
      webgazer.showVideoPreview(false);
      webgazer.showFaceOverlay(false);
      webgazer.showPredictionPoints(false);
      try {
        if (typeof webgazer.setStaticVideo === 'function' && v) webgazer.setStaticVideo(v);
      } catch (e1) {}
      const wg = webgazer.begin && webgazer.begin();
      if (wg && typeof wg.then === 'function') {
        wg.catch(() => {
          ZB.useWebGazer = false;
          ZB.useCursorGaze = true;
          document.body.classList.add('zb-cursor-gaze');
        });
      }
    } catch (e) {
      ZB.useWebGazer = false;
      ZB.useCursorGaze = true;
      document.body.classList.add('zb-cursor-gaze');
    }
  }

  function scrollToId(id) {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function sectionIndex() {
    let best = 0;
    let bestY = -Infinity;
    SECTION_IDS.forEach((id, i) => {
      const el = document.getElementById(id);
      if (!el) return;
      const r = el.getBoundingClientRect();
      if (r.top < 180 && r.top > bestY) {
        bestY = r.top;
        best = i;
      }
    });
    return best;
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

  function showFloatingText(t) {
    const el = document.createElement('div');
    el.style.cssText =
      'position:fixed;bottom:44px;left:50%;transform:translateX(-50%);background:rgba(44,62,80,0.95);color:#fff;padding:7px 14px;border-radius:8px;z-index:96000;font-size:0.82rem;pointer-events:none;transition:opacity 1.4s';
    el.textContent = t;
    document.body.appendChild(el);
    setTimeout(() => {
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 1400);
    }, 1400);
  }

  function runProximityCheck() {
    const el = document.elementFromPoint(ZB.gazeX, ZB.gazeY);
    if (!el) return;
    if (el.closest('#fitb-section') && typeof checkFITB === 'function') {
      checkFITB();
      addXp(5, 'voice-check');
      return;
    }
    if (el.closest('#label-section') && typeof checkLabels === 'function') {
      checkLabels();
      addXp(5, 'voice-check');
      return;
    }
    if (el.closest('#quiz-section') && typeof showQuizScore === 'function') {
      showQuizScore();
      addXp(5, 'voice-check');
    }
  }

  function handleVoiceCmd(raw) {
    const t = raw.toLowerCase().trim();
    if (t.includes('next')) {
      scrollToId(SECTION_IDS[Math.min(SECTION_IDS.length - 1, sectionIndex() + 1)]);
      addXp(5, 'voice');
      return;
    }
    if (t.includes('back')) {
      scrollToId(SECTION_IDS[Math.max(0, sectionIndex() - 1)]);
      addXp(5, 'voice');
      return;
    }
    if (t.includes('quiz')) {
      scrollToId('quiz-section');
      addXp(5, 'voice');
      return;
    }
    if (t.includes('explain')) {
      document.querySelectorAll('.zb-expand-panel').forEach((p) => p.classList.add('zb-open'));
      addXp(5, 'voice');
      return;
    }
    if (t.includes('hint')) {
      showHintOverlay('Robots use sensors, processors, and actuators. Think safety, precision, and repetitive tasks.');
      addXp(5, 'voice');
      return;
    }
    if (t.includes('check') || t.includes('submit')) {
      runProximityCheck();
      return;
    }
    if ((t.includes('show') && t.includes('answer')) || t.includes('reveal')) {
      if (typeof showFITBAnswers === 'function') showFITBAnswers();
      addXp(5, 'voice');
      return;
    }
    if (t.includes('true') || t.includes('false')) {
      const card = document.elementFromPoint(ZB.gazeX, ZB.gazeY);
      const tf = card && card.closest('.tf-card');
      if (tf && !tf.dataset.answered) {
        const wantTrue = t.includes('true') && !t.includes('false');
        const btn = Array.from(tf.querySelectorAll('.tf-btn')).find((b) =>
          wantTrue ? b.textContent.toLowerCase().includes('true') : b.textContent.toLowerCase().includes('false')
        );
        if (btn && typeof checkTF === 'function') {
          checkTF(btn, wantTrue ? 'true' : 'false');
          addXp(5, 'voice-tf');
        }
      }
    }
    if (t.includes('thumbs up') || t.includes('thumbs-up')) {
      addXp(20, 'voice-thumbs');
      showGestureHud('Voice: +XP');
    }
    tryFitbVoice(t);
  }

  const FITB_VOICE = [
    { keys: ['emerging'], id: 'b1' },
    { keys: ['reconnaissance', 'surveillance'], id: 'b2' },
    { keys: ['24', 'non-stop', 'nonstop'], id: 'b3' },
    { keys: ['precision', 'flexibility', 'control'], id: 'b4' },
    { keys: ['sensor', 'pre-programmed', 'preprogrammed', 'operator'], id: 'b5' },
    { keys: ['repetitive'], id: 'b6' }
  ];

  function tryFitbVoice(t) {
    const inFitb = document.elementFromPoint(ZB.gazeX, ZB.gazeY);
    if (!inFitb || !inFitb.closest('#fitb-section')) return;
    FITB_VOICE.forEach((row) => {
      if (row.keys.some((k) => t.includes(k))) {
        const inp = document.getElementById(row.id);
        if (inp) {
          const sample = row.keys[0];
          inp.value = sample === '24' ? '24/7' : sample === 'sensor' ? 'sensors' : sample.replace('-', ' ');
          inp.dispatchEvent(new Event('input', { bubbles: true }));
        }
      }
    });
  }

  function bootVoice() {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) {
      const vb = document.querySelector('.zb-voice-bar span');
      if (vb) vb.textContent = 'Keys: n b q e h c t f';
      document.addEventListener('keydown', onKeyShortcut);
      return;
    }
    try {
      const rec = new SR();
      rec.continuous = true;
      rec.interimResults = false;
      rec.lang = 'en-US';
      rec.onresult = (ev) => {
        const t = (ev.results[ev.results.length - 1][0].transcript || '').trim();
        showFloatingText(t);
        handleVoiceCmd(t.toLowerCase());
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
    } catch (e) {
      document.addEventListener('keydown', onKeyShortcut);
    }
  }

  function onKeyShortcut(e) {
    const k = e.key.toLowerCase();
    if (k === 'n') scrollToId(SECTION_IDS[Math.min(SECTION_IDS.length - 1, sectionIndex() + 1)]);
    if (k === 'b') scrollToId(SECTION_IDS[Math.max(0, sectionIndex() - 1)]);
    if (k === 'q') scrollToId('quiz-section');
    if (k === 'e') document.querySelectorAll('.zb-expand-panel').forEach((p) => p.classList.add('zb-open'));
    if (k === 'h') showHintOverlay('Use sensors + program + actuators framework.');
    if (k === 'c') runProximityCheck();
  }

  /** Index fingertip → screen (mirrored X like a selfie preview). Used during calibration. */
  function updateIndexFingerScreen(lm) {
    const tip = lm[8];
    const pip = lm[6];
    if (!tip || !pip) {
      ZB.fingerX = null;
      return;
    }
    const extended = tip.y < pip.y - 0.035;
    if (!extended) {
      ZB.fingerX = null;
      return;
    }
    const w = window.innerWidth;
    const h = window.innerHeight;
    ZB.fingerX = (1 - tip.x) * w;
    ZB.fingerY = tip.y * h;
    ZB.fingerTs = performance.now();
  }

  function ensureHandsPipeline() {
    if (ZB.handsPipelineStarted) return;
    if (typeof Hands === 'undefined' || typeof Camera === 'undefined') return;
    if (!ZB.camStream) return;
    ZB.handsPipelineStarted = true;
    if (!ZB.handVideo) {
      ZB.handVideo = document.createElement('video');
      ZB.handVideo.srcObject = ZB.camStream;
      ZB.handVideo.playsInline = true;
      ZB.handVideo.muted = true;
      ZB.handVideo.setAttribute('playsinline', '');
      ZB.handVideo.play().catch(() => {});
    }
    const hands = new Hands({
      locateFile: (f) => 'https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4.1675469240/' + f
    });
    hands.setOptions({ maxNumHands: 1, modelComplexity: 1, minDetectionConfidence: 0.45, minTrackingConfidence: 0.4 });
    hands.onResults((res) => {
      if (res.multiHandLandmarks && res.multiHandLandmarks[0]) {
        const lm = res.multiHandLandmarks[0];
        ZB.lastHandLandmarks = res.multiHandLandmarks;
        updateIndexFingerScreen(lm);
        if (ZB.calibrationActive) return;
        const wrist = lm[0];
        ZB.swipeHist.push({ x: wrist.x, y: wrist.y, t: performance.now() });
        if (ZB.swipeHist.length > 14) ZB.swipeHist.shift();
        detectSwipe();
        handlePalmFist(lm);
        if (isPinch(lm) && gestureDebounce()) {
          const m = document.querySelector('#applications .mermaid-wrap') || document.querySelector('.mermaid-wrap');
          const rw = document.querySelector('.robot-diagram-wrap');
          const z = m && isInView(m) ? m : rw;
          if (z) {
            z.style.transform = 'scale(1.22)';
            z.style.transition = 'transform 0.35s ease';
            showGestureHud('Pinch zoom');
            setTimeout(() => {
              z.style.transform = '';
            }, 1100);
          }
        }
        if (isThumbsUp(lm) && gestureDebounce()) {
          addXp(20, 'thumbs');
          showGestureHud('Thumbs up');
        }
        if (isPeace(lm) && gestureDebounce()) {
          showHintOverlay('Tip: match labels to what you see on the robot diagram.');
        }
      } else {
        ZB.fingerX = null;
      }
    });
    try {
      const camera = new Camera(ZB.handVideo, {
        onFrame: async () => {
          await hands.send({ image: ZB.handVideo });
        },
        width: 480,
        height: 360
      });
      camera.start();
      ZB.handsCamera = camera;
    } catch (e) {
      ZB.handsPipelineStarted = false;
    }
  }

  function initMediaPipeHands() {
    ensureHandsPipeline();
  }

  function detectSwipe() {
    const h = ZB.swipeHist;
    if (h.length < 8) return;
    const a = h[0];
    const b = h[h.length - 1];
    const dt = b.t - a.t;
    if (dt > 280) return;
    const vx = (b.x - a.x) / (dt || 1);
    if (Math.abs(vx) > 0.001 && gestureDebounce()) {
      if (vx > 0) navSwipe('right');
      else navSwipe('left');
      ZB.swipeHist = [];
    }
  }

  function navSwipe(dir) {
    if (isInView(document.getElementById('worked')) && typeof nextStep === 'function' && dir === 'right') {
      nextStep();
      showGestureHud('Swipe → next step');
      return;
    }
    if (isInView(document.getElementById('worked')) && typeof resetSteps === 'function' && dir === 'left') {
      resetSteps();
      showGestureHud('Swipe ← reset steps');
      return;
    }
    const i = sectionIndex();
    if (dir === 'right') scrollToId(SECTION_IDS[Math.min(SECTION_IDS.length - 1, i + 1)]);
    else scrollToId(SECTION_IDS[Math.max(0, i - 1)]);
    showGestureHud(dir === 'right' ? 'Swipe right' : 'Swipe left');
  }

  /**
   * Open palm + slow vertical drift of the wrist → calm smooth scroll.
   * (No index-finger “pointing” — thumb is included in open palm.)
   */
  function handleOpenPalmScroll(lm) {
    if (!isOpenPalm(lm)) {
      if (performance.now() - (ZB._palmYsLastT || 0) > 450) ZB._palmYs = null;
      return false;
    }
    ZB._palmYsLastT = performance.now();
    const wy = lm[0].y;
    const now = performance.now();
    if (!ZB._palmYs) ZB._palmYs = [];
    ZB._palmYs.push({ y: wy, t: now });
    while (ZB._palmYs.length > 22) ZB._palmYs.shift();
    if (ZB._palmYs.length < 10) return false;
    const a = ZB._palmYs[0];
    const b = ZB._palmYs[ZB._palmYs.length - 1];
    const dt = b.t - a.t;
    if (dt < 200) return false;
    const vy = (b.y - a.y) / dt;
    const thresh = 0.00022;
    if (Math.abs(vy) < thresh) return false;
    if (now - (ZB._lastPalmScroll || 0) < 260) return false;
    ZB._lastPalmScroll = now;
    const scale = 22000;
    let px = vy * scale;
    px = Math.max(-32, Math.min(32, px));
    window.scrollBy({ top: px, behavior: 'smooth' });
    showGestureHud(px < 0 ? 'Palm moving up — scroll up' : 'Palm moving down — scroll down');
    ZB._palmYs = null;
    return true;
  }

  function handlePalmFist(lm) {
    const el = document.elementFromPoint(ZB.gazeX, ZB.gazeY);
    const card =
      (el && el.closest('#sidebar .sidebar-card')) ||
      (el && el.closest('#sidebar .key-term')) ||
      (el && el.closest('#applications .app-card'));
    const panel = card && card.querySelector('.zb-expand-panel');

    if (isFist(lm) && panel && gestureDebounce()) {
      panel.classList.remove('zb-open');
      showGestureHud('Fist — collapse');
    }

    if (handleOpenPalmScroll(lm)) return;

    if (!card || !panel) return;
    if (performance.now() - (ZB._lastPalmScroll || 0) < 550) return;

    if (isOpenPalm(lm) && gestureDebounce()) {
      panel.classList.add('zb-open');
      showGestureHud('Open palm — expand');
    }
  }

  function isOpenPalm(lm) {
    const tips = [8, 12, 16, 20];
    let ext = 0;
    tips.forEach((i) => {
      if (lm[i].y < lm[i - 2].y) ext++;
    });
    return ext >= 4;
  }

  function isFist(lm) {
    const tips = [8, 12, 16, 20];
    const wrist = lm[0];
    let curled = 0;
    tips.forEach((idx) => {
      if (Math.hypot(lm[idx].x - wrist.x, lm[idx].y - wrist.y) < 0.09) curled++;
    });
    return curled >= 4;
  }

  function isPeace(lm) {
    return lm[8].y < lm[6].y && lm[12].y < lm[10].y && lm[16].y > lm[14].y && lm[20].y > lm[18].y;
  }

  function isPinch(lm) {
    return Math.hypot(lm[4].x - lm[8].x, lm[4].y - lm[8].y) < 0.045;
  }

  function isThumbsUp(lm) {
    return lm[4].y < lm[3].y && lm[8].y > lm[6].y;
  }

  function initTilt() {
    window.addEventListener(
      'deviceorientation',
      (e) => {
        if (e.beta != null) ZB.tiltBeta = e.beta;
        if (e.gamma != null) ZB.tiltGamma = e.gamma;
        const adv = document.getElementById('adv-dis');
        if (adv && isInView(adv)) {
          const g = ZB.tiltGamma || 0;
          adv.style.setProperty('--zb-tilt', String(g));
          const cols = adv.querySelectorAll('.adv-dis-grid > div');
          if (cols[0])
            cols[0].style.transform = 'translateX(' + Math.max(-8, Math.min(8, g * 0.15)) + 'px)';
          if (cols[1])
            cols[1].style.transform = 'translateX(' + Math.max(-8, Math.min(8, -g * 0.15)) + 'px)';
        }
        const quiz = document.getElementById('quiz-section');
        if (quiz && isInView(quiz)) tiltQuiz(e);
      },
      { passive: true }
    );
  }

  let quizTiltIdx = null;
  let quizTiltT0 = 0;
  function tiltQuiz(e) {
    const mid = document.elementFromPoint(innerWidth / 2, innerHeight / 2);
    const card = mid && mid.closest('.question-card');
    if (!card) return;
    const opts = card.querySelectorAll('.option-btn');
    if (opts.length < 4) return;
    const gamma = e.gamma != null ? e.gamma : 0;
    const beta = e.beta != null ? e.beta : 45;
    let idx = 0;
    if (gamma < -14) idx = 0;
    else if (gamma > 14) idx = 1;
    else if (beta < 38) idx = 2;
    else idx = 3;
    if (quizTiltIdx !== idx) {
      quizTiltIdx = idx;
      quizTiltT0 = performance.now();
      return;
    }
    if (performance.now() - quizTiltT0 > 1600) {
      const b = opts[idx];
      if (b && !b.disabled && typeof b.click === 'function') b.click();
      quizTiltT0 = performance.now();
      quizTiltIdx = null;
    }
  }

  function setupHero() {
    const svg = document.querySelector('#hero .hero-robot-svg');
    const inner = document.querySelector('#hero .hero-inner');
    const text = document.querySelector('#hero .hero-text');
    if (!svg || !inner) return;
    document.addEventListener(
      'mousemove',
      (e) => {
        const r = svg.getBoundingClientRect();
        const mx = r.left + r.width / 2;
        const my = r.top + r.height / 2;
        svg.style.transform =
          'translate(' + (e.clientX - mx) * 0.15 + 'px,' + (e.clientY - my) * 0.15 + 'px)';
        if (text) {
          const tr = text.getBoundingClientRect();
          const d = distPointToRect(e.clientX, e.clientY, tr);
          const cl = Math.max(0, 1 - Math.min(1, d / 140));
          text.style.filter = cl > 0.92 ? 'none' : 'blur(' + ((1 - cl) * 1).toFixed(2) + 'px)';
          text.style.opacity = String(0.9 + cl * 0.1);
        }
        if (inner) {
          const ox = (e.clientX - innerWidth / 2) * 0.02;
          const oy = (e.clientY - innerHeight / 2) * 0.02;
          inner.style.transform = 'translate(' + ox + 'px,' + oy + 'px)';
        }
      },
      { passive: true }
    );
  }

  function setupObjectives() {
    const objXp = new Set();
    document.querySelectorAll('.objectives-list li').forEach((li) => {
      li.classList.add('zb-obj-li');
    });
    let lastLi = null;
    let t0 = 0;
    function tick() {
      const el = document.elementFromPoint(ZB.gazeX, ZB.gazeY);
      const li = el && el.closest('.objectives-list li');
      document.querySelectorAll('.objectives-list li').forEach((x) => x.classList.remove('zb-scan'));
      if (li) {
        li.classList.add('zb-scan');
        if (lastLi !== li) {
          lastLi = li;
          t0 = performance.now();
        }
        if (performance.now() - t0 > 1000 && !objXp.has(li)) {
          objXp.add(li);
          addXp(3, 'objective');
        }
      } else lastLi = null;
      requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  function wrapKeyTerms() {
    const main = document.querySelector('#what-is .main-content');
    if (!main || main.dataset.zbTerms) return;
    main.dataset.zbTerms = '1';
    const terms = [
      { re: /\bRobotics\b/g, tip: 'Design and use of machines that can act autonomously or with guidance.' },
      { re: /\bArtificial Intelligence\b/g, tip: 'Computer systems that can learn, reason, or recognise patterns.' },
      { re: /\bBiometrics\b/g, tip: 'Measuring human features (fingerprints, face) for identity.' },
      { re: /\bemerging technologies\b/gi, tip: 'New tech that is still growing fast and changing industries.' }
    ];
    const ps = main.querySelectorAll('p, .highlight-box, .definition-box');
    ps.forEach((p) => {
      if (p.querySelector('.zb-term-wrap')) return;
      let html = p.innerHTML;
      terms.forEach(({ re, tip }) => {
        re.lastIndex = 0;
        const safeTip = tip.replace(/</g, ' ').replace(/"/g, '&quot;');
        html = html.replace(re, (m) => {
          return (
            '<span class="zb-term-wrap"><span class="zb-term zb-blur" data-tip="' +
            safeTip +
            '">' +
            m +
            '</span><span class="zb-term-tip">' +
            tip.replace(/</g, ' ') +
            '</span></span>'
          );
        });
      });
      p.innerHTML = html;
    });
    let dwellEl = null;
    let dwellT = 0;
    function tick() {
      const el = document.elementFromPoint(ZB.gazeX, ZB.gazeY);
      const term = el && el.closest('.zb-term');
      document.querySelectorAll('.zb-term-tip').forEach((tip) => tip.classList.remove('zb-show'));
      if (term) {
        term.classList.add('zb-lit');
        term.classList.remove('zb-blur');
        const tip = term.parentElement && term.parentElement.querySelector('.zb-term-tip');
        if (dwellEl !== term) {
          dwellEl = term;
          dwellT = performance.now();
        }
        if (performance.now() - dwellT > 1000 && tip) {
          tip.classList.add('zb-show');
          if (!term.dataset.zbXpTerm) {
            term.dataset.zbXpTerm = '1';
            addXp(5, 'term');
          }
        }
      } else {
        dwellEl = null;
        document.querySelectorAll('.zb-term').forEach((x) => {
          x.classList.remove('zb-lit');
          x.classList.add('zb-blur');
        });
      }
      requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  function setupSidebarPanels() {
    document
      .querySelectorAll('#sidebar .sidebar-card, #sidebar .key-term, #applications .app-card')
      .forEach((card) => {
        if (card.querySelector('.zb-expand-panel')) return;
        card.style.position = 'relative';
        const p = document.createElement('div');
        p.className = 'zb-expand-panel';
        p.textContent =
          'Think: input (sensors) → process (computer) → output (motors, lights, movement). How would you use this in real life?';
        card.appendChild(p);
      });
  }

  function setupAppMagnetic() {
    const cards = document.querySelectorAll('#applications .app-card');
    document.addEventListener(
      'mousemove',
      (e) => {
        cards.forEach((card) => {
          const r = card.getBoundingClientRect();
          const cx = r.left + r.width / 2;
          const cy = r.top + r.height / 2;
          const d = Math.hypot(e.clientX - cx, e.clientY - cy);
          if (d < 80) {
            card.style.transform =
              'translate(' + (e.clientX - cx) * 0.15 + 'px,' + (e.clientY - cy) * 0.15 + 'px)';
          } else card.style.transform = '';
        });
      },
      { passive: true }
    );
  }

  function setupWorkedSteps() {
    let dwell = 0;
    function tick() {
      if (!isInView(document.getElementById('worked'))) {
        dwell = 0;
        requestAnimationFrame(tick);
        return;
      }
      const el = document.elementFromPoint(ZB.gazeX, ZB.gazeY);
      const step = el && el.closest('.step-box.visible');
      if (step) {
        if (!dwell) dwell = performance.now();
        if (performance.now() - dwell > 1800 && typeof nextStep === 'function') {
          nextStep();
          dwell = 0;
        }
      } else dwell = 0;
      requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  function setupTfDwell() {
    function tick() {
      const el = document.elementFromPoint(ZB.gazeX, ZB.gazeY);
      const btn = el && el.closest('.tf-btn');
      const card = btn && btn.closest('.tf-card');
      if (btn && card && !card.dataset.answered) {
        if (setupTfDwell._el !== btn) {
          setupTfDwell._el = btn;
          setupTfDwell._t = performance.now();
        }
        if (performance.now() - setupTfDwell._t > 2000) {
          btn.click();
          setTimeout(() => {
            if (btn.classList.contains('selected-correct')) addXp(15, 'tf');
          }, 0);
          setupTfDwell._t = 0;
          setupTfDwell._el = null;
        }
      } else {
        setupTfDwell._t = 0;
        setupTfDwell._el = null;
      }
      requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  function setupFitbChips() {
    const card = document.querySelector('#fitb-section .fitb-card');
    if (!card || document.getElementById('zb-fitb-chips')) return;
    const wrap = document.createElement('div');
    wrap.id = 'zb-fitb-chips';
    wrap.className = 'zb-fitb-chips';
    ['emerging', 'reconnaissance', '24/7', 'precision', 'sensors', 'repetitive'].forEach((label) => {
      const c = document.createElement('div');
      c.className = 'zb-fitb-chip';
      c.textContent = label;
      c.dataset.fitb = label;
      wrap.appendChild(c);
    });
    card.appendChild(wrap);
    let chipDwell = 0;
    let chipEl = null;
    function tick() {
      const el = document.elementFromPoint(ZB.gazeX, ZB.gazeY);
      const chip = el && el.closest('.zb-fitb-chip');
      document.querySelectorAll('.zb-fitb-chip').forEach((x) => x.classList.remove('zb-hot'));
      if (chip) {
        chip.classList.add('zb-hot');
        if (chipEl !== chip) {
          chipEl = chip;
          chipDwell = performance.now();
        }
        if (performance.now() - chipDwell > 1400) {
          const v = chip.dataset.fitb;
          const map = {
            emerging: { id: 'b1', val: 'emerging' },
            reconnaissance: { id: 'b2', val: 'reconnaissance' },
            '24/7': { id: 'b3', val: '24/7' },
            precision: { id: 'b4', val: 'precision' },
            sensors: { id: 'b5', val: 'sensors' },
            repetitive: { id: 'b6', val: 'repetitive' }
          };
          const m = map[v];
          if (m) {
            const inp = document.getElementById(m.id);
            if (inp) {
              inp.value = m.val;
              inp.dispatchEvent(new Event('input', { bubbles: true }));
            }
          }
          chipDwell = performance.now();
        }
      } else {
        chipEl = null;
      }
      requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  function setupLabelGaze() {
    let lastPickT = 0;
    let pick = null;
    let pickT = 0;
    let dropDwell = 0;
    function tick() {
      const el = document.elementFromPoint(ZB.gazeX, ZB.gazeY);
      const lab = el && el.closest('#label-section .drag-label:not(.used)');
      const drop = el && el.closest('#label-section .drop-target');
      if (lab) {
        if (pick !== lab) {
          pick = lab;
          pickT = performance.now();
        }
        if (performance.now() - pickT > 1200 && typeof window.selectLabel === 'function') {
          window.selectLabel(lab);
          lastPickT = performance.now();
          pickT = performance.now();
        }
      }
      if (drop && performance.now() - lastPickT < 12000) {
        if (!dropDwell) dropDwell = performance.now();
        if (performance.now() - dropDwell > 1100) {
          drop.click();
          dropDwell = 0;
          lastPickT = 0;
        }
      } else dropDwell = 0;
      requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  function setupQuizDwell() {
    let elD = null;
    let t0 = 0;
    function tick() {
      const el = document.elementFromPoint(ZB.gazeX, ZB.gazeY);
      const opt = el && el.closest('#quiz-section .option-btn:not([disabled])');
      if (opt) {
        if (elD !== opt) {
          elD = opt;
          t0 = performance.now();
        }
        const p = Math.min(1, (performance.now() - t0) / 2000);
        opt.style.boxShadow = '0 0 0 ' + (3 + p * 4) + 'px rgba(106,176,76,' + (0.2 + p * 0.5) + ')';
        if (p >= 1) {
          opt.click();
          if (opt.dataset.correct === 'true') addXp(15, 'quiz');
          const card = opt.closest('.question-card');
          if (card) card.querySelectorAll('.option-btn').forEach((b) => (b.style.boxShadow = ''));
          elD = null;
          t0 = 0;
        }
      } else {
        if (elD) elD.style.boxShadow = '';
        elD = null;
      }
      requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  function setupQuizScoreDwell() {
    const scoreBtn = document.querySelector('#quiz-section button[onclick*="showQuizScore"]');
    function tick() {
      const el = document.elementFromPoint(ZB.gazeX, ZB.gazeY);
      const onBtn = scoreBtn && (el === scoreBtn || scoreBtn.contains(el));
      if (onBtn && isInView(document.getElementById('quiz-section'))) {
        if (!setupQuizScoreDwell._t) setupQuizScoreDwell._t = performance.now();
        if (performance.now() - setupQuizScoreDwell._t > 2200) {
          if (typeof showQuizScore === 'function') showQuizScore();
          setupQuizScoreDwell._t = 0;
        }
      } else setupQuizScoreDwell._t = 0;
      requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  function setupLabParticles() {
    document.querySelectorAll('#lab .lab-step').forEach((step) => {
      if (step.querySelector('.zb-lab-particles')) return;
      const p = document.createElement('div');
      p.className = 'zb-lab-particles';
      for (let i = 0; i < 8; i++) {
        const s = document.createElement('span');
        s.style.left = Math.random() * 90 + '%';
        s.style.top = Math.random() * 80 + '%';
        s.style.animationDelay = Math.random() * 2 + 's';
        p.appendChild(s);
      }
      step.appendChild(p);
    });
    let scrollStop = performance.now();
    let lastY = window.scrollY;
    window.addEventListener(
      'scroll',
      () => {
        if (Math.abs(window.scrollY - lastY) > 2) {
          scrollStop = performance.now();
          lastY = window.scrollY;
        }
      },
      { passive: true }
    );
    function tick() {
      const idle = performance.now() - scrollStop;
      document.querySelectorAll('#lab .lab-step').forEach((step) => {
        const r = step.getBoundingClientRect();
        const vis = r.top < innerHeight && r.bottom > 0;
        const p = step.querySelector('.zb-lab-particles');
        if (p && vis && idle > 3000) p.classList.add('zb-on');
        else if (p) p.classList.remove('zb-on');
      });
      requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  function setupFooterBurst() {
    const foot = document.querySelector('footer');
    if (!foot) return;
    const io = new IntersectionObserver(
      (ents) => {
        ents.forEach((en) => {
          if (en.isIntersecting) {
            saveXp();
            const orb = document.querySelector('.zb-reading-orb');
            if (orb) {
              orb.animate([{ transform: 'scale(1)' }, { transform: 'scale(1.25)' }, { transform: 'scale(1)' }], {
                duration: 800
              });
            }
            addXp(10, 'footer');
            io.disconnect();
          }
        });
      },
      { threshold: 0.2 }
    );
    io.observe(foot);
  }

  /** Distance from point to rectangle; 0 if inside the box (for torch: stay sharp while reading). */
  function distPointToRect(px, py, r) {
    const cx = Math.max(r.left, Math.min(px, r.right));
    const cy = Math.max(r.top, Math.min(py, r.bottom));
    return Math.hypot(px - cx, py - cy);
  }

  function setupTorchParallax() {
    const layers = document.querySelectorAll(
      '#hero, .objectives-strip, #what-is, #applications, #adv-dis, #tf-section, #fitb-section, #label-section, #quiz-section, #lab'
    );
    layers.forEach((el) => {
      if (!el) return;
      el.classList.add('zb-torch-target');
    });
    const falloff = 200;
    document.addEventListener(
      'mousemove',
      (e) => {
        const px = e.clientX;
        const py = e.clientY;
        layers.forEach((sec) => {
          if (!sec) return;
          const r = sec.getBoundingClientRect();
          const d = distPointToRect(px, py, r);
          const t = Math.max(0, 1 - d / falloff);
          const opacity = 0.94 + t * 0.06;
          const blurPx = (1 - t) * 1.2;
          sec.style.opacity = String(opacity);
          sec.style.filter = blurPx < 0.05 ? 'none' : 'blur(' + blurPx.toFixed(2) + 'px)';
          if (t > 0.55) sec.style.boxShadow = 'inset 0 0 0 1px rgba(106,176,76,0.18)';
          else sec.style.boxShadow = 'none';
        });
      },
      { passive: true }
    );
  }

  function setupScrollVelocity() {
    let lastY = window.scrollY;
    let lastT = performance.now();
    let vel = 0;
    let slowSince = 0;
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
        if (Math.abs(vel) > 6) msg.classList.add('zb-on');
      },
      { passive: true }
    );
    function decayMsg() {
      if (Math.abs(vel) < 0.8) {
        if (!slowSince) slowSince = performance.now();
        if (performance.now() - slowSince > 350) msg.classList.remove('zb-on');
      } else {
        slowSince = 0;
      }
      vel *= 0.92;
      requestAnimationFrame(decayMsg);
    }
    requestAnimationFrame(decayMsg);
  }

  function setupReadingOrb() {
    function tick() {
      const pct = Math.min(1, window.scrollY / Math.max(1, document.body.scrollHeight - innerHeight));
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

  function setupSectionXp() {
    function tick() {
      SECTION_IDS.forEach((id) => {
        const sec = document.getElementById(id);
        if (!sec || !isInView(sec)) return;
        const el = document.elementFromPoint(ZB.gazeX, ZB.gazeY);
        if (el && sec.contains(el)) {
          if (!ZB.sectionDwellT[id]) ZB.sectionDwellT[id] = performance.now();
          if (performance.now() - ZB.sectionDwellT[id] > 5000) {
            addXp(10, 'section-read');
            ZB.sectionDwellT[id] = performance.now() + 60000;
          }
        }
      });
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
    initMediaPipeHands();
    initTilt();
    setupHero();
    setupObjectives();
    setupSidebarPanels();
    wrapKeyTerms();
    setupAppMagnetic();
    setupWorkedSteps();
    setupTfDwell();
    setupFitbChips();
    setupLabelGaze();
    setupQuizDwell();
    setupQuizScoreDwell();
    setupLabParticles();
    setupFooterBurst();
    setupTorchParallax();
    setupScrollVelocity();
    setupReadingOrb();
    setupSectionXp();
  }

  function boot() {
    loadXp();
    injectStyles();
    cursorAsGaze();
    waitForCurtain(() => {
      createIntroOverlay();
      const el = document.getElementById('zb-intro');
      if (!el) return;
      const refs = {
        title: el.querySelector('.zb-intro-title'),
        tag: el.querySelector('.zb-intro-tag'),
        typeEl: document.getElementById('zb-type-text'),
        sub: document.getElementById('zb-intro-status')
      };
      setTimeout(() => refs.title && refs.title.classList.add('zb-show'), 900);
      setTimeout(() => refs.tag && refs.tag.classList.add('zb-show'), 1700);
      typeWriter(
        refs.typeEl,
        'Look at the dots to calibrate. Use your hands to explore the lesson.',
        2500
      );
      setTimeout(() => {
        const sub = document.getElementById('zb-intro-status');
        if (sub) sub.textContent = 'Requesting camera…';
        ZB.calibrationActive = true;
        ZB.useCursorGaze = true;
        navigator.mediaDevices
          .getUserMedia({ video: true, audio: false })
          .then((stream) => {
            ZB.camStream = stream;
            bootHud();
            const vid = document.getElementById('zb-hud-video');
            const v = document.getElementById('zb-hud-v');
            if (v) {
              v.srcObject = stream;
              v.play().catch(() => {});
            }
            if (vid) vid.style.display = 'block';
            const pupil = document.querySelector('.zb-pupil');
            if (pupil) pupil.setAttribute('fill', '#6AB04C');
            if (sub) sub.textContent = 'Calibrating…';
            startWebGazerPipeline(stream);
            ensureHandsPipeline();
            return new Promise((resolve) => {
              setTimeout(() => runCalibrationSequence(resolve), 700);
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
            setTimeout(startAfterIntro, 1800);
          });
      }, 3400);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
