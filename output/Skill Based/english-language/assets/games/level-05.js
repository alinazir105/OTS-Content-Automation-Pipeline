/** Level 5 — Punctuation Pop: pop correctly punctuated bubbles */
(function () {
  var SETS = [
    [
      { t: 'The dog runs fast.', ok: true },
      { t: 'The dog runs fast', ok: false },
      { t: 'the dog runs fast.', ok: false },
    ],
    [
      { t: 'Where is my bag?', ok: true },
      { t: 'Where is my bag', ok: false },
      { t: 'Where is my bag.', ok: false },
    ],
    [
      { t: 'What a goal!', ok: true },
      { t: 'What a goal', ok: false },
      { t: 'What a goal.', ok: false },
    ],
  ];

  class PunctPopGame extends SkillGame {
    constructor() {
      super({ lives: 3, timer: 90, objective: 'Pop only the bubbles with correct end punctuation!' });
      this.round = 0;
      this.bubbles = [];
    }

    onMount() {
      this.round = 0;
      this.stage.innerHTML = '';
      this.canvas = document.createElement('canvas');
      this.canvas.className = 'g-canvas-game';
      this.canvas.width = 640;
      this.canvas.height = 360;
      this.stage.appendChild(this.canvas);
      this.ctx = this.canvas.getContext('2d');
      var self = this;
      this.canvas.onclick = function (e) {
        self._click(e);
      };
      this._nextRound();
    }

    _nextRound() {
      if (this.round >= SETS.length) {
        this.win(3);
        return;
      }
      this.bubbles = [];
      var set = SETS[this.round];
      var self = this;
      set.forEach(function (s, i) {
        self.bubbles.push({
          x: 100 + (i % 3) * 180,
          y: 80 + Math.floor(i / 3) * 120,
          r: 58,
          text: s.t,
          ok: s.ok,
          alive: true,
          bob: Math.random() * Math.PI * 2,
        });
      });
      this.setProgress(this.round / SETS.length);
    }

    onTick() {
      this._draw();
    }

    _draw() {
      var ctx = this.ctx;
      var w = this.canvas.width;
      var h = this.canvas.height;
      ctx.fillStyle = '#1a2b3c';
      ctx.fillRect(0, 0, w, h);
      var t = Date.now() / 500;
      var self = this;
      this.bubbles.forEach(function (b) {
        if (!b.alive) return;
        b.bob += 0.04;
        var by = b.y + Math.sin(b.bob) * 8;
        ctx.beginPath();
        ctx.arc(b.x, by, b.r, 0, Math.PI * 2);
        ctx.fillStyle = b.ok ? '#6AB04C' : '#F0932B';
        ctx.fill();
        ctx.strokeStyle = 'rgba(255,255,255,.4)';
        ctx.lineWidth = 3;
        ctx.stroke();
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 12px Poppins,sans-serif';
        ctx.textAlign = 'center';
        self._wrap(ctx, b.text, b.x, by, b.r * 1.6);
      });
    }

    _wrap(ctx, text, x, y, maxW) {
      var words = text.split(' ');
      var line = '';
      var lines = [];
      var ly = y - 8;
      words.forEach(function (w) {
        var test = line + w + ' ';
        if (ctx.measureText(test).width > maxW && line) {
          lines.push(line);
          line = w + ' ';
        } else line = test;
      });
      lines.push(line);
      lines.forEach(function (ln, i) {
        ctx.fillText(ln.trim(), x, ly + i * 15);
      });
    }

    _click(e) {
      var r = this.canvas.getBoundingClientRect();
      var x = ((e.clientX - r.left) / r.width) * this.canvas.width;
      var y = ((e.clientY - r.top) / r.height) * this.canvas.height;
      var self = this;
      this.bubbles.forEach(function (b) {
        if (!b.alive) return;
        var by = b.y + Math.sin(b.bob) * 8;
        var dx = x - b.x;
        var dy = y - by;
        if (dx * dx + dy * dy < b.r * b.r) {
          if (b.ok) {
            b.alive = false;
            self.addScore(25, 'Correct!');
            self.burst(b.x, by, '#6AB04C');
            var alive = self.bubbles.some(function (bb) {
              return bb.alive && bb.ok;
            });
            if (!alive) {
              self.round++;
              setTimeout(function () {
                self._nextRound();
              }, 500);
            }
          } else {
            self.breakCombo();
            self.loseLife();
          }
        }
      });
    }
  }

  window.SKILL_GAMES[5] = PunctPopGame;
})();
