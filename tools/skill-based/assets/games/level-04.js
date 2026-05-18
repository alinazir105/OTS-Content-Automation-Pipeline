/** Level 4 — Sentence Train: slot words into S-V-O carriages */
(function () {
  var ROUNDS = [
    ['Ali', 'plays', 'cricket.'],
    ['We', 'went', 'home.'],
    ['The cat', 'sits', 'quietly.'],
  ];

  class SentenceTrainGame extends SkillGame {
    constructor() {
      super({ lives: 3, objective: 'Tap words in Subject → Verb → Object order into the train.' });
      this.ri = 0;
      this.slots = [];
      this.pool = [];
    }

    onMount() {
      this.ri = 0;
      this._loadRound();
    }

    _loadRound() {
      this.slots = [];
      this.stage.innerHTML = '';
      var wrap = this.createEl('div', 'g-train');
      wrap.appendChild(this.createEl('p', '', 'Build: <strong>Who → Action → What</strong>'));
      var slots = this.createEl('div', 'g-train-slots');
      var labels = ['Subject', 'Verb', 'Object'];
      var self = this;
      labels.forEach(function (lab, i) {
        var s = self.createEl('div', 'g-slot', lab);
        s.dataset.idx = String(i);
        slots.appendChild(s);
        self.slots.push(s);
      });
      this.poolEl = this.createEl('div', 'g-pool');
      var parts = ROUNDS[this.ri].slice().sort(function () {
        return Math.random() - 0.5;
      });
      parts.forEach(function (p) {
        var car = self.createEl('button', 'g-car', p);
        car.type = 'button';
        car.dataset.text = p;
        car.onclick = function () {
          self._place(car);
        };
        self.poolEl.appendChild(car);
      });
      wrap.appendChild(slots);
      wrap.appendChild(this.poolEl);
      this.stage.appendChild(wrap);
      this.setObjective('Round ' + (this.ri + 1) + ' of ' + ROUNDS.length);
    }

    _place(car) {
      if (car.classList.contains('used')) return;
      var idx = this.slots.findIndex(function (s) {
        return !s.classList.contains('filled');
      });
      if (idx < 0) return;
      var slot = this.slots[idx];
      slot.textContent = car.dataset.text;
      slot.classList.add('filled');
      car.classList.add('used');
      car.style.visibility = 'hidden';
      this.slotsFilled = (this.slotsFilled || 0) + 1;
      if (this.slots.every(function (s) {
        return s.classList.contains('filled');
      })) {
        var built = this.slots.map(function (s) {
          return s.textContent.replace('.', '');
        });
        var target = ROUNDS[this.ri].map(function (s) {
          return s.replace('.', '');
        });
        if (built.join('|') === target.join('|')) {
          this.addScore(30, 'Great sentence!');
          this.ri++;
          this.setProgress(this.ri / ROUNDS.length);
          var self = this;
          if (this.ri >= ROUNDS.length) this.win(3);
          else setTimeout(function () {
            self._loadRound();
          }, 600);
        } else {
          this.loseLife();
          var self = this;
          setTimeout(function () {
            self._loadRound();
          }, 800);
        }
      }
    }
  }

  window.SKILL_GAMES[4] = SentenceTrainGame;
})();
