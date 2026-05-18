/** Level 1 — Letter Pop: falling letters, build CVC words in order */
(function () {
  var WORDS = [
    { w: 'cat', letters: ['c', 'a', 't'] },
    { w: 'dog', letters: ['d', 'o', 'g'] },
    { w: 'sun', letters: ['s', 'u', 'n'] },
    { w: 'pen', letters: ['p', 'e', 'n'] },
  ];

  class LetterPopGame extends SkillGame {
    constructor() {
      super({ lives: 3, objective: 'Pop letters in sound order before they fall off the screen!' });
      this.wi = 0;
      this.li = 0;
      this.letters = [];
      this.arena = null;
    }

    onMount() {
      this.wi = 0;
      this.li = 0;
      this.stage.innerHTML = '';
      this.targetEl = this.createEl('div', 'g-word-target', '_ _ _');
      this.stage.appendChild(this.targetEl);
      this.arena = this.createEl('div', 'g-arena');
      this.stage.appendChild(this.arena);
      this._spawnWord();
    }

    _spawnWord() {
      this.li = 0;
      this.letters.forEach(function (l) {
        if (l.el && l.el.parentNode) l.el.remove();
      });
      this.letters = [];
      var wd = WORDS[this.wi];
      this._updateTarget(wd);
      var pool = wd.letters.concat(
        'bcdefghjklmnpqrstvwxyz'.split('').sort(function () {
          return Math.random() - 0.5;
        })
      );
      var extras = [];
      for (var i = 0; i < 5; i++) extras.push(pool[i % pool.length]);
      var spawn = wd.letters.concat(extras).sort(function () {
        return Math.random() - 0.5;
      });
      var self = this;
      spawn.forEach(function (ch, i) {
        setTimeout(function () {
          self._dropLetter(ch, wd);
        }, i * 400);
      });
    }

    _updateTarget(wd) {
      var t = wd.letters
        .map(function (c, i) {
          return i < this.li ? c : '_';
        }, this)
        .join(' ');
      this.targetEl.textContent = t;
    }

    _dropLetter(ch, wd) {
      if (this.state !== 'playing') return;
      var el = this.createEl('button', 'g-letter', ch);
      el.type = 'button';
      var x = 10 + Math.random() * 75;
      el.style.left = x + '%';
      el.style.top = '-60px';
      this.arena.appendChild(el);
      var letter = { el: el, ch: ch, y: -60, vy: 0.8 + Math.random() * 0.4 };
      this.letters.push(letter);
      var self = this;
      el.onclick = function (e) {
        self._tap(letter, wd, e);
      };
    }

    onTick(dt) {
      var self = this;
      var h = this.arena ? this.arena.clientHeight : 300;
      this.letters.forEach(function (L) {
        if (!L.el || L.dead) return;
        L.y += L.vy * (dt * 60);
        L.el.style.top = L.y + 'px';
        if (L.y > h + 20) {
          L.dead = true;
          L.el.remove();
          if (L.ch === WORDS[self.wi].letters[self.li]) self.loseLife();
        }
      });
      this.letters = this.letters.filter(function (L) {
        return !L.dead;
      });
    }

    _tap(letter, wd, e) {
      if (letter.dead) return;
      var need = wd.letters[this.li];
      if (letter.ch !== need) {
        letter.el.classList.add('wrong');
        this.breakCombo();
        this.loseLife();
        return;
      }
      letter.dead = true;
      letter.el.classList.add('gone');
      var rect = letter.el.getBoundingClientRect();
      var ar = this.arena.getBoundingClientRect();
      this.burst(rect.left - ar.left + 26, rect.top - ar.top + 26, '#6AB04C');
      this.li++;
      this.addScore(15, 'Correct!');
      this._updateTarget(wd);
      setTimeout(function () {
        letter.el.remove();
      }, 200);
      if (this.li >= wd.letters.length) {
        var self = this;
        setTimeout(function () {
          self.wi++;
          self.setProgress(self.wi / WORDS.length);
          if (self.wi >= WORDS.length) self.win(3);
          else self._spawnWord();
        }, 500);
      }
    }
  }

  window.SKILL_GAMES[1] = LetterPopGame;
})();
