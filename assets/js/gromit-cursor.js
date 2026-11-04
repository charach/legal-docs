/* 마우스 포인터: 그로밋 GIF가 따라온다 — 크리스마스 여행 페이지(travel/christmas_2026.html)와 충북 여행 페이지(travel/chungbuk_nov.html) 전용.
   브라우저는 움직이는 커서 파일을 지원하지 않아서 실제 커서를 숨기고 GIF를 따라오게 만든다.
   정확한 위치는 점으로 표시하고(색은 페이지의 --accent), 움직이면 달리는 그로밋, 멈추면 책 읽는 그로밋이 된다.
   터치 기기 · 동작 줄이기 설정에서는 쓰지 않는다(그러면 gromit.css의 정적 커서가 그대로 보인다). GIF는 Tenor 핫링크. */
(function () {
  var mq = function (q) { return window.matchMedia && window.matchMedia(q).matches; };
  if (mq('(pointer: coarse)') || mq('(prefers-reduced-motion: reduce)') || !mq('(hover: hover)')) return;
  var RUN = 'https://media.tenor.com/e546XteiF08AAAAM/aardman-gromit.gif';
  var IDLE = 'https://media.tenor.com/CbKp4SBzTr0AAAAM/wallace-and-gromit-gromit.gif';
  var st = document.createElement('style');
  st.textContent =
    '.gcur-on, .gcur-on * { cursor: none !important; }' +
    '#gcur { position: fixed; left: 0; top: 0; width: 0; height: 0; z-index: 2147483000; pointer-events: none; will-change: transform; opacity: 0; transition: opacity .2s ease; }' +
    '#gcur.on { opacity: 1; }' +
    '#gcur .bx { position: absolute; left: 16px; top: 12px; width: 124px; transition: transform .15s ease; transform-origin: 50% 60%; }' +
    '#gcur img { display: none; width: 124px; height: auto; border-radius: 10px; border: 3px solid #FFF8EF; background: #fff; box-shadow: 0 6px 14px rgba(0,0,0,.3); }' +
    '#gcur.run .gr, #gcur:not(.run) .gi { display: block; }' +
    '#gcur .dot { position: absolute; left: -5px; top: -5px; width: 10px; height: 10px; border-radius: 50%; background: var(--accent, #C1272D); box-shadow: 0 0 0 2px #fff, 0 0 8px 2px rgba(0,0,0,.35); }';
  document.head.appendChild(st);
  var el = document.createElement('div');
  el.id = 'gcur'; el.setAttribute('aria-hidden', 'true');
  el.innerHTML = '<div class="bx"><img class="gr" src="' + RUN + '" alt=""><img class="gi" src="' + IDLE + '" alt=""></div><span class="dot"></span>';
  document.body.appendChild(el);
  var bx = el.firstChild, tx = -100, ty = -100, x = -100, y = -100, dir = 1, lastMove = 0, started = false, press = false;
  document.addEventListener('mousemove', function (e) {
    tx = e.clientX; ty = e.clientY; lastMove = performance.now();
    if (!started) { started = true; x = tx; y = ty; document.documentElement.classList.add('gcur-on'); el.classList.add('on'); }
  });
  document.addEventListener('mouseleave', function () { el.classList.remove('on'); });
  document.addEventListener('mouseenter', function () { if (started) el.classList.add('on'); });
  document.addEventListener('mousedown', function () { press = true; });
  document.addEventListener('mouseup', function () { press = false; });
  (function loop() {
    var dx = tx - x, dy = ty - y; x += dx * .34; y += dy * .34;
    var sp = Math.sqrt(dx * dx + dy * dy);
    if (Math.abs(dx) > 3) dir = dx > 0 ? -1 : 1;           // 그림 속 그로밋은 왼쪽을 본다
    var run = sp > 2.2 || (performance.now() - lastMove < 120 && sp > .6);
    el.classList.toggle('run', run);
    el.style.transform = 'translate3d(' + x + 'px,' + y + 'px,0)';
    var tilt = run ? Math.max(-14, Math.min(14, dy * .5)) * (dir < 0 ? 1 : -1) : 0;
    bx.style.transform = 'scaleX(' + dir + ') rotate(' + tilt + 'deg)' + (press ? ' scale(.85)' : '');
    requestAnimationFrame(loop);
  })();
})();
