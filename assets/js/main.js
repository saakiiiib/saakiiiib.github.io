// ---- reduced-motion preference & SVG SMIL control --------------------------
const reduceMotionQuery = matchMedia('(prefers-reduced-motion: reduce)');
let reduce = reduceMotionQuery.matches;

function syncSmilAnimations(shouldPause) {
  document.querySelectorAll('svg').forEach(svg => {
    if (shouldPause) {
      if (typeof svg.pauseAnimations === 'function') svg.pauseAnimations();
      if (typeof svg.setCurrentTime === 'function') svg.setCurrentTime(0);
    } else if (typeof svg.unpauseAnimations === 'function') {
      svg.unpauseAnimations();
    }
  });
}
syncSmilAnimations(reduce);

// ---- sunlight particles falling onto the page ------------------------------
const c = document.getElementById('sky');
const x = c ? c.getContext('2d') : null;
let W = 0, H = 0, P = [], raf = null, heroVisible = true;

function size() {
  if (!c) return;
  W = c.width = c.offsetWidth * devicePixelRatio;
  H = c.height = c.offsetHeight * devicePixelRatio;
}

if (c && x) {
  size();
  addEventListener('resize', () => { size(); if (!running()) frame(false); });

  for (let i = 0; i < 90; i++) {
    P.push({
      x: Math.random(), y: Math.random(),
      v: .0006 + Math.random() * .0018,
      l: 8 + Math.random() * 28,
      a: .15 + Math.random() * .5
    });
  }
}

// one painted frame; advance only when animating
function frame(step) {
  if (!x) return;
  const g = x.createRadialGradient(W * .85, -H * .1, 0, W * .85, -H * .1, H * 1.1);
  g.addColorStop(0, 'rgba(255,170,70,.28)');
  g.addColorStop(1, 'rgba(11,16,32,0)');
  x.fillStyle = '#0b1020'; x.fillRect(0, 0, W, H);
  x.fillStyle = g;         x.fillRect(0, 0, W, H);
  for (const p of P) {
    x.strokeStyle = `rgba(255,${170 + Math.floor(p.a * 60)},80,${p.a})`;
    x.lineWidth = 1.4 * devicePixelRatio;
    x.beginPath();
    x.moveTo(p.x * W, p.y * H);
    x.lineTo(p.x * W - p.l * .35, p.y * H - p.l);
    x.stroke();
    if (step) {
      p.y += p.v; p.x += p.v * .35;
      if (p.y > 1.05) { p.y = -.05; p.x = Math.random(); }
    }
  }
}

const running = () => raf !== null;
function loop() { frame(true); raf = requestAnimationFrame(loop); }
function start() { if (x && !reduce && !running()) raf = requestAnimationFrame(loop); }
function stop() { if (running()) { cancelAnimationFrame(raf); raf = null; } }

if (c && x) {
  if (reduce) {
    frame(false);
  } else {
    start();
  }
  const topEl = document.getElementById('top');
  if (topEl) {
    new IntersectionObserver(es => {
      heroVisible = es[0].isIntersecting;
      heroVisible && !document.hidden && !reduce ? start() : stop();
    }).observe(topEl);
  }
  document.addEventListener('visibilitychange', () => {
    document.hidden || !heroVisible || reduce ? stop() : start();
  });
}

reduceMotionQuery.addEventListener('change', event => {
  reduce = event.matches;
  syncSmilAnimations(reduce);
  if (reduce) {
    stop();
    frame(false);
  } else if (heroVisible && !document.hidden) {
    start();
  }
});

// ---- mobile nav ------------------------------------------------------------
const navBtn = document.getElementById('navtoggle');
const navMenu = document.getElementById('navmenu');
const mobile = () => matchMedia('(max-width:720px)').matches;
function closeNav() {
  if (!navBtn || !navMenu) return;
  navBtn.setAttribute('aria-expanded', 'false');
  if (mobile()) navMenu.hidden = true;
}
function syncNav() {
  if (!navMenu) return;
  mobile() ? closeNav() : (navMenu.hidden = false);
}
if (navBtn && navMenu) {
  syncNav();
  addEventListener('resize', syncNav);
  navBtn.addEventListener('click', () => {
    const open = navBtn.getAttribute('aria-expanded') === 'true';
    navBtn.setAttribute('aria-expanded', String(!open));
    navMenu.hidden = open;
  });
  navMenu.addEventListener('click', e => { if (e.target.tagName === 'A') closeNav(); });
  addEventListener('keydown', e => {
    if (e.key === 'Escape' && navBtn.getAttribute('aria-expanded') === 'true') {
      closeNav();
      navBtn.focus();
    }
  });
}

// ---- exploded stack after load ---------------------------------------------
const stackEl = document.getElementById('stack');
if (stackEl) {
  if (reduce) stackEl.classList.add('split');
  else setTimeout(() => stackEl.classList.add('split'), 600);
}

// ---- nav background + scroll progress --------------------------------------
const navEl = document.getElementById('nav');
const progEl = document.getElementById('prog');
function syncScroll() {
  if (navEl) navEl.classList.toggle('solid', scrollY > 40);
  if (progEl) {
    const h = document.documentElement;
    const denom = h.scrollHeight - h.clientHeight;
    const pct = denom > 0 ? Math.min(100, Math.max(0, (scrollY / denom) * 100)) : 0;
    progEl.style.width = pct + '%';
  }
}
syncScroll();
addEventListener('scroll', syncScroll, { passive: true });

// ---- reveal + counters -----------------------------------------------------
// the final value is already in the HTML and in aria-label; this only animates
// the visible text, so assistive tech never reads a partial number
const io = new IntersectionObserver(es => es.forEach(e => {
  if (!e.isIntersecting) return;
  e.target.classList.add('in');
  if (!reduce) {
    e.target.querySelectorAll('[data-n]').forEach(b => {
      const n = +b.dataset.n, final = b.textContent, t0 = performance.now();
      (function f(t) {
        const k = Math.min(1, (t - t0) / 1400);
        b.textContent = k < 1
          ? Math.round(n * (1 - Math.pow(1 - k, 3))).toLocaleString('en-US')
          : final;
        if (k < 1) requestAnimationFrame(f);
      })(t0);
    });
  }
  io.unobserve(e.target);
}), { threshold: .15 });
document.querySelectorAll('.reveal').forEach(el => io.observe(el));

// landing straight on a #hash skips past everything above the target, so those
// sections would never intersect and would sit at opacity 0 until scrolled back
function revealAbove(hash) {
  let target = null;
  try { target = hash && hash.length > 1 ? document.querySelector(hash) : null; } catch { return; }
  if (!target) return;
  const cut = target.getBoundingClientRect().top + scrollY;
  document.querySelectorAll('.reveal:not(.in)').forEach(el => {
    if (el.getBoundingClientRect().top + scrollY < cut) {
      el.classList.add('in');
      io.unobserve(el);
    }
  });
}
if (location.hash) requestAnimationFrame(() => revealAbove(location.hash));
addEventListener('hashchange', () => requestAnimationFrame(() => revealAbove(location.hash)));
