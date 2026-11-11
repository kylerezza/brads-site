// brads.io — the kinetic wall. Lacquered two-sided tiles that flip, tilt and settle.
// Render on demand: nothing runs while the wall is still. No tracking, no storage, no network.
(() => {
  "use strict";
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const dark = matchMedia("(prefers-color-scheme: dark)").matches;
  const fine = matchMedia("(hover: hover) and (pointer: fine)").matches;
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  const FLIP = reduce ? 0 : 520;
  const T = dark
    ? { plate: "#0f0d0c", tile: "#2a2622", ink: "#ece4d6", frame: "#25211d" }
    : { plate: "#e4ddd0", tile: "#efeae1", ink: "#2e2822", frame: "#e9e3d8" };

  console.log("%cbrads%c\nEvery tile on this page is drawn by hand-written code. Say hi: support@brads.io",
    "font: 600 20px ui-serif, Georgia, serif", "font: 12px system-ui");

  // ---------------------------------------------------------------- colour helpers
  const hexToRgb = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
  const shade = (h, f) => {
    const c = hexToRgb(h).map((v) => Math.round(f > 0 ? v + (255 - v) * f : v * (1 + f)));
    return "rgb(" + c.join(",") + ")";
  };
  const SHADOW = dark ? "rgba(0,0,0,0.45)" : "rgba(60,40,20,0.13)";
  const varyHex = (h, k) => {
    const n = Math.sin(k * 12.9898) * 43758.5453, f = ((n - Math.floor(n)) - 0.5) * 0.06;
    const c = hexToRgb(h).map((v) => Math.max(0, Math.min(255, Math.round(v * (1 + f)))));
    return "#" + c.map((v) => v.toString(16).padStart(2, "0")).join("");
  };
  const easeInOut = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);

  // ---------------------------------------------------------------- sprites
  const sprites = new Map();
  function sprite(color, mark, size, stitch) {
    const key = color + "|" + mark + "|" + size + "|" + (stitch || "");
    let s = sprites.get(key);
    if (s) return s;
    const px = Math.max(2, Math.round(size * dpr));
    s = document.createElement("canvas"); s.width = px; s.height = px;
    const g = s.getContext("2d"), r = Math.max(1, px * 0.12), e = Math.max(1, Math.round(px * 0.07));
    const rr = (x, y, w, h) => { g.beginPath(); g.roundRect ? g.roundRect(x, y, w, h, r) : g.rect(x, y, w, h); };
    g.fillStyle = shade(color, -0.12); rr(0, 0, px, px); g.fill();                 // bottom-right edge
    g.fillStyle = shade(color, 0.1); rr(0, 0, px - e, px - e); g.fill();           // top-left highlight
    g.fillStyle = color; rr(e * 0.6, e * 0.6, px - e * 1.6, px - e * 1.6); g.fill(); // face
    const sheen = g.createLinearGradient(0, 0, px, px);
    sheen.addColorStop(0, "rgba(255,255,255,0.10)"); sheen.addColorStop(0.5, "rgba(255,255,255,0)");
    g.fillStyle = sheen; rr(0, 0, px, px); g.fill();
    if (mark === 1) { // a two-leg cross stitch: "/" first, "\" laid over it
      const p = px * 0.22, lw = px * 0.2;
      g.lineCap = "round";
      const leg = (x1, y1, x2, y2) => {
        g.lineWidth = lw; g.strokeStyle = "rgba(40,20,10,0.25)";
        g.beginPath(); g.moveTo(x1 + lw * 0.15, y1 + lw * 0.25); g.lineTo(x2 + lw * 0.15, y2 + lw * 0.25); g.stroke();
        g.strokeStyle = stitch; g.beginPath(); g.moveTo(x1, y1); g.lineTo(x2, y2); g.stroke();
        g.lineWidth = lw * 0.3; g.strokeStyle = "rgba(255,255,255,0.35)";
        g.beginPath(); g.moveTo(x1 - lw * 0.15, y1 - lw * 0.15); g.lineTo(x2 - lw * 0.15, y2 - lw * 0.15); g.stroke();
      };
      leg(p, px - p, px - p, p); leg(p, p, px - p, px - p);
    }
    sprites.set(key, s);
    return s;
  }

  // ---------------------------------------------------------------- the wall
  class Wall {
    constructor(canvas, opts) {
      this.cv = canvas; this.g = canvas.getContext("2d");
      this.o = Object.assign({ pitch: 18, cols: 0, rows: 0, gap: 0.12, plate: T.plate }, opts);
      this.raf = 0; this.W = 0;
      this.frame = this.frame.bind(this);
      this.layout();
      if ("ResizeObserver" in window) new ResizeObserver(() => this.layout()).observe(canvas);
      if (fine && !reduce) {
        canvas.addEventListener("pointermove", (e) => this.tiltAt(e));
      }
    }
    layout() {
      const w = this.cv.clientWidth, h = this.cv.clientHeight;
      if (!w || (w === this.W && h === this.H)) return;
      const first = !this.W;
      this.W = w; this.H = h;
      const o = this.o;
      let cols = o.cols, rows = o.rows;
      if (!o.cols) { const p = w < 600 ? o.pitchPhone || 12 : o.pitch; cols = Math.floor(w / p); rows = Math.floor(h / p); }
      this.p = Math.min(w / cols, h / rows);
      this.ox = (w - cols * this.p) / 2; this.oy = (h - rows * this.p) / 2;
      const changed = cols !== this.cols || rows !== this.rows;
      this.cols = cols; this.rows = rows;
      this.cv.width = Math.round(w * dpr); this.cv.height = Math.round(h * dpr);
      if (changed || first) {
        const n = cols * rows;
        this.base = Array.from({ length: n }, (_, k) => o.vary ? varyHex(o.base || T.tile, k) : (o.base || T.tile));
        this.front = this.base.slice(); this.back = this.front.slice();
        this.fm = new Uint8Array(n); this.bm = new Uint8Array(n);
        this.fs = new Array(n).fill(""); this.bs = new Array(n).fill("");
        this.start = new Float64Array(n).fill(-1); this.tilt = new Float32Array(n);
        if (this.onLayout) this.onLayout(changed && !first);
      }
      this.draw(performance.now());
    }
    idx(i, j) { return j * this.cols + i; }
    set(k, color, mark, stitch) { // instant
      this.front[k] = this.back[k] = color; this.fm[k] = this.bm[k] = mark || 0;
      this.fs[k] = this.bs[k] = stitch || ""; this.start[k] = -1;
    }
    flip(k, color, mark, stitch, delay) {
      if (!FLIP) { this.set(k, color, mark, stitch); this.kick(); return; }
      this.back[k] = color; this.bm[k] = mark || 0; this.bs[k] = stitch || "";
      this.start[k] = performance.now() + (delay || 0);
      this.kick();
    }
    cellAt(e) {
      const r = this.cv.getBoundingClientRect();
      const i = Math.floor((e.clientX - r.left - this.ox) / this.p), j = Math.floor((e.clientY - r.top - this.oy) / this.p);
      return i >= 0 && j >= 0 && i < this.cols && j < this.rows ? { i, j, k: this.idx(i, j) } : null;
    }
    tiltAt(e) {
      const c = this.cellAt(e); if (!c) return;
      const R = 2.6;
      for (let dj = -3; dj <= 3; dj++) for (let di = -3; di <= 3; di++) {
        const i = c.i + di, j = c.j + dj;
        if (i < 0 || j < 0 || i >= this.cols || j >= this.rows) continue;
        const d = Math.hypot(di, dj); if (d > R) continue;
        const k = this.idx(i, j), v = 0.85 * (1 - d / R);
        if (v > this.tilt[k]) this.tilt[k] = v;
      }
      this.kick();
    }
    kick() { if (!this.raf) this.raf = requestAnimationFrame(this.frame); }
    frame(now) { this.raf = 0; if (this.draw(now)) this.kick(); }
    draw(now) {
      const g = this.g, p = this.p, size = p * (1 - this.o.gap), pad = (p - size) / 2;
      g.setTransform(dpr, 0, 0, dpr, 0, 0);
      g.fillStyle = this.o.plate; g.fillRect(0, 0, this.W, this.H);
      let busy = false;
      for (let j = 0; j < this.rows; j++) for (let i = 0; i < this.cols; i++) {
        const k = j * this.cols + i;
        let sc = 1, col = this.front[k], mk = this.fm[k], st = this.fs[k], shadeAmt = 0;
        const s0 = this.start[k];
        if (s0 >= 0) {
          if (now >= s0) {
            const t = Math.min(1, (now - s0) / FLIP), a = easeInOut(t) * Math.PI;
            sc = Math.abs(Math.cos(a)); shadeAmt = 1 - sc;
            if (a > Math.PI / 2) { col = this.back[k]; mk = this.bm[k]; st = this.bs[k]; }
            if (t >= 1) { this.front[k] = this.back[k]; this.fm[k] = this.bm[k]; this.fs[k] = this.bs[k]; this.start[k] = -1; sc = 1; shadeAmt = 0; }
          }
          busy = true;
        }
        const tl = this.tilt[k];
        if (tl > 0.01) { sc *= Math.cos(tl); shadeAmt = Math.max(shadeAmt, tl * 0.35); this.tilt[k] = tl * 0.86; busy = true; }
        else if (tl) this.tilt[k] = 0;
        const x = this.ox + i * p + pad, y = this.oy + j * p + pad, h = size * Math.max(0.04, sc);
        g.fillStyle = sc < 1 ? "rgba(0,0,0,0.2)" : SHADOW;
        g.fillRect(x + 1, y + (size - h) / 2 + Math.max(1.5, p * 0.1), size, h);
        g.drawImage(sprite(col, mk, Math.round(size * 2) / 2, st), x, y + (size - h) / 2, size, h);
        if (shadeAmt > 0.02) { g.fillStyle = "rgba(0,0,0," + (shadeAmt * 0.35).toFixed(3) + ")"; g.fillRect(x, y + (size - h) / 2, size, h); }
      }
      return busy;
    }
  }

  const observers = []; // keep references so the browser never collects a waiting observer
  const onScreen = (el, fn, threshold) => {
    if (!("IntersectionObserver" in window)) return fn();
    const io = new IntersectionObserver((es) => {
      if (es.some((x) => x.isIntersecting)) { io.disconnect(); fn(); }
    }, { threshold: threshold || 0.2 });
    observers.push(io);
    io.observe(el);
  };

  // ---------------------------------------------------------------- hero: the wordmark wall
  const GLYPHS = {
    b: ["10000", "10000", "11110", "10001", "10001", "10001", "11110"],
    r: ["00000", "00000", "10110", "11001", "10000", "10000", "10000"],
    a: ["00000", "00000", "01110", "00001", "01111", "10001", "01111"],
    d: ["00001", "00001", "01111", "10001", "10001", "10001", "01111"],
    s: ["00000", "00000", "01111", "10000", "01110", "00001", "11110"],
  };
  const palettes = JSON.parse((document.getElementById("palettes") || {}).textContent || "[]");
  const accents = palettes.flat().length ? palettes.flat() : ["#b5525e", "#c9a27c"];

  const heroCv = document.querySelector("[data-wall=hero]");
  if (heroCv) {
    const wall = new Wall(heroCv, { pitch: 18, pitchPhone: 11, vary: true });
    let word = new Set();
    const placeWord = () => {
      word = new Set();
      const sc = Math.max(1, Math.min(3, Math.floor((wall.cols - 4) / 29)));
      const w = 29 * sc, h = 7 * sc;
      const x0 = Math.floor((wall.cols - w) / 2), y0 = Math.max(1, Math.floor((wall.rows - h) / 2) - 1);
      "brads".split("").forEach((ch, n) => {
        GLYPHS[ch].forEach((row, gy) => row.split("").forEach((bit, gx) => {
          if (bit !== "1") return;
          for (let sy = 0; sy < sc; sy++) for (let sx = 0; sx < sc; sx++) {
            const i = x0 + (n * 6 + gx) * sc + sx, j = y0 + gy * sc + sy;
            if (i < wall.cols && j < wall.rows) word.add(wall.idx(i, j));
          }
        }));
      });
    };
    const quilt = (i, j) => {
      const band = Math.floor((i * 0.55 + j + Math.sin(i * 0.35) * 2) / 3);
      return accents[((band % accents.length) + accents.length + ((i * 5 + j * 3) % 3 === 0 ? 1 : 0)) % accents.length];
    };
    const build = (instant) => {
      placeWord();
      for (let k = 0; k < wall.cols * wall.rows; k++) {
        const i = k % wall.cols, j = (k / wall.cols) | 0, target = word.has(k) ? T.ink : wall.base[k];
        if (instant || reduce) { wall.set(k, target); continue; }
        wall.set(k, quilt(i, j));
        wall.flip(k, target, 0, "", 700 + i * 22 + j * 14 + ((i * 7 + j * 11) % 5) * 12);
      }
      wall.kick();
    };
    wall.onLayout = (resized) => { if (resized) build(true); };
    build(false);

    // A tap sends one calm wave of colour across the wall, then the tiles turn back.
    heroCv.addEventListener("click", (e) => {
      const c = wall.cellAt(e); if (!c) return;
      const step = 34, maxD = Math.hypot(wall.cols, wall.rows);
      for (let j = 0; j < wall.rows; j++) for (let i = 0; i < wall.cols; i++) {
        const k = wall.idx(i, j), d = Math.hypot(i - c.i, j - c.j);
        if (d > maxD * 0.55) continue;
        const keep = word.has(k) ? T.ink : wall.base[k];
        const tint = word.has(k) ? T.ink : accents[(i * 7 + j * 13) % accents.length];
        if (!word.has(k)) {
          wall.flip(k, tint, 0, "", d * step);
          setTimeout(() => wall.flip(k, keep, 0, "", 0), d * step + 1500 + (reduce ? 0 : 0));
        }
      }
    });
  }

  // ---------------------------------------------------------------- one scene per app
  const SCENES = {
    // Stitchwell: a hoop on cloth with a stitched heart. Tapping the cloth inside the hoop lays a stitch.
    stitchwell(cols, rows, pal) {
      const [rose, madder, linen, wood, linen2, dark] = pal;
      const cx = (cols - 1) / 2, cy = (rows - 1) / 2 + 0.5, R = Math.min(cols, rows) * 0.44;
      const out = [];
      for (let j = 0; j < rows; j++) for (let i = 0; i < cols; i++) {
        const d = Math.hypot(i - cx, j - cy);
        let t = { c: (i + j) % 2 ? linen2 : shadeHex(linen2, -0.03), m: 0, s: "", canStitch: false };
        if (d < R - 1) {
          t = { c: linen, m: 0, s: "", canStitch: true };
          const x = (i - cx) / (R * 0.62), y = -(j - cy) / (R * 0.62) + 0.15;
          if ((x * x + y * y - 1) ** 3 - x * x * y ** 3 <= 0) t = { c: linen, m: 1, s: y - x * 0.4 > 0.5 ? rose : madder, canStitch: false };
        } else if (d < R + 0.6) t = { c: wood, m: 0, s: "" };
        if (Math.abs(i - cx) < 1 && j < cy - R + 0.2 && j >= cy - R - 1.6) t = { c: dark, m: 0, s: "" };
        out.push(t);
      }
      return { tiles: out, action: "stitch", stitch: madder };
    },
  };
  function shadeHex(h, f) { const c = hexToRgb(h).map((v) => Math.max(0, Math.min(255, Math.round(v * (1 + f))))); return "#" + c.map((v) => v.toString(16).padStart(2, "0")).join(""); }
  // Any app without a hand-made scene gets a calm woven gradient through its palette.
  function generic(cols, rows, pal) {
    const out = [];
    for (let j = 0; j < rows; j++) for (let i = 0; i < cols; i++) {
      const t = (i / cols) * 0.7 + (j / rows) * 0.3 + Math.sin(i * 0.5 + j * 0.3) * 0.05;
      const n = Math.min(pal.length - 1, Math.max(0, Math.floor(t * pal.length + ((i * 31 + j * 17) % 7) / 14 - 0.25)));
      out.push({ c: pal[n], m: 0, s: "" });
    }
    return { tiles: out, action: "flip" };
  }

  document.querySelectorAll("[data-wall=scene]").forEach((cv) => {
    const slug = cv.dataset.slug, pal = JSON.parse(cv.dataset.palette);
    const cols = 40, rows = 28;
    const wall = new Wall(cv, { cols, rows, base: T.frame });
    const make = SCENES[slug] || generic;
    const scene = make(cols, rows, pal);
    const counter = document.querySelector('[data-count-for="' + slug + '"]');
    let placed = 0;
    onScreen(cv, () => {
      scene.tiles.forEach((t, k) => {
        const i = k % cols, j = (k / cols) | 0;
        wall.flip(k, t.c, t.m, t.s, 100 + (i + j) * 18 + ((i * 7 + j * 3) % 5) * 10);
      });
    });
    cv.addEventListener("click", (e) => {
      const c = wall.cellAt(e); if (!c) return;
      const t = scene.tiles[c.k];
      if (scene.action === "stitch" && t.canStitch) {
        t.canStitch = false; t.m = 1; t.s = scene.stitch;
        wall.flip(c.k, t.c, 1, scene.stitch, 0);
        placed++;
        if (counter) { counter.hidden = false; counter.querySelector("b").textContent = placed; }
      } else {
        wall.flip(c.k, wall.front[c.k], wall.fm[c.k], wall.fs[c.k], 0);
      }
    });
  });

  // ---------------------------------------------------------------- still on the frame
  const frameCv = document.querySelector("[data-wall=frame]");
  if (frameCv) {
    const wall = new Wall(frameCv, { pitch: 22, pitchPhone: 16, base: T.tile, vary: true });
    frameCv.addEventListener("click", (e) => {
      const c = wall.cellAt(e); if (!c) return;
      for (let j = 0; j < wall.rows; j++) for (let i = 0; i < wall.cols; i++) {
        const d = Math.hypot(i - c.i, j - c.j);
        if (d < 6) { const k = wall.idx(i, j); wall.flip(k, wall.base[k], 0, "", d * 60); }
      }
    });
  }
})();
