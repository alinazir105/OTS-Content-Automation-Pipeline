/** Level 12 — Story Architect: write then fix errors */
(function () {
  var FIXES = [
    { err: 'the cat sat.', fix: 'The cat sat.' },
    { err: 'We go to school yesterday.', fix: 'We went to school yesterday.' },
    { err: 'It was fun', fix: 'It was fun!' },
    { err: 'We walk home.', fix: 'We walked home.' },
  ];

  class StoryArchitectGame extends SkillGame {
    constructor() {
      super({ objective: 'Write 4 sentences, then tap each error to fix it.' });
      this.step = 0;
      this.sentences = ['', '', '', ''];
      this.fixed = 0;
    }

    onMount() {
      this.step = 0;
      this.fixed = 0;
      this._render();
    }

    _render() {
      this.stage.innerHTML = '';
      var wrap = this.createEl('div', 'g-arch');
      var steps = this.createEl('div', 'g-arch-steps');
      ['S1', 'S2', 'S3', 'S4', 'Edit'].forEach(function (l, i) {
        var s = document.createElement('span');
        s.className = 'g-arch-step' + (i === this.step ? ' active' : i < this.step ? ' done' : '');
        s.textContent = l;
        steps.appendChild(s);
      }, this);
      wrap.appendChild(steps);
      var panel = this.createEl('div', '');
      if (this.step < 4) {
        var inp = document.createElement('input');
        inp.className = 'g-arch-input';
        inp.placeholder = 'Write sentence ' + (this.step + 1);
        inp.value = this.sentences[this.step];
        var btn = this.createEl('button', 'playlab-launch', 'Next sentence');
        btn.type = 'button';
        var self = this;
        btn.onclick = function () {
          self.sentences[self.step] = inp.value;
          self.step++;
          self.addScore(10, 'Sentence saved');
          self.setProgress(self.step / 5);
          self._render();
        };
        panel.appendChild(inp);
        panel.appendChild(btn);
      } else {
        var self = this;
        FIXES.forEach(function (f, i) {
          var d = self.createEl('div', 'g-arch-err', f.err);
          d.onclick = function () {
            if (d.classList.contains('fixed')) return;
            d.classList.add('fixed');
            d.textContent = f.fix;
            self.fixed++;
            self.addScore(20, 'Fixed!');
            self.setProgress(0.8 + self.fixed * 0.05);
            if (self.fixed >= FIXES.length) self.win(3);
          };
          panel.appendChild(d);
        });
      }
      wrap.appendChild(panel);
      this.stage.appendChild(wrap);
    }
  }

  window.SKILL_GAMES[12] = StoryArchitectGame;
})();
