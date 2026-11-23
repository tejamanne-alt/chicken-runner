// Chicken Runner browser preview. A port of the Unity build's rules (KidController, RoosterBrain, RoosterMind,
// ChaseDirector, ChaseCamera, LevelStreamer) and of GameBuilder's nine levels, drawn with the same painted art.
'use strict';

// ------------------------------------------------------------------ tuning (ChaseTuning.ForZone)
function tuningFor(zone) {
  const t = {
    kidRunSpeed: 6, roosterRunSpeed: 5.5, courseLength: 500, startGapNoBasket: 12, grabDistance: 0.8,
    grabHeightTolerance: 1, escapeDistance: 25, tauntDistance: 18, tauntDuration: 1.4, tauntCooldown: 5,
    panicDistance: 2, panicSpeedMultiplier: 1.3, panicDuration: 0.8, panicCooldown: 3, maxPanicBursts: 2,
    mischiefMinKidDistance: 7, jumpHeight: 1.4, tapJumpHeight: 0.9, jumpLength: 3.7, jumpReferenceSpeed: 6,
    doubleJumpTotalHeight: 2.6, fallGravityMultiplier: 1, maxFallSpeed: 20, fastDropSpeed: 16, jumpBuffer: 0.1,
    coyoteTime: 0.08, cotBounceHeight: 2.4, slideDuration: 0.6, vaultDuration: 0.45, vaultSpeedFactor: 0.1,
    maxVaultHeight: 2.8, ladderClimbDuration: 0.35, ladderSpeedFactor: 0.6, wadeSpeedFactor: 0.45,
    stumbleDuration: 0.7, stumbleSpeedFactor: 0.45, hitGracePeriod: 0.35, boostSpeedBonus: 0.35, boostDuration: 2.2,
    framingMaxGap: 14, mangoStarFraction: 0.7,
  };
  if (zone === 2) Object.assign(t, { kidRunSpeed: 7, roosterRunSpeed: 6.4, courseLength: 600 });
  if (zone === 3) Object.assign(t, { kidRunSpeed: 8, roosterRunSpeed: 7.4, courseLength: 700 });
  return t;
}
const JumpMath = {
  gravity: t => 8 * t.jumpHeight * t.jumpReferenceSpeed ** 2 / (t.jumpLength ** 2),
  vForH: (g, h) => (h <= 0 ? 0 : Math.sqrt(2 * g * h)),
  jump: t => JumpMath.vForH(JumpMath.gravity(t), t.jumpHeight),
  double: t => JumpMath.vForH(JumpMath.gravity(t), Math.max(0, t.doubleJumpTotalHeight - t.jumpHeight)),
  bounce: (t, h) => JumpMath.vForH(JumpMath.gravity(t), h > 0 ? h : t.cotBounceHeight),
  lowMult: t => (t.tapJumpHeight <= 0 ? 1 : Math.max(1, t.jumpHeight / t.tapJumpHeight)),
  lengthAt: (t, v) => v * 2 * JumpMath.jump(t) / JumpMath.gravity(t),
};
const clamp01 = v => Math.min(1, Math.max(0, v));
const lerp = (a, b, k) => a + (b - a) * k;
const moveTowards = (a, b, d) => (Math.abs(b - a) <= d ? b : a + Math.sign(b - a) * d);

// System.Random (the Knuth subtractive generator Unity's Mono uses), so seeded shuffles and the chunks' picks match.
class NetRandom {
  constructor(seed) {
    const MBIG = 2147483647, MSEED = 161803398;
    this.a = new Array(56).fill(0);
    let mj = MSEED - Math.abs(seed | 0), mk = 1;
    this.a[55] = mj;
    for (let i = 1; i < 55; i++) {
      const ii = (21 * i) % 55;
      this.a[ii] = mk; mk = mj - mk; if (mk < 0) mk += MBIG; mj = this.a[ii];
    }
    for (let k = 1; k < 5; k++) for (let i = 1; i < 56; i++) {
      this.a[i] -= this.a[1 + (i + 30) % 55]; if (this.a[i] < 0) this.a[i] += MBIG;
    }
    this.inext = 0; this.inextp = 21; this.MBIG = MBIG;
  }
  sample() {
    if (++this.inext >= 56) this.inext = 1;
    if (++this.inextp >= 56) this.inextp = 1;
    let r = this.a[this.inext] - this.a[this.inextp];
    if (r === this.MBIG) r--;
    if (r < 0) r += this.MBIG;
    this.a[this.inext] = r;
    return r / this.MBIG;
  }
  nextDouble() { return this.sample(); }
  next(max) { return Math.floor(this.sample() * max); }
}

// ------------------------------------------------------------------ obstacle definitions (GameBuilder.CreateObstacles)
const DEFS = {
  pots: { scale: 1, reaction: 'smash', color: '#c75c33', bark: 'SMASH!' },
  dung: { scale: 1.15, reaction: 'splat', color: '#5c421f', bark: 'SPLAT!' },
  dog: { scale: 1, reaction: 'wake', color: '#d1a86b', bark: 'WOOF!' },
  puddle: { scale: 1, reaction: 'splat', color: '#5a8cd9', bark: 'SPLOSH!' },
  clothesline: { scale: 1.1, reaction: 'wobble', color: '#d91f4d', bark: 'TANGLED!' },
  hens: { scale: 0.9, reaction: 'wake', color: '#e6dcc7', bark: 'BAWK BAWK!' },
  tank: { scale: 1, reaction: 'wobble', color: '#1a1414', bark: 'CLONG!' },
};
const ROOF = 2.35;

