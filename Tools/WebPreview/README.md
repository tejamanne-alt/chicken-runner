# Web version

A browser version of the game for sharing and playtesting, published from `Web/` as a static site. It ports the
Unity build's rules (`KidController`, `RoosterBrain`, `RoosterMind`, `ChaseDirector`, `ChaseCamera`, the level
streamer's seeded shuffle) and `GameBuilder`'s nine levels to JavaScript (`src/game.js`), and draws them with the
same painted art: each zone's scenery from `Assets/ChickenRunner/Art/Layouts`, the pieces, and the kid's and
rooster's poses, projected with the game camera's framing (`src/main.js`).

The level designs live twice, in `Assets/ChickenRunner/Scripts/Editor/GameBuilder.Chunks.cs` and in `src/game.js`.
Change both when a level changes.

Rebuild after the art, the layouts or the code change:

```bash
ArtSource/blender/venv/bin/python Tools/WebPreview/build_assets.py   # about 15 minutes; only when art or layouts change
ArtSource/blender/venv/bin/python Tools/WebPreview/atlas.py
python3 Tools/WebPreview/make_site.py
```

Any Python with Pillow and NumPy works for the first two. `Web/` keeps its images out of Git LFS (see
`Web/.gitattributes`) so a host that builds from the repository serves the pictures themselves.
