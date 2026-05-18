/** Level 10 — Story Bridge: comic connectors */
(function () {
  var PANELS = [
    { text: 'I was tired', ans: 'so' },
    { text: 'It rained', ans: 'but' },
    { text: 'We stayed in', ans: 'because' },
  ];

  class StoryBridgeGame extends SkillGame {
    constructor() {
      super({ lives: 3, objective: 'Drag a connector into each comic panel slot.' });
      this.done = 0;
      this.drag = null;
    }

    onMount() {
      this.done = 0;
      this.stage.innerHTML = '';
      var wrap = this.createEl('div', 'g-comic');
      var strip = this.createEl('div', '');
      var bank = this.createEl('div', 'g-connectors');
      var self = this;
      PANELS.forEach(function (p, i) {
        var pan = self.createEl('div', 'g-panel');
        pan.innerHTML = '<div>' + p.text + '</div><div class="g-slot-drop" data-i="' + i + '">Drop here</div>';
        var slot = pan.querySelector('.g-slot-drop');
        slot.ondragover = function (e) {
          e.preventDefault();
        };
        slot.ondrop = function (e) {
          e.preventDefault();
          if (!self.drag) return;
          if (self.drag.textContent === p.ans) {
            slot.textContent = p.ans;
            slot.classList.add('filled');
            self.drag.remove();
            self.done++;
            self.addScore(25, 'Connected!');
            self.setProgress(self.done / PANELS.length);
            if (self.done >= PANELS.length) self.win(3);
          } else self.loseLife();
          self.drag = null;
        };
        strip.appendChild(pan);
      });
      ['and', 'but', 'because', 'so'].forEach(function (c) {
        var ch = self.createEl('div', 'g-conn', c);
        ch.draggable = true;
        ch.ondragstart = function () {
          self.drag = ch;
        };
        bank.appendChild(ch);
      });
      wrap.appendChild(strip);
      wrap.appendChild(bank);
      this.stage.appendChild(wrap);
    }
  }

  window.SKILL_GAMES[10] = StoryBridgeGame;
})();