// ------------------------------------------------------------------ the chunk kit (GameBuilder.Kit)
class Kit {
  constructor(name, length, zone, seed) {
    this.name = name; this.length = length; this.zone = zone; this.t = tuningFor(zone);
    this.rand = new NetRandom(seed);
    this.solids = []; this.obstacles = []; this.bouncers = []; this.waters = []; this.pickups = [];
    this.hops = []; this.mischief = []; this.cards = []; this.prims = []; this.holes = []; this.puddles = [];
  }
  finish() {
    this.holes.sort((a, b) => a[0] - b[0]);
    let x = 0;
    for (const [a, b] of this.holes) { if (a > x) this.slab(x, a); x = Math.max(x, b); }
    if (x < this.length) this.slab(x, this.length);
    return this;
  }
  slab(a, b) { this.solids.push({ x0: a, x1: b, y0: -0.5, y1: 0, ground: true }); }
  // A painted cut-out, bottom centre at (x, y, z), or null when the piece is missing.
  art(piece, x, y, z, o = {}) {
    const p = PIECES[piece];
    const mirror = o.mirror || false;
    if (!p) return null;
    const aspect = p.w / p.h;
    let w = p.w, h = p.h;
    if (o.height) { h = o.height; w = h * aspect; } else if (o.width) { w = o.width; h = w / aspect; }
    const card = { piece, img: p.img, x, y, z, w, h, mirror, order: o.order ?? 5, parent: o.parent || null, flat: !!o.flat, turn: o.turn || 0 };
    this.cards.push(card);
    return card;
  }
  decal(piece, x, z, width, turn) {
    const p = PIECES[piece]; if (!p) return null;
    return this.art(piece, x, 0.004, z, { width, flat: true, turn, order: 4 });
  }
  obstacle(name, x, def, w, h, bottom = 0, hidden = false, y = 0) {
    const o = { name, x, y, w, h, bottom, def: DEFS[def], hidden };
    this.obstacles.push(o);
    return o;
  }
  potStack(x, hidden = false, y = 0) {
    const o = this.obstacle('PotStack', x, 'pots', 0.45, 0.6, 0, hidden, y);
    this.art('pot_stack', 0, 0, 0.05, { height: 0.68, mirror: this.rand.nextDouble() < 0.5, parent: o });
    return o;
  }
  dung(x) { const o = this.obstacle('CowDung', x, 'dung', 0.55, 0.2); this.art('dung', 0, 0, 0.05, { width: 0.6, parent: o }); }
  dog(x) { const o = this.obstacle('SleepingDog', x, 'dog', 0.9, 0.36); this.art('dog_sleeping', 0, 0, 0.05, { width: 0.95, parent: o }); }
  puddle(x, width) {
    const o = this.obstacle('Puddle', x, 'puddle', width, 0.15);
    this.puddles.push({ x, w: width, parent: o });
    this.art('hand_pump', x - width * 0.3, 0, 0.9, { height: 1.2 });
  }
  clothesline(x) {
    const o = this.obstacle('Clothesline', x, 'clothesline', 1.7, 0.9, 0.7);
    this.art('clothesline', 0, 0, 0.05, { width: 2.2, mirror: this.rand.nextDouble() < 0.5, parent: o });
  }
  cot(x) {
    const b = { x0: x, x1: x + 1.9, y0: 0, y1: 0.5, height: 0, bark: 'BOING!', squash: -1 };
    this.bouncers.push(b);
    this.art('rope_cot', x + 0.95, 0, 0.05, { width: 1.9, parent: b });
  }
  cart(x) {
    const width = 3.6;
    const card = this.art('bullock_cart', x + width * 0.5, 0, 0.05, { width });
    const bed = card ? width * 0.62 : 2.6;
    this.solids.push({ x0: x, x1: x + bed, y0: 0, y1: 0.95 });
  }
  hens(x, count) {
    const width = 0.3 + count * 0.36;
    const o = this.obstacle('Hens', x, 'hens', width, 0.45);
    for (let i = 0; i < count; i++) {
      const piece = 'hen_' + (1 + (i + this.rand.next(3)) % 3);
      const hx = -width * 0.5 + 0.3 + i * 0.36;
      this.art(piece, hx, 0, 0.05 + 0.02 * i, { height: 0.42, mirror: this.rand.nextDouble() < 0.3, parent: o });
    }
  }
  hensBasket(x, hidden = false) {
    const o = this.obstacle('HensBasket', x, 'hens', 0.6, 0.55, 0, hidden);
    this.art('hens_basket', 0, 0, 0.05, { height: 0.6, parent: o });
    return o;
  }
  tank(x, y) {
    const o = this.obstacle('WaterTank', x, 'tank', 0.55, 0.7, 0, false, y);
    this.art('black_tank', 0, 0, 0.05, { height: 0.75, parent: o });
  }
  roofRow(x, fronts, ladder) {
    const cardHeight = ROOF + 0.15;
    const start = x;
    for (let i = 0; i < fronts.length; i++) {
      const withLadder = ladder && i === 0;
      const piece = withLadder ? 'house_turmeric_ladder' : fronts[i];
      const card = this.art(piece, 0, 0, 0.4, { height: cardHeight, mirror: withLadder });
      const width = card ? card.w : 2.6;
      if (card) card.x = x + width * 0.5;
      this.solids.push({ x0: x, x1: x + width, y0: 0, y1: ROOF, ladder: withLadder });
      x += width;
    }
    this.hop(start - 1.5, 1.7, 0.6);
    return x;
  }
  canal(x, width, bridge) {
    this.holes.push([x, x + width]);
    this.solids.push({ x0: x, x1: x + width, y0: -0.78, y1: -0.28, bed: true });
    this.hop(x - 0.6, width + 1.2, 0.5 + width * 0.1);
    if (!bridge) { this.waters.push({ x0: x, x1: x + width, y0: -0.38, y1: -0.1 }); return; }
    this.solids.push({ x0: x - 0.2, x1: x + width + 0.2, y0: -0.1, y1: 0, plank: true });
    this.prims.push({ kind: 'bridge', x0: x - 0.2, x1: x + width + 0.2 });
  }
  haystack(x, big) {
    const height = big ? 2.0 : 1.25, top = big ? 1.85 : 1.05;
    const card = this.art(big ? 'haystack' : 'haystack_small', 0, 0, 0.15, { height, mirror: this.rand.nextDouble() < 0.5 });
    const width = card ? card.w : (big ? 2.2 : 1.2);
    if (card) card.x = x + width * 0.5;
    const solid = width * 0.8;
    this.solids.push({ x0: x + width * 0.5 - solid / 2, x1: x + width * 0.5 + solid / 2, y0: 0, y1: top });
    this.hop(x - 0.8, width + 1.6, top + 0.4);
    return x + width;
  }
  buffalo(x) {
    const card = this.art('buffalo_mud', 0, 0, 0.15, { height: 1.5 });
    const width = card ? card.w : 2.6;
    if (card) card.x = x + width * 0.5;
    this.decal('cracked_mud', x + width * 0.5, 0, width + 1.2, 0);
    const back = 1.1, c = x + width * 0.5;
    this.solids.push({ x0: c - width * 0.35, x1: c + width * 0.35, y0: 0, y1: back });
    this.bouncers.push({ x0: c - width * 0.3, x1: c + width * 0.3, y0: back, y1: back + 0.2, height: 2.6, bark: 'MOO!', squash: -1 });
    this.hop(x - 1, width + 2, 1.6);
    return x + width;
  }
  mangoTree(x) {
    this.art('tree_mango_1', x + 3, 0, 0.9, { height: 5.2 });
    this.solids.push({ x0: x + 1, x1: x + 5, y0: 2.14, y1: 2.3, ladder: true, branch: true });
    this.hop(x + 0.2, 1.0, 0.5);
    this.mangoLine(x + 1.4, 6, 0.6, 2.85);
  }
  stall(x, piece) {
    const card = this.art(piece, 0, 0, 0.55, {});
    const width = card ? card.w : 3.2, height = card ? card.h : 2.8;
    if (card) card.x = x + width * 0.5;
    const cy = Math.min(2.3, Math.max(1.95, height * 0.74));
    const c = x + width * 0.5;
    this.bouncers.push({ x0: c - width * 0.4, x1: c + width * 0.4, y0: cy - 0.1, y1: cy + 0.1, height: 2.0, bark: '', awning: true, squash: -1 });
    return x + width;
  }
  steps(x, count, landing) {
    const rise = 0.25, tread = 0.7, end = x + count * tread * 2 + landing;
    for (let i = 0; i < count; i++) {
      const from = x + i * tread, to = end - i * tread;
      this.solids.push({ x0: from, x1: to, y0: i * rise, y1: (i + 1) * rise });
      this.prims.push({ kind: 'step', x0: from, x1: to, y0: i * rise, y1: (i + 1) * rise, z0: -0.7, z1: 1.5, shade: i % 2 });
    }
    const top = count * rise;
    for (let k = 0; k < 2; k++) this.art('lamp_step', x + count * tread + landing * (0.25 + 0.5 * k), top, 1.2, { height: 1.9 });
    this.art('lantern', x + count * tread + landing * 0.5, top, 0.9, { height: 0.45 });
    return end;
  }
  hop(x, length, height) { this.hops.push({ x, length, height }); }
  mischiefAt(x, target) { this.mischief.push({ x, target }); }
  mango(x, y) { this.pickups.push({ kind: 'mango', x, y, r: 0.25 }); }
  chilli(x, y) { this.pickups.push({ kind: 'chilli', x, y, r: 0.3 }); }
  feather(x, y, index) { this.pickups.push({ kind: 'feather', x, y, r: 0.3, index }); }
  mangoLine(x, count, spacing, y) { for (let i = 0; i < count; i++) this.mango(x + i * spacing, y); }
  jumpArc(centre, lift = 0) {
    const L = JumpMath.lengthAt(this.t, this.t.kidRunSpeed);
    this.arc(centre - L * 0.5, L, this.t.jumpHeight, 5, lift);
  }
  arc(start, length, peak, count, lift = 0) {
    for (let i = 0; i < count; i++) {
      const s = (i + 1) / (count + 1);
      this.mango(start + s * length, lift + 0.55 + 4 * peak * s * (1 - s));
    }
  }
  inHole(x) { return this.holes.some(([a, b]) => x > a - 0.5 && x < b + 0.5); }
  litter(count) {
    const pieces = ['leaf_1', 'leaf_2', 'twigs', 'husk', 'footprints', 'hen_prints', 'pebbles', 'tuft_1', 'tuft_2'];
    for (let i = 0; i < count; i++) {
      const x = this.rand.nextDouble() * this.length;
      if (this.inHole(x)) continue;
      const piece = pieces[this.rand.next(pieces.length)];
      const z = -0.9 + this.rand.nextDouble() * 2.2;
      const w = 0.45 + this.rand.nextDouble() * 0.4;
      this.decal(piece, x, z, w, this.rand.nextDouble() * 360);
    }
  }
}

