/* motion.js: the runtime under the plan-view graphics on the case pages.

   A graphic is an inline SVG with a draw function. This file owns the clock,
   so every graphic behaves the same way: it starts when it scrolls into view,
   stops when it leaves, pauses on a button, freezes to a composed frame under
   prefers-reduced-motion or when the page is opened with ?static=1&t=<seconds>
   (which is how the cover captures are taken), and exposes toggles and
   tooltips that work from the keyboard as well as the pointer.

   Usage, from a graphic's own script:

     Motion.mount(root, {
       duration: 48,                       // seconds in one loop
       freeze: 31,                         // the composed moment for static frames
       state: { host: true },              // toggles write here
       draw: function (t, s) { ... },      // t in seconds, s the state; draw the frame
       describe: function (s) { ... }      // one sentence for the live region
     });

   root is the element with class "mo" that wraps the SVG and the control bar.
   Toggles are <button data-toggle="host" aria-pressed="true"> inside root.
   Hotspots are elements with data-tip="text" inside the SVG; they get a
   tooltip on hover, focus and tap. */
(function () {
  'use strict';
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var params = new URLSearchParams(location.search);
  var STATIC = params.get('static') === '1' || reduce;
  var T_STATIC = params.has('t') ? parseFloat(params.get('t')) : null;
  /* ?set=host:0,routine:1 forces a toggle before the first frame, so a capture or an
     audit can ask for either state of a graphic without clicking anything. */
  var PRESET = {};
  (params.get('set') || '').split(',').filter(Boolean).forEach(function (pair) {
    var kv = pair.split(':'); PRESET[kv[0]] = kv[1] !== '0';
  });

  function q(el, s) { return el.querySelector(s); }
  function qa(el, s) { return Array.prototype.slice.call(el.querySelectorAll(s)); }

  function tooltip(root) {
    var tip = document.createElement('div');
    tip.className = 'mo-tip'; tip.setAttribute('role', 'status'); tip.hidden = true;
    root.appendChild(tip);
    var open = null;
    function place(x, y) {
      var r = root.getBoundingClientRect();
      var left = x - r.left, top = y - r.top;
      tip.style.left = Math.max(8, Math.min(left, r.width - tip.offsetWidth - 8)) + 'px';
      tip.style.top = Math.max(8, top - tip.offsetHeight - 14) + 'px';
    }
    function show(el, x, y) {
      tip.textContent = el.getAttribute('data-tip'); tip.hidden = false; open = el;
      el.classList.add('is-tipped');
      if (x == null) { var b = el.getBoundingClientRect(); x = b.left + b.width / 2; y = b.top; }
      place(x, y);
    }
    function hide() { if (open) open.classList.remove('is-tipped'); open = null; tip.hidden = true; }
    root.addEventListener('pointermove', function (e) {
      var el = e.target.closest ? e.target.closest('[data-tip]') : null;
      if (el && root.contains(el)) { if (open !== el) show(el, e.clientX, e.clientY); else place(e.clientX, e.clientY); }
      else if (open && !open.matches(':focus')) hide();
    });
    root.addEventListener('pointerleave', function () { if (open && !open.matches(':focus')) hide(); });
    root.addEventListener('focusin', function (e) { var el = e.target.closest('[data-tip]'); if (el) show(el); });
    root.addEventListener('focusout', function (e) { var el = e.target.closest('[data-tip]'); if (el) hide(); });
    root.addEventListener('keydown', function (e) { if (e.key === 'Escape') hide(); });
    qa(root, '[data-tip]').forEach(function (el) {
      if (!el.hasAttribute('tabindex')) el.setAttribute('tabindex', '0');
      if (!el.hasAttribute('role')) el.setAttribute('role', 'img');
      if (!el.hasAttribute('aria-label')) el.setAttribute('aria-label', el.getAttribute('data-tip'));
    });
    return { show: show, hide: hide };
  }

  function mount(root, spec) {
    var svg = q(root, 'svg');
    var state = spec.state || {};
    Object.keys(PRESET).forEach(function (k) { state[k] = PRESET[k]; });
    var duration = spec.duration || 40;
    var live = q(root, '.mo-live');
    if (!live) { live = document.createElement('p'); live.className = 'mo-live'; live.setAttribute('aria-live', 'polite'); root.appendChild(live); }
    tooltip(root);

    var playing = false, raf = 0, last = 0, t = 0, inView = false;
    var bar = q(root, '.mo-bar');
    var play = bar ? q(bar, '[data-play]') : null;

    function say() { if (spec.describe) live.textContent = spec.describe(state, t); }
    function frame(now) {
      if (!playing) return;
      var dt = last ? Math.min(0.05, (now - last) / 1000) : 0; last = now;
      t = (t + dt) % duration;
      spec.draw(t, state, dt);
      raf = requestAnimationFrame(frame);
    }
    function start() {
      if (STATIC || playing || !inView) return;
      playing = true; last = 0; raf = requestAnimationFrame(frame);
      root.classList.add('is-playing'); if (play) { play.setAttribute('aria-pressed', 'true'); play.textContent = 'Pause'; }
    }
    function stop(byUser) {
      playing = false; cancelAnimationFrame(raf); root.classList.remove('is-playing');
      if (play) { play.setAttribute('aria-pressed', 'false'); play.textContent = 'Play'; }
      if (byUser) root.classList.add('is-paused');
    }
    function still() {
      t = T_STATIC != null ? T_STATIC : (spec.freeze != null ? spec.freeze : duration * 0.6);
      spec.draw(t, state, 0); say();
    }

    if (play) {
      play.addEventListener('click', function () {
        if (playing) stop(true); else { root.classList.remove('is-paused'); inView = true; start(); }
      });
    }
    qa(root, '[data-toggle]').forEach(function (b) {
      var key = b.getAttribute('data-toggle');
      b.setAttribute('aria-pressed', state[key] ? 'true' : 'false');
      b.addEventListener('click', function () {
        state[key] = !state[key];
        b.setAttribute('aria-pressed', state[key] ? 'true' : 'false');
        if (spec.onToggle) spec.onToggle(key, state);
        if (!playing) spec.draw(t, state, 0);
        say();
      });
    });
    qa(root, '[data-action]').forEach(function (b) {
      b.addEventListener('click', function () {
        if (spec.onAction) { var nt = spec.onAction(b.getAttribute('data-action'), state, t); if (typeof nt === 'number') t = nt; }
        if (!playing) spec.draw(t, state, 0);
        say();
      });
    });

    if (STATIC) {
      root.classList.add('is-static');
      if (play) play.hidden = true;
      still();
      return { state: state, redraw: function () { spec.draw(t, state, 0); } };
    }
    spec.draw(0, state, 0); say();
    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          inView = en.isIntersecting;
          if (inView && !root.classList.contains('is-paused')) start(); else if (!inView) stop(false);
        });
      }, { threshold: 0.2 });
      io.observe(root);
    } else { inView = true; start(); }
    document.addEventListener('visibilitychange', function () { if (document.hidden) stop(false); else if (inView && !root.classList.contains('is-paused')) start(); });
    return { state: state, redraw: function () { spec.draw(t, state, 0); } };
  }

  /* ---- small drawing helpers shared by the graphics ---- */
  var NS = 'http://www.w3.org/2000/svg';
  function el(name, attrs, parent) {
    var e = document.createElementNS(NS, name);
    if (attrs) Object.keys(attrs).forEach(function (k) { e.setAttribute(k, attrs[k]); });
    if (parent) parent.appendChild(e);
    return e;
  }
  function text(parent, x, y, s, attrs) {
    var t = el('text', Object.assign({ x: x, y: y }, attrs || {}), parent); t.textContent = s; return t;
  }
  /* a point along a polyline at distance d, with the heading */
  function polyline(pts) {
    var segs = [], total = 0;
    for (var i = 1; i < pts.length; i++) {
      var dx = pts[i][0] - pts[i - 1][0], dy = pts[i][1] - pts[i - 1][1], L = Math.hypot(dx, dy);
      segs.push({ a: pts[i - 1], dx: dx, dy: dy, L: L, from: total }); total += L;
    }
    return {
      length: total,
      at: function (d) {
        d = Math.max(0, Math.min(total, d));
        for (var i = 0; i < segs.length; i++) {
          var s = segs[i];
          if (d <= s.from + s.L || i === segs.length - 1) {
            var u = s.L ? (d - s.from) / s.L : 0;
            return { x: s.a[0] + s.dx * u, y: s.a[1] + s.dy * u, ang: Math.atan2(s.dy, s.dx) };
          }
        }
      }
    };
  }
  function ease(u) { return u < 0.5 ? 2 * u * u : 1 - Math.pow(-2 * u + 2, 2) / 2; }
  function clamp(v, a, b) { return Math.max(a, Math.min(b, v)); }
  /* deterministic pseudo-random, so a frozen frame is the same every capture */
  function rng(seed) { var a = seed >>> 0; return function () { a |= 0; a = (a + 0x6d2b79f5) | 0; var t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }

  window.Motion = { mount: mount, el: el, text: text, polyline: polyline, ease: ease, clamp: clamp, rng: rng, isStatic: STATIC };
})();
