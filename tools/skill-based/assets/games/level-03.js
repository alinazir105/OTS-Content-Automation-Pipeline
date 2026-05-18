/** Level 3 — Article Toss: pick bin then launch word */
(function () {
  var ITEMS = [
    { w: 'apple', a: 'an' },
    { w: 'ball', a: 'a' },
    { w: 'egg', a: 'an' },
    { w: 'park', a: 'the' },
    { w: 'umbrella', a: 'an' },
    { w: 'book', a: 'a' },
  ];

  class ArticleTossGame extends SkillGame {
    constructor() {
      super({ lives: 3, objective: 'Tap a bin (a / an / the), then tap the word that belongs there.' });
      this.bin = null;
      this.done = 0;
      this.queue = [];
    }

    onMount() {
      this.done = 0;
      this.bin = null;
      this.queue = ITEMS.slice().sort(function () {
        return Math.random() - 0.5;
      });
      this.stage.innerHTML = '';
      var layout = this.createEl('div', 'g-toss-layout');
      var bins = this.createEl('div', 'g-bins');
      var self = this;
      ['a', 'an', 'the'].forEach(function (b) {
        var el = self.createEl('button', 'g-bin', b);
        el.type = 'button';
        el.dataset.bin = b;
        el.onclick = function () {
          self._selectBin(el, b);
        };
        bins.appendChild(el);
      });
      this.binEls = bins.querySelectorAll('.g-bin');
      this.queueEl = this.createEl('div', 'g-toss-queue');
      layout.appendChild(bins);
      layout.appendChild(this.queueEl);
      this.stage.appendChild(layout);
      this._renderQueue();
    }

    _selectBin(el, b) {
      this.bin = b;
      this.binEls.forEach(function (x) {
        x.classList.toggle('target', x === el);
      });
    }

    _renderQueue() {
      var self = this;
      this.queueEl.innerHTML = '';
      this.queue.forEach(function (it) {
        var chip = self.createEl('button', 'g-chip', it.w);
        chip.type = 'button';
        chip.onclick = function () {
          self._toss(chip, it);
        };
        self.queueEl.appendChild(chip);
      });
    }

    _toss(chip, it) {
      if (!this.bin) {
        this._toast('Pick a bin first!');
        return;
      }
      if (it.a === this.bin) {
        chip.remove();
        this.binEls.forEach(function (x) {
          if (x.dataset.bin === this.bin) x.classList.add('caught');
        }, this);
        var self = this;
        setTimeout(function () {
          self.binEls.forEach(function (x) {
            x.classList.remove('caught');
          });
        }, 400);
        this.done++;
        this.addScore(20, 'Perfect toss!');
        this.setProgress(this.done / ITEMS.length);
        this.bin = null;
        this.binEls.forEach(function (x) {
          x.classList.remove('target');
        });
        if (this.done >= ITEMS.length) this.win(3);
      } else {
        this.breakCombo();
        this.loseLife();
        this.shake(chip);
      }
    }
  }

  window.SKILL_GAMES[3] = ArticleTossGame;
})();
