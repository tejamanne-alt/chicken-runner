"""Packs site/assets/*.webp into a few sprite sheets per group (shared pieces, then each zone's scenery) and rewrites
site/data.json to point at them. Ground tiles stay separate (they repeat as patterns)."""
import json, pathlib
from PIL import Image
site = pathlib.Path(__file__).resolve().parent / 'build'; src = site / 'assets'
out = site / 'sheets'; out.mkdir(exist_ok=True)
for f in out.glob('*'): f.unlink()
d = json.loads((site / 'data.json').read_text())
groups = {'common': [p['img'] for p in d['pieces'].values()] + [p['img'] for p in d['kid'].values()] + [p['img'] for p in d['rooster'].values()]}
for z, v in d['zones'].items(): groups[f'zone{z}'] = [c['img'] for t in v['tracks'] for c in t['cards']]
seen, sprites, sheets = set(), {}, {}
MAX, PAD = 4096, 2
for g, names in groups.items():
    names = [n for n in dict.fromkeys(names) if n not in seen]; seen.update(names)
    ims = sorted(((n, Image.open(src / n).convert('RGBA')) for n in names), key=lambda t: -t[1].height)
    pages, cur = [], None
    def new_page():
        p = {'im': Image.new('RGBA', (MAX, MAX), (0, 0, 0, 0)), 'x': 0, 'y': 0, 'row': 0, 'used_w': 0, 'used_h': 0}
        pages.append(p); return p
    for n, im in ims:
        w, h = im.width + PAD * 2, im.height + PAD * 2
        if cur is None: cur = new_page()
        if cur['x'] + w > MAX: cur['x'] = 0; cur['y'] += cur['row']; cur['row'] = 0
        if cur['y'] + h > MAX: cur = new_page()
        cur['im'].paste(im, (cur['x'] + PAD, cur['y'] + PAD))
        sprites[n] = [len(sheets) + len(pages) - 1, cur['x'] + PAD, cur['y'] + PAD, im.width, im.height]
        cur['x'] += w; cur['row'] = max(cur['row'], h)
        cur['used_w'] = max(cur['used_w'], cur['x']); cur['used_h'] = max(cur['used_h'], cur['y'] + cur['row'])
    for i, p in enumerate(pages):
        name = f'{g}_{i}.webp'
        p['im'].crop((0, 0, p['used_w'], p['used_h'])).save(out / name, 'WEBP', quality=82, method=4)
        sheets[len(sheets)] = {'file': name, 'group': g}
d['sheets'] = [sheets[i] for i in range(len(sheets))]
d['sprites'] = sprites
(site / 'data.json').write_text(json.dumps(d, separators=(',', ':')))
tot = sum((out / s['file']).stat().st_size for s in d['sheets'])
print(len(d['sheets']), 'sheets', round(tot / 1e6, 1), 'MB', [(s['file'], round((out / s['file']).stat().st_size / 1e6, 1)) for s in d['sheets']])
