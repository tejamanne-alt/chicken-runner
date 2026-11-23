# Models from Meshy

Put each model made in Meshy here as `<folder>/<name>.glb`, named as its cut-out in `ArtSource/cutouts/<folder>/`
(for example `lane/house_pink.glb`, `animals/cow.glb`), with its texture inside the GLB. The kid and the rooster go in
`characters/`, the mango, chilli and feather in `pickups/`.

The four-view sheets they are made from come from the prompts in `docs/art/prompt-sheet-3d.md`
(`ArtSource/tools/models/view_prompts.py`). Then:

```bash
python ArtSource/tools/models/finish_models.py --only house_pink,cow
```

fits each to its painting (the same size and place as the card it replaces, its front to the camera) and exports it
to `Assets/ChickenRunner/Art/Models/`, where Build Game picks it up. A Meshy model replaces the TRELLIS or extruded
one of the same name.
