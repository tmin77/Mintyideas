(function () {
  // Keep the current page's tab visible in the scrollable mobile nav
  var cur = document.querySelector('.nav-links a[aria-current="page"]');
  if (cur && cur.scrollIntoView && window.innerWidth < 760) cur.scrollIntoView({ block: 'nearest', inline: 'center' });

  var y = document.querySelector('[data-year]');
  if (y) y.textContent = new Date().getFullYear();

  // Contact form: on the live site FormSubmit emails the message and redirects back with ?sent=1.
  // In preview builds, keep the visitor on the page and explain.
  var form = document.querySelector('form.contact');
  if (form && /[?&]sent=1/.test(location.search)) {
    var ok = form.querySelector('.form-note');
    if (ok) { ok.hidden = false; ok.textContent = 'Thanks! Your message is in. Tyler will reply within two business days.'; }
  }
  if (form && document.documentElement.hasAttribute('data-preview')) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var note = form.querySelector('.form-note');
      if (note) {
        note.hidden = false;
        note.textContent = 'Preview only: this form starts sending to Tyler@mintyideas.com once the site is live on mintyideas.com.';
      }
    });
  }

  // Work page: tap-to-play. On the live site the card swaps in the platform's player.
  // In preview, or if no embed is available, the card simply opens the post on the platform.
  var preview = document.documentElement.hasAttribute('data-preview');
  document.querySelectorAll('a.vc[data-embed]').forEach(function (card) {
    if (preview) return;
    card.addEventListener('click', function (ev) {
      if (card.classList.contains('is-playing')) return;
      ev.preventDefault();
      var f = document.createElement('iframe');
      f.src = card.getAttribute('data-embed');
      f.title = card.getAttribute('aria-label') || 'Video';
      f.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
      f.allowFullscreen = true;
      card.classList.add('is-playing');
      card.removeAttribute('href');
      card.innerHTML = '';
      card.appendChild(f);
    });
  });

  // Work page: platform filter
  var filters = document.querySelectorAll('.filter');
  filters.forEach(function (b) {
    b.addEventListener('click', function () {
      var p = b.getAttribute('data-filter');
      filters.forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      document.querySelectorAll('.work-sec [data-group]').forEach(function (c) {
        c.hidden = !(p === 'all' || c.getAttribute('data-group') === p);
      });
      document.querySelectorAll('[data-sec]').forEach(function (s) {
        s.hidden = !s.querySelector('[data-group]:not([hidden])');
      });
    });
  });
})();
