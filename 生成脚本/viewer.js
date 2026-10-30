/* 412 箱体 3D 查看器 —— 纯 Canvas 2D 软件渲染，无任何外部依赖 */
(function () {
  'use strict';
  var D = window.__CAB__;
  var cv = document.getElementById('cv');
  var ctx = cv.getContext('2d');
  var W = D.W, H = D.H, DP = D.D;
  var center = [W / 2, H / 2, DP / 2];
  var LIGHT = norm([-0.45, 0.85, -0.35]);

  var az = 146 * Math.PI / 180, el = 21 * Math.PI / 180;
  var zoom = 1, explode = 0, culling = true, dimsOn = false, focus = null, spin = false;
  var hide = { grille: false, baffle: false, spk: false, cloth: true };

  function norm(v) {
    var l = Math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]) || 1;
    return [v[0] / l, v[1] / l, v[2] / l];
  }
  function cross(a, b) {
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  }
  function dot(a, b) { return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]; }

  function basis() {
    var d = [Math.cos(el) * Math.sin(az), Math.sin(el), Math.cos(el) * Math.cos(az)];
    var r = norm(cross([-d[0], 0, -d[2]], [0, 1, 0]));
    if (Math.abs(r[0]) + Math.abs(r[2]) < 1e-6) r = [1, 0, 0];
    var u = norm(cross(d, r));
    return { d: d, r: r, u: u };
  }

  function shade(hex, k) {
    hex = hex.replace('#', '');
    var r = parseInt(hex.substr(0, 2), 16) * k;
    var g = parseInt(hex.substr(2, 2), 16) * k;
    var b = parseInt(hex.substr(4, 2), 16) * k;
    return 'rgb(' + Math.min(255, r | 0) + ',' + Math.min(255, g | 0) + ',' + Math.min(255, b | 0) + ')';
  }

  function visible(p) {
    if (hide.grille && p.id === 'grille') return false;
    if (hide.baffle && p.id === 'baffle') return false;
    if (hide.spk && p.id.indexOf('spk') === 0) return false;
    if (hide.cloth && p.id === 'cloth') return false;
    return true;
  }

  function draw() {
    var w = cv.width, h = cv.height;
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    var grd = ctx.createLinearGradient(0, 0, 0, h);
    grd.addColorStop(0, '#fbfaf7');
    grd.addColorStop(1, '#e7e2d8');
    ctx.fillStyle = grd;
    ctx.fillRect(0, 0, w, h);

    var B = basis(), d = B.d, r = B.r, u = B.u;
    var ex = explode * 430;
    var faces = [], xs = [], ys = [], i, j, k;
    for (i = 0; i < D.parts.length; i++) {
      var p = D.parts[i];
      if (!visible(p)) continue;
      var off = [p.explode[0] * ex, p.explode[1] * ex, p.explode[2] * ex];
      var dimAlpha = (focus && focus !== p.id) ? 0.22 : 1;
      for (var f = 0; f < p.faces.length; f++) {
        var rings = p.faces[f], first = rings[0];
        var n = norm(cross(
          [first[1][0] - first[0][0], first[1][1] - first[0][1], first[1][2] - first[0][2]],
          [first[2][0] - first[0][0], first[2][1] - first[0][1], first[2][2] - first[0][2]]));
        if (culling && dot(n, d) <= 0) continue;
        var pr = [], cx = 0, cy = 0, cz = 0, np = 0;
        for (j = 0; j < rings.length; j++) {
          var ring = rings[j], rr = [];
          for (k = 0; k < ring.length; k++) {
            var q = [ring[k][0] + off[0] - center[0],
                     ring[k][1] + off[1] - center[1],
                     ring[k][2] + off[2] - center[2]];
            var sx = dot(q, r), sy = -dot(q, u);
            rr.push([sx, sy]);
            xs.push(sx); ys.push(sy);
            cx += q[0]; cy += q[1]; cz += q[2]; np++;
          }
          pr.push(rr);
        }
        faces.push({ pr: pr, n: n, depth: dot([cx / np, cy / np, cz / np], d),
                     color: p.color, alpha: dimAlpha, layer: p.layer || 0 });
      }
    }
    if (!faces.length) return;
    var x0 = Math.min.apply(null, xs), x1 = Math.max.apply(null, xs);
    var y0 = Math.min.apply(null, ys), y1 = Math.max.apply(null, ys);
    var pad = 44;
    var sc = Math.min((w - 2 * pad) / Math.max(1, x1 - x0),
                      (h - 2 * pad) / Math.max(1, y1 - y0)) * zoom;
    var ox = w / 2 - (x0 + x1) / 2 * sc, oy = h / 2 - (y0 + y1) / 2 * sc;

    faces.sort(function (a, b) { return (a.layer - b.layer) || (a.depth - b.depth); });
    for (i = 0; i < faces.length; i++) {
      var F = faces[i];
      var lam = Math.max(0, dot(F.n, LIGHT));
      ctx.globalAlpha = F.alpha;
      ctx.beginPath();
      for (j = 0; j < F.pr.length; j++) {
        var rg = F.pr[j];
        ctx.moveTo(rg[0][0] * sc + ox, rg[0][1] * sc + oy);
        for (k = 1; k < rg.length; k++) ctx.lineTo(rg[k][0] * sc + ox, rg[k][1] * sc + oy);
        ctx.closePath();
      }
      ctx.fillStyle = shade(F.color, 0.55 + 0.5 * lam);
      ctx.fill('evenodd');
      ctx.strokeStyle = 'rgba(62,45,30,0.5)';
      ctx.lineWidth = Math.max(0.7, sc * 0.12);
      ctx.stroke();
    }
    ctx.globalAlpha = 1;
    if (dimsOn) drawDims(B, sc, ox, oy);
  }

  function P3(q, B, sc, ox, oy) {
    var t = [q[0] - center[0], q[1] - center[1], q[2] - center[2]];
    return [dot(t, B.r) * sc + ox, -dot(t, B.u) * sc + oy];
  }

  function dimLine(B, sc, ox, oy, a, b, label, off) {
    var pa = P3(a, B, sc, ox, oy), pb = P3(b, B, sc, ox, oy);
    var dx = pb[0] - pa[0], dy = pb[1] - pa[1], L = Math.hypot(dx, dy);
    if (L < 1) return;
    var nx = -dy / L * off, ny = dx / L * off;
    var A = [pa[0] + nx, pa[1] + ny], Bp = [pb[0] + nx, pb[1] + ny];
    ctx.strokeStyle = '#0b5fa5';
    ctx.lineWidth = 1.2;
    ctx.beginPath();
    ctx.moveTo(pa[0], pa[1]); ctx.lineTo(A[0], A[1]);
    ctx.moveTo(pb[0], pb[1]); ctx.lineTo(Bp[0], Bp[1]);
    ctx.moveTo(A[0], A[1]); ctx.lineTo(Bp[0], Bp[1]);
    ctx.stroke();
    ctx.fillStyle = '#0b5fa5';
    ctx.font = '600 ' + Math.round(13 * (window.devicePixelRatio || 1)) + 'px system-ui, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(label, (A[0] + Bp[0]) / 2, (A[1] + Bp[1]) / 2 - 5);
  }

  function drawDims(B, sc, ox, oy) {
    dimLine(B, sc, ox, oy, [0, 0, 0], [W, 0, 0], '760 宽', 30);
    dimLine(B, sc, ox, oy, [0, 0, 0], [0, H, 0], '760 高', 30);
    dimLine(B, sc, ox, oy, [W, 0, 0], [W, 0, DP], '355 深', 30);
    dimLine(B, sc, ox, oy, [0, H, 0], [0, H, 60], '斜收 60', 22);
    var pa = P3([0, H, 0], B, sc, ox, oy);
    ctx.textAlign = 'left';
    ctx.fillStyle = '#0b5fa5';
    ctx.fillText('前脸 4.51°', pa[0] + 8, pa[1] - 12);
  }

  // ---------------- 交互 ----------------
  var drag = null;
  cv.addEventListener('pointerdown', function (e) {
    drag = { x: e.clientX, y: e.clientY };
    cv.setPointerCapture(e.pointerId);
  });
  cv.addEventListener('pointermove', function (e) {
    if (!drag) return;
    az -= (e.clientX - drag.x) * 0.008;
    el += (e.clientY - drag.y) * 0.006;
    el = Math.max(-1.45, Math.min(1.45, el));
    drag = { x: e.clientX, y: e.clientY };
    draw();
  });
  cv.addEventListener('pointerup', function () { drag = null; });
  cv.addEventListener('wheel', function (e) {
    e.preventDefault();
    zoom *= Math.exp(-e.deltaY * 0.0012);
    zoom = Math.max(0.35, Math.min(4, zoom));
    draw();
  }, { passive: false });

  function resize() {
    var r = cv.getBoundingClientRect();
    var dpr = window.devicePixelRatio || 1;
    cv.width = Math.round(r.width * dpr);
    cv.height = Math.round(r.height * dpr);
    draw();
  }
  window.addEventListener('resize', resize);

  // ---------------- 控件 ----------------
  var elExp = document.getElementById('exp');
  elExp.addEventListener('input', function () {
    explode = +elExp.value / 100;
    culling = explode < 0.06;
    draw();
  });
  function btn(id, fn) { var b = document.getElementById(id); if (b) b.onclick = fn; }
  btn('bFront', function () { az = Math.PI; el = 0.02; draw(); });
  btn('bSide', function () { az = Math.PI / 2; el = 0.05; draw(); });
  btn('bTop', function () { az = Math.PI; el = 1.35; draw(); });
  btn('bIso', function () { az = 146 * Math.PI / 180; el = 21 * Math.PI / 180; zoom = 1; draw(); });
  btn('bDim', function () { dimsOn = !dimsOn; draw(); });
  btn('bGrille', function () {
    hide.grille = !hide.grille;
    culling = explode < 0.06 && !hide.grille && !hide.baffle;
    draw();
  });
  btn('bBaffle', function () {
    hide.baffle = !hide.baffle;
    culling = explode < 0.06 && !hide.grille && !hide.baffle;
    draw();
  });
  btn('bSpk', function () { hide.spk = !hide.spk; draw(); });
  btn('bCloth', function () { hide.cloth = !hide.cloth; draw(); });
  btn('bSpin', function () { spin = !spin; if (spin) loop(); });

  var list = document.getElementById('list');
  D.parts.forEach(function (p) {
    if (p.id.indexOf('spk') === 0 && p.id !== 'spk00') return;
    var li = document.createElement('div');
    li.className = 'item';
    li.innerHTML = '<span class="sw" style="background:' + p.color + '"></span>' +
      '<b>' + p.name + '</b><i>' + p.size + '</i>';
    li.onmouseenter = function () { focus = (p.id === 'spk00') ? null : p.id; draw(); };
    li.onmouseleave = function () { focus = null; draw(); };
    list.appendChild(li);
  });

  function loop() {
    if (!spin) return;
    az += 0.006;
    draw();
    requestAnimationFrame(loop);
  }

  // 支持地址栏参数，便于分享视角：#e=1&az=180&el=8
  (function () {
    var hp = new URLSearchParams(location.hash.replace('#', ''));
    if (hp.has('e')) {
      explode = Math.min(1, Math.max(0, parseFloat(hp.get('e')) || 0));
      elExp.value = explode * 100;
      culling = explode < 0.06;
    }
    if (hp.has('az')) az = (parseFloat(hp.get('az')) || 0) * Math.PI / 180;
    if (hp.has('el')) el = (parseFloat(hp.get('el')) || 0) * Math.PI / 180;
  })();
  resize();
})();
