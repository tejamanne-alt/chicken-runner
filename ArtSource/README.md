# Art source

Source art for the Blender pipeline. It lives outside `Assets/` on purpose: Unity would import every image in
`Assets/` as a game texture, and these are references, not game assets.

| Folder | What goes in it |
| --- | --- |
| `references/` | The ChatGPT or Gemini images from [the prompt sheet](../docs/art/prompt-sheet.md), exactly as generated and named as the sheet says (`A1_key_art.png`, `C4_house_kit_elevations.png` …). One flat folder: the ID at the start of each name keeps them in order. |
| `supplied/` | Your own files: the kid reference art, the rooster photo and the kid model (FBX or `.blend`, with its rig). |
| `placeholders/` | Stand-ins for images not made yet, named as the prompt sheet names them and laid out as each prompt asks. Made by `tools/placeholders.py`; used only until the real image is in `references/`. |
| `cutouts/` | Pieces cut from the references with alpha, by kind: `lane/` (house fronts, props, kolam, middle layers), `plants/`, `animals/`, `people/`, `ground/` (things lying on the ground), `fields/`, `market/`, `kid/`, and seamless `textures/`. Made by `tools/cutouts.py`; sizes and scales are in `lane/manifest.json`. |
| `blender/` | The Blender scenes, built by script from the cut-outs (`lane_zone1.blend`, `fields_zone2.blend`, `market_zone3.blend`), and their preview renders in `blender/renders/`. |
| `tools/` | The scripts that make the folders above. |

Finished, game-ready exports (FBX models, cleaned textures) go into `Assets/ChickenRunner/Art/` instead.

Images, models and `.blend` files are stored with Git LFS (see `.gitattributes`). Run `git lfs install` once on
your machine before committing them; without it they go into the repository as ordinary files and make every
clone slower.

## Rebuilding

The scripts run with Blender's Python module (`pip install bpy==5.3.0 pillow numpy scipy`, Python 3.13):

```bash
python ArtSource/tools/placeholders.py
python ArtSource/tools/cutouts.py
python ArtSource/tools/build_lane_scene.py
python ArtSource/tools/build_fields_scene.py
python ArtSource/tools/build_market_scene.py
```

The first draws the placeholders, the second cuts the references into `cutouts/`, and the others build one zone each
and render its previews (Cycles; add `--samples 16` for a quick look, `--only gameplay` for one view, `--no-render` to
only build, `--seed 4` for a different street). What the scene builders share (cards, haze, middle layers, light,
camera, rendering) is in `tools/stage.py`.

## The era

The game is set in a South Indian village of the 1970s and 1980s, like a vintage storybook. Every prompt says so, and
nothing modern goes into the scenes: no plastic (buckets, chairs, sheets, black water tanks), no concrete or half-built
multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights or printed posters. So the
half-built concrete house (the old G12) and the overhead water tank (the old G16) are no longer used; their prompts now
ask for a house being built with mud bricks and a bamboo scaffold, and a stone lamp pillar. The black plastic water
tanks in E1 and E4 are left out too.

Striped awnings are out too: red-and-white stripes look like a modern or Western market, not a 1970s Indian village.
Every prompt now asks for plain faded cotton, palm-leaf mats, thatch or black cloth umbrellas instead, and the striped
stalls already made (the two in E5, E8's vegetable stall, E9's sweets stall) are marked `"striped": true` in the
manifest and left out of the scenes.

## Into Unity

Each scene builder also writes its painted cards to `Assets/ChickenRunner/Art/Layouts/<zone>.json` (position, size,
mirroring, haze and fades of every card). In Unity, **Chicken Runner > Import Art Layouts** copies the art each layout
uses into `Assets/ChickenRunner/Art/Textures/`, makes materials with the `ChickenRunner/PaintedCard` shader (the art
unlit, as painted, faded into the haze like in Blender) and saves a prefab per zone in `Assets/ChickenRunner/Art/Prefabs/`,
cards grouped by layer. Place it at the origin of a level scene: its lane runs along +X at depth 0, as the grey-box's
does. Not exported yet: the ground and water (made in Blender's shaders) and the 3D bits (walls, fences, pebbles,
grass); they need baking to textures or meshes first.

## Placeholders, and swapping in the real images

Every tool loads a reference through `tools/refs.py`: the real image in `references/` when there is one, else its
placeholder in `placeholders/`. So the scenes are complete before all the art exists, and a new image takes its
placeholder's place just by being pushed under the sheet's file name and re-running the cut-outs and scenes. Pieces cut
from a placeholder are marked `"placeholder": true` in the manifest, and are labelled in the renders.

An image that came out wrong and is being made again (D7 and H3 so far) is listed with its hash in
`placeholders/rejected.json`: until a new version with a different hash is pushed, its placeholder is used instead,
and the prompt sheet keeps it marked "make again".

| Placeholder for | Used in |
| --- | --- |
| D7 fields middle layer | the fields scene's middle distance |
| H3 peepal on its platform | a landmark in a break on the lane |
| E6, E7 rooftop houses | the houses behind the market |
| G12 house being built, G16 stone lamp pillar | the lane (G12 in the deck of houses, G16 seen over the rooftops) |
| E8, E9 market stalls | the market row |
| E10 temple street | the end of the market, before the temple steps |
| T10, T11, T12 textures | not used: the scenes keep their own stand-ins (the woven fence, the shader-made ground) until the real textures arrive |
| F7, F8 story frames | not used yet |

