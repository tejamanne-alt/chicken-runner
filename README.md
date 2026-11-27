# Chicken Runner

A side-scrolling chase runner: a village kid chases a smug rooster through an Indian village. The design is in [docs/game-design-document.md](docs/game-design-document.md).

**Status: the whole game, on placeholder art where pictures are still being made.** Nine levels across the three zones, the painted kid and rooster, painted obstacles and scenery, the title, story strip, village map, results and finale, and a save. Pictures still to come (D12, D13 and the D9, E17, E18 remakes) are covered by placeholders and swap in when they arrive. The milestone 1 grey-box chase is still there for tuning with no art at all.

## Open it

1. In Unity Hub, choose **Add project from disk** and pick this folder. Open it with **Unity 6.3 LTS** (6000.3.x). If Hub offers a different 6000.3 patch, accept it.
2. On first open Unity installs the Input System package. If it asks whether to enable the new input backends, choose **Yes** and let the editor restart. Choosing No also works, because the game falls back to the old Input Manager.
3. Choose **Chicken Runner > Build Game** from the menu bar. This copies the art it needs from `ArtSource` into `Assets/ChickenRunner/Art/Textures`, generates the tuning and obstacle assets, every zone's chunk prefabs, the nine levels and each zone's scenery, and saves `Assets/ChickenRunner/Game/Game.unity` (first in the build settings). Then **Chicken Runner > Open Game Scene**.
4. Press **Play**: the title, then the story strip the first time, then level 1. Tap, click or press Space to start each chase. Levels 1, 4 and 7 (the first of each zone, laid from audited plans) are open on the village map from the start. To go straight into one, use **Chicken Runner > Play Level 1: Pots and the sleeping dog**, **Play Level 4: The canal** or **Play Level 7: Rooftop run**.

To try any level straight away, tick **Unlock All** on the `Game` object's GameSession: Play then opens on the village map with every stop open. The save lives in the app's persistent data folder; **Reset** on the title screen (tap twice) erases it.

Re-run **Build Game** after new art arrives (after `cutouts.py` and the zone scene builders in `ArtSource/tools`, see [ArtSource/README.md](ArtSource/README.md)). It keeps the tuning and obstacle assets, so numbers tuned in the Inspector survive. Commit what it generates (the `Game`, `Config` and `Art` folders and their `.meta` files) so every machine shares the same assets.

The milestone 1 grey-box (**Chicken Runner > Build Grey-box Level**) still builds its own scene, `Assets/ChickenRunner/Greybox/Chase_Greybox.unity`, with capsules and one looping level.

## Controls

Everything works with one thumb anywhere on the screen. In the editor, the mouse behaves like a finger.

| Action | Touch or mouse | Keyboard |
| --- | --- | --- |
| Jump (hold for higher) | Tap; hold for the full 1.4 m | Space, Up or W |
| Double jump | Tap again in the air | Space again |
| Slide, or fast drop in the air | Swipe down | Down or S |
| Climb a ladder or a branch | Run into the ladder; jump at the branch | |
| Pause | II button, top right | Esc or P |
| Retry | Retry on the result screen | R |
| Debug readout | | F1 or backquote |

A touch waits 60 ms before it becomes a jump, so a swipe down never starts with one. Jump buffer (0.1 s) and coyote time (0.08 s) follow the doc. Ladders climb on their own when the kid runs into them, so a swipe up stays a jump.

## What's in the game

