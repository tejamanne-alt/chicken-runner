# Chicken Runner

A side-scrolling chase runner: a village kid chases a smug rooster through an Indian village. The design is in [docs/game-design-document.md](docs/game-design-document.md).

**Status: milestone 1, grey-box chase.** Capsule kid, block rooster, gap bar, jump and slide, six chunks. The milestone gate is that the chase is fun with no art at all.

## Open it

1. In Unity Hub, choose **Add project from disk** and pick this folder. Open it with **Unity 6.3 LTS** (6000.3.x). If Hub offers a different 6000.3 patch, accept it.
2. On first open Unity installs the Input System package. If it asks whether to enable the new input backends, choose **Yes** and let the editor restart. Choosing No also works, because the game falls back to the old Input Manager.
3. Choose **Chicken Runner > Build Grey-box Level** from the menu bar. This generates the tuning assets, chunk prefabs, level and scene, then opens `Assets/ChickenRunner/Greybox/Chase_Greybox.unity`.
4. Press **Play**, then tap, click or press Space to start the chase.

Commit what the builder generates (the `Greybox` and `Config` folders and their `.meta` files) so every machine shares the same assets.

## Controls

Everything works with one thumb anywhere on the screen. In the editor, the mouse behaves like a finger.

| Action | Touch or mouse | Keyboard |
| --- | --- | --- |
| Jump (hold for higher) | Tap; hold for the full 1.4 m | Space, Up or W |
| Double jump | Tap again in the air | Space again |
| Slide, or fast drop in the air | Swipe down | Down or S |
| Pause | II button, top right | Esc or P |
| Retry | Tap on the result screen | R |
| Debug readout | | F1 or backquote |

A touch waits 60 ms before it becomes a jump, so a swipe down never starts with one. Jump buffer (0.1 s) and coyote time (0.08 s) follow the doc. Climbing (swipe up beside a ladder) arrives with ladders in milestone 2; until then a swipe up jumps.

## What's in the grey-box

- **The chase.** The kid auto-runs at 6 m/s and the rooster at 5.5 m/s, starting 12 m ahead. The gap bar shows the metres. Inside 0.8 m the kid dives and the rooster wriggles free; past 25 m, or at the 500 m course end, he escapes.
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
                       stars, gestures, a chase forecast and the tuning report (no UnityEngine)
  Scripts/Gameplay/    GameFlow, ChaseDirector, KidController, RoosterBrain, LevelStreamer, chunks,
                       obstacles, pickups, camera and HUD
  Scripts/Editor/      The grey-box builder and the tuning Inspector
  Tests/EditMode/      NUnit tests for Core
  Config/, Greybox/    Generated by the builder
Tools/CoreTests/       Runs the Core tests without Unity
docs/                  Game design document
```

The architecture follows the doc. GameFlow owns the level state machine and a fixed 120 Hz simulation clock, and kid and rooster are interpolated between ticks, so jumps are the same on every device. ChaseDirector owns the gap, win and loss, and the stats the HUD reads. A level is a `LevelDefinition` asset (a tuning config plus an ordered chunk list), so designers reorder chunks without code. Chunks are prefabs with ground colliders, obstacle and pickup objects and rooster route markers. They are pooled and recycled behind the kid.

## Tests

```bash
dotnet test Tools/CoreTests
```

This runs 52 tests on the Core rules with the .NET 8 SDK and no Unity install. The same test files run in Unity's Test Runner once you add the **Test Framework** package from the Package Manager.

## Render pipeline

The grey-box renders in the Built-in pipeline or in URP. The builder picks the lit shader of whichever pipeline is active, and every prop is tinted through a property block. The doc's URP and toon shader setup belongs to milestone 2, with the kid model. After switching to URP, run the builder again so the grey-box material picks up the URP shader.

## Next

Play the grey-box against the milestone 1 gate. Tune in the Inspector, then move to milestone 2 (the supplied kid model, animation states, ladder, canal wade and the basket intro). Several of the doc's open decisions are worth settling before milestone 2 starts.