// ------------------------------------------------------------------ the chunks (GameBuilder.Chunks)
function jumpPots(k, x) { k.potStack(x); k.jumpArc(x); k.hop(x - 0.9, 1.8, 0.9); }
const CHUNKS = {
  Runway: z => { const k = new Kit('Runway', 24, z, 100 + z); k.mangoLine(14, 5, 2, 0.6); k.litter(6); return k.finish(); },
  Pots: z => { const k = new Kit('Pots', 16, z, 1); jumpPots(k, 5); jumpPots(k, 11); k.litter(3); return k.finish(); },
  DungAndDog: z => {
    const k = new Kit('DungAndDog', 18, z, 2);
    k.dung(4.5); k.jumpArc(4.5); k.hop(4, 1, 0.45); k.mangoLine(6.8, 3, 0.8, 0.55);
    k.dog(10.5); k.jumpArc(10.5); k.hop(9.7, 1.6, 0.8); k.feather(10.6, 2.8, 0); k.chilli(15, 0.6); k.litter(3);
    return k.finish();
  },
  Puddle: z => {
    const k = new Kit('Puddle', 18, z, 3);
    k.puddle(5, 1.6); k.jumpArc(5); k.hop(4, 2, 0.5); jumpPots(k, 12); k.feather(12.1, 2.8, 2); k.litter(3);
    return k.finish();
  },
  Clotheslines: z => {
    const k = new Kit('Clotheslines', 18, z, 4);
    k.clothesline(5); k.mangoLine(4.2, 3, 0.6, 0.3); k.clothesline(12); k.mangoLine(11.2, 3, 0.6, 0.3); k.litter(3);
    return k.finish();
  },
  CotBounce: z => {
    const k = new Kit('CotBounce', 20, z, 5);
    k.cot(3); k.arc(2.9, 4.8, 2.4, 6); k.hop(3, 4.8, 2.2); k.feather(5.8, 4.3, 2); jumpPots(k, 14);
    return k.finish();
  },
  Cart: z => {
    const k = new Kit('Cart', 18, z, 6);
    k.cart(4); k.mangoLine(4.4, 4, 0.5, 1.5); k.mangoLine(4.8, 3, 0.7, 2.9); k.hop(3.2, 4, 1.6); k.feather(7.2, 3.4, 1);
    jumpPots(k, 13.5);
    return k.finish();
  },
  Mischief: z => {
    const k = new Kit('Mischief', 20, z, 7);
    k.puddle(4, 1.6); k.jumpArc(4); k.hop(3, 2, 0.5);
    if (!k.art('water_pot_stand', 12.3, 0, 1.6, { height: 1.1 })) k.art('brass_pots', 12.3, 0, 1.6, { height: 0.5 });
    const knocked = k.potStack(12, true); k.mischiefAt(13, knocked);
    k.clothesline(17); k.mangoLine(16.2, 3, 0.6, 0.3);
    return k.finish();
  },
  ClothesAndPots: z => {
    const k = new Kit('ClothesAndPots', 20, z, 8);
    k.clothesline(4); k.mangoLine(3.2, 3, 0.6, 0.3); jumpPots(k, 10); k.clothesline(16); k.mangoLine(15.2, 3, 0.6, 0.3);
    return k.finish();
  },
  Houses: z => {
    const k = new Kit('Houses', 24, z, 9);
    const end = k.roofRow(5, ['', 'house_pink', 'house_limewash'], true);
    k.mangoLine(5.6, Math.floor((end - 6) / 0.65), 0.65, ROOF + 0.55); k.feather(end - 1, ROOF + 1.45, 2); jumpPots(k, end + 7);
    return k.finish();
  },
  RoofHop: z => {
    const k = new Kit('RoofHop', 26, z, 10);
    k.arc(1.2, 3.4, 2.6, 4);
    const end = k.roofRow(5, ['house_indigo_veranda', 'house_pink'], false);
    k.arc(end - 0.6, 3, 1.2, 3, ROOF);
    const end2 = k.roofRow(end + 1.8, ['house_limewash', 'house_indigo_veranda'], false);
    k.mangoLine(end + 2.4, 4, 0.7, ROOF + 0.55); k.chilli(end2 + 3, 0.6);
    return k.finish();
  },
  Canal: z => {
    const k = new Kit('Canal', 18, z, 21);
    k.canal(6, 2.5, false); k.jumpArc(7.25); k.feather(7.25, 3.1, 0); k.dung(14); k.jumpArc(14); k.hop(13.5, 1, 0.45);
    return k.finish();
  },
  BridgeCanal: z => { const k = new Kit('BridgeCanal', 18, z, 22); k.canal(6, 3.5, true); k.mangoLine(6.1, 5, 0.75, 0.55); k.litter(3); return k.finish(); },
  WideCanal: z => { const k = new Kit('WideCanal', 20, z, 23); k.canal(7, 4.5, false); k.arc(5.4, 7.6, 2.3, 7); k.feather(9.25, 3.5, 0); return k.finish(); },
  FieldDung: z => {
    const k = new Kit('FieldDung', 18, z, 24);
    k.dung(5); k.jumpArc(5); k.hop(4.5, 1, 0.45); k.dung(10.5); k.jumpArc(10.5); k.hop(10, 1, 0.45); k.chilli(15, 0.6); k.litter(3);
    return k.finish();
  },
  FieldCart: z => {
    const k = new Kit('FieldCart', 20, z, 25);
    k.cart(5); k.mangoLine(5.4, 4, 0.5, 1.5); k.hop(4.2, 4, 1.6); k.feather(8.4, 3.4, 1); k.dung(15); k.jumpArc(15); k.hop(14.5, 1, 0.45);
    return k.finish();
  },
  SmallHaystacks: z => {
    const k = new Kit('SmallHaystacks', 20, z, 26);
    k.haystack(4, false); k.mangoLine(4.1, 3, 0.45, 1.75); k.haystack(10, false); k.haystack(15, false); k.feather(15.6, 3.2, 2);
    return k.finish();
  },
  HaystackChain: z => {
    const k = new Kit('HaystackChain', 24, z, 27);
    k.haystack(3, false); const end = k.haystack(8, true); k.arc(6.5, 4.5, 2.4, 5); k.feather(end - 0.8, 3.7, 2);
    k.haystack(14, false); k.haystack(18.5, true);
    return k.finish();
  },
  MangoBranch: z => {
    const k = new Kit('MangoBranch', 20, z, 28);
    k.haystack(2.2, false); k.mangoTree(5); k.feather(9.3, 3.2, 1); k.dung(15); k.jumpArc(15); k.hop(14.5, 1, 0.45);
    return k.finish();
  },
  Buffalo: z => {
    const k = new Kit('Buffalo', 22, z, 29);
    const end = k.buffalo(6); k.arc(6.5, 7, 2.8, 6, 1.1); k.feather(end + 1.6, 4.4, 2); k.dung(17); k.jumpArc(17); k.hop(16.5, 1, 0.45);
    return k.finish();
  },
  FieldMischief: z => {
    const k = new Kit('FieldMischief', 22, z, 30);
    k.dung(4); k.jumpArc(4); k.hop(3.5, 1, 0.45); k.art('well', 12.4, 0, 2.2, { height: 2.0 });
    const knocked = k.potStack(12, true); k.mischiefAt(13, knocked); k.canal(16.5, 2.5, false); k.jumpArc(17.75);
    return k.finish();
  },
  RoofRun: z => {
    const k = new Kit('RoofRun', 30, z, 31);
    const end = k.roofRow(4, ['', 'house_indigo_veranda', 'house_pink', 'house_limewash'], true);
    k.tank(9.2, ROOF); k.arc(9.2 - 2.4, 4.8, 1.4, 5, ROOF); k.art('chilli_mat', end - 1.4, ROOF, 0.3, { height: 0.25 });
    const end2 = k.roofRow(end + 2, ['house_indigo_veranda', 'house_pink'], false);
    k.arc(end - 0.8, 3.6, 1.2, 4, ROOF); k.feather((end + 2 + end2) * 0.5, ROOF + 1.6, 0); k.chilli(end2 + 3, 0.6);
    return k.finish();
  },
  RoofTanks: z => {
    const k = new Kit('RoofTanks', 28, z, 32);
    const end = k.roofRow(3, ['', 'house_indigo_veranda', 'house_pink', 'house_indigo_veranda'], true);
    k.tank(6.6, ROOF); k.tank(end - 2, ROOF); k.art('papad_mat', 8.6, ROOF, 0.3, { height: 0.25 });
    const end2 = k.roofRow(end + 2.2, ['house_limewash', 'house_pink', 'house_indigo_veranda'], false);
    k.feather(end2 - 1.5, ROOF + 1.6, 1); k.mangoLine(end + 2.8, 5, 0.7, ROOF + 0.55);
    return k.finish();
  },
  MarketClotheslines: z => {
    const k = new Kit('MarketClotheslines', 20, z, 33);
    k.clothesline(5); k.mangoLine(4.2, 3, 0.6, 0.3); k.clothesline(12); k.feather(12, 2.7, 2); k.litter(3);
    return k.finish();
  },
  MarketPots: z => {
    const k = new Kit('MarketPots', 18, z, 34);
    k.potStack(4); k.potStack(4.7); k.jumpArc(4.35); k.hop(3.3, 2.1, 0.9); k.hensBasket(12); k.jumpArc(12); k.hop(11.2, 1.6, 0.8); k.litter(3);
    return k.finish();
  },
  Awnings: z => {
    const k = new Kit('Awnings', 24, z, 35);
    let x = 3;
    for (const s of ['stall_c_1', 'stall_d_2', 'stall_e_3']) x = k.stall(x, s) + 0.25;
    k.mangoLine(3.6, Math.floor((x - 4) / 1.1), 1.1, 3.4); k.feather(x - 2, 4.7, 2); k.hens(x + 3, 2); k.jumpArc(x + 3);
    return k.finish();
  },
  AwningsLong: z => {
    const k = new Kit('AwningsLong', 28, z, 36);
    let x = 2.5;
    for (const s of ['stall_f_1', 'stall_g_2', 'stall_h_1', 'stall_flowers']) x = k.stall(x, s) + 0.2;
    k.mangoLine(3, Math.floor((x - 3.5) / 1.1), 1.1, 3.5); k.feather(x * 0.5, 4.8, 2); k.chilli(x + 2, 0.6);
    return k.finish();
  },
  Hens: z => {
    const k = new Kit('Hens', 20, z, 37);
    k.hens(5, 3); k.jumpArc(5); k.hop(4.2, 1.6, 0.7); k.hensBasket(11); k.jumpArc(11); k.hop(10.2, 1.6, 0.8); k.feather(11, 2.9, 1);
    k.hens(16, 2); k.jumpArc(16); k.hop(15.3, 1.4, 0.7);
    return k.finish();
  },
  HensBaskets: z => {
    const k = new Kit('HensBaskets', 18, z, 38);
    k.hensBasket(4); k.hensBasket(4.8); k.jumpArc(4.4); k.hop(3.4, 2, 0.8); k.hens(12, 3); k.jumpArc(12); k.hop(11.2, 1.6, 0.7);
    return k.finish();
  },
  MarketMischief: z => {
    const k = new Kit('MarketMischief', 22, z, 39);
    const x = k.stall(2, 'stall_vessels'); k.feather((2 + x) * 0.5, 4.5, 0); k.art('hens_basket', 14.4, 0, 1.4, { height: 0.6 });
    const knocked = k.hensBasket(14, true); k.mischiefAt(15, knocked); k.clothesline(19.5); k.mangoLine(18.7, 3, 0.6, 0.3);
    return k.finish();
  },
  TempleSteps: z => {
    const k = new Kit('TempleSteps', 30, z, 40);
    k.art('mandapam', 11, 0, 3, { height: 2.9 });
    const end = k.steps(4, 6, 6); k.mangoLine(8.8, 7, 0.75, 2.05); k.feather(11.2, 3.6, 0); jumpPots(k, end + 5);
    return k.finish();
  },
};

