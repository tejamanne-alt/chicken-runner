// Renderer, game flow, input and page wiring for the preview.
let PIECES = {};
const HAZE = [250, 195, 139];
const ZONE_NAMES = ['The lane', 'Fields and canal', 'Terraces and market'];

const view = document.getElementById('view');
const ctx = view.getContext('2d');
const ground = document.createElement('canvas');
const gctx = ground.getContext('2d');
const overlay = document.getElementById('overlay');
const statusEl = document.getElementById('status');

let DATA = null;
const images = new Map();
function image(path) {
  let im = images.get(path);
  if (!im) { im = new Image(); im.decoding = 'async'; im.src = path; images.set(path, im); }
  return im;
}
// Every picture lives on a sprite sheet: [sheet, x, y, width, height].
const sprites = new Map();
function sprite(name) {
  let sp = sprites.get(name);
  if (!sp) {
    const s = DATA.sprites[name];
    sp = { img: image('sheets/' + DATA.sheets[s[0]].file), x: s[1], y: s[2], w: s[3], h: s[4] };
    sprites.set(name, sp);
  }
  return sp;
}
const sheetsOf = group => DATA.sheets.filter(s => s.group === group).map(s => 'sheets/' + s.file);
function loadAll(names, onProgress) {
  const list = [...new Set(names)].map(image);
  let done = 0;
  return Promise.all(list.map(im => (im.complete && im.naturalWidth ? Promise.resolve() : new Promise(res => { im.onload = im.onerror = res; }))
    .then(() => onProgress(++done, list.length))));
}

// ------------------------------------------------------------------ game state
const game = { level: 0, mode: window.CR_DEFAULT_MODE || 'watch', state: 'loading', stateT: 0, acc: 0, course: null, kid: null, rooster: null, t: null,
  stats: null, barks: [], debris: [], auto: null, cam: { dist: 0, dv: 0, h: 0, hv: 0 }, nextIn: 0, loadedZones: new Set() };

const events = {
  jumped() { dust(game.kid.x, game.kid.y, 3); },
  landed() { dust(game.kid.x, game.kid.y, 4); game.kidFx.squash = 0.2; game.kidFx.land = 0.12; },
  vaulted() {},
  bounced(b) { if (b.bark) bark(b.bark, (b.x0 + b.x1) / 2, b.y1 + 0.7, '#2f8f4a'); game.kidFx.squash = -0.3; },
  collected(p) {
    if (p.kind === 'mango') game.stats.mangoes++;
    if (p.kind === 'chilli') bark('CHILLI! +' + Math.round(game.t.kidRunSpeed * game.t.boostSpeedBonus * game.t.boostDuration) + ' m', game.kid.x, game.kid.y + 1.6, '#2f8f4a');
    if (p.kind === 'feather') { game.stats.feathers |= 1 << p.index; bark('FEATHER!', game.kid.x, game.kid.y + 1.6, '#2f8f4a'); }
  },
  hit(o, lost) {
    if (game.state !== 'chase') return;
    game.stats.stumbles++;
    bark(o.def.bark, o.x, o.y + 1.2, '#7a3b1d');
    bark('-' + lost.toFixed(1) + ' m', game.kid.x, game.kid.y + 1.7, '#d4261a');
    if (o.def.reaction === 'smash') { o.gone = true; burst(o.x, o.y + 0.3, o.def.color, 12, 4); }
    if (o.def.reaction === 'splat') burst(o.x, o.y + 0.05, o.def.color, 8, 2.5);
    game.kidFx.wobble = 1;
  },
  splash() { if (game.state === 'chase') bark('SPLASH!', game.kid.x, game.kid.y + 1.4, '#2f63b8'); burst(game.kid.x, -0.06, '#8fb4e8', 10, 3); },
  bark: (text, x, y, color) => bark(text, x, y, color),
  feathers: (x, y, n) => burst(x, y, '#e6731a', n, 3),
};
function bark(text, x, y, color) { game.barks.push({ text, x, y, color, age: 0, life: 1.2 }); }
function burst(x, y, color, n, speed) {
  for (let i = 0; i < n; i++) {
    const a = Math.random() * Math.PI, s = speed * (0.4 + Math.random() * 0.8);
    game.debris.push({ x, y, vx: Math.cos(a) * s, vy: Math.sin(a) * s + 1, size: 0.05 + Math.random() * 0.07, color, age: 0, life: 0.6 + Math.random() * 0.5 });
  }
}
function dust(x, y, n) { burst(x, y + 0.02, '#c9955e', n, 1.4); }

async function loadLevel(index) {
  game.level = index;
  const L = LEVELS[index];
  game.state = 'loading';
  renderLevelButtons();
  showOverlay(null);
  if (!game.loadedZones.has(L.zone)) {
    statusEl.textContent = `Loading the ${ZONE_NAMES[L.zone - 1].toLowerCase()} scenery...`;
    await loadAll(sheetsOf('zone' + L.zone), (d, n) => { statusEl.textContent = `Loading the ${ZONE_NAMES[L.zone - 1].toLowerCase()} scenery: ${d} of ${n}`; });
    game.loadedZones.add(L.zone);
    // Keep the next zone's art coming in the background.
    sheetsOf('zone' + (L.zone % 3 + 1)).forEach(image);
  }
  statusEl.textContent = '';
  game.course = new Course(index);
  game.t = game.course.t;
  reset();
}

