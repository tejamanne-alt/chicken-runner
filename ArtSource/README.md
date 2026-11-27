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
does. Not exported yet: the 3D bits (walls, fences, pebbles, grass); they need baking to textures or meshes first.

**Chicken Runner > Build Game** uses the same layouts for the game's scenery. It leaves out what stood on the lane in
the previews (the obstacles, the kid and rooster: the levels' chunks put the real ones there), turns the distant bands
(cards 20 m wide or more) into strips that repeat without a seam, and repeats the rest as one set every stretch the
scene covers. The ground is redone in Unity by the `ChickenRunner/PaintedGround` shader from `plain_red_earth` (T12),
`paddy_water` and `canal_water` (T6). The kid's and rooster's poses and the obstacles' cut-outs are used directly, sized
from the manifest. So after new art: run `cutouts.py`, the zone scene builders (they rewrite the layouts), then Build
Game.

## Placeholders, and swapping in the real images

Every tool loads a reference through `tools/refs.py`: the real image in `references/` when there is one, else its
placeholder in `placeholders/`. So the scenes are complete before all the art exists, and a new image takes its
placeholder's place just by being pushed under the sheet's file name and re-running the cut-outs and scenes. Pieces cut
from a placeholder are marked `"placeholder": true` in the manifest, and are labelled in the renders.

An image that came out wrong and is being made again (D9, E17 and E18 now) is listed with its hash in
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
| D12 more crops, D13 fields band 2 | the fields' crops and their second distant band |
| T10, T11, T12 textures | not used: the scenes keep their own stand-ins (the woven fence, the shader-made ground) until the real textures arrive |
| F7, F8 story frames | not used yet |

## The rooster

`cutouts/rooster/` holds the four turnaround views for modelling (B11-B14: front, back, left, right, beak closed),
the B1 side view and the eight B2 poses (two run frames, flutter, crow, startled, tumble,
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
  thatch shades the kid bounces across, and baskets of hens. No kind of stall comes back within 45 m (the two flower
  stalls count as one kind), counting the lane and the market row together; where no stall is free the row fills
  with goods spread on the ground and the odd animal. The village houses behind are dealt once each before any
  returns, with shade trees between; behind, a row of stalls of every kind (E8, E9 and the E5 stalls) with goods and
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

## 3D models

Every painted piece is also a 3D model, built in Blender from the paintings themselves, so the models are the
paintings in the round.

### The scenery, hand-built in Blender (the models the game uses)

Every piece of scenery that is not a person or an animal (houses, shops, sheds, stalls, temple pieces, wells, carts,
pots, baskets, trees, palms, plants, crops, ground details: 179 pieces) is modelled part by part in a Blender script,
the way a 3D artist builds it from the painting: real walls, roofs, pillars, steps and recessed doors; turned pots,
posts and lamps; bamboo with its nodes and lashings; sagging cloth awnings; heaps of goods; trunks traced off the
painted limbs, crowns, fronds and flowers as cut-out cards of the painting's own foliage. Each is textured from its
painting (tiles and colours cut from it, the painting itself projected onto everything the camera sees, a little
ambient occlusion), so from the game's camera it is the painting and from every other side the same thing painted by
the same hand. People and animals painted into a piece (a vendor, hens in their basket, bullocks at the well) stay the
painted cut-outs they are everywhere else, standing in the model where they are painted.

The scripts are in `tools/kit/`, one module per kind (`lane_houses`, `lane_props`, `stalls_cdef`, `stalls_ghx`,
`market_props`, `fields`, `trees`, `palms_plants`, `ground_crops`); the kit itself, the method and its lessons are in
[tools/kit/README.md](tools/kit/README.md).

```bash
ArtSource/blender/venv/bin/python ArtSource/tools/kit/build.py --only house_pink --review /tmp/review   # one model + its review sheet
ArtSource/blender/venv/bin/python ArtSource/tools/kit/build.py --all                                   # every model (a few hours)
ArtSource/blender/venv/bin/python ArtSource/tools/kit/build.py --merge                                 # their records into models.json
```

They go to `Assets/ChickenRunner/Art/Models/<folder>/<name>.fbx` (with `<name>.jpg`, and `<name>_leaves.png` for the
cards), listed in `models.json` with `"source": "blender"`; the game uses them wherever the piece's card was. The
paintings drawn in perspective (a house's side wall, a tray seen from above) are modelled true and square, so from the
front a model can differ from its painting a little at those edges; everywhere else the front is the painting. The
older routes below (extrusions, TRELLIS, Meshy sheets) remain for the animals and people, and as fallbacks.

### The kid, from her rigged Meshy model

`tools/characters/meshy_kid.py` builds the game's kid from the rigged Meshy model generated from her four views
(`ArtSource/supplied/kid_meshy.fbx`):

1. The model is taken at rest, scaled to the kid's height (1.08 m, feet on the ground), welded along Meshy's texture
   seams and reduced to the character's budget (36,000 faces).
2. Its texture is fixed to her brief (`view_prompts.KID_LOOKS`, `KID_JEWELS`, `KID_HENNA`): the hairband repainted plain
   peacock blue, the grey smudges on the cheeks taken back to skin, and the maruthani painted on (dyed fingertips and
   toe tips, a leaf vine on the back of each hand ending in dots below the bangles, a band round each sole, a vine from
   the big toe to the ankle, dots below each anklet, a vine halfway up each shin). Every texel's place on the body comes
   from a bake of the surface's position and normal, so the design is laid on the body, not on the texture's islands.
3. What the model lacks is added: a matching pair of gold jhumkas, five bangles on each wrist (gold with red and green
   glass between), and, because Meshy's legs stop at the knee inside a hollow skirt, her thighs and peacock-blue
   bloomers with their seat up to under the waist.
4. The rig is the hand-built kid's (`kid_model.BONES`) with its joints moved to Meshy's, skinned with Meshy's own
   weights (fingers, toes and the upper chest folded into the hand, foot and chest); the frock hangs on the skirt bones
   and the hair below the ears on the hair bones, so every clip in `kid_anims.py` plays on it. Exported as
   `Assets/ChickenRunner/Art/Characters/Kid.fbx` with `Kid_painted.png` and `Kid.clips.json`.

```bash
python ArtSource/tools/characters/meshy_kid.py --sheet kid.png --closeup kid_close.png --check CHECK_DIR
```

`--check DIR` renders her from eight sides, close looks at the jewellery, the henna and under the skirt, and every
clip at three moments.

### The rooster, from his rigged Meshy model

`tools/characters/meshy_rooster.py` builds the game's rooster from his rigged Meshy model
(`ArtSource/supplied/rooster_meshy.glb`): at rest, scaled to 0.64 m to the top of his comb, welded along the texture's
seams, and skinned with Meshy's own weights, its 65 numbered bones folded onto the hand-built rooster's 14 by where they
sit (spine into the Body, the neck's chain into Neck1 and Neck2, skull, comb, eyes, beak and wattles into the Head, the
lower beak by its colour onto the Jaw, the tail, wings and legs into theirs), so every clip in `rooster_anims.py` plays.

```bash
python ArtSource/tools/characters/meshy_rooster.py --sheet rooster.png --check CHECK_DIR
```

### Running, jumping and landing, as in Kick Off

The clips follow Kick Off's `KidAnimator`: each step as long as the ground covered while that foot is down, so a planted
foot stays put; knees folding early in the swing, elbows driving against the legs, the head steady against the lean;
the jump driving a knee up, the double jump a second push in the air (no spin), the landing a quick crouch. The kid's
run solves each planted foot by two-bone IK (`kid_anims.run_leg`: flat on the ground, sliding back under her at the
game's 6 m/s, rolling onto the toes to push off), with her model's leg lengths. Both builders then set every grounded
clip down so its lowest point touches the ground (`charkit.ground`, like Kick Off's `CharacterRig.KeepOnGround`) and
measure the run (`charkit.gait`: how fast a sole point that is down slides back, against the run speed; the kid's is
1.07). The rooster's 0.18 m legs cannot stay planted at 5.5 m/s, so he scuttles with a quick, long stride.

### The earlier kid and rooster, from their turnarounds

`tools/characters/hull_character.py` builds each from its four painted views (A0 front/back/left/right, B11-B14). It
built both until their Meshy models came; running it now would replace `Kid.fbx` or `Rooster.fbx` with the carved one:

1. Each view is cut from its background and scaled to the character's height (1.08 m and 0.64 m).
2. The shape is carved slice by slice: every span the front and back views see is paired with every span the side
   views see and filled with a rounded section touching both, so the outline matches all four paintings and the body
   is round between them. Small gaps (between feathers, curls, toes) are bridged when choosing the sections and kept
   open in the carve. The kid's arms take their depth and place from the skin in the side views, her head is the face
   (as wide as the skin in the front view) with the hair beside and behind it, and the rooster's tail is a thin fan.
3. Each point is painted from the view that sees it most squarely and is not hidden there (a depth buffer per view),
   blended by angle and baked to one texture (`Kid_painted.png`, `Rooster_painted.png`). Points no view sees, under
   the arms or inside the hem, take the colour around them.
4. The rig is the hand-built one (`kid_model.BONES`, `rooster_model.BONES`) with its joints moved to where the
   paintings put them, skinned with automatic weights (the frock hangs on the skirt bones), so every clip in
   `kid_anims.py` and `rooster_anims.py` plays on it. Exported as `Assets/ChickenRunner/Art/Characters/Kid.fbx` and
   `Rooster.fbx` with every clip as a take.

```bash
python ArtSource/tools/characters/hull_character.py kid --sheet kid.png --closeup kid_close.png
python ArtSource/tools/characters/hull_character.py rooster --sheet rooster.png --closeup rooster_close.png
python ArtSource/tools/characters/pickups.py --sheet pickups.png
```

`--frames DIR` renders every frame of every clip (for the web version: `Tools/WebPreview/pack_characters.py DIR`).

The clips are functions of time in `kid_anims.py` (Idle, Run, JumpUp, Fall, Land, DoubleJump, Slide, Vault, Climb,
Stumble, Dive, Wade) and `rooster_anims.py` (Idle, Run, Panic, Flutter, Crow, Startled, Tumble), so loops are seamless
and the hair and skirt follow through. The hand-built models in `kid_model.py` and `rooster_model.py`
(`build_character.py kid|rooster`) are the fallback when the turnarounds are missing; `pickups.py` builds the mango,
the chilli and the tail feather the same way. In Unity the `ChickenRunner/Toon` shader gives them two-tone shading
and an ink outline.

### Everything else, from its cut-out

`tools/models/build_models.py` turns every cut-out (about 200 pieces; not the distant bands, which stay painted cards)
into a model at its real size, with the painting on its front:

| Recipe | Pieces | How |
| --- | --- | --- |
| volume | animals, people, trees, plants, pots, baskets, crops | the outline inflated into a rounded solid, thickest where the shape is widest |
| slab | cots, carts, cycles, clotheslines, mats, kolams, ground details | the outline extruded to the thing's real thickness |
| building | houses, shops, sheds, stalls, temple pieces, walls, wells | the facade extruded back to the building's depth; walls and roof show the painting just inside each edge (plaster, brick, thatch, tiles), mirrored to and fro |

```bash
python ArtSource/tools/models/build_models.py --sheet models.png            # all of them, about 10 minutes
python ArtSource/tools/models/build_models.py --only house_pink,cow --sheet check.png
```

### Full 3D from four-view sheets (Meshy)

The most faithful models come from four views of each piece in your own style. Only the pieces the kid touches on
the lane, and the pickups, are worth one (36 of them, `MODEL_ORDER` in `tools/models/view_prompts.py`): the camera
watches the lane from the side, so everything else is only seen from the front, where its painting is already right.
`view_prompts.py` writes their prompts ([docs/art/prompt-sheet-3d.md](../docs/art/prompt-sheet-3d.md); `--all` for
every asset): attach the piece's painting, and ChatGPT or Gemini draws it four times in a 2 by 2 grid (front, left
side, right side, back). The web
version cuts each sheet into the four images; Meshy builds the model from them; the GLB goes in
`ArtSource/models_meshy/<folder>/<name>.glb`, and `finish_models.py` fits it into the game ahead of any TRELLIS or
extruded model of the same name.

### Full 3D from TRELLIS

A single front painting cannot say what the sides, back and top look like, so the pieces are also generated whole
by TRELLIS (image to 3D) and then fitted back to the paintings:

```bash
python ArtSource/tools/models/trellis_models.py      # each cut-out to ArtSource/models_ai/<folder>/<name>.glb
python ArtSource/tools/models/finish_models.py       # fit, repaint the front, export over the extruded model
```

`trellis_models.py` sends each cut-out to the TRELLIS Space on Hugging Face by its public GitHub URL and keeps the
GLB. It needs the Space's host allowed on the network and a Hugging Face token for it (a network secret, so the GPU
time counts against that account). The free GPU quota covers about seven pieces a day, Hugging Face PRO about 60;
when it runs out the run stops, and running it again later carries on with the pieces still missing, the lane's
own obstacles, roofs and stalls first. Ground details and kolams stay flat slabs (they are painted from above).
`--only name --seed N --redo` makes one again with another seed.

`finish_models.py` turns each model to the heading where, seen from the front, it looks most like the painting
(TRELLIS repeats the painting on the side it was shown; colour picks that side), fits its outline to the cut-out's
painted area at the cut-out's real size, and projects the painting back onto the surfaces facing the camera where
it agrees with the generated colour (sharper than the generated texture; where a leg or edge sits differently the
generated colour stays). It then replaces that piece's extruded model and its `models.json` entry.

They go to `Assets/ChickenRunner/Art/Models/<folder>/<name>.fbx` with a JPEG texture beside each and `models.json`
listing their sizes and where each came from (`meshy`, `trellis` or `extruded`). Build Game and Import Art Layouts
stand a piece's model where its card would be (same spot, size and haze; a building stops short of whatever stands
behind it) when it is a full model, from Meshy or TRELLIS. A piece with only an extrusion of its one painting stays
its painted card, which is exactly right from the camera, unless **Chicken Runner > Include Extruded Scenery Models**
is on. **Use 3D Scenery Models** switches all of them back to cards.

### The bamboo ladder

The kid climbs a real ladder onto the first roof of a row, not a painted one. `tools/models/ladder_model.py` builds it
(two bamboo poles with growth rings, nine rungs 27 cm apart lashed with coir, 2.6 m long, in the painted ladder's
colours) as `Assets/ChickenRunner/Art/Models/lane/bamboo_ladder.fbx`; `--picture` also renders it leaning as it stands
in the game, for the web version (`Tools/WebPreview/art/bamboo_ladder.png`). Build Game leans it against the turmeric
house where the painting had its ladder (whether or not the scenery models are on) and gives the wall's `Ladder` its
foot and head, which the kid climbs rung by rung. So the card does not show a second ladder, `tools/paint_out_ladder.py`
paints the ladder off the house's cut-out; `cutouts.py` runs it after cutting the house from C4.

```bash
python ArtSource/tools/models/ladder_model.py --picture
```
