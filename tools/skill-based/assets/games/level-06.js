/** Level 6 — Noun / Verb Sort */
(function () {
  var TILES = [
    { w: 'run', t: 'verb' },
    { w: 'school', t: 'noun' },
    { w: 'eat', t: 'verb' },
    { w: 'sister', t: 'noun' },
    { w: 'jump', t: 'verb' },
    { w: 'ball', t: 'noun' },
    { w: 'teacher', t: 'noun' },
    { w: 'write', t: 'verb' },
  ];

  class NounVerbSortGame extends SkillGame {
    constructor() {
      super({ lives: 3, objective: 'Tap a tile, then tap the correct lane (Noun or Verb).' });
      this.sel = null;
      this.done = 0;
    }

    onMount() {
      this.done = 0;
      this.sel = null;
      this.stage.innerHTML = '';
      var grid = this.createEl('div', 'g-sort');
      this.laneN = this.createEl('div', 'g-lane noun');
      this.laneN.innerHTML = '<h4>Nouns</h4>';
      this.laneV = this.createEl('div', 'g-lane verb');
      this.laneV.innerHTML = '<h4>Verbs</h4>';
      grid.appendChild(this.laneN);
      grid.appendChild(this.laneV);
      this.pool = this.createEl('div', 'g-pool');
      grid.appendChild(this.pool);
      this.stage.appendChild(grid);
      var self = this;
      this.laneN.onclick = function () {
        self._drop('noun');
      };
      this.laneV.onclick = function () {
        self._drop('verb');
      };
      TILES.slice()
        .sort(function () {
          return Math.random() - 0.5;
        })
        .forEach(function (t) {
          var el = self.createEl('button', 'g-tile', t.w);
          el.type = 'button';
          el.dataset.type = t.t;
          el.onclick = function (e) {
            e.stopPropagation();
            self._select(el, t);
          };
          self.pool.appendChild(el);
        });
    }

    _select(el, t) {
      if (el.classList.contains('sorted')) return;
      document.querySelectorAll('.g-tile').forEach(function (x) {
        x.style.outline = '';
      });
      this.sel = { el: el, t: t };
      el.style.outline = '3px solid #F0932B';
    }

    _drop(lane) {
      if (!this.sel) return;
      var el = this.sel.el;
      var t = this.sel.t;
      if (t.t === lane) {
        (lane === 'noun' ? this.laneN : this.laneV).appendChild(el);
        el.classList.add('sorted');
        el.style.outline = '';
        this.done++;
        this.addScore(18, 'Sorted!');
        this.setProgress(this.done / TILES.length);
        if (this.done >= TILES.length) this.win(3);
      } else {
        this.loseLife();
        this.shake(el);
      }
      this.sel = null;
    }
  }

  window.SKILL_GAMES[6] = NounVerbSortGame;
})();
