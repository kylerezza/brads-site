// brads.io home page: the living hoop and the photo-to-pattern studio. No tracking, no storage, no network.
(() => {
  "use strict";
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const dark = matchMedia("(prefers-color-scheme: dark)").matches;
  const coarse = matchMedia("(pointer: coarse)").matches;
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  const LINEN = dark ? "#2b2a28" : "#f1eadc";
  const HOLES = dark ? "#3a3835" : "#d5cbb8";

  console.log("%cHello, fellow maker.%c\nThis page was stitched by hand. Say hi: support@brads.io",
    "font: italic 18px Georgia, serif; color: #9a3b48", "font: 12px system-ui");

  // ---------------------------------------------------------------- running-stitch seams
  const seams = document.querySelectorAll(".seam.sew");
  if ("IntersectionObserver" in window && !reduce) {
    const io = new IntersectionObserver((entries) => {
      for (const e of entries) if (e.isIntersecting) { e.target.classList.add("sewn"); io.unobserve(e.target); }
    }, { threshold: 1 });
    seams.forEach((s) => io.observe(s));
  } else seams.forEach((s) => s.classList.add("sewn"));

  // ---------------------------------------------------------------- one cross stitch
  // "/" first, then "\" laid over it, the way stitchers do it. t = 0..1 draws both legs in turn.
  function drawX(ctx, x, y, s, color, t) {
    const p = s * 0.18, lw = s * 0.26;
    const legs = [[x + p, y + s - p, x + s - p, y + p], [x + p, y + p, x + s - p, y + s - p]];
    ctx.lineCap = "round";
    for (let i = 0; i < 2; i++) {
      const k = Math.min(1, Math.max(0, t * 2 - i));
      if (k <= 0) break;
      const [x1, y1, x2, y2] = legs[i];
      const ex = x1 + (x2 - x1) * k, ey = y1 + (y2 - y1) * k;
      ctx.lineWidth = lw;
      ctx.strokeStyle = "rgba(40,20,10,0.22)";
      ctx.beginPath(); ctx.moveTo(x1 + lw * 0.1, y1 + lw * 0.2); ctx.lineTo(ex + lw * 0.1, ey + lw * 0.2); ctx.stroke();
      ctx.strokeStyle = color;
      ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(ex, ey); ctx.stroke();
      ctx.lineWidth = lw * 0.3;
      ctx.strokeStyle = "rgba(255,255,255,0.33)";
      ctx.beginPath(); ctx.moveTo(x1 - lw * 0.14, y1 - lw * 0.14); ctx.lineTo(ex - lw * 0.14, ey - lw * 0.14); ctx.stroke();
    }
  }

  function fabric(ctx, w, h, s, cols, rows, cream) {
    ctx.fillStyle = cream ? "#f1eadc" : LINEN; ctx.fillRect(0, 0, w, h);
    ctx.fillStyle = cream ? "#d5cbb8" : HOLES;
    const r = Math.max(0.7, s * 0.07);
    for (let j = 0; j <= rows; j++) for (let i = 0; i <= cols; i++) {
      ctx.beginPath(); ctx.arc(i * s, j * s, r, 0, 6.2832); ctx.fill();
    }
  }

  function sizeCanvas(cv, w, h) {
    cv.width = Math.round(w * dpr); cv.height = Math.round(h * dpr);
    const ctx = cv.getContext("2d"); ctx.setTransform(dpr, 0, 0, dpr, 0, 0); return ctx;
  }

  // ---------------------------------------------------------------- the living hoop
  const hoop = document.querySelector("[data-hoop]");
  if (hoop) initHoop(hoop);

  function initHoop(root) {
    const cloth = root.querySelector(".cloth");
    const top = cloth.querySelector("canvas");
    const base = document.createElement("canvas");
    base.setAttribute("aria-hidden", "true");
    cloth.insertBefore(base, top);
    const countEl = root.querySelector("[data-count]");
    const totalEl = root.querySelector("[data-total]");
    const mineEl = root.querySelector("[data-mine]");
    const hint = root.querySelector(".hint");

    const N = 31;
    const tones = dark ? ["#fbd9dd", "#efa2ac", "#b9606f"] : ["#c06272", "#9a3b48", "#74293a"];
    const tone = new Int8Array(N * N).fill(-1);
    const inHeart = (i, j) => {
      const x = ((i + 0.5) / N) * 3.5 - 1.75, y = 1.62 - ((j + 0.5) / N) * 3.45;
      return (x * x + y * y - 1) ** 3 - x * x * y ** 3 <= 0;
    };
    for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) {
      if (!inHeart(i, j)) continue;
      const edge = !inHeart(i - 1, j) || !inHeart(i + 1, j) || !inHeart(i, j - 1) || !inHeart(i, j + 1);
      const x = ((i + 0.5) / N) * 3.5 - 1.75, y = 1.62 - ((j + 0.5) / N) * 3.45;
      const light = -x * 0.55 + y * 0.8;
      tone[j * N + i] = edge ? 2 : light > 0.62 ? 0 : light < -0.75 ? 2 : 1;
    }
    const order = [];
    for (let k = 0; k < N * N; k++) if (tone[k] >= 0) order.push(k);
    order.sort((a, b) => ((a % N) + ((a / N) | 0)) - ((b % N) + ((b / N) | 0)) || a - b);
    const total = order.length;
    totalEl.textContent = total;

    const done = new Uint8Array(N * N);
    let count = 0, mine = 0, anims = [], raf = 0, W = 0, s = 0, ctx = null;
    let introIdx = 0, introCount = 0, introStart = 0, finishing = false, finished = false, touched = false;

    function layout() {
      const w = cloth.clientWidth;
      if (!w || w === W) return;
      W = w; s = W / N;
      const bctx = sizeCanvas(base, W, W);
      fabric(bctx, W, W, s, N, N);
      bctx.globalAlpha = dark ? 0.2 : 0.14;
      for (const k of order) {
        bctx.fillStyle = tones[tone[k]];
        bctx.beginPath(); bctx.arc((k % N) * s + s / 2, ((k / N) | 0) * s + s / 2, s * 0.22, 0, 6.2832); bctx.fill();
      }
      bctx.globalAlpha = 1;
      ctx = sizeCanvas(top, W, W);
      for (const k of order) if (done[k]) drawX(ctx, (k % N) * s, ((k / N) | 0) * s, s, tones[tone[k]], 1);
    }

    function status() {
      countEl.textContent = count;
      if (mineEl) mineEl.textContent = mine;
    }

    function stitch(k, delay, byHand) {
      if (tone[k] < 0 || done[k]) return;
      done[k] = 1; count++;
      if (byHand) mine++;
      if (reduce) drawX(ctx, (k % N) * s, ((k / N) | 0) * s, s, tones[tone[k]], 1);
      else anims.push({ k, start: performance.now() + (delay || 0) });
      status();
      if (!finishing && count >= total * 0.85) finishRest(600);
      if (count === total && reduce) markFinished();
      loop();
    }

    function finishRest(ms) {
      if (finishing) return;
      finishing = true; introIdx = introCount;
      const rest = order.filter((k) => !done[k]);
      rest.forEach((k, n) => stitch(k, reduce ? 0 : (n / Math.max(1, rest.length)) * ms, false));
      if (!rest.length) markFinished();
    }

    function markFinished() {
      if (finished) return;
      finished = true;
      hint.classList.remove("show");
      root.classList.add("finished");
    }

    function loop() {
      if (!raf && !reduce) raf = requestAnimationFrame(frame);
    }

    function frame(now) {
      raf = 0;
      while (introIdx < introCount && now >= introStart + introIdx * 8) stitch(order[introIdx++], 0, false);
      const keep = [];
      for (const a of anims) {
        const t = (now - a.start) / 120;
        if (t < 0) { keep.push(a); continue; }
        const x = (a.k % N) * s, y = ((a.k / N) | 0) * s;
        ctx.clearRect(x, y, s, s);
        drawX(ctx, x, y, s, tones[tone[a.k]], Math.min(1, t));
        if (t < 1) keep.push(a);
      }
      anims = keep;
      if (finishing && !anims.length && count === total) markFinished();
      if (anims.length || introIdx < introCount) loop();
    }

    function start() {
      done.fill(0); count = 0; mine = 0; anims = []; finishing = false; finished = false;
      root.classList.remove("finished");
      if (ctx) ctx.clearRect(0, 0, W, W);
      status();
      if (reduce) { order.forEach((k) => stitch(k, 0, false)); return; }
      introCount = Math.round(total * 0.55); introIdx = 0; introStart = performance.now() + 400;
      loop();
    }

    // pointer: mouse stitches on hover; touch and pen stitch while pressed. Vertical swipes still scroll (touch-action: pan-y).
    let down = false, last = null;
    const r = coarse ? 2 : 1;
    function at(px, py) {
      const ci = Math.floor(px / s), cj = Math.floor(py / s);
      for (let dj = -r; dj <= r; dj++) for (let di = -r; di <= r; di++) {
        if (di * di + dj * dj > r * r + 1) continue;
        const i = ci + di, j = cj + dj;
        if (i >= 0 && j >= 0 && i < N && j < N) stitch(j * N + i, 0, true);
      }
    }
    function trail(e) {
      const rect = top.getBoundingClientRect();
      const pts = e.getCoalescedEvents ? e.getCoalescedEvents() : [e];
      for (const p of pts.length ? pts : [e]) {
        const x = p.clientX - rect.left, y = p.clientY - rect.top;
        if (last) {
          const d = Math.hypot(x - last.x, y - last.y), steps = Math.ceil(d / (s * 0.5));
          for (let n = 1; n <= steps; n++) at(last.x + ((x - last.x) * n) / steps, last.y + ((y - last.y) * n) / steps);
        } else at(x, y);
        last = { x, y };
      }
    }
    function interact() {
      if (!touched) { touched = true; introIdx = introCount; hint.classList.remove("show"); }
    }
    top.addEventListener("pointerdown", (e) => {
      interact(); down = true; last = null;
      try { top.setPointerCapture(e.pointerId); } catch (_) {}
      trail(e);
    });
    top.addEventListener("pointermove", (e) => {
      if (down || e.pointerType === "mouse") { if (!down) interact(); trail(e); }
    });
    const lift = () => { down = false; last = null; };
    top.addEventListener("pointerup", lift);
    top.addEventListener("pointercancel", lift);
    top.addEventListener("pointerleave", () => { if (!down) last = null; });

    root.querySelector("#finish").addEventListener("click", () => { interact(); finishRest(600); });
    root.querySelector("#again").addEventListener("click", () => { start(); });

    function hintLater() { setTimeout(() => {
      if (!touched && !finished) {
        hint.textContent = coarse ? "Swipe sideways across the cloth to stitch" : "Move across the cloth to stitch";
        hint.classList.add("show");
      }
    }, 3500); }

    layout();
    if ("ResizeObserver" in window) new ResizeObserver(layout).observe(cloth);
    // Begin the intro only once the hoop is on screen (on phones it starts below the fold).
    status();
    if (reduce || !("IntersectionObserver" in window)) { start(); hintLater(); }
    else {
      const seen = new IntersectionObserver((es) => {
        if (es[0].isIntersecting) { seen.disconnect(); if (!count) start(); hintLater(); }
      }, { threshold: 0.35 });
      seen.observe(cloth);
    }
  }

  // ---------------------------------------------------------------- photo → pattern studio
  const studio = document.querySelector("[data-studio]");
  if (studio) initStudio(studio);

  function scene() {
    const c = document.createElement("canvas"); c.width = 480; c.height = 360;
    const g = c.getContext("2d");
    const sky = g.createLinearGradient(0, 0, 0, 260);
    sky.addColorStop(0, "#f2b46d"); sky.addColorStop(0.55, "#e7826a"); sky.addColorStop(1, "#b2566b");
    g.fillStyle = sky; g.fillRect(0, 0, 480, 360);
    g.fillStyle = "#fbe6b2"; g.beginPath(); g.arc(320, 170, 48, 0, 6.3); g.fill();
    const hill = (col, y0, amp, ph) => {
      g.fillStyle = col; g.beginPath(); g.moveTo(0, 360);
      for (let x = 0; x <= 480; x += 8) g.lineTo(x, y0 + Math.sin(x / 70 + ph) * amp + Math.sin(x / 23 + ph * 2) * amp * 0.25);
      g.lineTo(480, 360); g.fill();
    };
    hill("#8a5f86", 215, 18, 1.2);
    hill("#5d7d6c", 255, 14, 3.1);
    hill("#355446", 300, 10, 0.4);
    g.fillStyle = "#24382f"; g.fillRect(118, 228, 8, 50);
    g.beginPath(); g.arc(122, 214, 30, 0, 6.3); g.fill();
    g.strokeStyle = "#6b2f40"; g.lineWidth = 4; g.lineCap = "round";
    for (const [bx, by] of [[200, 90], [236, 110], [176, 120]]) {
      g.beginPath(); g.moveTo(bx - 12, by - 6); g.quadraticCurveTo(bx - 4, by - 9, bx, by); g.quadraticCurveTo(bx + 4, by - 9, bx + 12, by - 6); g.stroke();
    }
    return c;
  }

  function kmeans(px, n, K) {
    // px: Float32Array rgb triples. Farthest-point init, then a few Lloyd rounds. Deterministic.
    const d2 = (a, b, c, i) => { const dr = a - px[i], dg = b - px[i + 1], db = c - px[i + 2]; return 2 * dr * dr + 4 * dg * dg + 3 * db * db; };
    const cen = [];
    let mr = 0, mg = 0, mb = 0;
    for (let i = 0; i < n * 3; i += 3) { mr += px[i]; mg += px[i + 1]; mb += px[i + 2]; }
    cen.push([mr / n, mg / n, mb / n]);
    const best = new Float32Array(n).fill(Infinity);
    while (cen.length < K) {
      const c = cen[cen.length - 1];
      let far = 0, fi = 0;
      for (let p = 0; p < n; p++) { const v = d2(c[0], c[1], c[2], p * 3); if (v < best[p]) best[p] = v; if (best[p] > far) { far = best[p]; fi = p; } }
      if (far < 30) break;
      cen.push([px[fi * 3], px[fi * 3 + 1], px[fi * 3 + 2]]);
    }
    const lab = new Uint8Array(n);
    for (let it = 0; it < 8; it++) {
      const sum = cen.map(() => [0, 0, 0, 0]);
      for (let p = 0; p < n; p++) {
        let bi = 0, bv = Infinity;
        for (let c = 0; c < cen.length; c++) { const v = d2(cen[c][0], cen[c][1], cen[c][2], p * 3); if (v < bv) { bv = v; bi = c; } }
        lab[p] = bi; const sm = sum[bi]; sm[0] += px[p * 3]; sm[1] += px[p * 3 + 1]; sm[2] += px[p * 3 + 2]; sm[3]++;
      }
      sum.forEach((sm, c) => { if (sm[3]) cen[c] = [sm[0] / sm[3], sm[1] / sm[3], sm[2] / sm[3]]; });
    }
    return { cen, lab };
  }

  function initStudio(root) {
    const frameEl = root.querySelector(".studio-frame");
    const cv = frameEl.querySelector("canvas");
    const range = root.querySelector("input[type=range]");
    const out = root.querySelector("output");
    const file = root.querySelector("input[type=file]");
    const list = root.querySelector(".swatches");
    const save = root.querySelector("[data-save]");
    let src = scene(), pending = 0, sweep = 0;

    function render(animate) {
      const cols = +range.value, rows = Math.round((cols * 3) / 4);
      out.textContent = cols + " × " + rows;
      const W = frameEl.clientWidth, H = (W * 3) / 4, s = W / cols;
      const small = document.createElement("canvas"); small.width = cols; small.height = rows;
      const sg = small.getContext("2d", { willReadFrequently: true });
      sg.imageSmoothingQuality = "high";
      const sw = src.width, sh = src.height, want = cols / rows;
      let cw = sw, ch = sh;
      if (sw / sh > want) cw = sh * want; else ch = sw / want;
      sg.drawImage(src, (sw - cw) / 2, (sh - ch) / 2, cw, ch, 0, 0, cols, rows);
      const data = sg.getImageData(0, 0, cols, rows).data, n = cols * rows;
      const px = new Float32Array(n * 3);
      for (let p = 0; p < n; p++) { px[p * 3] = data[p * 4]; px[p * 3 + 1] = data[p * 4 + 1]; px[p * 3 + 2] = data[p * 4 + 2]; }
      const { cen, lab } = kmeans(px, n, 12);
      const hex = cen.map((c) => "#" + c.map((v) => Math.round(v).toString(16).padStart(2, "0")).join(""));
      const cloth = [241, 234, 220];
      const bare = cen.map((c) => Math.hypot(c[0] - cloth[0], c[1] - cloth[1], c[2] - cloth[2]) < 26);
      const counts = cen.map(() => 0);
      for (let p = 0; p < n; p++) if (!bare[lab[p]]) counts[lab[p]]++;

      list.innerHTML = "";
      cen.map((_, c) => c).filter((c) => counts[c]).sort((a, b) => counts[b] - counts[a]).forEach((c) => {
        const li = document.createElement("li");
        li.innerHTML = '<i style="background:' + hex[c] + '"></i>' + counts[c].toLocaleString();
        li.title = hex[c];
        list.appendChild(li);
      });

      const ctx = sizeCanvas(cv, W, H);
      fabric(ctx, W, H, s, cols, rows, true);
      const draw = (from, to) => {
        for (let p = from; p < to; p++) {
          const k = byDiag[p];
          if (!bare[lab[k]]) drawX(ctx, (k % cols) * s, ((k / cols) | 0) * s, s, hex[lab[k]], 1);
        }
      };
      const byDiag = Array.from({ length: n }, (_, k) => k).sort((a, b) => ((a % cols) + ((a / cols) | 0)) - ((b % cols) + ((b / cols) | 0)));
      cancelAnimationFrame(sweep);
      if (!animate || reduce) { draw(0, n); return; }
      const t0 = performance.now(); let doneTo = 0;
      const step = (now) => {
        const to = Math.min(n, Math.round(((now - t0) / 900) * n));
        draw(doneTo, to); doneTo = to;
        if (to < n) sweep = requestAnimationFrame(step);
      };
      sweep = requestAnimationFrame(step);
    }

    function useFile(f) {
      if (!f || !/^image\//.test(f.type)) return;
      const url = URL.createObjectURL(f), img = new Image();
      img.onload = () => {
        const c = document.createElement("canvas"), m = Math.min(1, 640 / Math.max(img.width, img.height));
        c.width = Math.max(1, Math.round(img.width * m)); c.height = Math.max(1, Math.round(img.height * m));
        c.getContext("2d").drawImage(img, 0, 0, c.width, c.height);
        URL.revokeObjectURL(url); src = c; render(true);
      };
      img.src = url;
    }

    range.addEventListener("input", () => { cancelAnimationFrame(pending); pending = requestAnimationFrame(() => render(false)); });
    file.addEventListener("change", () => useFile(file.files[0]));
    ["dragenter", "dragover"].forEach((t) => frameEl.addEventListener(t, (e) => { e.preventDefault(); frameEl.classList.add("over"); }));
    ["dragleave", "drop"].forEach((t) => frameEl.addEventListener(t, (e) => { e.preventDefault(); frameEl.classList.remove("over"); }));
    frameEl.addEventListener("drop", (e) => useFile(e.dataTransfer.files[0]));
    save.addEventListener("click", () => {
      cv.toBlob((b) => {
        const a = document.createElement("a");
        a.href = URL.createObjectURL(b); a.download = "my-cross-stitch.png";
        document.body.appendChild(a); a.click(); a.remove();
        setTimeout(() => URL.revokeObjectURL(a.href), 4000);
      });
    });

    let lastW = 0, seen = false;
    const go = () => { const w = frameEl.clientWidth; if (w && w !== lastW) { lastW = w; render(false); } };
    if ("IntersectionObserver" in window) {
      new IntersectionObserver((es, o) => {
        if (es[0].isIntersecting && !seen) { seen = true; lastW = frameEl.clientWidth; render(true); o.disconnect(); }
      }, { threshold: 0.3 }).observe(frameEl);
    } else { seen = true; go(); }
    if ("ResizeObserver" in window) new ResizeObserver(() => { if (seen) go(); }).observe(frameEl);
  }
})();