| Level | Zone | What it teaches | Chunks |
| --- | --- | --- | --- |
| 1. Pots and the sleeping dog | The lane | Jump; lifting the basket | the neighbour's yard and the basket intro, then pot stacks, dung, the sleeping dog, the hand-pump puddle and the bullock cart, laid from an audited plan ([beat sheet](docs/levels/level1.md)) |
| 2. Washing day | The lane | Slide; the rope-cot bounce | clotheslines, the cot, sarees and pots, the rooster's mischief |
| 3. Up on the roofs | The lane | Ladders, roofs, the jump between them | a row of houses with a ladder, two rows with a gap |
| 4. The canal | Fields | Jump it, wade it or take the plank | canals 2.5, 3.5 (with a plank bridge) and 4.5 m wide, small haystacks, dung and the cart along the bund, laid from an audited plan ([beat sheet](docs/levels/level4.md)) |
| 5. Mango trees | Fields | Jump at a branch to climb up | the mango-tree branch route, small haystacks |
| 6. Buffalo and haystacks | Fields | Bounce off a buffalo's back | the buffalo in its mud, haystack chains, mischief by the well |
| 7. Rooftop run | Terraces | Gaps and water tanks | ladders up to long roof runs, gaps between houses, tanks to jump, clotheslines, pots and the hens' basket in the street, laid from an audited plan ([beat sheet](docs/levels/level7.md)) |
| 8. Market day | Market | Bounce across the awnings | rows of stalls, hens, the hens-basket fake-out |
| 9. The temple steps | Temple | Everything, 800 m | the temple steps and a bit of everything |