## The rooster

`cutouts/rooster/` holds the B1 side view and the eight B2 poses (two run frames, flutter, crow, startled, tumble,
peck, strut), all facing right, the way the chase runs. Every scene puts the rooster 8 m ahead of the kid, as the
chase camera frames them in play.

## The three zones

- **Zone 1, the lane** (`build_lane_scene.py`): see below.
- **Zone 2, fields and canal** (`build_fields_scene.py`): the kid runs along a raised earthen bund between flooded
  paddy. Canals 2.5, 3.5 and 4.5 m wide cross it (the design doc's widths), one with a plank bridge, one by a sluice
  gate. A haystack, a buffalo and a scarecrow stand on the bund. Each field has its own crop (young, tall or ripe
  paddy, sugarcane, or open water), in rows of D6 cards; the water between them is made in the shader (sky reflection,
  muddy drifts, ripples, seedling rows), so it never repeats. In front of the bund only young paddy grows, low enough
  to stay under the kid's feet in the game view. Behind: the D5 field buildings, haystacks, a well and a scarecrow,
  mango, neem and tamarind trees, rows of palmyra and coconut palms, then the D7 band and the D2 far layer. The haze
  starts later here (10 m) than in the lane, as open fields see further.
- **Zone 3, market day and the temple street** (`build_market_scene.py`): stalls on the lane whose palm-leaf and
  thatch shades the kid bounces across, and baskets of hens; behind, a row of stalls of every kind (E8, E9 and the E5 stalls) with goods and
  bunting, then two-storey houses with flat roofs (E6, E7); near the end the temple street (E10) and lamp-lit steps,
  with the temple tower in the far layer. Villagers, animals, kites over the roofs.

## Keeping the street natural and from repeating

The street is generated, not laid out by hand, so it never shows the same thing twice in view, and it has room to
breathe. Everything in it that stands for a building, a tree or a plant comes from the reference art:

- **Buildings** are the painted fronts cut from the references (`cutouts/lane/`), all facing the street square on:
  the four from the C4 kit and G1-G16, each scaled to match the kid (mostly by its door). Landmarks stand once per
  street: the village head's house (G5) near the start, the panchayat office (G14) further on, the shrine under its
  tree (G15) in a break, and the stone lamp pillar (G16) seen over the rooftops. The peepal on its platform (H3) joins them once
  it's drawn front-on.
- The rest are dealt like cards: each comes up once before any comes back, none twice in any 45 m, and never two of a
  kind side by side (huts, mud houses, tiled houses, shops, sheds).
- **Spacing**: 0.8-2.4 m of open ground between buildings, and every 2-4 a wider break: a compound wall, a gateway,
  a yard with hens, or a grove, each with a tree. Setbacks run from 4.3 to 6.8 m.
- **Compounds**: some huts and mud houses sit back in a yard fenced with woven dried coconut leaves (or split-bamboo
  matting), with an opening at the door, coconut palms and a garden plant inside; never two side by side.
- **Trees and plants** (`cutouts/plants/`): H1 neem, H2 tamarind and drumstick, H4 coconut palms and the D4 mangoes;
  H5 garden plants and H6 flowering bushes at house corners; a few H7 low plants and stones 6-7 m in front of the
  lane, which in the game view rise into the bottom of the screen and stay below the kid's feet. Each pool skips its last few picks, and pieces are mirrored and scaled a little.
- **Distance**: three painted middle layers stand behind the houses, each further back: C3 palm clumps scattered at
  12-13 m, clusters of the C8 village (tiled roofs and banana groves) at 15 m, and the C9 band (big shade trees, small
  houses, a hillock with a shrine) at 29 m, repeated mirrored. C8 is used as two slices without its water tower,
  which is too modern for the 1970s. Every layer's foot, and each C8 cluster's ends, fade out instead of ending in a line.
- **Haze**: everything fades into the warm haze painted at the foot of the C2 far layer by the same amount as the ground
  under it (none in front of the houses, all of it where the ground ends at 40 m), so nothing looks pasted on and
  there's no horizon line.
- **The ground** is built in the shader (`tools/ground.py`), not tiled from T1, whose footprints and tyre track
  repeated every 3 m: earth tones in patches 10-20 m across, dusty and compacted patches, the painted mud tile's
  brush grain at two scales and angles, pebble specks, two cart ruts that wander along the lane, a worn path and grassy
  verges. Real 3D pebbles lie in loose drifts and grass tufts grow along walls, fences and the lane's edges.
- **Life**: yard animals (B8, B9) in the open breaks, never two of a kind side by side; a cat and crows on walls, a goat
  on a wall, a peacock and a squirrel in the groves, once each; each villager (B10) once per street, by doorsteps or
  walking along the verge; things lying on the ground (C10: leaves, twigs, husks, pebbles, footprints, hoof and hen
  prints, cart ruts, cracked mud) every few metres, at any angle, with prints and ruts along the lane.
- Kolam, hens and doorstep props come from pools that skip their last few picks, and are mirrored and scaled.

`tools/village_kit.py` builds the compound walls and palm-leaf fences. It can also build houses and coconut palms in 3D
(see `tools/build_house_catalog.py`), but the street doesn't use them: buildings and trees come only from the art.