const LEVELS = [
  { title: 'Pots and the sleeping dog', sub: 'Tap to jump. Hold for higher.', zone: 1, seed: 11, chunks: ['Pots', 'DungAndDog', 'Puddle', 'Cart'] },
  { title: 'Washing day', sub: 'Swipe down to slide. Bounce on the cot.', zone: 1, seed: 12, chunks: ['Clotheslines', 'CotBounce', 'DungAndDog', 'ClothesAndPots', 'Cart', 'Mischief'] },
  { title: 'Up on the roofs', sub: 'Ladders, roofs and the jump between them.', zone: 1, seed: 13, chunks: ['Houses', 'Clotheslines', 'CotBounce', 'RoofHop', 'Cart', 'Mischief', 'DungAndDog'] },
  { title: 'The canal', sub: 'Jump it, wade it, or take the plank.', zone: 2, seed: 21, chunks: ['Canal', 'BridgeCanal', 'FieldDung', 'WideCanal', 'FieldCart', 'SmallHaystacks'] },
  { title: 'Mango trees', sub: 'Jump at a branch to climb up for mangoes.', zone: 2, seed: 22, chunks: ['MangoBranch', 'SmallHaystacks', 'Canal', 'BridgeCanal', 'FieldDung', 'FieldCart'] },
  { title: 'Buffalo and haystacks', sub: "Bounce off a buffalo's back.", zone: 2, seed: 23, chunks: ['Buffalo', 'HaystackChain', 'FieldMischief', 'WideCanal', 'MangoBranch'] },
  { title: 'Rooftop run', sub: 'Mind the gaps and the water tanks.', zone: 3, seed: 31, chunks: ['RoofRun', 'MarketPots', 'RoofTanks', 'MarketClotheslines'] },
  { title: 'Market day', sub: 'Bounce across the awnings.', zone: 3, seed: 32, chunks: ['Awnings', 'Hens', 'AwningsLong', 'HensBaskets', 'MarketMischief'] },
  { title: 'The temple steps', sub: 'Everything at once. Catch him for good!', zone: 3, seed: 33, course: 800, chunks: ['TempleSteps', 'Awnings', 'RoofRun', 'Hens', 'MarketClotheslines', 'MarketPots', 'MarketMischief'] },
];

