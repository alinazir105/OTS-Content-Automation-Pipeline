/**
 * OTS Skill Game Engine — shared state, HUD, particles, lifecycle for English skill games.
 */
(function (global) {
  'use strict';

  function $(id) {
    return document.getElementById(id);
  }

  function clamp(n, a, b) {
    return Math.max(a, Math.min(b, n));
  }

  class SkillGame {
    constructor(config) {
      this.config = Object.assign(
        {
          lives: 3,
          timer: null,
          objective: 'Complete the challenge!',
        },
        config || {}
      );
      this.score = 0;
      this.lives = this.config.lives;
      this.combo = 0;
      this.maxCombo = 0;
      this.state = 'idle';
      this._raf = null;
      this._last = 0;
      this._timeLeft = this.config.timer;
      this.root = null;
      this.stage = null;
      this._particles = [];
      this._particleCanvas = null;
      this._particleCtx = null;
      this._onTick = null;
    }

    mount(stageEl) {
      this.stage = stageEl;
      this.root = stageEl;
      if (!this.stage) return;
      this.stage.innerHTML = '';
      this._bindHud();
      this.setObjective(this.config.objective);
      this._updateHud();
      this._ensureParticles();
      this.state = 'playing';
      if (this.config.timer) this._startTimer();
      this._loop = this._loop.bind(this);
      this._raf = requestAnimationFrame(this._loop);
      this.onMount();
    }

    destroy() {
      this.state = 'idle';
      if (this._raf) cancelAnimationFrame(this._raf);
      this._raf = null;
      if (this._timerId) clearInterval(this._timerId);
      this.onDestroy();
      if (this.stage) this.stage.innerHTML = '';
    }

    onMount() {}
    onDestroy() {}
    onTick() {}

    setObjective(text) {
      var el = $('gameObjective');
      if (el) el.textContent = text;
    }

    setProgress(ratio) {
      var bar = $('plProgressBar');
      if (bar) bar.style.width = clamp(ratio, 0, 1) * 100 + '%';
    }

    addScore(points, reason) {
      this.combo += 1;
      this.maxCombo = Math.max(this.maxCombo, this.combo);
      var mult = 1 + Math.min(this.combo - 1, 5) * 0.1;
      var gained = Math.round(points * mult);
      this.score += gained;
      this._updateHud();
      this._flashScore();
      if (reason) this._toast(reason + ' +' + gained);
      return gained;
    }

    breakCombo() {
      this.combo = 0;
      this._updateHud();
    }

    loseLife() {
      this.lives = Math.max(0, this.lives - 1);
      this.breakCombo();
      this._updateHud();
      this.shake(this.stage);
      if (this.lives <= 0) this.gameOver();
    }

    gameOver() {
      this.state = 'lost';
      this._toast('Out of lives — try again!');
      var self = this;
      setTimeout(function () {
        if (typeof global.restartSkillGame === 'function') global.restartSkillGame();
      }, 1400);
    }

    win(stars) {
      if (this.state === 'won') return;
      this.state = 'won';
      stars = clamp(stars || 3, 1, 3);
      if (typeof global.endGame === 'function') global.endGame(stars, this.score, this.maxCombo);
    }

    shake(el) {
      if (!el) return;
      try {
        if (global.gsap) {
          global.gsap.fromTo(el, { x: 0 }, { x: 12, duration: 0.06, repeat: 5, yoyo: true });
        } else {
          el.classList.add('shake');
          setTimeout(function () {
            el.classList.remove('shake');
          }, 400);
        }
      } catch (e) {}
    }

    burst(x, y, color) {
      color = color || '#F0932B';
      for (var i = 0; i < 12; i++) {
        var a = (Math.PI * 2 * i) / 12;
        this._particles.push({
          x: x,
          y: y,
          vx: Math.cos(a) * (2 + Math.random() * 4),
          vy: Math.sin(a) * (2 + Math.random() * 4),
          life: 1,
          color: color,
          r: 3 + Math.random() * 4,
        });
      }
    }

    createEl(tag, className, html) {
      var el = document.createElement(tag);
      if (className) el.className = className;
      if (html != null) el.innerHTML = html;
      return el;
    }

    _bindHud() {
      this._updateHud();
    }

    _updateHud() {
      var s = $('plScore');
      var c = $('plCombo');
      var l = $('plLives');
      var t = $('plTimer');
      if (s) s.textContent = String(this.score);
      if (c) {
        c.textContent = this.combo > 1 ? '×' + this.combo : '—';
        c.classList.toggle('hot', this.combo >= 3);
      }
      if (l) {
        l.textContent = '♥'.repeat(this.lives) + '♡'.repeat(Math.max(0, this.config.lives - this.lives));
      }
      if (t && this.config.timer) t.textContent = String(Math.ceil(this._timeLeft || 0));
    }

    _flashScore() {
      var s = $('plScore');
      if (!s) return;
      s.classList.add('pop');
      var self = this;
      setTimeout(function () {
        s.classList.remove('pop');
      }, 200);
    }

    _toast(msg) {
      var box = $('plToast');
      if (!box) return;
      box.textContent = msg;
      box.classList.add('show');
      clearTimeout(this._toastT);
      this._toastT = setTimeout(function () {
        box.classList.remove('show');
      }, 1200);
    }

    _startTimer() {
      var self = this;
      this._timerId = setInterval(function () {
        if (self.state !== 'playing') return;
        self._timeLeft -= 1;
        self._updateHud();
        if (self._timeLeft <= 0) self.gameOver();
      }, 1000);
    }

    _ensureParticles() {
      if (this._particleCanvas) return;
      this._particleCanvas = document.createElement('canvas');
      this._particleCanvas.className = 'pl-particles';
      this._particleCanvas.width = 800;
      this._particleCanvas.height = 500;
      this._particleCtx = this._particleCanvas.getContext('2d');
      var shell = document.querySelector('.playlab-stage-wrap');
      if (shell) shell.appendChild(this._particleCanvas);
    }

    _loop(ts) {
      if (this.state !== 'playing' && this.state !== 'won') return;
      var dt = this._last ? (ts - this._last) / 1000 : 0;
      this._last = ts;
      this.onTick(dt);
      this._drawParticles(dt);
      this._raf = requestAnimationFrame(this._loop);
    }

    _drawParticles() {
      if (!this._particleCtx || !this._particleCanvas) return;
      var ctx = this._particleCtx;
      var w = this._particleCanvas.width;
      var h = this._particleCanvas.height;
      ctx.clearRect(0, 0, w, h);
      this._particles = this._particles.filter(function (p) {
        p.x += p.vx;
        p.y += p.vy;
        p.vy += 0.15;
        p.life -= 0.03;
        if (p.life <= 0) return false;
        ctx.globalAlpha = p.life;
        ctx.fillStyle = p.color;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fill();
        return true;
      });
      ctx.globalAlpha = 1;
    }
  }

  global.SkillGame = SkillGame;
  global.SKILL_GAMES = global.SKILL_GAMES || {};

  global.initSkillGame = function (levelNum) {
    if (global._activeSkillGame) {
      global._activeSkillGame.destroy();
      global._activeSkillGame = null;
    }
    var Factory = global.SKILL_GAMES[levelNum];
    var stage = $('gameStage');
    if (!Factory || !stage) return null;
    var game = new Factory();
    global._activeSkillGame = game;
    game.mount(stage);
    return game;
  };

  global.restartSkillGame = function () {
    var n = global.CURRENT_LEVEL_NUM;
    if (n) global.initSkillGame(n);
  };
})(window);
