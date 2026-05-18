/** Level 7 — Paint the Picture: adjectives reveal scene layers */
(function () {
  var MAP = {
    bright: { layer: 'layerSun', label: 'Bright sun' },
    tall: { layer: 'layerTree', label: 'Tall tree' },
    fluffy: { layer: 'layerCloud', label: 'Fluffy cloud' },
    blue: { layer: 'layerSky', label: 'Blue sky' },
  };
  var NEED = ['bright', 'tall', 'fluffy'];

  class PaintPictureGame extends SkillGame {
    constructor() {
      super({ objective: 'Choose adjectives to paint the scene — find bright, tall, and fluffy!' });
      this.picked = 0;
    }

    onMount() {
      this.picked = 0;
      this.stage.innerHTML = '';
      var wrap = this.createEl('div', 'g-paint');
      var scene = this.createEl('div', 'g-scene');
      scene.innerHTML =
        '<svg id="layerSky" viewBox="0 0 400 280" style="position:absolute;inset:0;opacity:0;transition:.4s"><rect width="400" height="280" fill="#5dade2"/></svg>' +
        '<svg id="layerSun" viewBox="0 0 400 280" style="position:absolute;inset:0;opacity:0;transition:.4s"><circle cx="320" cy="60" r="42" fill="#F0932B"/></svg>' +
        '<svg id="layerTree" viewBox="0 0 400 280" style="position:absolute;inset:0;opacity:0;transition:.4s"><rect x="50" y="130" width="28" height="110" fill="#5D4037"/><ellipse cx="64" cy="115" rx="50" ry="45" fill="#2E7D32"/></svg>' +
        '<svg id="layerCloud" viewBox="0 0 400 280" style="position:absolute;inset:0;opacity:0;transition:.4s"><ellipse cx="180" cy="75" rx="55" ry="30" fill="#fff"/></svg>';
      wrap.appendChild(scene);
      var row = this.createEl('div', 'g-adj-row');
      var self = this;
      Object.keys(MAP).forEach(function (key) {
        var btn = self.createEl('button', 'g-adj-btn', key);
        btn.type = 'button';
        btn.onclick = function () {
          self._paint(btn, key);
        };
        row.appendChild(btn);
      });
      wrap.appendChild(row);
      this.stage.appendChild(wrap);
    }

    _paint(btn, key) {
      if (btn.classList.contains('used')) return;
      var info = MAP[key];
      var layer = document.getElementById(info.layer);
      if (layer) layer.style.opacity = '1';
      btn.classList.add('used');
      this.addScore(15, info.label);
      if (NEED.indexOf(key) >= 0) {
        this.picked++;
        this.setProgress(this.picked / NEED.length);
      }
      if (this.picked >= NEED.length) this.win(3);
    }
  }

  window.SKILL_GAMES[7] = PaintPictureGame;
})();