function reset() {
  const c = game.course;
  c.reset();
  game.kid = new Kid(c, game.t, events);
  game.rooster = new Rooster(c, game.t, events);
  game.kid.resetTo(0); game.rooster.resetTo(game.t.startGapNoBasket);
  game.stats = { mangoes: 0, stumbles: 0, feathers: 0, time: 0, outcome: null };
  game.barks = []; game.debris = [];
  game.auto = game.mode === 'watch' ? new Autopilot(game) : null;
  game.kidFx = { squash: 0, sv: 0, land: 0, wobble: 0, lean: 0, dist: 0, lastX: 0 };
  game.roosterFx = { dist: 0, lastX: game.rooster.x, spin: 0 };
  game.acc = 0;
  enter('ready');
  frameCamera(true);
  showReady();
}

function enter(state) { game.state = state; game.stateT = 0; }

function startChase() {
  if (game.state !== 'ready') return;
  enter('chase');
  game.rooster.startChase();
  showOverlay(null);
}

function simulate(dt) {
  const k = game.kid, r = game.rooster, t = game.t;
  if (game.state === 'chase') { game.stats.time += dt; if (game.auto) game.auto.tick(dt); }
  k.tick(dt);
  r.tick(dt, r.x - k.x, k.x);
  if (game.state === 'chase') {
    const gap = r.x - k.x;
    let outcome = null;
    if (gap <= t.grabDistance && Math.abs(k.y - r.y) <= t.grabHeightTolerance) outcome = 'caught';
    else if (gap > t.escapeDistance) outcome = 'far';
    else if (r.x >= game.course.length) outcome = 'end';
    if (outcome) {
      game.stats.outcome = outcome;
      game.stats.passed = game.course.mangoesBefore(k.x);
      if (outcome === 'caught') {
        enter('grab'); k.beginDive(); r.beginWriggle(); bark('GOTCHA!', k.x, k.y + 1.5, '#2659b8');
      } else { enter('escape'); k.beginStop(); r.beginFlee(); }
    }
  } else if (game.state === 'grab' && game.stateT >= 1.4) finish();
  else if (game.state === 'escape' && game.stateT >= 1.6) finish();
  // Obstacles knocked down by the rooster fall into the lane; reactions play out.
  for (const o of game.course.obstacles) {
    if (o.reveal >= 0) { o.reveal += dt; if (o.reveal >= 0.35) { o.reveal = -1; o.hidden = false; o.armed = true; burst(o.x, 0.3, '#a0623a', 6, 1.5); } }
    if (o.react >= 0) { o.react += dt; if (o.react > 0.7) o.react = -1; }
  }
  for (const b of game.course.bouncers) if (b.squash >= 0) { b.squash += dt; if (b.squash > 0.3) b.squash = -1; }
}

function finish() {
  enter('result');
  const s = game.stats, t = game.t;
  const caught = s.outcome === 'caught';
  s.stars = { grab: caught, mangoes: caught && (s.passed <= 0 || s.mangoes >= t.mangoStarFraction * s.passed), clean: caught && s.stumbles === 0 };
  showResult();
}

// ------------------------------------------------------------------ camera (ChaseCamera)
function smoothDamp(cur, target, vel, time, dt) {
  const omega = 2 / time, x = omega * dt, exp = 1 / (1 + x + 0.48 * x * x + 0.235 * x * x * x);
  const change = cur - target, temp = (vel + omega * change) * dt;
  const v = (vel - omega * temp) * exp;
  return [target + (change + temp) * exp, v];
}
const TAN_V = Math.tan(15 * Math.PI / 180);
function frameCamera(snap, dt = 0) {
  const k = game.kidDraw || { x: game.kid.x, y: game.kid.y }, cam = game.cam;
  const aspect = view.width / view.height;
  const tanH = TAN_V * aspect;
  const gap = Math.min(Math.max((game.rooster.x - game.kid.x), 0), game.t.framingMaxGap);
  const width = Math.max(13, (gap + 0.8) / (0.88 - 1 / 3));
  const targetDist = width / (2 * tanH), targetH = k.y * 0.45;
  if (snap || cam.dist <= 0) { cam.dist = targetDist; cam.h = targetH; cam.dv = 0; cam.hv = 0; }
  else { [cam.dist, cam.dv] = smoothDamp(cam.dist, targetDist, cam.dv, 0.45, dt); [cam.h, cam.hv] = smoothDamp(cam.h, targetH, cam.hv, 0.3, dt); }
  const visW = 2 * cam.dist * tanH, visH = 2 * cam.dist * TAN_V;
  cam.x = k.x + (0.5 - 1 / 3) * visW;
  const lookY = cam.h + (0.5 - 0.28) * visH;
  cam.y = lookY + 0.8; cam.z = -cam.dist;
  cam.pitch = Math.atan2(0.8, cam.dist);
  cam.sp = Math.sin(cam.pitch); cam.cp = Math.cos(cam.pitch);
  cam.F = (view.height / 2) / TAN_V;
}
function project(x, y, z) {
  const c = game.cam, vx = x - c.x, vy = y - c.y, vz = z - c.z;
  const zc = -vy * c.sp + vz * c.cp, yc = vy * c.cp + vz * c.sp;
  return [view.width / 2 + vx * c.F / zc, view.height / 2 - yc * c.F / zc, zc];
}

