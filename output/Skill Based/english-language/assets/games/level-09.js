/** Level 9 — Time Machine: slide to past tense */
(function () {
  var VERBS = ['play', 'walk', 'help', 'jump', 'clean'];

  class TimeMachineGame extends SkillGame {
    constructor() {
      super({ lives: 3, objective: 'Slide the dial to PAST, then press Lock in for each verb.' });
      this.vi = 0;
    }

    onMount() {
      this.vi = 0;
      this.stage.innerHTML = '';
      var wrap = this.createEl('div', 'g-time');
      wrap.innerHTML =
        '<div style="display:flex;justify-content:space-between;font-weight:600;opacity:.8"><span>Present</span><span>Past</span></div>';
      this.slider = document.createElement('input');
      this.slider.type = 'range';
      this.slider.className = 'g-time-slider';
      this.slider.min = '0';
      this.slider.max = '100';
      this.slider.value = '0';
      this.verbEl = this.createEl('div', 'g-time-verb', VERBS[0]);
      var btn = this.createEl('button', 'playlab-launch', 'Lock in!');
      btn.type = 'button';
      var self = this;
      btn.onclick = function () {
        self._check();
      };
      this.slider.oninput = function () {
        var v = VERBS[self.vi];
        var past = v + (v.endsWith('e') ? 'd' : 'ed');
        self.verbEl.textContent = self.slider.value > 50 ? past : v;
      };
      wrap.appendChild(this.slider);
      wrap.appendChild(this.verbEl);
      wrap.appendChild(btn);
      this.stage.appendChild(wrap);
    }

    _check() {
      if (+this.slider.value > 55) {
        this.addScore(22, 'Past tense!');
        this.vi++;
        this.setProgress(this.vi / VERBS.length);
        if (this.vi >= VERBS.length) this.win(3);
        else {
          this.slider.value = '0';
          this.verbEl.textContent = VERBS[this.vi];
        }
      } else {
        this.loseLife();
        this.shake(this.verbEl);
      }
    }
  }

  window.SKILL_GAMES[9] = TimeMachineGame;
})();