// ------------------------------------------------------------------ the course (LevelStreamer.BuildCourse)
class Course {
  constructor(levelIndex) {
    const L = LEVELS[levelIndex];
    this.level = L; this.zone = L.zone; this.t = tuningFor(L.zone);
    this.length = L.course || this.t.courseLength;
    const built = {};
    const chunk = name => (built[name] ||= CHUNKS[name](L.zone));
    const placements = [];
    let x = -10;
    const place = name => { placements.push({ name, x }); x += chunk(name).length; };
    place('Runway');
    const order = L.chunks.slice();
    const rand = new NetRandom(L.seed);
    let prev = null, i = 0;
    while (x < this.length) {
      if (i >= order.length) {
        i = 0;
        for (let k = order.length - 1; k > 0; k--) { const j = rand.next(k + 1); [order[k], order[j]] = [order[j], order[k]]; }
        if (order.length > 1 && order[0] === prev) { const s = 1 + rand.next(order.length - 1); [order[0], order[s]] = [order[s], order[0]]; }
      }
      const name = order[i++]; place(name); prev = name;
    }
    while (x < this.length + 40) place('Runway');
    this.end = x;
    // Lay every placement's parts into world space. Each placement gets its own obstacles and pickups.
    this.solids = []; this.obstacles = []; this.bouncers = []; this.waters = []; this.pickups = [];
    this.hops = []; this.mischief = []; this.cards = []; this.prims = []; this.holes = []; this.puddles = [];
    for (const p of placements) {
      const k = chunk(p.name), ox = p.x;
      const objMap = new Map();
      for (const s of k.solids) this.solids.push({ ...s, x0: s.x0 + ox, x1: s.x1 + ox });
      for (const o of k.obstacles) {
        const c = { ...o, x: o.x + ox, armed: !o.hidden, react: -1, reveal: -1, hidden: o.hidden };
        objMap.set(o, c); this.obstacles.push(c);
      }
      for (const b of k.bouncers) { const c = { ...b, x0: b.x0 + ox, x1: b.x1 + ox, squash: -1 }; objMap.set(b, c); this.bouncers.push(c); }
      for (const w of k.waters) this.waters.push({ ...w, x0: w.x0 + ox, x1: w.x1 + ox });
      for (const pk of k.pickups) this.pickups.push({ ...pk, x: pk.x + ox, taken: false, pop: -1 });
      for (const h of k.hops) this.hops.push({ start: h.x + ox, end: h.x + ox + h.length, length: h.length, height: h.height });
      for (const m of k.mischief) this.mischief.push({ x: m.x + ox, target: objMap.get(m.target), used: false });
      for (const c of k.cards) {
        const parent = c.parent ? objMap.get(c.parent) : null;
        // An obstacle's pictures sit relative to it (it can be knocked about); a cot's are placed in the chunk.
        const relative = !!(parent && parent.def);
        this.cards.push({ ...c, x: relative ? c.x : c.x + ox, parent, relative });
      }
      for (const pr of k.prims) this.prims.push({ ...pr, x0: pr.x0 + ox, x1: pr.x1 + ox });
      for (const [a, b] of k.holes) this.holes.push([a + ox, b + ox]);
      for (const pd of k.puddles) this.puddles.push({ ...pd, x: pd.x + ox, parent: objMap.get(pd.parent) });
    }
    this.hops.sort((a, b) => a.start - b.start);
  }
  reset() {
    for (const o of this.obstacles) { o.armed = !o.hidden; o.react = -1; o.reveal = -1; o.gone = false; }
    for (const b of this.bouncers) b.squash = -1;
    for (const p of this.pickups) { p.taken = false; p.pop = -1; }
    for (const m of this.mischief) m.used = false;
  }
  // Highest solid top at x that is at or below originY and within dist of it (a downward raycast).
  topBelow(x, originY, dist = Infinity) {
    let best = -Infinity;
    for (const s of this.solids) {
      if (x < s.x0 || x > s.x1 || s.y1 > originY + 1e-6 || s.y1 < originY - dist) continue;
      if (s.y0 < originY - 1e-6 && s.y1 > originY + 1e-6) continue;
      if (s.y1 > best) best = s.y1;
    }
    return best;
  }
  roosterGround(x) { const y = this.topBelow(x, 20); return y === -Infinity ? 0 : y; }
  hopAt(x) { for (const h of this.hops) { if (x >= h.start && x < h.end) return h; if (h.start > x) break; } return null; }
  mangoesBefore(x) { let n = 0; for (const p of this.pickups) if (p.kind === 'mango' && p.x < x) n++; return n; }
}

