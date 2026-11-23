"""Packs the art for the browser preview: the scenery of each zone (split like ZoneArtBuilder.cs), the pieces the
chunks use, the kid's and rooster's poses and the ground tiles, downscaled to what each needs on screen, with haze and
fades baked in, as WebP. Writes site/assets/*.webp and site/data.json."""
import json, math, pathlib, re, hashlib, sys
import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[2]
SITE = pathlib.Path(__file__).resolve().parent / 'build'
ASSETS = SITE / 'assets'
ASSETS.mkdir(parents=True, exist_ok=True)
for f in ASSETS.glob('*'): f.unlink()
HAZE = np.array([0.98, 0.765, 0.545]) * 255
MANIFEST = json.loads((ROOT / 'ArtSource/cutouts/lane/manifest.json').read_text())
FOLDERS = ["lane", "market", "fields", "animals", "people", "plants", "ground", "kid", "rooster", "textures"]
NEAR_PPM = 150.0      # pixels per metre for things on the lane
D0 = 14.0             # camera distance at the closest zoom

def cutout(name):
    for f in FOLDERS:
        p = ROOT / f'ArtSource/cutouts/{f}/{name}.png'
        if p.exists(): return p
    return None

made = {}
total = [0]
def bake(src, w_m, h_m, ppm, haze=0.0, fade_b=0.0, fade_s=0.0, maxdim=4096):
    """Returns the asset file name for this picture at this look."""
    src = pathlib.Path(src)
    im = Image.open(src).convert('RGBA')
    tw = max(4, min(im.width, round(w_m * ppm), maxdim))
    th = max(4, min(im.height, round(tw * im.height / im.width)))
    key = (str(src), tw, round(haze * 20) / 20, round(fade_b, 2), round(fade_s, 2))
    if key in made: return made[key]
    im = im.resize((tw, th), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32)
    h = round(haze * 20) / 20
    if h > 0: a[..., :3] = a[..., :3] * (1 - h) + HAZE * h
    if fade_b > 0:
        v = 1 - (np.arange(th) + 0.5) / th          # 0 at the bottom row
        f = np.clip(v / fade_b, 0, 1); f = f * f * (3 - 2 * f)
        a[..., 3] *= f[:, None]
    if fade_s > 0:
        u = (np.arange(tw) + 0.5) / tw
        d = np.minimum(u, 1 - u); f = np.clip(d / fade_s, 0, 1); f = f * f * (3 - 2 * f)
        a[..., 3] *= f[None, :]
    out = Image.fromarray(a.clip(0, 255).astype(np.uint8), 'RGBA')
    name = f'{src.stem}_{hashlib.md5(repr(key).encode()).hexdigest()[:6]}.webp'
    out.save(ASSETS / name, 'WEBP', quality=82, method=6)
    total[0] += (ASSETS / name).stat().st_size
    made[key] = name
    return name

def real_size(name, im_w, im_h):
    m = MANIFEST.get(name) if isinstance(MANIFEST.get(name), dict) else None
    aspect = im_w / im_h
    if m:
        if 'px' in m: aspect = m['px'][0] / m['px'][1]
        if m.get('px_per_m') and 'px' in m: return m['px'][0] / m['px_per_m'], m['px'][1] / m['px_per_m']
        if m.get('height_m'): return m['height_m'] * aspect, m['height_m']
        if m.get('width_m'): return m['width_m'], m['width_m'] / aspect
    return aspect, 1.0

# ------------------------------------------------------------------ scenery, split as ZoneArtBuilder does
LF, LB, NEAR_DEPTH = -2.0, 1.4, 11.0
zones = {}
for zone, layout in [(1, 'lane_zone1'), (2, 'fields_zone2'), (3, 'market_zone3')]:
    cards = json.loads((ROOT / f'Assets/ChickenRunner/Art/Layouts/{layout}.json').read_text())['cards']
    def keep(c):
        if c['layer'] in ('Characters', 'Ground'): return False
        if c['flat']: return zone != 2 or c['z'] < LF or c['z'] > LB
        return c['z'] <= LF or c['z'] >= LB
    cards = [c for c in cards if keep(c) and (ROOT / c['image']).exists()]
    wide = [c for c in cards if not c['flat'] and c['w'] >= 20]
    rest = [c for c in cards if c not in wide]
    tracks = []
    def pack(group, period):
        out = []
        for c in group:
            depth = max(c['z'], -4.0)
            ppm = NEAR_PPM * D0 / (D0 + depth) * 1.15
            img = bake(ROOT / c['image'], c['w'], c['h'], ppm, c['haze'], c['fade_bottom'], c['fade_sides'])
            out.append(dict(img=img, x=round(c['x'], 3), y=round(c['y'], 3), z=round(c['z'], 3), w=round(c['w'], 3),
                            h=round(c['h'], 3), m=int(c['mirror']), f=int(c['flat']), t=round(c['turn'], 1),
                            o=20 if c['z'] <= LF else 0))
        return dict(period=round(period, 3), min=round(min(c['x'] - c['w'] / 2 for c in group), 2),
                    max=round(max(c['x'] + c['w'] / 2 for c in group), 2),
                    reach=round((30 + max(c['z'] for c in group)) * 0.6 + 5, 1), cards=out)
    for z in sorted({round(c['z']) for c in wide}, reverse=True):
        g = sorted([c for c in wide if round(c['z']) == z], key=lambda c: c['x'])
        if len(g) > 1 and g[0]['image'] == g[-1]['image'] and g[0]['mirror'] == g[-1]['mirror']: g = g[:-1]
        step = (g[-1]['x'] - g[0]['x']) / (len(g) - 1) if len(g) > 1 else g[0]['w']
        tracks.append(pack(g, g[-1]['x'] - g[0]['x'] + step))
    near = [c for c in rest if c['z'] < NEAR_DEPTH]
    start = min(c['x'] for c in near) - 2; period = max(c['x'] for c in near) - start + 2
    tracks.append(pack([c for c in rest if start <= c['x'] < start + period], period))
    zones[zone] = dict(tracks=tracks)
    print(f'zone {zone}: {sum(len(t["cards"]) for t in tracks)} cards, {total[0]/1e6:.1f} MB so far', file=sys.stderr)

