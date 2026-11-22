# Art source

Source art for the Blender pipeline. It lives outside `Assets/` on purpose: Unity would import every image in
`Assets/` as a game texture, and these are references, not game assets.

| Folder | What goes in it |
| --- | --- |
| `references/` | The ChatGPT or Gemini images from [the prompt sheet](../docs/art/prompt-sheet.md), exactly as generated and named as the sheet says (`A1_key_art.png`, `C4_house_kit_elevations.png` …). One flat folder: the ID at the start of each name keeps them in order. |
| `supplied/` | Your own files: the kid reference art, the rooster photo and the kid model (FBX or `.blend`, with its rig). |
| `cutouts/` | Pieces cut from the reference sheets with alpha: house fronts, props, kolam, the palm layer, the kid's poses and A0 views, and the seamless lane ground. Made by `tools/cutouts.py`. |
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
(Cycles; add `--samples 16` for a quick look, `--only gameplay` for one view, `--no-render` to only build).
