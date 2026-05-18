/** Level 11 — Echo Chamber: speech or tap words in order */
(function () {
  var PHRASES = [
    ['Good', 'morning,', 'teacher.'],
    ['Please', 'open', 'the', 'door.'],
    ['Thank', 'you', 'very', 'much.'],
  ];

  class EchoChamberGame extends SkillGame {
    constructor() {
      super({ objective: 'Tap words in order — or use the mic to speak the phrase.' });
      this.pi = 0;
      this.tapIdx = 0;
    }

    onMount() {
      this.pi = 0;
      this._showPhrase();
    }

    _showPhrase() {
      if (this.pi >= PHRASES.length) {
        this.win(3);
        return;
      }
      this.tapIdx = 0;
      var words = PHRASES[this.pi];
      this.stage.innerHTML = '';
      var wrap = this.createEl('div', 'g-echo');
      this.phraseEl = this.createEl('div', 'g-echo-phrase', words.join(' '));
      var mic = this.createEl('button', 'g-echo-mic', '🎤');
      mic.type = 'button';
      mic.setAttribute('aria-label', 'Speak');
      this.statusEl = this.createEl('div', '', '');
      this.statusEl.style.minHeight = '1.5em';
      this.statusEl.style.marginTop = '8px';
      var chips = this.createEl('div', 'g-echo-chips');
      var self = this;
      words.forEach(function (w, i) {
        var c = self.createEl('button', 'g-echo-chip', w);
        c.type = 'button';
        c.onclick = function () {
          self._tapWord(c, i, words);
        };
        chips.appendChild(c);
      });
      var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (SR) {
        this.statusEl.textContent = 'Tap mic or tap each word in order';
        var rec = new SR();
        rec.lang = 'en-GB';
        mic.onclick = function () {
          self.statusEl.textContent = 'Listening…';
          rec.onresult = function (ev) {
            var said = (ev.results[0][0].transcript || '').toLowerCase();
            var target = words.join(' ').toLowerCase();
            if (said.replace(/[^a-z, ]/g, '').indexOf(target.split(' ')[0]) >= 0) {
              self.addScore(35, 'Great speaking!');
              self.pi++;
              self.setProgress(self.pi / PHRASES.length);
              setTimeout(function () {
                self._showPhrase();
              }, 600);
            } else self.statusEl.textContent = 'Try again or tap words';
          };
          rec.onerror = function () {
            self.statusEl.textContent = 'Mic blocked — tap words below';
          };
          try {
            rec.start();
          } catch (e) {
            self.statusEl.textContent = 'Tap words below';
          }
        };
      } else {
        this.statusEl.textContent = 'Tap each word in order';
      }
      wrap.appendChild(this.phraseEl);
      wrap.appendChild(mic);
      wrap.appendChild(this.statusEl);
      wrap.appendChild(chips);
      this.stage.appendChild(wrap);
    }

    _tapWord(el, i, words) {
      if (i !== this.tapIdx) {
        this.statusEl.textContent = 'Wrong order — try again';
        this.tapIdx = 0;
        this.stage.querySelectorAll('.g-echo-chip').forEach(function (c) {
          c.classList.remove('done');
        });
        this.breakCombo();
        return;
      }
      el.classList.add('done');
      this.tapIdx++;
      this.addScore(12, 'Word!');
      if (this.tapIdx >= words.length) {
        this.pi++;
        this.setProgress(this.pi / PHRASES.length);
        var self = this;
        setTimeout(function () {
          self._showPhrase();
        }, 500);
      }
    }
  }

  window.SKILL_GAMES[11] = EchoChamberGame;
})();