// ------------------------------------------------------------------ the kid (KidController + KidSpeedModel)
class Kid {
  constructor(course, t, events) {
    this.c = course; this.t = t; this.ev = events;
    this.r = 0.175; this.standH = 1.05; this.slideH = 0.525; this.stepH = 0.3; this.skin = 0.02; this.inset = 0.7;
    this.resetTo(0);
  }
  resetTo(x) {
    const gy = this.castGround(x, 3, 6);
    this.x = x; this.y = gy ?? 0; this.px = this.x; this.py = this.y;
    Object.assign(this, { vs: 0, vstep: 0, grounded: true, tsg: 0, jumpedSince: false, doubleUsed: false, rising: false, cut: false,
      held: false, jumpBuf: 0, slideReq: false, slideQueued: false, slideTimer: 0, grace: 0, stopping: false, inWater: false,
      wasWading: false, pose: 'run', speed: 0, penalty: 0, penaltyFactor: 1, boost: 0, vaultT: 0 });
  }
  get height() { return this.pose === 'slide' ? this.slideH : this.standH; }
  get wading() { return this.inWater && this.grounded; }
  get stumbling() { return this.penalty > 0; }
  get boosted() { return this.boost > 0; }
  get modelSpeed() { return this.t.kidRunSpeed * (this.penalty > 0 ? this.penaltyFactor : 1) * (this.boost > 0 ? 1 + this.t.boostSpeedBonus : 1); }
  pressJump() { this.jumpBuf = this.t.jumpBuffer; }
  pressSlide() { this.slideReq = true; }
  beginStop() { this.stopping = true; }
  beginDive() {
    this.pose = 'dive'; this.diveT = 0; this.diveFrom = [this.x, this.y];
    const top = this.y + this.t.maxVaultHeight + 0.5;
    this.diveGround = this.castGround(this.x + 1.3, top, top + 10) ?? this.y;
  }
  tick(dt) {
    this.px = this.x; this.py = this.y;
    this.grace = Math.max(0, this.grace - dt);
    if (this.penalty > 0) { this.penalty -= dt; if (this.penalty <= 0) { this.penalty = 0; this.penaltyFactor = 1; } }
    if (this.boost > 0) this.boost = Math.max(0, this.boost - dt);
    if (this.pose === 'dive') return this.tickDive(dt);
    if (this.pose === 'vault' || this.pose === 'climb') {
      this.jumpBuf = Math.max(0, this.jumpBuf - dt); this.slideReq = false; this.tickVault(dt); this.touch(true); return;
    }
    this.speed = this.stopping ? moveTowards(this.speed, 0, 12 * dt) : this.modelSpeed * (this.wading ? this.t.wadeSpeedFactor : 1);
    this.handleJump(dt); this.handleSlide(dt); this.gravity(dt);
    let dx = this.speed * dt;
    const wall = this.probeWall(dx);
    if (wall) {
      const rise = wall.topY - this.y;
      if (rise <= this.stepH + 1e-4) {
        this.y = wall.topY; this.vs = Math.max(0, this.vs); this.vstep = 0;
        this.x = Math.max(this.x + dx, wall.x - this.r * this.inset + this.skin); dx = 0;
      } else if (rise <= this.t.maxVaultHeight) { this.startVault(wall); return; }
      else dx = Math.max(0, wall.x - (this.x + this.r) - this.skin);
    }
    this.x += dx; this.y += this.vstep;
    this.updateGround(); this.touch(false);
    this.tsg = this.grounded ? 0 : this.tsg + dt;
    if (this.pose !== 'slide' || !this.grounded) this.pose = this.grounded ? 'run' : 'air';
    if (this.y < -10) this.resetTo(this.x);
  }
  handleJump(dt) {
    if (this.jumpBuf <= 0) return;
    const canGround = this.grounded || (this.tsg <= this.t.coyoteTime && !this.jumpedSince);
    if (canGround) {
      this.vs = JumpMath.jump(this.t); this.grounded = false; this.jumpedSince = true; this.rising = true; this.cut = false;
      this.jumpBuf = 0; this.slideQueued = false; if (this.pose === 'slide') this.pose = 'air'; this.ev.jumped();
    } else if (!this.doubleUsed) {
      this.vs = JumpMath.double(this.t); this.doubleUsed = true; this.rising = false; this.jumpBuf = 0; this.slideQueued = false; this.ev.jumped();
      if (this.ev.doubleJumped) this.ev.doubleJumped();
    } else this.jumpBuf -= dt;
  }
  handleSlide(dt) {
    if (this.slideReq) {
      this.slideReq = false;
      if (this.grounded) this.startSlide();
      else { this.vs = Math.min(this.vs, -this.t.fastDropSpeed); this.rising = false; this.slideQueued = true; }
    }
    if (this.pose === 'slide') { this.slideTimer -= dt; if (this.slideTimer <= 0) this.pose = 'run'; }
  }
  startSlide() { this.pose = 'slide'; this.slideTimer = this.t.slideDuration; this.slideQueued = false; }
  gravity(dt) {
    const start = this.vs;
    if (this.grounded) { this.vstep = start * dt; return; }
    let g = JumpMath.gravity(this.t);
    if (this.vs > 0 && this.rising) { if (!this.held) this.cut = true; if (this.cut) g *= JumpMath.lowMult(this.t); }
    else if (this.vs < 0) g *= this.t.fallGravityMultiplier;
    this.vs = Math.max(this.vs - g * dt, -this.t.maxFallSpeed);
    this.vstep = (start + this.vs) * 0.5 * dt;
    if (this.vs <= 0) this.rising = false;
  }
  updateGround() {
    if (this.vs > 0) { this.grounded = false; return; }
    const snap = this.grounded ? this.stepH : 0;
    const gy = this.castGround(this.x, this.y + this.stepH, this.stepH + snap + this.skin);
    if (gy !== null) {
      const wasAir = !this.grounded;
      Object.assign(this, { y: gy, vs: 0, grounded: true, jumpedSince: false, doubleUsed: false, rising: false, cut: false });
      if (wasAir) { this.ev.landed(); if (this.slideQueued) this.startSlide(); }
    } else this.grounded = false;
  }
  castGround(x, originY, dist) {
    const inset = this.r * this.inset;
    const a = this.c.topBelow(x + inset, originY, dist), b = this.c.topBelow(x - inset, originY, dist);
    const y = Math.max(a, b);
    return y === -Infinity ? null : y;
  }
  probeWall(dx) {
    const bottom = this.y + this.skin, top = this.y + this.height - 0.05, ox = this.x + this.r - this.skin, dist = dx + this.skin * 2;
    let wx = Infinity, lowest = Infinity, solid = null;
    for (let i = 0; i < 3; i++) {
      const ry = lerp(bottom, top, i / 2);
      for (const s of this.c.solids) {
        if (s.x0 <= ox || s.x0 > ox + dist || ry < s.y0 || ry > s.y1) continue;
        if (s.x0 < wx) { wx = s.x0; solid = s; lowest = Math.min(lowest, ry); }
      }
    }
    if (wx === Infinity) return null;
    const probeTop = this.y + this.t.maxVaultHeight + 0.5;
    const t = this.c.topBelow(wx + 0.05, probeTop, probeTop - this.y);
    return { x: wx, topY: t !== -Infinity && t >= lowest ? t : Infinity, solid };
  }
  startVault(wall) {
    const ladder = !!wall.solid.ladder;
    this.pose = ladder ? 'climb' : 'vault'; this.vaultT = 0;
    this.vaultDur = Math.max(0.01, ladder ? this.t.ladderClimbDuration : this.t.vaultDuration);
    this.vFrom = [this.x, this.y];
    const creep = this.t.kidRunSpeed * (ladder ? this.t.ladderSpeedFactor : this.t.vaultSpeedFactor) * this.vaultDur;
    this.vTo = [Math.max(this.x + creep, wall.x + this.r + 0.05), wall.topY];
    this.vs = 0; this.grounded = false; this.slideQueued = false;
    this.speed = (this.vTo[0] - this.vFrom[0]) / this.vaultDur;
    if (!ladder) this.ev.vaulted();
  }
  tickVault(dt) {
    this.vaultT += dt;
    const k = clamp01(this.vaultT / this.vaultDur), up = 1 - (1 - k) * (1 - k);
    this.x = lerp(this.vFrom[0], this.vTo[0], k * k); this.y = lerp(this.vFrom[1], this.vTo[1], up);
    if (k < 1) return;
    Object.assign(this, { pose: 'run', grounded: true, jumpedSince: false, doubleUsed: false, tsg: 0 });
  }
  tickDive(dt) {
    this.diveT += dt;
    const k = clamp01(this.diveT / 0.5);
    this.x = this.diveFrom[0] + 1.3 * (1 - (1 - k) * (1 - k));
    this.y = lerp(this.diveFrom[1], this.diveGround, k) + 0.35 * Math.sin(Math.PI * k);
    this.speed = k < 1 ? 2.6 : 0;
  }
  touch(pickupsOnly) {
    const h = this.height, x0 = this.x - this.r, x1 = this.x + this.r, y0 = this.y, y1 = this.y + h;
    for (const p of this.c.pickups) {
      if (p.taken || Math.abs(p.x - this.x) > 1) continue;
      const cy = Math.min(Math.max(p.y, y0 + this.r), y1 - this.r);
      if (Math.hypot(p.x - this.x, p.y - cy) < this.r + p.r) {
        p.taken = true; p.pop = 0;
        if (p.kind === 'chilli') this.boost = this.t.boostDuration;
        this.ev.collected(p);
      }
    }
    if (pickupsOnly) return;
    this.inWater = false;
    for (const b of this.c.bouncers) {
      if (b.x1 < x0 || b.x0 > x1 || b.y1 < y0 || b.y0 > y1) continue;
      if (this.stopping || this.vs > 0.5 || this.y > b.y1 + 0.2) continue;
      this.vs = JumpMath.bounce(this.t, b.height);
      Object.assign(this, { grounded: false, jumpedSince: true, doubleUsed: false, rising: false, cut: false, slideQueued: false, pose: 'air' });
      b.squash = 0; this.ev.bounced(b);
    }
    for (const w of this.c.waters) if (!(w.x1 < x0 || w.x0 > x1 || w.y1 < y0 || w.y0 > y1)) this.inWater = true;
    for (const o of this.c.obstacles) {
      if (!o.armed || this.grace > 0) continue;
      const ox0 = o.x - o.w / 2, ox1 = o.x + o.w / 2, oy0 = o.y + o.bottom, oy1 = oy0 + o.h;
      if (ox1 < x0 || ox0 > x1 || oy1 < y0 || oy0 > y1) continue;
      const dur = this.t.stumbleDuration * o.def.scale;
      if (this.penalty > 0) { this.penaltyFactor = Math.min(this.penaltyFactor, this.t.stumbleSpeedFactor); this.penalty = Math.max(this.penalty, dur); }
      else { this.penaltyFactor = this.t.stumbleSpeedFactor; this.penalty = dur; }
      this.grace = this.t.hitGracePeriod;
      o.armed = false; o.react = 0;
      this.ev.hit(o, this.t.kidRunSpeed * (1 - this.t.stumbleSpeedFactor) * dur);
    }
    if (this.wading && !this.wasWading) this.ev.splash();
    this.wasWading = this.wading;
  }
}

