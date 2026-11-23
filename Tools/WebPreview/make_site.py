"""Assembles the public web version in Web/ from src/ and the packed art in build/ (made by build_assets.py, then
atlas.py). Web/ is a plain static site: index.html, data.json, sheets/*.webp and assets/tile_*.webp.

    python Tools/WebPreview/build_assets.py   # slow: about 15 minutes, only after the art or layouts change
    python Tools/WebPreview/atlas.py
    python Tools/WebPreview/make_site.py
"""
import pathlib, shutil
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SRC, BUILD, WEB = HERE / 'src', HERE / 'build', ROOT / 'Web'

page = (SRC / 'page.html').read_text()
head, body = page.split('</style>', 1)
script = (SRC / 'game.js').read_text() + '\n' + (SRC / 'main.js').read_text()
body = body.replace('/*GAME_JS*/\n/*MAIN_JS*/', script)
html = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        + head + '</style>\n<script>window.CR_DEFAULT_MODE = "play";</script>\n</head>\n<body>' + body + '</body>\n</html>\n')

for sub in ('sheets', 'assets'):
    if (WEB / sub).exists(): shutil.rmtree(WEB / sub)
    (WEB / sub).mkdir(parents=True)
(WEB / 'index.html').write_text(html)
shutil.copy(BUILD / 'data.json', WEB / 'data.json')
for f in (BUILD / 'sheets').glob('*.webp'): shutil.copy(f, WEB / 'sheets' / f.name)
for f in (BUILD / 'assets').glob('tile_*.webp'): shutil.copy(f, WEB / 'assets' / f.name)
# The site's pictures stay in plain git, not LFS, so a host that builds from the repository serves the images
# themselves rather than LFS pointer files.
(WEB / '.gitattributes').write_text('*.webp !filter !diff !merge binary\n')
(WEB / 'vercel.json').write_text('{\n  "headers": [\n    { "source": "/sheets/(.*)", "headers": [{ "key": "Cache-Control", "value": "public, max-age=604800" }] }\n  ]\n}\n')
print('Web/ built:', sum(f.stat().st_size for f in WEB.rglob('*') if f.is_file()) // 1000, 'KB')
