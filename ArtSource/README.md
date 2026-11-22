# Art source

Source art for the Blender pipeline. It lives outside `Assets/` on purpose: Unity would import every image in
`Assets/` as a game texture, and these are references, not game assets.

| Folder | What goes in it |
| --- | --- |
| `references/` | The ChatGPT or Gemini images from [the prompt sheet](../docs/art/prompt-sheet.md), exactly as generated and named as the sheet says (`A1_key_art.png`, `C4_house_kit_elevations.png` …). One flat folder: the ID at the start of each name keeps them in order. |
| `supplied/` | Your own files: the kid reference art, the rooster photo and the kid model (FBX or `.blend`, with its rig). |
| `cutouts/` | Pieces cut from the reference sheets with alpha: house fronts, props, kolam, trees, animals, the palm layer in slices, the kid's poses and A0 views, the seamless lane ground, and seamless texture tiles (`cutouts/textures/`) for the built houses. Made by `tools/cutouts.py`. |
| `blender/` | The Blender scenes, built by script from the cut-outs (`lane_zone1.blend`), and their preview renders in `blender/renders/`. |
| `tools/` | The scripts that make the two folders above. |

Finished, game-ready exports (FBX models, cleaned textures) go into `Assets/ChickenRunner/Art/` instead.

Images, models and `.blend` files are stored with Git LFS (see `.gitattributes`). Run `git lfs install` once on
your machine before committing them; without it they go into the repository as ordinary files and make every
clone slower.

## Rebuilding

The scripts run with Blender's Python module (`pip install bpy==5.3.0 pillow numpy scipy`, Python 3.13):

```bash
python ArtSource/tools/cutouts.py
python ArtSource/tools/build_lane_scene.py
```

The first cuts the reference sheets into `cutouts/`. The second builds `blender/lane_zone1.blend` and renders the previews
(Cycles; add `--samples 16` for a quick look, `--only gameplay` for one view, `--no-render` to only build, `--seed 4`
for a different street).

## Keeping the street natural and from repeating

The street is generated, not laid out by hand, so it never shows the same thing twice in view, and it has room to
breathe. Everything in it that stands for a house or a tree comes from the reference art:

- **Houses** are the painted fronts cut from the references, all facing the street square on: the four from the C4
  kit, G4, G5 and G6, each scaled by its door so it matches the kid. G1-G3 came out three-quarter on and wait until
  they're drawn again front-on. The village head's house (G5) stands once per street, near where the chase starts. The
  others are dealt like cards: each comes up once before any comes back, the G houses first, and none appears twice in
  any 45 m. More houses (G7 onwards) join the deck as they arrive.
- **Spacing**: 0.8-2.4 m of open ground between houses, and every 2-4 houses a wider break: a compound wall, a gateway
  or a yard with hens. Setbacks run from 4.3 to 6.8 m.
- **Compounds**: some of the huts and mud houses (G1-G4; for now only G4) sit back in a yard fenced with woven dried coconut leaves (or
  split-bamboo matting), with an opening at the door; never two side by side.
- **Trees** are the two D4 mango trees, at least 30 m apart, and the painted palm groves of the C3 middle layer.
  Coconut palms, neem and other trees go in when H1 and H4 arrive.
- **The ground** is built in the shader (`tools/ground.py`), not tiled from T1, whose footprints and tyre track
  repeated every 3 m: earth tones in patches 10-20 m across, dusty and compacted patches, the painted mud tile's
  brush grain at two scales and angles, pebble specks, two cart ruts that wander along the lane, a worn path and grassy
  verges. Real 3D pebbles lie in loose drifts and grass tufts grow along walls, fences and the lane's edges.
- Kolam, hens and doorstep props come from pools that skip their last few picks, and are mirrored and scaled.

`tools/village_kit.py` builds the compound walls and palm-leaf fences. It can also build houses and coconut palms in 3D
(see `tools/build_house_catalog.py`), but the street doesn't use them: houses and trees come only from the art.
