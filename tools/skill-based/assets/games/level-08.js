/** Level 8 — Grammar Detective */
(function () {
  var ROUNDS = [
    { passage: 'At the park the dogs bowl was empty.', wrong: 'dogs' },
    { passage: 'The boys kite flew high in the sky.', wrong: 'boys' },
    { passage: 'My friends bike is red.', wrong: 'friends' },
  ];

  class GrammarDetectiveGame extends SkillGame {
    constructor() {
      super({ lives: 3, objective: 'Find the word that needs an apostrophe fix (tap it).' });
      this.ri = 0;
    }

    onMount() {
      this.ri = 0;
      this._showRound();
    }

    _showRound() {
      if (this.ri >= ROUNDS.length) {
        this.win(3);
        return;
      }
      var R = ROUNDS[this.ri];
      this.stage.innerHTML = '';
      var p = this.createEl('div', 'g-passage');
      var self = this;
      R.passage.split(/(\s+)/).forEach(function (tok) {
        if (!tok.trim()) {
          p.appendChild(document.createTextNode(tok));
          return;
        }
        var clean = tok.replace(/[.,]/g, '');
        var span = self.createEl('span', 'w', tok);
        span.onclick = function () {
          if (clean === R.wrong) {
            span.classList.add('hit');
            self.addScore(40, 'Found it!');
            self.ri++;
            self.setProgress(self.ri / ROUNDS.length);
            setTimeout(function () {
              self._showRound();
            }, 700);
          } else {
            self.loseLife();
            self.shake(span);
          }
        };
        p.appendChild(span);
      });
      this.stage.appendChild(p);
    }
  }

  window.SKILL_GAMES[8] = GrammarDetectiveGame;
})();
