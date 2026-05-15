/**
 * Unit 7 — horseshoe magnet on rope + floor pile, MediaPipe Hands.
 * Pinch or fist to grab; green ring = pointer; mirrored video preview for alignment.
 */
(function () {
  'use strict';

  const MP_VER = '0.4.1675469240';
  const MP_SRC = 'https://cdn.jsdelivr.net/npm/@mediapipe/hands@' + MP_VER + '/hands.js';

  const root = document.getElementById('mp7-root');
  const canvas = document.getElementById('mp7-canvas');
  const video = document.getElementById('mp7-video');
  const btnStart = document.getElementById('mp7-start');
  const btnReset = document.getElementById('mp7-reset');
  const statusEl = document.getElementById('mp7-status');
  const hintEl = document.getElementById('mp7-magnet-hint');
  const legendEl = document.getElementById('mp7-legend');

  if (!root || !canvas || !video || !btnStart) return;

  const ctx = canvas.getContext('2d');
  const W = 960;
  const H = 540;
  const GRAB_RADIUS = 62;
  const GRAB_RADIUS_PINCH_BONUS = 24;
  /** Consecutive frames (hand callbacks ~30/s) before grab/release latch toggles */
  const GRAB_ARM_FRAMES = 2;
  const RELEASE_ARM_FRAMES = 4;
  const ICON_FONT = '48px "Segoe UI Emoji","Apple Color Emoji","Noto Color Emoji",sans-serif';
  const LABEL_FONT = '11px Inter,system-ui,sans-serif';

  /** Horseshoe layout (must match drawHangingHorseshoe) */
  const KNOT_Y = 32;
  const TOP_PAD = 4;
  const LEG_LEN = 62;
  const SPAN = 42;
  const TIP_Y = KNOT_Y + TOP_PAD + LEG_LEN;
  const MAGNET_ZONE_BOTTOM = TIP_Y + 48;
  const MAGNET_ZONE_HALF_W = 132;

  const SPECS = [
    { label: 'Iron bolt', magnetic: true, emoji: '🔩' },
    { label: 'Steel clip', magnetic: true, emoji: '📎' },
    { label: 'Nickel coin', magnetic: true, emoji: '🪙' },
    { label: 'Cobalt chip', magnetic: true, emoji: '🔷' },
    { label: 'Steel key', magnetic: true, emoji: '🔑' },
    { label: 'Tin can', magnetic: true, emoji: '🥫' },
    { label: 'Plastic toy', magnetic: false, emoji: '🧸' },
    { label: 'Rubber ball', magnetic: false, emoji: '⚪' },
    { label: 'Glass jar', magnetic: false, emoji: '🫙' },
    { label: 'Wood block', magnetic: false, emoji: '🪵' },
    { label: 'Paper card', magnetic: false, emoji: '🃏' },
    { label: 'Foam cube', magnetic: false, emoji: '🟪' },
    { label: 'Ceramic cup', magnetic: false, emoji: '☕' },
    { label: 'Cotton ball', magnetic: false, emoji: '☁️' },
    { label: 'Copper wire', magnetic: false, emoji: '🔗' },
    { label: 'Aluminium foil', magnetic: false, emoji: '✨' }
  ];

  let stream = null;
  let hands = null;
  let pipelineRunning = false;
  let grabLatch = false;
  let wasGrab = false;
  let grabOnStreak = 0;
  let grabOffStreak = 0;
  let heldObject = null;
  let holdOffsetX = 0;
  let holdOffsetY = 0;
  let sx = null;
  let sy = null;
  let requireOpenBeforeGrab = false;
  let objects = [];
  let rafId = 0;
  let hintTimer = 0;
  let lastHintAt = 0;
  /** Latest smoothed grab point for pointer (canvas px) */
  let lastSmoothedPick = null;
  /** Recent pick points for stable release placement */
  const pickHistory = [];
  const PICK_HISTORY_MAX = 5;

  function liveMagnetSway() {
    return Math.sin(performance.now() * 0.0022) * 10;
  }

  function liveMagnetX() {
    return W / 2 + liveMagnetSway();
  }

  function setStatus(msg) {
    if (statusEl) statusEl.textContent = msg || '';
  }

  function setLegend(msg) {
    if (legendEl) legendEl.textContent = msg || '';
  }

  function clearHint() {
    if (!hintEl) return;
    hintEl.textContent = '';
    hintEl.classList.remove('mp7-on', 'mp7-warn', 'mp7-info');
    clearTimeout(hintTimer);
  }

  function showHint(msg, kind, ms, minGapMs) {
    if (!hintEl || !msg) return;
    const now = performance.now();
    const gap = minGapMs != null ? minGapMs : kind === 'info' ? 1200 : 5200;
    if (now - lastHintAt < gap) return;
    lastHintAt = now;
    hintEl.textContent = msg;
    hintEl.classList.remove('mp7-warn', 'mp7-info');
    hintEl.classList.add('mp7-on', kind === 'info' ? 'mp7-info' : 'mp7-warn');
    clearTimeout(hintTimer);
    hintTimer = setTimeout(clearHint, ms || (kind === 'info' ? 2800 : 4500));
  }

  function pinchDist(lm) {
    const a = lm[4];
    const b = lm[8];
    if (!a || !b) return 1;
    return Math.hypot(a.x - b.x, a.y - b.y);
  }

  function curledCount(lm) {
    const wrist = lm[0];
    const tips = [8, 12, 16, 20];
    let n = 0;
    for (let i = 0; i < tips.length; i++) {
      const t = lm[tips[i]];
      if (!t) continue;
      if (Math.hypot(t.x - wrist.x, t.y - wrist.y) < 0.14) n++;
    }
    return n;
  }

  function fingerCanvas(lm) {
    const t = lm[8];
    if (!t) return null;
    return { x: (1 - t.x) * W, y: t.y * H };
  }

  function grabPointCanvas(lm) {
    const f = fingerCanvas(lm);
    const w = lm[0];
    const m = lm[9];
    if (!f || !w || !m) return f;
    return {
      x: 0.5 * f.x + 0.5 * (1 - (w.x + m.x) / 2) * W,
      y: 0.5 * f.y + 0.5 * ((w.y + m.y) / 2) * H
    };
  }

  /** Pinch midpoint when fingers are pinched — steadier for grab/hit than index alone */
  function pinchMidCanvas(lm) {
    const a = lm[4];
    const b = lm[8];
    if (!a || !b) return null;
    return { x: (1 - (a.x + b.x) / 2) * W, y: ((a.y + b.y) / 2) * H };
  }

  function pickPointRaw(lm) {
    const d = pinchDist(lm);
    const mid = pinchMidCanvas(lm);
    if (d < 0.092 && mid) return mid;
    return grabPointCanvas(lm);
  }

  function blendPickPoint(lm) {
    const raw = pickPointRaw(lm);
    const finger = fingerCanvas(lm);
    if (raw && finger) {
      return { x: 0.32 * finger.x + 0.68 * raw.x, y: 0.32 * finger.y + 0.68 * raw.y };
    }
    return raw || finger;
  }

  function smoothPoint(pt) {
    const aFree = 0.7;
    const aHold = 0.78;
    const a = heldObject ? aHold : aFree;
    if (!pt) return null;
    if (sx == null) {
      sx = pt.x;
      sy = pt.y;
      return { x: sx, y: sy };
    }
    sx = a * pt.x + (1 - a) * sx;
    sy = a * pt.y + (1 - a) * sy;
    return { x: sx, y: sy };
  }

  function resetSmooth() {
    sx = null;
    sy = null;
  }

  function pushPickHistory(pt) {
    if (!pt) return;
    pickHistory.push({ x: pt.x, y: pt.y });
    while (pickHistory.length > PICK_HISTORY_MAX) pickHistory.shift();
  }

  function meanPickHistory() {
    if (!pickHistory.length) return null;
    let x = 0;
    let y = 0;
    for (let i = 0; i < pickHistory.length; i++) {
      x += pickHistory[i].x;
      y += pickHistory[i].y;
    }
    const n = pickHistory.length;
    return { x: x / n, y: y / n };
  }

  function clearPickHistory() {
    pickHistory.length = 0;
  }

  function updateGrabDebounced(lm) {
    const d = pinchDist(lm);
    const cur = curledCount(lm);
    const rawClosed = d < 0.078 || cur >= 2;
    const rawOpen = d > 0.11 && cur <= 1;

    if (rawClosed) {
      grabOffStreak = 0;
      grabOnStreak = Math.min(grabOnStreak + 1, 12);
    } else if (rawOpen) {
      grabOnStreak = 0;
      grabOffStreak = Math.min(grabOffStreak + 1, 12);
    } else {
      grabOnStreak = Math.max(0, grabOnStreak - 1);
      grabOffStreak = Math.max(0, grabOffStreak - 1);
    }

    if (!grabLatch && grabOnStreak >= GRAB_ARM_FRAMES) grabLatch = true;
    if (grabLatch && grabOffStreak >= RELEASE_ARM_FRAMES) grabLatch = false;
  }

  function inMagnetZone(ox, oy) {
    const mx = liveMagnetX();
    return oy < MAGNET_ZONE_BOTTOM && Math.abs(ox - mx) < MAGNET_ZONE_HALF_W;
  }

  function scatterObjects() {
    const cx = W * 0.5 + (Math.random() - 0.5) * 36;
    const cy = H * 0.78 + (Math.random() - 0.5) * 20;
    const placed = [];
    objects = SPECS.map(function (s) {
      let x;
      let y;
      let tries = 0;
      do {
        const ang = Math.random() * Math.PI * 2;
        const rad = 22 + Math.random() * 72;
        x = cx + Math.cos(ang) * rad;
        y = cy + Math.sin(ang) * rad * 0.72;
        x = Math.max(48, Math.min(W - 48, x));
        y = Math.max(H * 0.58, Math.min(H - 36, y));
        tries++;
      } while (tries < 100 && placed.some(function (p) {
        return Math.hypot(p[0] - x, p[1] - y) < 32;
      }));
      placed.push([x, y]);
      return {
        label: s.label,
        magnetic: s.magnetic,
        emoji: s.emoji,
        x: x,
        y: y,
        state: 'floor',
        magnetSlot: -1,
        _nmHintSent: false
      };
    });
    heldObject = null;
    requireOpenBeforeGrab = false;
    resetSmooth();
    grabLatch = false;
    wasGrab = false;
    grabOnStreak = 0;
    grabOffStreak = 0;
    clearPickHistory();
  }

  function attachHeldToMagnet() {
    if (!heldObject || !heldObject.magnetic) return;
    const slot = objects.filter(function (o) {
      return o.state === 'magnet';
    }).length;
    heldObject.state = 'magnet';
    heldObject.magnetSlot = slot;
    heldObject = null;
    requireOpenBeforeGrab = true;
    clearPickHistory();
    clearHint();
    setStatus('Stuck to the magnet! Relax pinch / open hand, then grab another icon.');
  }

  function tryPickFromFloor(pickPt, lm) {
    if (!pickPt || heldObject || requireOpenBeforeGrab) return;
    const pinched = pinchDist(lm) < 0.092;
    const reach = GRAB_RADIUS + (pinched ? GRAB_RADIUS_PINCH_BONUS : 10);
    let best = null;
    let bestD = reach;
    for (let i = 0; i < objects.length; i++) {
      const o = objects[i];
      if (o.state !== 'floor') continue;
      const d = Math.hypot(o.x - pickPt.x, o.y - pickPt.y);
      if (d < bestD) {
        bestD = d;
        best = o;
      }
    }
    if (best) {
      heldObject = best;
      best.state = 'held';
      holdOffsetX = best.x - pickPt.x;
      holdOffsetY = best.y - pickPt.y;
      sx = pickPt.x;
      sy = pickPt.y;
      clearPickHistory();
      pushPickHistory({ x: pickPt.x, y: pickPt.y });
      setStatus('Holding — lift into dashed zone (metals stick). Release pinch / open hand to drop.');
    }
  }

  function releaseHeld(smoothPt) {
    if (!heldObject) return;
    const ox = heldObject.x;
    const oy = heldObject.y;
    if (heldObject.magnetic && inMagnetZone(ox, oy)) {
      attachHeldToMagnet();
      clearPickHistory();
      return;
    }
    if (!heldObject.magnetic && inMagnetZone(ox, oy)) {
      showHint(
        'This material is not magnetic — it will not stick to the horseshoe magnet.',
        'warn',
        4500
      );
    }
    const stable = meanPickHistory() || smoothPt || { x: ox - holdOffsetX, y: oy - holdOffsetY };
    heldObject.state = 'floor';
    heldObject.x = Math.max(40, Math.min(W - 40, stable.x - holdOffsetX));
    heldObject.y = Math.max(H * 0.56, Math.min(H - 32, stable.y - holdOffsetY));
    heldObject = null;
    clearPickHistory();
    sx = stable.x;
    sy = stable.y;
    setStatus('Pinch or fist on an icon in the pile to grab it.');
  }

  function onHandResults(results) {
    const lm = results.multiHandLandmarks && results.multiHandLandmarks[0];

    if (!lm) {
      if (!heldObject) {
        wasGrab = false;
        grabLatch = false;
        grabOnStreak = 0;
        grabOffStreak = 0;
        resetSmooth();
        lastSmoothedPick = null;
        clearPickHistory();
        if (pipelineRunning) setLegend('○ Show your hand — green pointer when tracked');
      } else {
        lastSmoothedPick = sx != null ? { x: sx, y: sy } : null;
        if (pipelineRunning) setLegend('… Hand lost — object frozen; show hand again');
      }
      return;
    }

    updateGrabDebounced(lm);
    const grab = grabLatch;

    const blended = blendPickPoint(lm);
    const smooth = blended ? smoothPoint(blended) : null;
    if (smooth) {
      lastSmoothedPick = { x: smooth.x, y: smooth.y };
      pushPickHistory(smooth);
    }

    if (pipelineRunning) {
      const pinchOn = pinchDist(lm) < 0.085;
      setLegend(
        pinchOn || grab
          ? '● Tracking — pinch or fist = grab'
          : '● Tracking — move green ring over an icon, then pinch'
      );
    }

    if (!grab) requireOpenBeforeGrab = false;

    if (heldObject && smooth) {
      heldObject.x = smooth.x + holdOffsetX;
      heldObject.y = smooth.y + holdOffsetY;
    }

    if (heldObject && heldObject.magnetic && inMagnetZone(heldObject.x, heldObject.y)) {
      attachHeldToMagnet();
      wasGrab = grab;
      return;
    }
    if (heldObject && !heldObject.magnetic) {
      const inZ = inMagnetZone(heldObject.x, heldObject.y);
      if (inZ) {
        if (!heldObject._nmHintSent) {
          heldObject._nmHintSent = true;
          showHint(
            'This material is not magnetic — it will not stick to the horseshoe magnet.',
            'warn',
            4800,
            5200
          );
        }
      } else {
        heldObject._nmHintSent = false;
      }
    }

    if (grab && !wasGrab && !heldObject && !requireOpenBeforeGrab) {
      tryPickFromFloor(blended || smooth || fingerCanvas(lm), lm);
    }
    if (!grab && wasGrab && heldObject) {
      releaseHeld(smooth);
    }

    wasGrab = grab;
  }

  function drawHangingHorseshoe(mx) {
    ctx.strokeStyle = '#6d4c41';
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(mx, 0);
    ctx.lineTo(mx, KNOT_Y);
    ctx.stroke();
    ctx.fillStyle = '#5d4037';
    ctx.beginPath();
    ctx.arc(mx, KNOT_Y + 2, 7, 0, Math.PI * 2);
    ctx.fill();

    const topY = KNOT_Y + TOP_PAD;
    const tipY = TIP_Y;

    ctx.lineWidth = 14;
    ctx.lineJoin = 'round';
    ctx.lineCap = 'round';
    const grad = ctx.createLinearGradient(mx - SPAN - 10, 0, mx + SPAN + 10, 0);
    grad.addColorStop(0, '#e74c3c');
    grad.addColorStop(0.42, '#c0392b');
    grad.addColorStop(0.58, '#2980b9');
    grad.addColorStop(1, '#1f618d');
    ctx.strokeStyle = grad;

    ctx.beginPath();
    ctx.moveTo(mx - SPAN, topY);
    ctx.quadraticCurveTo(mx, topY - 26, mx + SPAN, topY);
    ctx.lineTo(mx + SPAN, tipY);
    ctx.moveTo(mx - SPAN, topY);
    ctx.lineTo(mx - SPAN, tipY);
    ctx.stroke();

    ctx.font = 'bold 12px Poppins,sans-serif';
    ctx.fillStyle = 'rgba(255,255,255,0.95)';
    ctx.textAlign = 'center';
    ctx.fillText('N', mx - SPAN - 2, topY + LEG_LEN * 0.5);
    ctx.fillText('S', mx + SPAN + 2, topY + LEG_LEN * 0.5);

    return tipY;
  }

  function drawEmojiIcon(o, x, y) {
    ctx.font = ICON_FONT;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.shadowColor = 'rgba(0,0,0,0.75)';
    ctx.shadowBlur = 8;
    ctx.shadowOffsetX = 0;
    ctx.shadowOffsetY = 2;
    ctx.fillText(o.emoji, x, y);
    ctx.shadowBlur = 0;
    ctx.shadowOffsetY = 0;
    ctx.font = LABEL_FONT;
    ctx.fillStyle = 'rgba(255,255,255,0.9)';
    ctx.fillText(o.label, x, y + 34);
  }

  function drawHandPointer() {
    if (!lastSmoothedPick || !pipelineRunning) return;
    const px = lastSmoothedPick.x;
    const py = lastSmoothedPick.y;
    ctx.beginPath();
    ctx.arc(px, py, 24, 0, Math.PI * 2);
    ctx.strokeStyle = 'rgba(106,176,76,0.95)';
    ctx.lineWidth = 3;
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(px, py, 6, 0, Math.PI * 2);
    ctx.fillStyle = '#f1c40f';
    ctx.fill();
    ctx.beginPath();
    ctx.moveTo(px - 6, py);
    ctx.lineTo(px + 6, py);
    ctx.moveTo(px, py - 6);
    ctx.lineTo(px, py + 6);
    ctx.strokeStyle = 'rgba(255,255,255,0.5)';
    ctx.lineWidth = 1;
    ctx.stroke();
  }

  function drawScene() {
    const mx = liveMagnetX();

    const g = ctx.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, '#1b2838');
    g.addColorStop(0.45, '#2c3e50');
    g.addColorStop(1, '#1e272e');
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, W, H);

    ctx.fillStyle = 'rgba(0,0,0,0.22)';
    ctx.fillRect(0, H * 0.48, W, H * 0.52);

    const tipY = drawHangingHorseshoe(mx);

    ctx.strokeStyle = 'rgba(241,196,15,0.38)';
    ctx.setLineDash([6, 8]);
    ctx.strokeRect(mx - MAGNET_ZONE_HALF_W, 6, MAGNET_ZONE_HALF_W * 2, MAGNET_ZONE_BOTTOM - 6);
    ctx.setLineDash([]);

    function drawObj(o) {
      let x = o.x;
      let y = o.y;
      if (o.state === 'magnet') {
        const col = o.magnetSlot % 3;
        const row = Math.floor(o.magnetSlot / 3);
        x = mx + (col - 1) * 44;
        y = tipY + 22 + row * 46;
      }
      drawEmojiIcon(o, x, y);
    }

    for (let i = 0; i < objects.length; i++) {
      if (objects[i].state === 'floor' || objects[i].state === 'magnet') drawObj(objects[i]);
    }
    if (heldObject) drawObj(heldObject);

    drawHandPointer();

    ctx.font = '13px Inter,system-ui,sans-serif';
    ctx.fillStyle = 'rgba(255,255,255,0.45)';
    ctx.textAlign = 'left';
    ctx.fillText('Green ring = hand pointer · Pinch or fist to grab · Metals stick in dashed zone', 10, H - 12);
  }

  function frame() {
    drawScene();
    rafId = requestAnimationFrame(frame);
  }

  async function mediaLoop() {
    while (pipelineRunning && hands && stream) {
      if (video.readyState >= 2) {
        try {
          await hands.send({ image: video });
        } catch (e) {}
      }
      await new Promise(function (r) {
        requestAnimationFrame(r);
      });
    }
  }

  function stopPipeline() {
    pipelineRunning = false;
    wasGrab = false;
    grabLatch = false;
    grabOnStreak = 0;
    grabOffStreak = 0;
    lastSmoothedPick = null;
    clearPickHistory();
    if (heldObject) {
      heldObject.state = 'floor';
      heldObject = null;
    }
    requireOpenBeforeGrab = false;
    resetSmooth();
    setLegend('● Green ring = your hand pointer');
    clearHint();
    if (hands && typeof hands.close === 'function') {
      try {
        hands.close();
      } catch (e) {}
    }
    hands = null;
    if (stream) {
      stream.getTracks().forEach(function (t) {
        t.stop();
      });
      stream = null;
    }
    video.srcObject = null;
    setStatus('Camera off — tap Start to play.');
  }

  function loadHandsScript() {
    if (typeof Hands !== 'undefined') return Promise.resolve();
    return new Promise(function (resolve, reject) {
      const s = document.createElement('script');
      s.src = MP_SRC;
      s.async = true;
      s.onload = function () {
        resolve();
      };
      s.onerror = function () {
        reject(new Error('Could not load MediaPipe Hands'));
      };
      document.head.appendChild(s);
    });
  }

  function startCamera() {
    btnStart.disabled = true;
    setStatus('Loading hand model…');
    loadHandsScript()
      .then(function () {
        return navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'user', width: { ideal: 640 }, height: { ideal: 480 } },
          audio: false
        });
      })
      .then(function (s) {
        stream = s;
        video.srcObject = stream;
        return video.play();
      })
      .then(function () {
        hands = new Hands({
          locateFile: function (file) {
            return 'https://cdn.jsdelivr.net/npm/@mediapipe/hands@' + MP_VER + '/' + file;
          }
        });
        hands.setOptions({
          maxNumHands: 1,
          modelComplexity: 1,
          minDetectionConfidence: 0.3,
          minTrackingConfidence: 0.42
        });
        hands.onResults(onHandResults);
        pipelineRunning = true;
        setStatus('Watch the green ring — pinch thumb+index or fist on an icon to grab.');
        setLegend('○ Wave at the camera — pointer appears when your hand is found');
        void mediaLoop();
      })
      .catch(function (err) {
        btnStart.textContent = '📷 Start camera';
        setStatus(
          err && err.message
            ? 'Could not start: ' + err.message
            : 'Camera blocked or unavailable. Use HTTPS or localhost.'
        );
      })
      .finally(function () {
        btnStart.disabled = false;
      });
  }

  scatterObjects();
  rafId = requestAnimationFrame(frame);

  btnStart.addEventListener('click', function () {
    if (pipelineRunning) {
      stopPipeline();
      btnStart.textContent = '📷 Start camera';
      scatterObjects();
      return;
    }
    btnStart.textContent = '⏹ Stop camera';
    startCamera();
  });

  btnReset.addEventListener('click', function () {
    scatterObjects();
    showHint('Objects reshuffled in the pile.', 'info', 2600, 800);
  });

  window.addEventListener('beforeunload', function () {
    stopPipeline();
  });
})();
