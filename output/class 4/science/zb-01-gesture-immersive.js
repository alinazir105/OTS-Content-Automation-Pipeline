/**
 * Immersive full-screen gesture lab — MediaPipe Hands, Class 4 Science 01.html
 * Fist = grab (over tile) · Open hand = drop (over column) · Smoothed pointer + dwell tooltips
 */
(function () {
  'use strict';

  const MP_VER = '0.4.1675469240';
  const MP_SRC = 'https://cdn.jsdelivr.net/npm/@mediapipe/hands@' + MP_VER + '/hands.js';
  const TOTAL_ANIMALS = 20;
  /** Higher = pointer follows the finger faster (less lag). Softer while carrying a tile. */
  const SMOOTH_FREE = 0.52;
  const SMOOTH_CARRY = 0.3;
  /** Extra hit-test samples so fist / column edges still register. */
  const HIT_OFFSETS = [
    [0, 0],
    [0, -16],
    [12, -8],
    [-12, -8],
    [0, 14],
    [18, 4],
    [-18, 4]
  ];
  const DWELL_MS = 420;
  const GRAB_MEMORY_MS = 750;
  /** Fingers “curled” (tip near wrist) required to latch / release fist — tuned for kids’ grab pose */
  const FIST_ON = 2;
  const FIST_OFF = 1;
  /** Normalized distance tip→wrist below this counts as curled (slightly looser than before) */
  const CURL_DIST = 0.138;

  const shell = document.getElementById('gx-immersive');
  const btnLaunch = document.getElementById('gx-launch');
  const btnClose = document.getElementById('gx-close');
  const introEl = document.getElementById('gx-intro');
  const activeEl = document.getElementById('gx-active');
  const btnStart = document.getElementById('gx-start-camera');
  const video = document.getElementById('gx-video');
  const statusEl = document.getElementById('gx-status');
  const feedbackEl = document.getElementById('gx-feedback');
  const source = document.getElementById('gx-source');
  const btnCheck = document.getElementById('gx-check');
  const btnReset = document.getElementById('gx-reset');
  const cursor = document.getElementById('gx-cursor');
  const hoverCard = document.getElementById('gx-hover-card');
  const hoverTitle = hoverCard && hoverCard.querySelector('.gx-hover-title');
  const hoverDesc = hoverCard && hoverCard.querySelector('.gx-hover-desc');

  const poolEl = document.getElementById('gx-pool');
  const POOL_LAYOUT_BREAK = 960;

  if (!shell || !btnLaunch) return;

  let stream = null;
  let hands = null;
  let pipelineRunning = false;
  let fistLatch = false;
  let wasFist = false;
  let carriedChip = null;
  let sx = null;
  let sy = null;
  let dwellChip = null;
  let dwellStart = 0;
  let lastHoverChip = null;
  let grabMemoryChip = null;
  let grabMemoryTime = 0;

  function setStatus(msg) {
    if (statusEl) statusEl.textContent = msg || '';
  }

  /** Pool column never narrower than this so the last chips stay easy to grab */
  const POOL_WIDTH_MIN = 288;
  const POOL_WIDTH_MAX = 620;

  function updateGxPoolLayout() {
    if (!poolEl || !source) return;
    if (window.innerWidth <= POOL_LAYOUT_BREAK) {
      poolEl.style.removeProperty('--gx-pool-w');
      return;
    }
    const n = source.querySelectorAll('.gx-chip:not(.gx-dim)').length;
    const ideal = 112 + n * 22;
    const w = Math.max(POOL_WIDTH_MIN, Math.min(POOL_WIDTH_MAX, ideal));
    poolEl.style.setProperty('--gx-pool-w', w + 'px');
  }

  let poolResizeTimer = null;
  window.addEventListener('resize', function () {
    if (poolResizeTimer) clearTimeout(poolResizeTimer);
    poolResizeTimer = setTimeout(function () {
      poolResizeTimer = null;
      updateGxPoolLayout();
    }, 120);
  });

  function resetSmooth() {
    sx = null;
    sy = null;
  }

  function fingerScreen(lm) {
    const tip = lm[8];
    if (!tip) return null;
    return {
      x: (1 - tip.x) * window.innerWidth,
      y: tip.y * window.innerHeight
    };
  }

  function palmScreen(lm) {
    const w = lm[0];
    const m = lm[9];
    if (!w || !m) return null;
    return {
      x: (1 - (w.x + m.x) / 2) * window.innerWidth,
      y: ((w.y + m.y) / 2) * window.innerHeight
    };
  }

  function grabPointScreen(lm) {
    const f = fingerScreen(lm);
    const p = palmScreen(lm);
    if (f && p) return { x: 0.5 * f.x + 0.5 * p.x, y: 0.5 * f.y + 0.5 * p.y };
    return f || p;
  }

  function smoothAlpha() {
    return carriedChip ? SMOOTH_CARRY : SMOOTH_FREE;
  }

  function smoothPoint(pt) {
    if (!pt) return null;
    const a = smoothAlpha();
    if (sx == null) {
      sx = pt.x;
      sy = pt.y;
      return { x: sx, y: sy };
    }
    sx = a * pt.x + (1 - a) * sx;
    sy = a * pt.y + (1 - a) * sy;
    return { x: sx, y: sy };
  }

  function curledCount(lm) {
    const wrist = lm[0];
    const tips = [8, 12, 16, 20];
    let n = 0;
    for (let i = 0; i < tips.length; i++) {
      const idx = tips[i];
      const t = lm[idx];
      if (!t) continue;
      if (Math.hypot(t.x - wrist.x, t.y - wrist.y) < CURL_DIST) n++;
    }
    return n;
  }

  /** Index clearly folded — helps register a “grab” even when other fingers stay straighter */
  function indexGrabCurl(lm) {
    const wrist = lm[0];
    const pip = lm[6];
    const tip = lm[8];
    if (!wrist || !pip || !tip) return false;
    const dTip = Math.hypot(tip.x - wrist.x, tip.y - wrist.y);
    const dPip = Math.hypot(pip.x - wrist.x, pip.y - wrist.y);
    return dTip < dPip * 0.88;
  }

  function updateFistLatch(lm) {
    if (!lm) {
      fistLatch = false;
      return false;
    }
    const c = curledCount(lm);
    const grabPose = c >= FIST_ON || (indexGrabCurl(lm) && c >= 1);
    const openHand = c <= FIST_OFF && !indexGrabCurl(lm);
    if (!fistLatch) {
      if (grabPose) fistLatch = true;
    } else {
      if (openHand) fistLatch = false;
    }
    return fistLatch;
  }

  function moveCursor(pt, carrying, fistClosed) {
    if (!cursor) return;
    if (!pt) {
      cursor.classList.remove('gx-on', 'gx-grab', 'gx-hand-closed');
      return;
    }
    cursor.style.left = pt.x + 'px';
    cursor.style.top = pt.y + 'px';
    cursor.classList.add('gx-on');
    cursor.classList.toggle('gx-grab', !!carrying);
    cursor.classList.toggle('gx-hand-closed', !!(carrying || fistClosed));
  }

  function positionHoverCard(pt) {
    if (!hoverCard || !pt || !hoverCard.classList.contains('gx-on')) return;
    const pad = 18;
    const w = hoverCard.offsetWidth || 280;
    const h = hoverCard.offsetHeight || 120;
    let x = pt.x + pad;
    let y = pt.y + pad;
    if (x + w > innerWidth - 8) x = pt.x - w - pad;
    if (y + h > innerHeight - 8) y = pt.y - h - pad;
    x = Math.max(8, Math.min(x, innerWidth - w - 8));
    y = Math.max(8, Math.min(y, innerHeight - h - 8));
    hoverCard.style.left = x + 'px';
    hoverCard.style.top = y + 'px';
  }

  function showHoverContent(title, desc, pt) {
    if (!hoverCard || !hoverTitle || !hoverDesc) return;
    hoverTitle.textContent = title || '';
    hoverDesc.textContent = desc || '';
    hoverCard.classList.add('gx-on');
    hoverCard.setAttribute('aria-hidden', 'false');
    positionHoverCard(pt);
  }

  function hideHoverCard() {
    if (!hoverCard) return;
    hoverCard.classList.remove('gx-on');
    hoverCard.setAttribute('aria-hidden', 'true');
  }

  function clearFingerHoverChips() {
    if (!source) return;
    source.querySelectorAll('.gx-finger-hover').forEach(function (el) {
      el.classList.remove('gx-finger-hover');
    });
  }

  function gxRowExists(animal) {
    return shell.querySelector('.gx-row[data-animal="' + animal + '"]');
  }

  function clearZoneHot() {
    shell.querySelectorAll('.gx-zone').forEach(function (z) {
      z.classList.remove('gx-zone-hot');
    });
  }

  function chipLabel(chip) {
    return (chip.dataset && chip.dataset.label) || chip.textContent.trim();
  }

  /** Geometry hit-test so overlays / stacking never steal picks from elementFromPoint */
  function chipUnderPoint(pt) {
    if (!pt || !source) return null;
    const chips = source.querySelectorAll('.gx-chip:not(.gx-dim)');
    for (let o = 0; o < HIT_OFFSETS.length; o++) {
      const x = pt.x + HIT_OFFSETS[o][0];
      const y = pt.y + HIT_OFFSETS[o][1];
      for (let i = chips.length - 1; i >= 0; i--) {
        const chip = chips[i];
        const r = chip.getBoundingClientRect();
        if (x >= r.left && x <= r.right && y >= r.top && y <= r.bottom) return chip;
      }
    }
    return null;
  }

  function zoneFromPoints(pts) {
    if (!shell) return null;
    const zones = shell.querySelectorAll('.gx-zone');
    for (let p = 0; p < pts.length; p++) {
      const pt = pts[p];
      if (!pt) continue;
      for (let o = 0; o < HIT_OFFSETS.length; o++) {
        const x = pt.x + HIT_OFFSETS[o][0];
        const y = pt.y + HIT_OFFSETS[o][1];
        for (let z = zones.length - 1; z >= 0; z--) {
          const zone = zones[z];
          const r = zone.getBoundingClientRect();
          if (x >= r.left && x <= r.right && y >= r.top && y <= r.bottom) return zone;
        }
      }
    }
    return null;
  }

  function gxPickChip(chip, anchorPt) {
    if (!chip || !source.contains(chip) || chip.classList.contains('gx-dim')) return false;
    if (gxRowExists(chip.dataset.animal)) return false;
    carriedChip = chip;
    chip.classList.add('gx-carry');
    grabMemoryChip = null;
    hideHoverCard();
    clearFingerHoverChips();
    const desc = chip.getAttribute('data-desc') || '';
    const rect = chip.getBoundingClientRect();
    const pt =
      anchorPt ||
      (rect.width
        ? { x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 }
        : { x: 0, y: 0 });
    showHoverContent(chipLabel(chip), 'Carrying — ' + desc, pt);
    setStatus('Carrying — open your hand over Vertebrates or Invertebrates to drop.');
    return true;
  }

  /** Try several screen points + recent “intent” chip — fist closes the index tip off the tile otherwise. */
  function gxTryPickMulti(smoothed, pickPt, grabRaw, palmPt) {
    const pts = [pickPt, smoothed, grabRaw, palmPt];
    for (let i = 0; i < pts.length; i++) {
      const c = chipUnderPoint(pts[i]);
      if (c && gxPickChip(c, pts[i] || smoothed)) return;
    }
    if (grabMemoryChip && performance.now() - grabMemoryTime <= GRAB_MEMORY_MS) {
      if (source.contains(grabMemoryChip) && !grabMemoryChip.classList.contains('gx-dim')) {
        gxPickChip(grabMemoryChip, smoothed || pickPt || grabRaw);
      }
    }
  }

  function gxTryPick(pt) {
    const c = chipUnderPoint(pt);
    if (c) gxPickChip(c, pt);
  }

  function gxTryDrop(smoothed, pickPt, grabRaw, palmPt) {
    if (!carriedChip) return;
    try {
      carriedChip.classList.remove('gx-carry');
      hideHoverCard();
      const ptsTry = [smoothed, pickPt, grabRaw, palmPt].filter(Boolean);
      if (!ptsTry.length) {
        carriedChip = null;
        clearZoneHot();
        return;
      }
      const zone = zoneFromPoints(ptsTry);
      clearZoneHot();
      if (!zone || !shell.contains(zone)) {
        carriedChip = null;
        setStatus('Drop cancelled — make a fist on a tile again, then open over a column.');
        return;
      }
      const animal = carriedChip.dataset.animal;
      if (gxRowExists(animal)) {
        carriedChip = null;
        return;
      }
      const zoneType = zone.dataset.type || '';
      const tray = zone.querySelector('.gx-tray');
      if (!tray) {
        carriedChip = null;
        return;
      }
      const row = document.createElement('div');
      row.className = 'gx-row';
      row.dataset.animal = animal;
      row.dataset.correct = carriedChip.dataset.correct || '';
      row.dataset.zone = zoneType;
      row.appendChild(document.createTextNode(chipLabel(carriedChip) + ' '));
      const rm = document.createElement('button');
      rm.type = 'button';
      rm.className = 'gx-remove';
      rm.setAttribute('aria-label', 'Remove');
      rm.textContent = '✕';
      row.appendChild(rm);
      tray.appendChild(row);
      carriedChip.classList.add('gx-dim');
      carriedChip = null;
      setStatus('Placed. Fist-grab another animal, or tap Check answers.');
      if (feedbackEl) {
        feedbackEl.style.display = 'none';
        feedbackEl.textContent = '';
      }
    } finally {
      updateGxPoolLayout();
    }
  }

  function updateDwellHover(pt, now, lm) {
    if (!source || carriedChip || !pt || !lm) {
      dwellChip = null;
      dwellStart = 0;
      if (!carriedChip) hideHoverCard();
      return;
    }
    const chip = chipUnderPoint(pt);
    if (!chip) {
      dwellChip = null;
      dwellStart = 0;
      clearFingerHoverChips();
      if (!carriedChip) hideHoverCard();
      return;
    }
    if (dwellChip !== chip) {
      dwellChip = chip;
      dwellStart = now;
      clearFingerHoverChips();
    }
    chip.classList.add('gx-finger-hover');
    if (now - dwellStart >= DWELL_MS) {
      if (lastHoverChip !== chip) {
        lastHoverChip = chip;
        showHoverContent(chipLabel(chip), chip.getAttribute('data-desc') || '', pt);
      } else {
        positionHoverCard(pt);
      }
    }
  }

  function onHandResults(results) {
    if (shell.classList.contains('gx-off') || !activeEl || activeEl.classList.contains('gx-hidden')) return;

    const lm = results.multiHandLandmarks && results.multiHandLandmarks[0];
    const now = performance.now();

    if (!lm) {
      wasFist = false;
      fistLatch = false;
      if (!carriedChip) {
        resetSmooth();
        moveCursor(null, false, false);
        hideHoverCard();
        clearFingerHoverChips();
        dwellChip = null;
        grabMemoryChip = null;
        grabMemoryTime = 0;
      } else {
        const frozen = sx != null && sy != null ? { x: sx, y: sy } : null;
        moveCursor(frozen, true, false);
      }
      return;
    }

    const rawFinger = fingerScreen(lm);
    const smoothed = rawFinger ? smoothPoint(rawFinger) : null;
    const grabRaw = grabPointScreen(lm);
    const pickPt =
      grabRaw && smoothed
        ? { x: 0.52 * grabRaw.x + 0.48 * smoothed.x, y: 0.52 * grabRaw.y + 0.48 * smoothed.y }
        : smoothed || grabRaw;

    const fist = updateFistLatch(lm);
    const palmPt = palmScreen(lm);

    if (!fist && !carriedChip && smoothed) {
      const over = chipUnderPoint(smoothed);
      if (over) {
        grabMemoryChip = over;
        grabMemoryTime = now;
      }
    }

    if (fist && !wasFist && !carriedChip) {
      gxTryPickMulti(smoothed, pickPt, grabRaw, palmPt);
    }
    if (!fist && wasFist && carriedChip) {
      gxTryDrop(smoothed, pickPt, grabRaw, palmPt);
    }

    wasFist = fist;

    if (carriedChip && smoothed) {
      const z = zoneFromPoints([smoothed, pickPt, grabRaw, palmPt]);
      clearZoneHot();
      if (z) z.classList.add('gx-zone-hot');
      positionHoverCard(smoothed);
    } else if (!carriedChip) {
      clearZoneHot();
      updateDwellHover(smoothed, now, lm);
    } else {
      clearZoneHot();
    }

    moveCursor(smoothed, !!carriedChip, fist);
  }

  async function mediaLoop() {
    while (pipelineRunning && hands && stream) {
      if (video && video.readyState >= 2) {
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
    wasFist = false;
    fistLatch = false;
    if (carriedChip) {
      carriedChip.classList.remove('gx-carry');
      carriedChip = null;
    }
    clearZoneHot();
    clearFingerHoverChips();
    dwellChip = null;
    lastHoverChip = null;
    grabMemoryChip = null;
    grabMemoryTime = 0;
    hideHoverCard();
    moveCursor(null, false, false);
    resetSmooth();
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
    if (video) video.srcObject = null;
  }

  function resetActivity() {
    shell.querySelectorAll('.gx-tray').forEach(function (t) {
      t.innerHTML = '';
    });
    shell.querySelectorAll('.gx-chip').forEach(function (c) {
      c.classList.remove('gx-dim', 'gx-carry', 'gx-finger-hover');
    });
    carriedChip = null;
    wasFist = false;
    fistLatch = false;
    clearZoneHot();
    dwellChip = null;
    lastHoverChip = null;
    grabMemoryChip = null;
    grabMemoryTime = 0;
    hideHoverCard();
    resetSmooth();
    if (feedbackEl) {
      feedbackEl.style.display = 'none';
      feedbackEl.textContent = '';
    }
    setStatus('');
    updateGxPoolLayout();
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
    if (!btnStart) return;
    btnStart.disabled = true;
    setStatus('Loading model…');
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
          minDetectionConfidence: 0.38,
          minTrackingConfidence: 0.45
        });
        hands.onResults(onHandResults);
        if (introEl) introEl.classList.add('gx-hidden');
        if (activeEl) activeEl.classList.remove('gx-hidden');
        setStatus('Camera on — point at a card, fist to grab, open hand over a column to drop.');
        pipelineRunning = true;
        void mediaLoop();
        updateGxPoolLayout();
      })
      .catch(function (err) {
        setStatus(
          err && err.message
            ? 'Could not start: ' + err.message
            : 'Camera blocked or unavailable. Try HTTPS / localhost.'
        );
      })
      .finally(function () {
        btnStart.disabled = false;
      });
  }

  function openLab() {
    shell.classList.remove('gx-off');
    shell.setAttribute('aria-hidden', 'false');
    document.body.classList.add('gx-immersive-open');
    stopPipeline();
    resetActivity();
    if (introEl) introEl.classList.remove('gx-hidden');
    if (activeEl) activeEl.classList.add('gx-hidden');
    if (btnStart) btnStart.disabled = false;
    setStatus('');
    if (btnClose) btnClose.focus();
  }

  function closeLab() {
    stopPipeline();
    resetActivity();
    if (introEl) introEl.classList.remove('gx-hidden');
    if (activeEl) activeEl.classList.add('gx-hidden');
    shell.classList.add('gx-off');
    shell.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('gx-immersive-open');
    moveCursor(null, false, false);
    hideHoverCard();
  }

  btnLaunch.addEventListener('click', openLab);
  if (btnClose) btnClose.addEventListener('click', closeLab);

  if (btnStart) btnStart.addEventListener('click', startCamera);

  document.addEventListener(
    'keydown',
    function (e) {
      if (e.key === 'Escape' && !shell.classList.contains('gx-off')) {
        e.preventDefault();
        closeLab();
      }
    },
    true
  );

  shell.addEventListener('click', function (e) {
    const rm = e.target.closest('.gx-remove');
    if (!rm) return;
    const row = rm.closest('.gx-row');
    if (!row || !shell.contains(row)) return;
    const animal = row.dataset.animal;
    row.remove();
    const chip = source && source.querySelector('.gx-chip[data-animal="' + animal + '"]');
    if (chip) chip.classList.remove('gx-dim');
    setStatus('Removed — fist-grab to place again.');
    updateGxPoolLayout();
    if (feedbackEl) {
      feedbackEl.style.display = 'none';
      feedbackEl.textContent = '';
    }
  });

  if (btnCheck) {
    btnCheck.addEventListener('click', function () {
      const rows = shell.querySelectorAll('.gx-row');
      let ok = 0;
      rows.forEach(function (row) {
        row.classList.remove('gx-ok', 'gx-bad');
        if (row.dataset.correct === row.dataset.zone) {
          row.classList.add('gx-ok');
          ok++;
        } else {
          row.classList.add('gx-bad');
        }
      });
      if (!feedbackEl) return;
      feedbackEl.style.display = 'block';
      if (rows.length === 0) {
        feedbackEl.textContent = 'Place at least one animal first.';
        feedbackEl.style.color = '#94a3b8';
        return;
      }
      if (ok === rows.length && rows.length === TOTAL_ANIMALS) {
        feedbackEl.textContent = '🎉 Perfect — all 20 sorted correctly!';
        feedbackEl.style.color = '#6AB04C';
      } else {
        feedbackEl.textContent =
          '📝 ' + ok + '/' + rows.length + ' correct. Aim for all ' + TOTAL_ANIMALS + ' animals in the right column.';
        feedbackEl.style.color = '#F0932B';
      }
    });
  }

  if (btnReset) {
    btnReset.addEventListener('click', function () {
      resetActivity();
      setStatus(pipelineRunning ? 'Reset — sort again with fist grab / open-hand drop.' : '');
    });
  }

  window.addEventListener('beforeunload', stopPipeline);
})();
