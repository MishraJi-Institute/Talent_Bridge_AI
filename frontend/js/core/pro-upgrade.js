/* TalentBridge AI — Pro Upgrade behaviours (progressive enhancement, no dependencies) */
(function () {
  'use strict';
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  function ready(fn) {
    if (document.readyState !== 'loading') fn(); else document.addEventListener('DOMContentLoaded', fn);
  }

  ready(function () {
    var nav = $('.navbar');

    /* 1. Scroll progress bar + condensed nav + back-to-top */
    var bar = document.createElement('div');
    bar.className = 'pro-progress';
    bar.setAttribute('aria-hidden', 'true');
    document.body.appendChild(bar);

    var top = document.createElement('button');
    top.className = 'pro-top';
    top.type = 'button';
    top.setAttribute('aria-label', 'Back to top');
    top.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 19V5M5 12l7-7 7 7"/></svg>';
    top.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' });
    });
    document.body.appendChild(top);

    var ticking = false;
    function onScroll() {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(function () {
        var h = document.documentElement;
        var max = h.scrollHeight - h.clientHeight;
        var y = window.pageYOffset || h.scrollTop;
        bar.style.transform = 'scaleX(' + (max > 0 ? Math.min(y / max, 1) : 0) + ')';
        if (nav) nav.classList.toggle('is-scrolled', y > 24);
        top.classList.toggle('show', y > 700);
        ticking = false;
      });
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();

    /* 3. Scroll-reveal for sections, cards and stats */
    var targets = $$([
      '.metrics-ribbon', '.feature-card-emp', '.success-story-card',
      '.jobseekers-card-side', '.faq-item', '.employers-title',
      '.jobseekers-title', '.success-stories-heading', '.faq-main-title'
    ].join(','));
    if ('IntersectionObserver' in window && !reduce) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) { e.target.classList.add('pro-in'); io.unobserve(e.target); }
        });
      }, { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
      targets.forEach(function (el, i) {
        el.classList.add('pro-reveal');
        el.style.transitionDelay = ((i % 4) * 70) + 'ms';
        io.observe(el);
      });
    }

    /* 4. Animated counters for metric values (e.g. "10x", "95%", "50K+") */
    var counters = $$('.metric-value');
    if ('IntersectionObserver' in window && !reduce && counters.length) {
      var co = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (!e.isIntersecting) return;
          co.unobserve(e.target);
          var el = e.target, raw = el.textContent.trim();
          var m = raw.match(/^([^\d]*)([\d][\d,.]*)(.*)$/);
          if (!m) return;
          var num = parseFloat(m[2].replace(/,/g, ''));
          if (!isFinite(num) || num === 0) return;
          var decimals = (m[2].split('.')[1] || '').length, hasComma = m[2].indexOf(',') > -1;
          var start = performance.now(), dur = 1400;
          (function tick(now) {
            var p = Math.min((now - start) / dur, 1), eased = 1 - Math.pow(1 - p, 3);
            var v = (num * eased).toFixed(decimals);
            if (hasComma) v = Number(v).toLocaleString('en-US', { minimumFractionDigits: decimals });
            el.textContent = m[1] + v + m[3];
            if (p < 1) requestAnimationFrame(tick); else el.textContent = raw;
          })(start);
        });
      }, { threshold: 0.6 });
      counters.forEach(function (c) { co.observe(c); });
    }

    /* 5. Highlight the nav link of the section currently in view */
    var links = $$('.nav-links a[href^="#"]');
    if (links.length && 'IntersectionObserver' in window) {
      var map = {};
      links.forEach(function (a) { map[a.getAttribute('href').slice(1)] = a; });
      var so = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting && map[e.target.id]) {
            links.forEach(function (l) { l.classList.remove('is-active'); });
            map[e.target.id].classList.add('is-active');
          }
        });
      }, { threshold: 0.4 });
      Object.keys(map).forEach(function (id) { var s = document.getElementById(id); if (s) so.observe(s); });
    }

    /* 6. Mark the link for the current page as active */
    var here = location.pathname.split('/').pop();
    $$('.nav-links a:not([href^="#"])').forEach(function (a) {
      if (here && a.getAttribute('href').split('/').pop() === here) a.classList.add('is-active');
    });
  });
})();