- **Speeds and courses** follow the doc: 6, 7 and 8 m/s for the kid, 500, 600 and 700 m courses (800 m for level 9). Levels 1, 4 and 7 are laid piece by piece from their plans (`ArtSource/tools/levels/levelN.py` on the shared `levelkit.py` writes `Art/Levels/levelN.json` and audits it with the zone's own speed, jump maths and kid body read from the C#: take-off windows, room to react after each landing, canal and roof-gap jumps, ladders and drops, the rooster's hops over everything, chilli reach, mangoes and the feathers; Build Game lays one chunk per section). The other levels play their chunks in order once, then repeat them in a seeded shuffle. Either way a course is the same on every retry and can be learnt.
- **The basket intro (level 1):** the kid tiptoes past the sleeping neighbour to the basket the rooster is under, and the player holds to lift it. A steady lift gives the rooster a 10 m head start, a dropped one 14 m. He bursts out, the neighbour wakes shouting, and the chase is on. A retry keeps the head start and skips the intro.
- **New moves:** wading (a canal's bed is 0.28 m down; the kid wades at 45% speed, which is slow but not a stumble), ladders and branches (cheaper than the slow vault: the kid climbs the bamboo ladder rung by rung in 0.45 s, about 0.6 m less lost to the rooster than a vault, her back to the camera and her hands and feet in time with the rungs, then steps off onto the roof; a branch is a quick pull-up at 60% speed), bounce pads with their own heights (cot, awnings 2.0 m, buffalo 2.6 m). Roofs are 2.35 m, inside the doc's range and low enough for a fair double jump (see Tuning).
- **Three hidden feathers per level,** on the harder routes: high over the dog or a canal, on the roofs and the branch, at the top of a bounce. The HUD shows the feathers found in a run, the map shows each level's.
- **Progression:** stars are kept star by star (each level's best grab, mango and no-stumble stars from any runs). 5 of the lane's 9 stars open the fields and 12 of the first 18 open the terraces, as in the doc; each level also needs the one before it won. Mangoes from every run, won or lost, go into a bank for the outfits to come.
- **Screens:** the title (F1), the wordless story strip the first time (F2 to F6, skippable), the village map (three painted zones, nine stops with stars, feathers and locks), the result with Next, Again and Map (the wriggle-free picture for a win, the rooster crowing (F7) for a loss), a pause with Carry on and Village map, and Amma's kitchen (F8) after level 9.
- **Characters:** the kid, the rooster and the pickups are rigged, animated 3D models. The kid and the rooster are their rigged Meshy models, fitted to the game's rigs (`ArtSource/tools/characters/meshy_kid.py`, with her jewellery, maruthani and bloomers added, and `meshy_rooster.py`; see [ArtSource/README.md](ArtSource/README.md)), toon-shaded with ink outlines to sit in the painted world. Their running and air moves follow Kick Off's KidAnimator: the kid's run plants each foot by IK so it keeps pace with the ground at 6 m/s, the jump drives a knee up, the double jump is a second push in the air and the landing a quick crouch, and every grounded clip is set down so the feet touch the ground. The kid has 12 clips (run, jump, fall, land, double jump, slide, vault, ladder climb, stumble, dive, wade, idle); the rooster has 7 (run, panic sprint, flutter, crow, startled, tumble, pecking about). Build Game sets up their Animator Controllers; `KidModelVisual` and `RoosterModelVisual` pick the clip from the game state and speed up the run with the run speed.
- **Art:** every piece of scenery that is not a person or an animal (houses, shops, stalls, temple pieces, wells, carts, pots, trees, palms, plants, crops, ground details: 179 pieces) stands in the game as a 3D model hand-built in Blender from its painting and textured from it, so it is the painting from the game's camera and solid from every side (`ArtSource/tools/kit`, see [ArtSource/README.md](ArtSource/README.md)); leaves, fronds and flowers are cut-out cards drawn both sides. People and animals painted into a piece stay painted cut-outs inside it; the animals on their own use their TRELLIS models where they have one, and their painted cards otherwise. Obstacles, houses, stalls, haystacks, the buffalo and the mango tree stand on colliders sized to their pictures. Each zone's scenery is its Blender scene, repeated along the course: the distant bands as continuous painted strips, the near houses and trees as a set. The ground is a world-space earth tile (paddy water away from the bund in the fields) with the same distance haze. **Chicken Runner > Use 3D Scenery Models** switches all models off; **Include Extruded Scenery Models** adds the single-painting extrusions for pieces with no full model. Anything without a painting yet falls back to a grey-box shape.

Still placeholder: the IMGUI screens and HUD (the doc's signboard UI comes later), the words that pop up for sounds, the cube debris, primitive mangoes, chillies and feathers, the temple steps (grey-box shapes), and the neighbour in level 1's yard (painted cut-outs, asleep and awake).

## What's in the grey-box (milestone 1)

- **The chase.** The kid auto-runs at 6 m/s and the rooster at 5.5 m/s, starting 12 m ahead. The gap bar shows the metres. Inside 0.8 m (and roughly level with him) the kid dives and the rooster wriggles free; past 25 m, or at the 500 m course end, he escapes.
- **Rooster behaviours, built before any art as the doc's risk table asks.** Gap-driven run speed, the taunt (stops, turns round and crows beyond 18 m), the panic burst under 2 m (sprints and sheds feathers, twice per chase), fluttering over obstacles along routes authored in each chunk, mischief (knocks a pot stack into the lane behind him, but only when the kid is at least 7 m back) and the wriggle-free gag.
- **Kid moves.** Variable-height jump, double jump, slide, fast drop, the slow wall vault (about 2.4 m lost), the rope-cot bounce, stumbles (2.3 to 2.7 m lost depending on the obstacle), chilli boost (+4.6 m) and the automatic dive.
- **Six chunks plus a runway**, looped into the 500 m zone-1 course: pot stacks; dung and a sleeping dog; clotheslines; the rope cot; the bullock cart; and the mischief lane. Mango lines trace the clean route.
- **Camera.** Side-on, kid on the left third, pulls back so the rooster stays in frame up to 14 m, then an edge arrow takes over.
- **Result screen** with the three stars (grab, mangoes, no stumble). Losing costs one tap.

Placeholders that later milestones replace: the IMGUI HUD (uGUI signboard HUD in milestone 3), the words that pop up for sounds ("SMASH!", "WOOF!"; real audio in milestone 3), the cube debris (the particle pass), and the plain follow camera (it can move to Cinemachine with the same framing rule).

## Tuning

All the doc's numbers live in `Assets/ChickenRunner/Config/Tuning_Zone1.asset` (and Zone2, Zone3). Gameplay reads them every tick, so you can edit them in the Inspector while the game runs. The Inspector also shows what the numbers add up to: jump length, metres per mistake, clean catch time and how many mistakes a player can afford. It warns where they break a promise in the doc. Re-running the builder keeps your tuning and obstacle assets.

Derived from the doc's starting values:

| | Zone 1 | Zone 2 | Zone 3 |
| --- | --- | --- | --- |
| Clean catch from a 12 m start | 27.8 s, 167 m | 23.9 s, 167 m | 24.7 s, 198 m |
| Smooth / clumsy basket lift | 23.8 s / 31.8 s | 20.6 s / 27.2 s | 21.4 s / 28.1 s |
| Rooster reaches course end | 89 s | 92 s | 93 s |
| Most mistakes that still win | one every 6.75 s | one every 6 s | one every 7 s |
| A stumble costs | 2.31 m | 2.70 m | 3.08 m |
| A chilli gains | 4.62 m | 5.39 m | 6.16 m |

So the doc's "about 30 s clean, up to 90 s messy" holds in all three zones. The tuning check flags two things for the doc:

- **Roof height against the double jump.** Roofs go up to 2.6 m and the double jump tops out at exactly 2.6 m, so the tallest roof can only be reached by a frame-perfect double jump. For a fair 150 ms timing window, either cap roofs at about 2.37 m or raise the double jump to about 2.83 m. This matters from level 3, the first rooftop stretch.
- **Zone 3 mistakes and chillies.** Both are defined in seconds, so at 8 m/s a stumble costs 3.1 m and a chilli gains 6.2 m, a little outside the doc's "2 to 3 m" and "about 5 m". In time terms they cost about the same as in zone 1, so this may be fine. Shorten them for zone 3 if playtests feel harsh.

## Project layout

```
Assets/ChickenRunner/
  Scripts/Core/        Engine-free rules: tuning, jump maths, kid speed, rooster moods, win/loss,
                       stars, progression and save data, gestures, a chase forecast and the tuning
                       report (no UnityEngine)
  Scripts/Gameplay/    GameSession (screens, levels, save), GameFlow, ChaseDirector, KidController,
                       RoosterBrain, LevelStreamer, chunks, obstacles, pickups, water, ladders,
                       the card visuals, BackdropStreamer, camera, HUD and menus
  Scripts/Editor/      The game builder, zone scenery builder, art importer, the grey-box builder
                       and the tuning Inspector
  Art/Shaders/         PaintedCard (the cut-outs) and PaintedGround (earth, paddy and canal water)
  Art/Layouts/         Each zone's Blender scene as cards, written by ArtSource/tools
  Tests/EditMode/      NUnit tests for Core
  Game/, Config/, Art/Textures, Art/Materials   Generated by Build Game
  Greybox/             Generated by Build Grey-box Level
Tools/CoreTests/       Runs the Core tests without Unity
docs/                  Game design document
```

The architecture follows the doc. GameSession owns everything around the chase (title, story, map, results, the save) and loads a level into GameFlow and its zone's scenery into the BackdropStreamer; GameMenus only draws the screens and calls the session. GameFlow owns the level state machine and a fixed 120 Hz simulation clock, and kid and rooster are interpolated between ticks, so jumps are the same on every device. ChaseDirector owns the gap, win and loss, and the stats the HUD reads. A level is a `LevelDefinition` asset (a tuning config plus an ordered chunk list), so designers reorder chunks without code. Chunks are prefabs with ground colliders, obstacle and pickup objects and rooster route markers. They are pooled and recycled behind the kid.

## Tests

```bash
dotnet test Tools/CoreTests
```

This runs 74 tests on the Core rules with the .NET 8 SDK and no Unity install. The same test files run in Unity's Test Runner once you add the **Test Framework** package from the Package Manager.

## Render pipeline

The game is set up for the Built-in pipeline. The painted cards and ground are unlit shaders (`ChickenRunner/PaintedCard`, `ChickenRunner/PaintedGround`) that also draw in URP; the few grey-box shapes left pick the lit shader of whichever pipeline is active. After switching to URP, run the builders again.

## Not checked yet

Everything here compiles under both input settings and the Core tests pass, but it was built without opening Unity, so nothing has been played yet. Worth checking first: the art's sizes and positions against the colliders (pot stacks, clotheslines, the cart's bed, roofs, awnings), that every feather can be reached, the scenery's repeat seams, and the frame rate in the fields (about 500 scenery cards per repeat).

## Next

Play all nine levels and tune in the Inspector. Then the basket intro, audio, the signboard UI, outfits, and the pictures still to come.
