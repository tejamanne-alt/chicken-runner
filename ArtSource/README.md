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
breathe. Everything in it that stands for a building, a tree or a plant comes from the reference art:

- **Buildings** are the painted fronts cut from the references (`cutouts/lane/`), all facing the street square on:
  the four from the C4 kit and G1-G16, each scaled to match the kid (mostly by its door). Landmarks stand once per
  street: the village head's house (G5) near the start, the panchayat office (G14) further on, the shrine under its
  tree (G15) and the peepal on its platform (H3) in breaks, and the water tank (G16) behind the houses.
- The rest are dealt like cards: each comes up once before any comes back, none twice in any 45 m, and never two of a
  kind side by side (huts, mud houses, tiled houses, shops, sheds).
- **Spacing**: 0.8-2.4 m of open ground between buildings, and every 2-4 a wider break: a compound wall, a gateway,
  a yard with hens, or a grove, each with a tree. Setbacks run from 4.3 to 6.8 m.
- **Compounds**: some huts and mud houses sit back in a yard fenced with woven dried coconut leaves (or split-bamboo
  matting), with an opening at the door, coconut palms and a garden plant inside; never two side by side.
- **Trees and plants** (`cutouts/plants/`): H1 neem, H2 tamarind and drumstick, H4 coconut palms and the D4 mangoes;
  H5 garden plants and H6 flowering bushes at house corners; a few H7 low plants and stones in front of the lane, clear
  of the obstacles. Each pool skips its last few picks, and pieces are mirrored and scaled a little.
- **Distance**: a row of trees and palms right behind the houses, then the C3 middle layer 12-15 m back, reshuffled in
  clumps with their bushy feet sunk into the ground. The ground fades into the haze painted at the foot of the C2 far
  layer, reaching it where the ground ends, so there's no horizon line.
- **The ground** is built in the shader (`tools/ground.py`), not tiled from T1, whose footprints and tyre track
  repeated every 3 m: earth tones in patches 10-20 m across, dusty and compacted patches, the painted mud tile's
  brush grain at two scales and angles, pebble specks, two cart ruts that wander along the lane, a worn path and grassy
  verges. Real 3D pebbles lie in loose drifts and grass tufts grow along walls, fences and the lane's edges.
- Kolam, hens and doorstep props come from pools that skip their last few picks, and are mirrored and scaled.

`tools/village_kit.py` builds the compound walls and palm-leaf fences. It can also build houses and coconut palms in 3D
(see `tools/build_house_catalog.py`), but the street doesn't use them: buildings and trees come only from the art.