// ------------------------------------------------------------------ the rooster (RoosterBrain + RoosterMind)
class Rooster {
  constructor(course, t, events) { this.c = course; this.t = t; this.ev = events; this.resetTo(12); }
  resetTo(x) {
    Object.assign(this, { mood: 'running', moodT: 0, tauntCd: 0, panicCd: 0, panics: 0, taunts: 0, vs: 0, hop: null, speed: 0, act: 'idle' });
    this.x = x; this.y = this.c.roosterGround(x); this.px = this.x; this.py = this.y;
  }
  get airborne() { return this.hop !== null || this.act === 'wriggle'; }
  startChase() { this.act = 'chase'; this.ev.bark('BAWK!', this.x, this.y + 1, '#d9331a'); this.ev.feathers(this.x, this.y + 0.4, 6); }
  beginWriggle() { this.act = 'wriggle'; this.hop = null; this.vs = 7.5; this.ev.bark('BAWK BAWK!', this.x, this.y + 1.2, '#d9331a'); this.ev.feathers(this.x, this.y + 0.4, 14); }
  beginFlee() { this.act = 'flee'; this.ev.bark('COCK-A-DOODLE-DOO!', this.x, this.y + 1.2, '#d9331a'); }
  mindTick(dt, gap, canTaunt) {
    const t = this.t;
    let changed = false;
    this.tauntCd = Math.max(0, this.tauntCd - dt); this.panicCd = Math.max(0, this.panicCd - dt);
    if (this.mood === 'running') {
      if (gap > t.tauntDistance && this.tauntCd <= 0 && canTaunt) { this.mood = 'taunting'; this.moodT = t.tauntDuration; this.taunts++; changed = true; }
      else if (gap < t.panicDistance && this.panicCd <= 0 && this.panics < t.maxPanicBursts) { this.mood = 'panicking'; this.moodT = t.panicDuration; this.panics++; changed = true; }
    } else {
      this.moodT -= dt;
      if (this.moodT <= 0) {
        if (this.mood === 'taunting') this.tauntCd = t.tauntCooldown; else this.panicCd = t.panicCooldown;
        this.mood = 'running';
      }
    }
    if (changed && this.mood === 'taunting') this.ev.bark('cock-a-doodle-doo~', this.x, this.y + 1.1, '#d9331a');
    if (changed && this.mood === 'panicking') {
      this.ev.bark('SQUAWK!', this.x, this.y + 1.1, '#d9331a'); this.ev.feathers(this.x, this.y + 0.4, 10);
      if (this.ev.panicked) this.ev.panicked();
    }
    return this.mood === 'taunting' ? 0 : this.mood === 'panicking' ? t.roosterRunSpeed * t.panicSpeedMultiplier : t.roosterRunSpeed;
  }
  tick(dt, gap, kidX) {
    this.px = this.x; this.py = this.y;
    if (this.act === 'chase') {
      this.speed = this.mindTick(dt, gap, this.hop === null);
      const from = this.x; this.x += this.speed * dt; this.route(dt);
      for (const m of this.c.mischief) {
        if (m.used || !(m.x > from && m.x <= this.x)) continue;
        m.used = true;
        if (m.target && m.target.x - kidX >= this.t.mischiefMinKidDistance) {
          m.target.reveal = 0; this.ev.bark('CLATTER!', m.x + 1, 1, '#bf5933');
        }
      }
    } else if (this.act === 'wriggle') {
      this.speed = 5; this.x += 5 * dt; this.vs -= 16 * dt; this.y += this.vs * dt;
      const g = this.c.roosterGround(this.x);
      if (this.vs < 0 && this.y <= g) { this.y = g; this.vs = 0; this.act = 'flee'; }
    } else if (this.act === 'flee') {
      this.speed = this.t.roosterRunSpeed * 1.5; this.x += this.speed * dt; this.route(dt);
    }
  }
  route(dt) {
    if (this.hop && this.x >= this.hop.end) this.hop = null;
    if (!this.hop) {
      const h = this.c.hopAt(this.x);
      if (h && this.x - h.start <= 0.5) { this.hop = h; this.hopFrom = this.y; this.hopTo = this.c.roosterGround(h.end + 0.05); }
    }
    if (this.hop) {
      const k = clamp01((this.x - this.hop.start) / this.hop.length);
      this.y = lerp(this.hopFrom, this.hopTo, k) + this.hop.height * Math.sin(Math.PI * k);
      return;
    }
    const g = this.c.roosterGround(this.x);
    this.y = g > this.y ? g : moveTowards(this.y, g, 8 * dt);
  }
}