# ------------------------------------------------------------------ pieces the chunks use
PIECES = ["pot_stack", "dung", "dog_sleeping", "hand_pump", "clothesline", "rope_cot", "bullock_cart", "hen_1", "hen_2",
          "hen_3", "hens_basket", "black_tank", "house_turmeric_ladder", "house_pink", "house_limewash",
          "house_indigo_veranda", "haystack", "haystack_small", "buffalo_mud", "cracked_mud", "tree_mango_1",
          "stall_c_1", "stall_d_2", "stall_e_3", "stall_f_1", "stall_g_2", "stall_h_1", "stall_flowers", "stall_vessels",
          "lamp_step", "lantern", "mandapam", "chilli_mat", "papad_mat", "well", "water_pot_stand", "brass_pots",
          "leaf_1", "leaf_2", "twigs", "husk", "footprints", "hen_prints", "pebbles", "tuft_1", "tuft_2"]
pieces = {}
for name in PIECES:
    p = cutout(name)
    if p is None: print('missing piece', name, file=sys.stderr); continue
    im = Image.open(p)
    w, h = real_size(name, im.width, im.height)
    # Sized for the largest it is drawn in the chunks (houses 2.5 m, stalls 3 m, the tree 5.2 m).
    longest = {"tree_mango_1": 5.2, "mandapam": 2.9}.get(name, max(h, 0.5))
    scale = longest / h
    pieces[name] = dict(img=bake(p, w * scale, h * scale, NEAR_PPM * 1.2), w=round(w, 4), h=round(h, 4))

# ------------------------------------------------------------------ characters
def frames(names, height, ppm):
    first = Image.open(cutout(names[0]))
    px_per_m = first.height / height
    out = {}
    for n in names:
        p = cutout(n)
        if p is None: continue
        im = Image.open(p)
        out[n] = dict(img=bake(p, im.width / px_per_m, im.height / px_per_m, ppm), w=round(im.width / px_per_m, 4),
                      h=round(im.height / px_per_m, 4))
    return out
kid = frames(["run_contact", "run_passing", "jump_up", "fall", "land", "slide", "vault", "stumble", "dive"], 1.1, 230)
rooster = frames(["rooster_run_1", "rooster_run_2", "rooster_flutter", "rooster_crow", "rooster_startled",
                  "rooster_tumble", "rooster_peck", "rooster_strut"], 0.62, 300)

# ------------------------------------------------------------------ ground tiles
def tile(name, size=384):
    p = cutout(name)
    im = Image.open(p).convert('RGB').resize((size, size), Image.LANCZOS)
    out = f'tile_{name}.webp'; im.save(ASSETS / out, 'WEBP', quality=80, method=6)
    total[0] += (ASSETS / out).stat().st_size
    return out
tiles = dict(earth=tile('plain_red_earth'), paddy=tile('paddy_water'), water=tile('canal_water', 256))

# The title picture, for the cover before the first level loads.
ref = ROOT / 'ArtSource/references/F1_title_screen_v2.png'
if not ref.exists(): ref = ROOT / 'ArtSource/references/F1_title_screen.png'
cover = Image.open(ref).convert('RGB'); cover.thumbnail((1280, 1280))
cover.save(ASSETS / 'cover.webp', 'WEBP', quality=78, method=6); total[0] += (ASSETS / 'cover.webp').stat().st_size

(SITE / 'data.json').write_text(json.dumps(dict(zones=zones, pieces=pieces, kid=kid, rooster=rooster, tiles=tiles,
                                                 haze=[0.98, 0.765, 0.545]), separators=(',', ':')))
print(f'{len(list(ASSETS.glob("*")))} files, {total[0]/1e6:.1f} MB of images, data.json {(SITE/"data.json").stat().st_size/1e3:.0f} KB', file=sys.stderr)
