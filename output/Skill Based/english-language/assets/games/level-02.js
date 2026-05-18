/** Level 2 — Rhyme Bridge: connect matching rhyme pairs across the bridge */
(function () {
  var PAIRS = [
    ['cat', 'hat'],
    ['dog', 'log'],
    ['pen', 'hen'],
    ['sun', 'fun'],
  ];

  class RhymeBridgeGame extends SkillGame {
    constructor() {
      super({ lives: 3, objective: 'Select a word on the left, then its rhyme on the right to build the bridge.' });
      this.sel = null;
      this.matched = 0;
    }

    onMount() {
      this.sel = null;
      this.matched = 0;
      this.stage.innerHTML = '';
      var board = this.createEl('div', 'g-rhyme-board');
      var left = this.createEl('div', 'g-rhyme-col');
      var bridge = this.createEl('div', 'g-rhyme-bridge');
      var right = this.createEl('div', 'g-rhyme-col');
      board.appendChild(left);
      board.appendChild(bridge);
      board.appendChild(right);
      this.stage.appendChild(board);
      this.bridge = bridge;
      var self = this;
      PAIRS.forEach(function (p) {
        var cL = self.createEl('button', 'g-card', p[0]);
        cL.type = 'button';
        cL.dataset.word = p[0];
        cL.dataset.pair = p[1];
        cL.onclick = function () {
          self._pick(cL, 'left');
        };
        left.appendChild(cL);
        var cR = self.createEl('button', 'g-card', p[1]);
        cR.type = 'button';
        cR.dataset.word = p[1];
        cR.dataset.pair = p[0];
        cR.onclick = function () {
          self._pick(cR, 'right');
        };
        right.appendChild(cR);
      });
    }

    _pick(card, side) {
      if (card.classList.contains('matched')) return;
      if (!this.sel) {
        this.sel = { card: card, side: side };
        card.classList.add('selected');
        return;
      }
      if (this.sel.card === card) {
        card.classList.remove('selected');
        this.sel = null;
        return;
      }
      if (this.sel.side === side) {
        this.sel.card.classList.remove('selected');
        this.sel = { card: card, side: side };
        card.classList.add('selected');
        return;
      }
      var ok =
        this.sel.card.dataset.pair === card.dataset.word ||
        card.dataset.pair === this.sel.card.dataset.word;
      if (ok) {
        this.sel.card.classList.remove('selected');
        this.sel.card.classList.add('matched');
        card.classList.add('matched');
        this.bridge.classList.add('live');
        var self = this;
        setTimeout(function () {
          self.bridge.classList.remove('live');
        }, 400);
        this.matched++;
        this.addScore(25, 'Rhyme!');
        this.setProgress(this.matched / PAIRS.length);
        if (this.matched >= PAIRS.length) this.win(3);
      } else {
        this.breakCombo();
        this.loseLife();
        this.shake(card);
      }
      this.sel = null;
    }
  }

  window.SKILL_GAMES[2] = RhymeBridgeGame;
})();