// ------------------------------------------------------------------ drawing
let groundPatterns = null;
function patterns() {
  if (groundPatterns) return groundPatterns;
  const make = (name, tile) => { const im = image('assets/' + DATA.tiles[name]); return im.naturalWidth ? { p: gctx.createPattern(im, 'repeat'), w: im.naturalWidth, h: im.naturalHeight, tile } : null; };
  const p = { earth: make('earth', 3.5), paddy: make('paddy', 6), water: make('water', 2.5) };
  if (p.earth && p.paddy && p.water) groundPatterns = p;
  return p;
}
function drawGround() {
  const W = view.width, H = view.height, gw = ground.width = Math.ceil(W / 2), gh = ground.height = Math.ceil(H / 2);
  const c = game.cam, F2 = c.F / 2, zone = game.course.zone, p = patterns();
  gctx.fillStyle = `rgb(${HAZE})`; gctx.fillRect(0, 0, gw, gh);
  if (!p.earth) return;
  const hazeFrom = zone === 2 ? 10 : 6, hazeTo = zone === 2 ? 55 : 40;
  const holes = game.course.holes.filter(([a, b]) => b > c.x - 80 && a < c.x + 80);
  for (let r = 0; r < gh; r++) {
    const b = (H / 2 - (r + 0.5) * 2) / c.F;
    const dy = b * c.cp - c.sp;
    if (dy >= -1e-4) continue;
    const t = -c.y / dy, zw = c.z + t * (b * c.sp + c.cp);
    if (zw > 95) continue;
    const ppm = F2 / t;
    const fill = (pat, x0, x1) => {
      const v = ((zw / pat.tile * pat.h) % pat.h + pat.h) % pat.h;
      pat.p.setTransform(new DOMMatrix([pat.tile / pat.w * ppm, 0, 0, 1, gw / 2 - c.x * ppm, r - v]));
      gctx.fillStyle = pat.p; gctx.fillRect(x0, r, x1 - x0, 1);
    };
    fill(zone === 2 && zw > 1.8 ? p.paddy : p.earth, 0, gw);
    if (zw <= 4.5 && zw >= -40) for (const [a, bb] of holes) fill(p.water, gw / 2 + (a - c.x) * ppm, gw / 2 + (bb - c.x) * ppm);
    if (zw > hazeFrom) {
      const h = Math.pow(clamp01((zw - hazeFrom) / (hazeTo - hazeFrom)), 0.85);
      gctx.fillStyle = `rgba(${HAZE},${h})`; gctx.fillRect(0, r, gw, 1);
    }
  }
  ctx.drawImage(ground, 0, 0, W, H);
}

function cardItem(list, img, x, y, z, w, h, mirror, order, fx) {
  list.push({ order, z, x, draw: () => drawCard(img, x, y, z, w, h, mirror, fx) });
}
function drawCard(name, x, y, z, w, h, mirror, fx) {
  const sp = sprite(name), im = sp.img;
  if (!im.naturalWidth) return;
  // The ground hides whatever is sunk below it (the far painting, the bands): draw only the part above y = 0.
  let srcH = sp.h;
  if (y < 0 && !(fx && fx.clipY !== undefined)) {
    if (y + h <= 0) return;
    srcH = sp.h * (y + h) / h; h = y + h; y = 0;
  }
  const [bx, by, zc] = project(x, y, z);
  if (zc < 0.4) return;
  const [, ty] = project(x, y + h, z);
  const sw = w * game.cam.F / zc, sh = by - ty;
  if (bx + sw < 0 || bx - sw > view.width || by < -10 || ty > view.height + 10) return;
  if (!fx && !mirror) { ctx.drawImage(im, sp.x, sp.y, sp.w, srcH, bx - sw / 2, ty, sw, sh); return; }
  ctx.save();
  if (fx && fx.clipY !== undefined) { ctx.beginPath(); ctx.rect(0, 0, view.width, fx.clipY); ctx.clip(); }
  const pivot = fx && fx.pivot ? fx.pivot * sh / h : 0;
  ctx.translate(bx, by - pivot);
  if (fx && fx.rot) ctx.rotate(fx.rot);
  ctx.scale((mirror ? -1 : 1) * (fx && fx.sx || 1), fx && fx.sy || 1);
  if (fx && fx.alpha !== undefined) ctx.globalAlpha = fx.alpha;
  ctx.drawImage(im, sp.x, sp.y, sp.w, srcH, -sw / 2, -sh + pivot, sw, sh);
  ctx.restore();
}
function drawFlat(name, x, z, w, h, turn) {
  const sp = sprite(name), im = sp.img;
  if (!im.naturalWidth) return;
  const [cx, cy, zc] = project(x, 0.004, z);
  if (zc < 0.4) return;
  const [, fy] = project(x, 0.004, z - h / 2), [, ky] = project(x, 0.004, z + h / 2);
  const sw = w * game.cam.F / zc, sh = Math.max(1, fy - ky);
  if (cx + sw < 0 || cx - sw > view.width) return;
  ctx.save(); ctx.translate(cx, cy);
  if (turn % 360 > 180) ctx.scale(-1, 1);
  ctx.drawImage(im, sp.x, sp.y, sp.w, sp.h, -sw / 2, -sh / 2, sw, sh); ctx.restore();
}

