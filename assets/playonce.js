/* Animations that play once, when the thing they belong to comes into view.

   Two behaviours, both opt-in by class, both one-shot. Nothing here loops, nothing
   follows the scroll wheel, and nothing takes the scroll away from the reader.

   .reveal   an artefact rises and fades in the first time it is seen.
   .seq      a stack of frames plays through in order once, then rests on the last.
             Each frame is an <img class="seq-frame">; the caption of the step it
             is on is highlighted if a matching <li data-frame="n"> exists.

   Under prefers-reduced-motion nothing moves: a .reveal is simply visible and a
   .seq shows its final frame straight away, which is the state that carries the
   meaning. Without script, the CSS leaves everything visible. */
(function () {
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function playSeq(fig) {
    var frames = Array.prototype.slice.call(fig.querySelectorAll('.seq-frame'));
    if (!frames.length) return;
    var steps = Array.prototype.slice.call(fig.querySelectorAll('[data-frame]'));
    var hold = parseInt(fig.getAttribute('data-hold') || 1150, 10);

    function show(i) {
      frames.forEach(function (f, k) { f.classList.toggle('is-on', k === i); });
      steps.forEach(function (s) {
        s.classList.toggle('is-on', parseInt(s.getAttribute('data-frame'), 10) === i);
      });
    }

    if (reduce) { show(frames.length - 1); steps.forEach(function (s) { s.classList.add('is-on'); }); return; }

    show(0);
    var i = 0;
    var timer = setInterval(function () {
      i += 1;
      if (i >= frames.length) {
        clearInterval(timer);
        show(frames.length - 1);
        fig.classList.add('has-played');
        return;
      }
      show(i);
    }, hold);
  }

  function init() {
    var reveals = document.querySelectorAll('.reveal, .seq');
    if (!('IntersectionObserver' in window)) {
      reveals.forEach(function (el) { el.classList.add('is-in'); if (el.classList.contains('seq')) playSeq(el); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        var el = e.target;
        io.unobserve(el);            /* once, and only once */
        el.classList.add('is-in');
        if (el.classList.contains('seq')) {
          /* let the reveal settle before the sequence starts */
          setTimeout(function () { playSeq(el); }, reduce ? 0 : 320);
        }
      });
    }, { rootMargin: '0px 0px -12% 0px', threshold: 0.2 });
    reveals.forEach(function (el) { io.observe(el); });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
