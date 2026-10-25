
(function () {
  var root = document.documentElement;
  var sidebar = document.getElementById('sidebar');
  var scrim = document.getElementById('scrim');
  var menuBtn = document.getElementById('menuBtn');
  var themeBtn = document.getElementById('themeBtn');
  var toTop = document.getElementById('toTop');
  var bar = document.getElementById('progressBar');
  var searchInput = document.getElementById('searchInput');
  var searchCount = document.getElementById('searchCount');
  var groups = Array.prototype.slice.call(document.querySelectorAll('.toc-group'));
  var sections = Array.prototype.slice.call(document.querySelectorAll('h2[id]'));
  var tocSecs = Array.prototype.slice.call(document.querySelectorAll('.toc-sec'));

  /* ---- hash landing fix (lazy images / svg may shift layout) ---- */
  function landOnHash() {
    if (!location.hash) return;
    var el = document.getElementById(location.hash.slice(1));
    if (!el) return;
    var y = el.getBoundingClientRect().top + window.pageYOffset - 72;
    window.scrollTo({ top: y, behavior: 'auto' });
  }
  window.addEventListener('load', function () { landOnHash(); setTimeout(landOnHash, 120); setTimeout(landOnHash, 450); setTimeout(landOnHash, 1200); setTimeout(function () { window.dispatchEvent(new Event('scroll')); }, 1250); });
  window.addEventListener('hashchange', function () { setTimeout(landOnHash, 30); });

  /* ---- theme ---- */
  var saved = null;
  try { saved = localStorage.getItem('fde-theme'); } catch (e) {}
  if (saved) root.setAttribute('data-theme', saved);
  else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) root.setAttribute('data-theme', 'dark');
  themeBtn.addEventListener('click', function () {
    var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    try { localStorage.setItem('fde-theme', next); } catch (e) {}
  });

  /* ---- mobile drawer ---- */
  function closeDrawer() { sidebar.classList.remove('open'); scrim.classList.remove('show'); }
  menuBtn && menuBtn.addEventListener('click', function () {
    sidebar.classList.toggle('open');
    scrim.classList.toggle('show', sidebar.classList.contains('open'));
  });
  scrim.addEventListener('click', closeDrawer);

  /* ---- progress + to top ---- */
  var ticking = false;
  function onScroll() {
    var h = document.documentElement;
    var max = h.scrollHeight - h.clientHeight;
    var p = max > 0 ? (h.scrollTop / max) * 100 : 0;
    bar.style.width = p.toFixed(1) + '%';
    toTop.classList.toggle('show', h.scrollTop > 700);
    ticking = false;
  }
  window.addEventListener('scroll', function () {
    if (!ticking) { ticking = true; window.requestAnimationFrame(onScroll); }
  }, { passive: true });
  onScroll();
  toTop.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: 'smooth' }); });

  /* ---- scroll spy ---- */
  var currentId = null;
  function setActive(id) {
    if (id === currentId) return;
    currentId = id;
    tocSecs.forEach(function (a) {
      var on = a.getAttribute('href') === '#' + id;
      a.classList.toggle('active', on);
      if (on) {
        var g = a.closest('.toc-group');
        groups.forEach(function (x) {
          x.classList.toggle('open', x === g);
          var c = x.querySelector('.toc-ch');
          if (c) c.classList.toggle('active', x === g);
        });
        if (sidebar.scrollHeight > sidebar.clientHeight) {
          var r = a.getBoundingClientRect(), sr = sidebar.getBoundingClientRect();
          if (r.top < sr.top + 40 || r.bottom > sr.bottom - 40) a.scrollIntoView({ block: 'center' });
        }
      }
    });
  }
  function spy() {
    var best = sections[0];
    for (var k = 0; k < sections.length; k++) {
      if (sections[k].getBoundingClientRect().top <= 96) best = sections[k];
      else break;
    }
    if (best) setActive(best.id);
  }
  window.addEventListener('scroll', spy, { passive: true });
  window.addEventListener('resize', spy);
  sections.length && spy();
  if (location.hash) {
    var hid = location.hash.slice(1);
    if (document.getElementById(hid) && sections.some(function (x) { return x.id === hid; })) setActive(hid);
  }

  /* ---- search (filters table of contents) ---- */
  function normalize(s) { return (s || '').toLowerCase().replace(/\s+/g, ''); }
  if (searchInput) {
    searchInput.addEventListener('input', function () {
      var q = normalize(searchInput.value);
      var hits = 0;
      groups.forEach(function (g) {
        var ghit = 0;
        var chTxt = normalize(g.querySelector('.toc-ch').textContent);
        var chHit = q && chTxt.indexOf(q) > -1;
        Array.prototype.forEach.call(g.querySelectorAll('.toc-sec'), function (a) {
          var ok = !q || chHit || normalize(a.getAttribute('data-txt')).indexOf(q) > -1;
          a.classList.toggle('hide', !ok);
          if (ok) ghit++;
        });
        g.classList.toggle('hide', q && ghit === 0);
        if (q) g.classList.toggle('open', ghit > 0);
        hits += ghit;
      });
      if (!q) {
        searchCount.textContent = '';
        groups.forEach(function (g, i) { g.classList.toggle('open', i === 0); g.classList.remove('hide'); });
      } else {
        searchCount.textContent = hits + ' 节';
      }
    });
    searchInput.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { searchInput.value = ''; searchInput.dispatchEvent(new Event('input')); }
    });
  }

  /* ---- toc clicks ---- */
  tocSecs.forEach(function (a) { a.addEventListener('click', closeDrawer); });
  Array.prototype.forEach.call(document.querySelectorAll('.toc-ch'), function (a) {
    a.addEventListener('click', function () {
      var g = a.closest('.toc-group');
      groups.forEach(function (x) { if (x !== g) x.classList.remove('open'); });
      g.classList.add('open');
      closeDrawer();
    });
  });

  /* ---- keyboard: / focuses search ---- */
  document.addEventListener('keydown', function (e) {
    if (e.key === '/' && document.activeElement !== searchInput) {
      e.preventDefault(); searchInput && searchInput.focus();
    }
  });
})();