function poly(points, fill) {
  ctx.beginPath();
  points.forEach(([x, y, z], i) => { const [sx, sy] = project(x, y, z); i ? ctx.lineTo(sx, sy) : ctx.moveTo(sx, sy); });
  ctx.closePath(); ctx.fillStyle = fill; ctx.fill();
}
function boxItem(list, x0, x1, y0, y1, z0, z1, front, top, order = 1) {
  list.push({ order, z: z0, x: (x0 + x1) / 2, draw: () => {
    poly([[x0, y1, z0], [x1, y1, z0], [x1, y1, z1], [x0, y1, z1]], top);
    poly([[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0]], front);
  } });
}

function render(alpha) {
  const W = view.width, H = view.height, c = game.cam;
  ctx.fillStyle = `rgb(${HAZE})`; ctx.fillRect(0, 0, W, H);
  if (!game.course) return;
  drawGround();
  const items = [];
  // Scenery: each track repeated every period, only the copies near the camera.
  for (const track of DATA.zones[game.course.zone].tracks) {
    const first = Math.floor((c.x - track.reach - track.max) / track.period), last = Math.ceil((c.x + track.reach - track.min) / track.period);
    for (let k = first; k <= last; k++) {
      const off = k * track.period;
      for (const cd of track.cards) {
        const x = cd.x + off;
        if (Math.abs(x - c.x) > track.reach + cd.w) continue;
        if (cd.f) items.push({ order: 3, z: cd.z, x, draw: () => drawFlat(cd.img, x, cd.z, cd.w, cd.h, cd.t) });
        else cardItem(items, cd.img, x, cd.y, cd.z, cd.w, cd.h, cd.m, cd.o, null);
      }
    }
  }
  // The course near the camera.
  const near = x => Math.abs(x - c.x) < 45;
  for (const cd of game.course.cards) {
    const o = cd.parent && cd.relative ? cd.parent : null;
    if (o && (o.gone || (o.hidden && o.reveal < 0))) continue;
    const x = o ? o.x + cd.x : cd.x;
    if (!near(x)) continue;
    if (cd.flat) { items.push({ order: 4, z: cd.z, x, draw: () => drawFlat(cd.img, x, cd.z, cd.w, cd.h, cd.turn) }); continue; }
    const fx = reactionFx(cd);
    const y = (o ? o.y : 0) + cd.y + (fx ? fx.dy || 0 : 0), z = cd.z + (fx ? fx.dz || 0 : 0);
    cardItem(items, cd.img, x, y, z, cd.w, cd.h, cd.mirror, cd.order, fx);
  }
  for (const pd of game.course.puddles) {
    if (!near(pd.x)) continue;
    items.push({ order: 4, z: 0, x: pd.x, draw: () => {
      const [cx, cy, zc] = project(pd.x, 0.004, 0), [, fy] = project(pd.x, 0.004, -0.45), [, by] = project(pd.x, 0.004, 0.45);
      ctx.beginPath(); ctx.ellipse(cx, cy, pd.w / 2 * c.F / zc, Math.max(2, (fy - by) / 2), 0, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(78,124,190,0.85)'; ctx.fill();
    } });
  }
  for (const pr of game.course.prims) {
    if (!near((pr.x0 + pr.x1) / 2) && !(pr.x0 < c.x && pr.x1 > c.x)) continue;
    if (pr.kind === 'step') boxItem(items, pr.x0, pr.x1, pr.y0, pr.y1, pr.z0, pr.z1, pr.shade ? '#8f8780' : '#9e958d', '#b9b0a6');
    if (pr.kind === 'bridge') {
      boxItem(items, pr.x0, pr.x1, -0.1, 0, -0.45, 0.45, '#7a5130', '#9b6b40');
      boxItem(items, pr.x0, pr.x1, 0.52, 0.57, -0.47, -0.43, '#c7a861', '#d9bf7a', 6);
      for (const px of [pr.x0, pr.x1]) boxItem(items, px - 0.03, px + 0.03, -0.05, 0.6, -0.48, -0.42, '#b39352', '#c7a861', 6);
    }
  }
  for (const p of game.course.pickups) {
    if (!near(p.x) || (p.taken && p.pop < 0)) continue;
    items.push({ order: 6, z: 0, x: p.x, draw: () => drawPickup(p) });
  }
  characterItems(items, alpha);
  items.sort((a, b) => a.order - b.order || b.z - a.z);
  for (const it of items) it.draw();
  drawEffects();
  drawHud();
}

function reactionFx(cd) {
  const o = cd.parent;
  if (!o) return null;
  if (o.def === undefined) {   // a bouncer: the cot squashes
    if (o.squash < 0) return null;
    const t = clamp01(o.squash / 0.3);
    return { sy: 1 - 0.45 * Math.sin(Math.PI * t) * (1 - t * 0.5) };
  }
  if (o.reveal >= 0) {
    const t = clamp01(o.reveal / 0.35), fall = 1 - t;
    return { dy: 1.2 * fall + 0.6 * Math.sin(Math.PI * t), dz: 1.6 * fall, rot: -2.4 * fall };
  }
  if (o.react < 0 && !(o.def.reaction === 'splat' && !o.armed)) return null;
  const k = clamp01(Math.max(0, o.react) / 0.7);
  switch (o.def.reaction) {
    case 'wake': return { dy: 0.7 * Math.sin(Math.PI * Math.min(1, k * 1.6)), rot: 0.44 * Math.sin(k * 18) * (1 - k) };
    case 'wobble': return { sy: 1 - 0.25 * Math.abs(Math.sin(k * 20)) * (1 - k) };
    case 'splat': return { sx: 1.15, sy: 0.5 };
  }
  return null;
}

function drawPickup(p) {
  const [sx, sy, zc] = project(p.x, p.y, 0);
  const s = game.cam.F / zc;
  let scale = 1, alpha = 1;
  if (p.pop >= 0) { scale = 1 + p.pop / 0.15; alpha = 1 - p.pop / 0.15; }
  const spin = Math.abs(Math.cos(performance.now() / 1000 * (p.kind === 'chilli' ? 5.2 : 3.1) + p.x));
  ctx.save(); ctx.globalAlpha = alpha; ctx.translate(sx, sy);
  if (p.kind === 'mango') {
    ctx.beginPath(); ctx.ellipse(0, 0, 0.11 * s * scale * Math.max(0.25, spin), 0.14 * s * scale, 0.3, 0, Math.PI * 2);
    ctx.fillStyle = '#f2b51f'; ctx.fill(); ctx.strokeStyle = 'rgba(120,70,10,0.55)'; ctx.lineWidth = Math.max(1, 0.012 * s); ctx.stroke();
    ctx.beginPath(); ctx.ellipse(0.05 * s, -0.15 * s, 0.06 * s * scale, 0.025 * s * scale, -0.5, 0, Math.PI * 2); ctx.fillStyle = '#4c9a2a'; ctx.fill();
  } else if (p.kind === 'chilli') {
    ctx.rotate(0.9); ctx.beginPath(); ctx.ellipse(0, 0, 0.06 * s * scale, 0.2 * s * scale * Math.max(0.3, spin), 0, 0, Math.PI * 2);
    ctx.fillStyle = '#d91a0d'; ctx.fill();
  } else {
    ctx.rotate(-0.5 + 0.2 * Math.sin(performance.now() / 300));
    ctx.beginPath(); ctx.ellipse(0, 0, 0.07 * s * scale * Math.max(0.3, spin), 0.24 * s * scale, 0, 0, Math.PI * 2);
    const g = ctx.createLinearGradient(0, -0.24 * s, 0, 0.24 * s); g.addColorStop(0, '#1f5a4a'); g.addColorStop(0.5, '#d9591a'); g.addColorStop(1, '#f2b51f');
    ctx.fillStyle = g; ctx.fill();
    ctx.strokeStyle = 'rgba(255,240,200,0.9)'; ctx.lineWidth = Math.max(1, 0.015 * s); ctx.stroke();
  }
  ctx.restore();
}

// The kid and the rooster: their poses picked as KidCardVisual and RoosterCardVisual do.
function characterItems(items, alpha) {
  const k = game.kid, r = game.rooster, dt = game.frameDt;
  const kx = lerp(k.px, k.x, alpha), ky = lerp(k.py, k.y, alpha);
  game.kidDraw = { x: kx, y: ky };
  const fx = game.kidFx;
  const dx = kx - fx.lastX; fx.lastX = kx; if (dx > 0 && dx < 2) fx.dist += dx;
  fx.land = Math.max(0, fx.land - dt); fx.wobble = Math.max(0, fx.wobble - dt * 1.6);
  [fx.squash, fx.sv] = smoothDamp(fx.squash, 0, fx.sv, 0.08, Math.max(dt, 1e-4));
  let pose, lean = 0;
  switch (k.pose) {
    case 'slide': pose = 'slide'; break;
    case 'vault': pose = 'vault'; break;
    case 'climb': pose = 'jump_up'; lean = 8; break;
    case 'dive': pose = 'dive'; break;
    case 'air': pose = k.vs > 0.5 ? 'jump_up' : 'fall'; lean = Math.max(-8, Math.min(8, -k.vs * 0.8)); break;
    default:
      pose = k.speed < 0.1 ? 'run_contact' : k.stumbling ? 'stumble' : fx.land > 0 ? 'land' : (Math.floor(fx.dist / 0.55) % 2 ? 'run_passing' : 'run_contact');
  }
  lean += Math.sin(fx.wobble * 30) * 14 * fx.wobble;
  fx.lean = lerp(fx.lean, lean, 1 - Math.exp(-16 * dt));
  const kf = DATA.kid[pose] || DATA.kid.run_contact;
  const sy = 1 - fx.squash, sx = 1 / Math.sqrt(Math.max(0.3, sy));
  const kidFx = { sx, sy, rot: fx.lean * Math.PI / 180 };
  if (ky < -0.04) kidFx.clipY = project(kx, -0.06, 0)[1];
  if (k.boosted) kidFx.alpha = 0.85 + 0.15 * Math.sin(performance.now() / 40);
  items.push({ order: 10, z: 0, x: kx, draw: () => drawCard(kf.img, kx, ky, 0, kf.w, kf.h, false, kidFx) });

  const rx = lerp(r.px, r.x, alpha), ry = lerp(r.py, r.y, alpha), rf = game.roosterFx;
  const rdx = rx - rf.lastX; rf.lastX = rx; if (rdx > 0 && rdx < 2) rf.dist += rdx;
  const second = Math.floor(rf.dist / 0.32) % 2 === 1;
  let rp, spin = 0;
  if (r.act === 'idle') rp = (performance.now() / 1000) % 1.8 < 1.08 ? 'rooster_peck' : 'rooster_strut';
  else if (r.act === 'wriggle') { rp = 'rooster_tumble'; spin = 540; }
  else if (r.airborne) rp = 'rooster_flutter';
  else if (r.mood === 'taunting' && r.speed < 1) rp = 'rooster_crow';
  else if (r.mood === 'panicking') rp = second ? 'rooster_startled' : 'rooster_run_1';
  else rp = second ? 'rooster_run_2' : 'rooster_run_1';
  rf.spin = spin ? rf.spin + spin * dt : 0;
  const rfr = DATA.rooster[rp] || DATA.rooster.rooster_run_1;
  items.push({ order: 10, z: 0.01, x: rx, draw: () => drawCard(rfr.img, rx, ry, 0, rfr.w, rfr.h, false, { rot: rf.spin * Math.PI / 180, pivot: 0.3 }) });
}

function drawEffects() {
  const dt = game.frameDt;
  for (const d of game.debris) {
    d.age += dt; d.vy -= 9 * dt; d.x += d.vx * dt; d.y += d.vy * dt;
    const [sx, sy, zc] = project(d.x, Math.max(d.y, 0), -0.05);
    const s = d.size * game.cam.F / zc;
    ctx.globalAlpha = 1 - clamp01(d.age / d.life); ctx.fillStyle = d.color; ctx.fillRect(sx - s / 2, sy - s / 2, s, s);
  }
  ctx.globalAlpha = 1;
  game.debris = game.debris.filter(d => d.age < d.life);
  const px = Math.max(14, view.height / 34);
  ctx.font = `800 ${px}px "Baloo 2", system-ui, sans-serif`; ctx.textAlign = 'center';
  for (const b of game.barks) {
    b.age += dt;
    const [sx, sy] = project(b.x, b.y + b.age * 0.5, 0);
    ctx.globalAlpha = 1 - clamp01((b.age - b.life * 0.6) / (b.life * 0.4));
    ctx.lineWidth = px / 5; ctx.strokeStyle = 'rgba(255,248,235,0.95)'; ctx.strokeText(b.text, sx, sy);
    ctx.fillStyle = b.color; ctx.fillText(b.text, sx, sy);
  }
  ctx.globalAlpha = 1;
  game.barks = game.barks.filter(b => b.age < b.life);
}

function roundRect(x, y, w, h, r, fill) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); ctx.fillStyle = fill; ctx.fill(); }
function drawHud() {
  if (game.state === 'ready' || game.state === 'loading') return;
  const W = view.width, H = view.height, u = H / 720;
  const gap = Math.max(0, game.rooster.x - game.kid.x), t = game.t;
  const bw = Math.min(500 * u, W * 0.5), bh = 26 * u, bx = W / 2 - bw / 2, by = 18 * u;
  roundRect(bx - 8 * u, by - 8 * u, bw + 16 * u, bh + 30 * u, 10 * u, 'rgba(30,22,48,0.72)');
  roundRect(bx, by, bw, bh, 6 * u, 'rgba(0,0,0,0.35)');
  const close = 1 - clamp01(gap / t.escapeDistance);
  roundRect(bx, by, Math.max(bh, bw * close), bh, 6 * u, gap <= 5 ? '#4fb85c' : gap <= t.tauntDistance ? '#f2b632' : '#e2462b');
  ctx.fillStyle = 'rgba(255,255,255,0.55)'; ctx.fillRect(bx + bw * (1 - t.tauntDistance / t.escapeDistance) - u, by, 2 * u, bh);
  ctx.font = `800 ${18 * u}px "Baloo 2", system-ui, sans-serif`; ctx.textAlign = 'center'; ctx.fillStyle = '#fff';
  ctx.fillText(gap.toFixed(1) + ' m', W / 2, by + bh * 0.78);
  ctx.fillStyle = 'rgba(0,0,0,0.35)'; ctx.fillRect(bx, by + bh + 8 * u, bw, 5 * u);
  ctx.fillStyle = '#e2462b'; ctx.fillRect(bx, by + bh + 8 * u, bw * clamp01(game.rooster.x / game.course.length), 5 * u);
  // Mangoes and feathers.
  roundRect(16 * u, 14 * u, 150 * u, 52 * u, 10 * u, 'rgba(30,22,48,0.72)');
  ctx.beginPath(); ctx.ellipse(42 * u, 40 * u, 11 * u, 14 * u, 0.3, 0, Math.PI * 2); ctx.fillStyle = '#f2b51f'; ctx.fill();
  ctx.textAlign = 'left'; ctx.fillStyle = '#fff'; ctx.font = `800 ${26 * u}px "Baloo 2", system-ui, sans-serif`;
  ctx.fillText(String(game.stats.mangoes), 64 * u, 50 * u);
  for (let i = 0; i < 3; i++) {
    ctx.beginPath(); ctx.ellipse(120 * u + i * 14 * u, 40 * u, 4 * u, 12 * u, -0.4, 0, Math.PI * 2);
    ctx.fillStyle = game.stats.feathers & (1 << i) ? '#e6731a' : 'rgba(255,255,255,0.22)'; ctx.fill();
  }
  ctx.textAlign = 'right'; ctx.font = `700 ${16 * u}px "Hind", system-ui, sans-serif`; ctx.fillStyle = 'rgba(30,22,48,0.8)';
  ctx.fillText(`${game.level + 1}. ${LEVELS[game.level].title}`, W - 16 * u, 32 * u);
  if (game.mode === 'watch') ctx.fillText('Watching the autopilot', W - 16 * u, 52 * u);
}

