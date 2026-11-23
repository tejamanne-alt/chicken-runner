"""Packs the 3D kid's, rooster's and pickups' rendered frames into sprite sheets for the web version.

    ArtSource/blender/venv/bin/python Tools/WebPreview/pack_characters.py FRAMES_DIR

FRAMES_DIR holds kid/, rooster/ and pickups/ as written by ArtSource/tools/characters/build_character.py --frames and
pickups.py --frames. Each frame is cropped to what it shows and remembers its offset, so the sheets stay small.
Adds "characters" to build/data.json (and the sheets to build/sheets); run make_site.py afterwards.
"""
import json
import pathlib
import sys

from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
BUILD = HERE / "build"
FRAMES = pathlib.Path(sys.argv[1])
MAX, PAD = 4096, 2

data = json.loads((BUILD / "data.json").read_text())
# Drop the sheets from an earlier run of this script.
keep = [i for i, s in enumerate(data["sheets"]) if s["group"] != "chars"]
remap = {old: new for new, old in enumerate(keep)}
data["sheets"] = [data["sheets"][i] for i in keep]
data["sprites"] = {k: [remap[v[0]]] + v[1:] for k, v in data["sprites"].items() if v[0] in remap}
for f in (BUILD / "sheets").glob("chars_*.webp"):
    f.unlink()

frames = []          # (sprite name, cropped image, offset x, offset y)
characters = {}
for who in ("kid", "rooster"):
    meta = json.loads((FRAMES / who / "frames.json").read_text())
    clips = {}
    for clip, info in meta["clips"].items():
        names = []
        for name in info["frames"]:
            im = Image.open(FRAMES / who / name).convert("RGBA")
            box = im.getbbox() or (0, 0, 1, 1)
            frames.append((name, im.crop(box), box[0], box[1]))
            names.append(name)
        clips[clip] = {"frames": names, "loop": info["loop"], "fps": info["fps"]}
    characters[who] = {"ppm": meta["pixelsPerMetre"], "anchor": meta["anchor"], "size": meta["size"], "clips": clips}
meta = json.loads((FRAMES / "pickups" / "pickups.json").read_text())
characters["pickups"] = {"ppm": meta["pixelsPerMetre"], "anchor": meta["anchor"], "size": meta["size"], "items": {}}
for item, info in meta["items"].items():
    for name in info["frames"]:
        im = Image.open(FRAMES / "pickups" / name).convert("RGBA")
        box = im.getbbox() or (0, 0, 1, 1)
        frames.append((name, im.crop(box), box[0], box[1]))
    characters["pickups"]["items"][item] = info["frames"]

frames.sort(key=lambda t: -t[1].height)
pages, cur = [], None
for name, im, ox, oy in frames:
    w, h = im.width + 2 * PAD, im.height + 2 * PAD
    if cur is None or cur["x"] + w > MAX and cur["y"] + cur["row"] + h > MAX:
        cur = {"im": Image.new("RGBA", (MAX, MAX)), "x": 0, "y": 0, "row": 0, "w": 0, "h": 0}
        pages.append(cur)
    if cur["x"] + w > MAX:
        cur["x"], cur["y"], cur["row"] = 0, cur["y"] + cur["row"], 0
    cur["im"].paste(im, (cur["x"] + PAD, cur["y"] + PAD))
    sheet_index = len(data["sheets"]) + len(pages) - 1
    data["sprites"][name] = [sheet_index, cur["x"] + PAD, cur["y"] + PAD, im.width, im.height, ox, oy]
    cur["x"] += w
    cur["row"] = max(cur["row"], h)
    cur["w"], cur["h"] = max(cur["w"], cur["x"]), max(cur["h"], cur["y"] + cur["row"])
for i, page in enumerate(pages):
    name = f"chars_{i}.webp"
    page["im"].crop((0, 0, page["w"], page["h"])).save(BUILD / "sheets" / name, "WEBP", quality=86, method=4)
    data["sheets"].append({"file": name, "group": "chars"})
data["characters"] = characters
(BUILD / "data.json").write_text(json.dumps(data, separators=(",", ":")))
size = sum((BUILD / "sheets" / f"chars_{i}.webp").stat().st_size for i in range(len(pages)))
print(f"{len(frames)} frames on {len(pages)} sheets, {size / 1e6:.1f} MB")