// ------------------------------------------------------------------ the autopilot for "Watch"
// Reads the course ahead like a player would: jumps pots, dung, hens and canals, slides under sarees, double jumps
// walls it cannot step onto, lets ladders climb, jumps at awnings to bounce across them and at branches to climb.
class Autopilot {
  constructor(game) { this.g = game; this.cool = 0; this.holdT = 0; this.pendingDouble = false; this.done = new Set(); }
  press(hold = 0.35) { const k = this.g.kid; k.pressJump(); k.held = true; this.holdT = hold; this.cool = 0.22; }
  tick(dt) {
    const k = this.g.kid, c = this.g.course, t = this.g.t;
    this.cool = Math.max(0, this.cool - dt);
    if (this.holdT > 0) { this.holdT -= dt; if (this.holdT <= 0) k.held = false; }
    if (this.pendingDouble && !k.grounded && k.vs < 1.2) { k.pressJump(); this.pendingDouble = false; this.cool = 0.2; return; }
    if (k.pose === 'vault' || k.pose === 'climb' || k.pose === 'dive' || k.stopping) return;
    if (!k.grounded || this.cool > 0) return;
    const L = JumpMath.lengthAt(t, Math.max(1, k.speed)), x = k.x, y = k.y;
    const ahead = (a, b) => a > x - 0.3 && a < x + 9;
    // Sarees: slide just before the line.
    for (const o of c.obstacles) {
      if (!o.armed || Math.abs(o.y - y) > 0.5 || !ahead(o.x, 0)) continue;
      const a = o.x - o.w / 2, b = o.x + o.w / 2;
      if (o.bottom >= 0.6) { if (a - x < 0.55 && a - x > 0) { k.pressSlide(); this.cool = 0.3; return; } continue; }
      const take = (a + b) / 2 - L / 2;
      if (x >= take - 0.05 && x < b) { this.press(); return; }
    }
    // Walls and ledges.
    for (const s of c.solids) {
      if (s.ground || s.bed || s.plank || s.x0 <= x || s.x0 > x + 6) continue;
      if (s.y0 > y + 1.0 && !s.branch) continue;
      const rise = s.y1 - y;
      if (rise <= 0.3 || s.ladder && !s.branch) continue;
      if (s.branch) { if (s.x0 - x < 1.6 && s.x0 - x > 0.6 && !this.done.has(s)) { this.done.add(s); this.press(); } continue; }
      if (rise <= 1.25) { if (s.x0 - x < L * 0.42) { this.press(); return; } }
      else if (rise <= t.maxVaultHeight && s.x0 - x < 1.9) { this.press(); this.pendingDouble = true; return; }
    }
    // Canals without a bridge, and gaps between roofs.
    for (const [a, b] of c.holes) {
      if (a <= x || a - x > 3) continue;
      const bridged = c.solids.some(s => s.plank && s.x0 <= a && s.x1 >= b);
      if (bridged) continue;
      if (b - a <= L - 1.2) { if (a - x < 0.45) { this.press(); return; } }
      else if (a - x < 0.5) { this.press(); this.pendingDouble = true; return; }
    }
    if (y > 0.5) {
      const edge = c.solids.find(s => !s.ground && Math.abs(s.y1 - y) < 0.05 && s.x0 <= x && s.x1 > x);
      if (edge) {
        let end = edge.x1;
        for (let more = true; more;) { more = false; for (const s of c.solids) if (Math.abs(s.y1 - y) < 0.05 && Math.abs(s.x0 - end) < 0.02) { end = s.x1; more = true; } }
        const next = c.solids.some(s => Math.abs(s.y1 - y) < 0.3 && s.x0 > end && s.x0 < end + 3.5);
        if (next && end - x < 0.45) { this.press(); return; }
      }
    }
    // Awnings and cots: jump under an awning to bounce across the row.
    for (const b of c.bouncers) {
      if (!b.awning || b.x0 < x || b.x0 - x > 1.2 || this.done.has(b)) continue;
      this.done.add(b); this.press(); return;
    }
  }
}