// ------------------------------------------------------------------ overlays
function showOverlay(html) { overlay.innerHTML = html || ''; overlay.hidden = !html; }
function showReady() {
  const L = LEVELS[game.level];
  showOverlay(`<div class="card ready"><p class="eyebrow">Level ${game.level + 1} &middot; ${ZONE_NAMES[L.zone - 1]}</p>
    <h2>${L.title}</h2><p>${L.sub}</p>
    <p class="hint">${game.mode === 'watch' ? 'The autopilot starts in a moment.' : 'Tap, click or press Space to start the chase.'}</p></div>`);
}
function showResult() {
  const s = game.stats, caught = s.outcome === 'caught';
  const why = caught ? `...and he wriggled free. ${s.time.toFixed(1)} s, ${s.stumbles} ${s.stumbles === 1 ? 'stumble' : 'stumbles'}.`
    : s.outcome === 'far' ? `He got more than ${game.t.escapeDistance} m ahead.` : 'He reached the end of the course first.';
  const star = (on, label) => `<span class="star ${on ? 'on' : ''}">${label}</span>`;
  const feathers = [0, 1, 2].filter(i => s.feathers & (1 << i)).length;
  const next = game.level + 1 < LEVELS.length;
  game.nextIn = game.mode === 'watch' ? 6 : 0;
  showOverlay(`<div class="card result"><h2>${caught ? 'Caught him!' : 'He got away!'}</h2><p>${why}</p>
    <div class="stars">${star(s.stars.grab, 'Grab')}${star(s.stars.mangoes, 'Mangoes')}${star(s.stars.clean, 'No stumble')}</div>
    <p class="stats">${s.mangoes} of ${s.passed} mangoes &middot; ${feathers} of 3 feathers</p>
    <div class="actions"><button type="button" id="again">Again</button>${next ? '<button type="button" id="next" class="primary">Next level</button>' : ''}</div>
    <p class="hint" id="countdown"></p></div>`);
  document.getElementById('again').onclick = () => { reset(); view.focus({ preventScroll: true }); };
  if (next) document.getElementById('next').onclick = () => { loadLevel(game.level + 1); view.focus({ preventScroll: true }); };
}

