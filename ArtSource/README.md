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

## Keeping the street from repeating

The street is generated, not laid out by hand, so it never shows the same thing twice in view:

- **Built houses** come from `tools/village_kit.py`, which builds six kinds in 3D, each with its own ranges of size,
  colour, roof and details: round or square thatched huts; orange mud houses under tin sheets (shed or gable roofs,
  silver, faded blue or green, stones and a tyre on top, often a plank lean-to); tiled houses, some with a pillared
  veranda; parapet houses; petty shops (counter, sweet jars, shelves, sachet strips, a striped or tin awning); and the
  village head's two-storey house with its raised pillared veranda.
- No kind comes back within three houses, a shop at most every 20 m, the head's house once per street. No house takes
  either of its two neighbours' wall colours, and a kind never reuses one of its own last three colours.
- **Painted fronts** from the reference art appear at most once in any 45 m.
- Every 3 to 5 houses the row breaks for a compound wall, a gateway or an open yard with hens.
- **Trees** stand at least 30 m apart (there are only two tree pictures until H1 and H4 arrive). Palm clumps, kolam,
  hens and doorstep props come from pools that skip their last few picks, and are mirrored and scaled.

To check the kit on its own, `python ArtSource/tools/build_house_catalog.py --seed 3` renders a row of every kind
to `blender/renders/house_catalog_seed3.png`; another seed gives another set.