// ------------------------------------------------------------------ input (Play mode)
const input = { down: false, startY: 0, startT: 0, jumped: false, timer: 0 };
function press() {
  if (game.mode !== 'play') return false;
  if (game.state === 'ready') { startChase(); return false; }
  return game.state === 'chase';
}
view.addEventListener('pointerdown', e => {
  view.setPointerCapture(e.pointerId);
  view.focus({ preventScroll: true });
  if (!press()) return;
  Object.assign(input, { down: true, startY: e.clientY, startT: performance.now(), jumped: false });
  // A touch waits 60 ms before it becomes a jump, so a swipe down never starts with one.
  clearTimeout(input.timer);
  input.timer = setTimeout(() => { if (input.down && !input.slid) { game.kid.pressJump(); game.kid.held = true; input.jumped = true; } }, 60);
  input.slid = false;
});
view.addEventListener('pointermove', e => {
  if (!input.down || input.slid) return;
  if (e.clientY - input.startY > 28 && performance.now() - input.startT < 300) { input.slid = true; game.kid.pressSlide(); }
});
const release = () => { input.down = false; if (game.kid) game.kid.held = false; };
view.addEventListener('pointerup', release);
view.addEventListener('pointercancel', release);
const keysDown = new Set();
window.addEventListener('keydown', e => {
  // Keys belong to the game unless a control has focus (then Space presses that control, as it should).
  if (e.target.closest && e.target.closest('button, select, input, a')) return;
  const k = e.key;
  if ([' ', 'ArrowUp', 'w', 'W', 'ArrowDown', 's', 'S'].includes(k)) e.preventDefault();
  if (keysDown.has(k)) return;
  keysDown.add(k);
  if (k === 'r' || k === 'R') { if (game.course) reset(); return; }
  if (!press()) return;
  if (k === ' ' || k === 'ArrowUp' || k === 'w' || k === 'W') { game.kid.pressJump(); game.kid.held = true; }
  if (k === 'ArrowDown' || k === 's' || k === 'S') game.kid.pressSlide();
});
window.addEventListener('keyup', e => {
  keysDown.delete(e.key);
  if ((e.key === ' ' || e.key === 'ArrowUp' || e.key === 'w' || e.key === 'W') && game.kid) game.kid.held = false;
});

// ------------------------------------------------------------------ page controls
function renderLevelButtons() {
  document.querySelectorAll('[data-level]').forEach(b => b.setAttribute('aria-pressed', String(+b.dataset.level === game.level)));
  document.querySelectorAll('[data-mode]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.mode === game.mode)));
}
function buildLevelButtons() {
  const host = document.getElementById('levels');
  host.innerHTML = [1, 2, 3].map(zone => `<div class="zone"><h3>${ZONE_NAMES[zone - 1]}</h3><div class="zone-levels">${
    LEVELS.map((L, i) => (L.zone === zone ? `<button type="button" class="level" data-level="${i}"><span class="num">${i + 1}</span><span class="name">${L.title}</span><span class="sub">${L.sub}</span></button>` : '')).join('')
  }</div></div>`).join('');
  // After a click the game takes the keyboard back, so Space jumps instead of pressing the same button again.
  const toGame = () => view.focus({ preventScroll: true });
  host.querySelectorAll('[data-level]').forEach(b => b.addEventListener('click', () => {
    loadLevel(+b.dataset.level); toGame();
    document.getElementById('stage').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }));
  document.querySelectorAll('[data-mode]').forEach(b => b.addEventListener('click', () => { game.mode = b.dataset.mode; renderLevelButtons(); if (game.course) reset(); toGame(); }));
  document.getElementById('restart').addEventListener('click', () => { if (game.course) reset(); toGame(); });
  const full = document.getElementById('fullscreen'), frameEl = document.querySelector('.frame');
  if (full && frameEl.requestFullscreen && document.fullscreenEnabled) {
    full.hidden = false;
    full.addEventListener('click', () => {
      if (document.fullscreenElement) document.exitFullscreen();
      else frameEl.requestFullscreen().then(() => { toGame(); if (screen.orientation && screen.orientation.lock) screen.orientation.lock('landscape').catch(() => {}); }).catch(() => {});
    });
    document.addEventListener('fullscreenchange', () => { full.textContent = document.fullscreenElement ? 'Exit full screen' : 'Full screen'; });
  }
}

function resize() {
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  const rect = view.getBoundingClientRect();
  view.width = Math.round(rect.width * dpr); view.height = Math.round(rect.height * dpr);
  groundPatterns = null;
}

// ------------------------------------------------------------------ main loop
let last = performance.now();
function frame(now) {
  const dt = Math.min(0.1, (now - last) / 1000); last = now;
  game.frameDt = dt;
  if (game.course && game.state !== 'loading') {
    game.stateT += dt;
    if (game.state === 'ready' && game.mode === 'watch' && game.stateT > 1.2) startChase();
    if (game.state !== 'ready' && game.state !== 'result' || game.state === 'result') {
      if (game.state !== 'ready') {
        game.acc += dt;
        const step = 1 / 120; let n = 0;
        while (game.acc >= step && n < 12) { simulate(step); game.acc -= step; n++; }
        if (n === 12) game.acc = 0;
      }
    }
    for (const p of game.course.pickups) if (p.pop >= 0) { p.pop += dt; if (p.pop > 0.15) p.pop = -1; }
    if (game.state === 'result' && game.nextIn > 0) {
      game.nextIn -= dt;
      const el = document.getElementById('countdown');
      if (el) el.textContent = game.level + 1 < LEVELS.length ? `Next level in ${Math.ceil(game.nextIn)}` : '';
      if (game.nextIn <= 0) loadLevel((game.level + 1) % LEVELS.length);
    }
    const alpha = game.acc * 120;
    game.kidDraw = { x: lerp(game.kid.px, game.kid.x, alpha), y: lerp(game.kid.py, game.kid.y, alpha) };
    frameCamera(false, dt);
    render(alpha);
  }
  requestAnimationFrame(frame);
}

async function boot() {
  buildLevelButtons();
  resize();
  new ResizeObserver(() => { resize(); if (game.course) frameCamera(true); }).observe(view);
  statusEl.textContent = 'Loading the art...';
  DATA = await fetch('data.json').then(r => r.json());
  PIECES = DATA.pieces;
  const common = [...sheetsOf('common'), ...Object.values(DATA.tiles).map(t => 'assets/' + t)];
  await loadAll(common, (d, n) => { statusEl.textContent = `Loading the kid, the rooster and the obstacles: ${d} of ${n}`; });
  const fromHash = () => { const m = /^#level-([1-9])$/.exec(location.hash); return m ? +m[1] - 1 : null; };
  window.addEventListener('hashchange', () => { const l = fromHash(); if (l !== null && l !== game.level) loadLevel(l); });
  await loadLevel(fromHash() ?? 0);
  requestAnimationFrame(frame);
}
boot();
