using System.Collections.Generic;
using System.IO;
using ChickenRunner.Core;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

namespace ChickenRunner.EditorTools
{
    /// <summary>
    /// Builds the whole game from code and the painted art: tuning and obstacle assets, every zone's chunks as prefabs
    /// (painted pieces where the art exists, grey-box shapes where it does not yet), the nine story levels, each zone's
    /// repeating scenery from its Blender layout, and the Game scene with the title, story strip, village map, chase,
    /// results and finale. Placeholder art in ArtSource/placeholders stands in for pictures still being made; re-running
    /// this after new art arrives (and after cutouts.py and the scene builders) swaps it in.
    ///
    /// Re-running keeps existing tuning and obstacle assets, so numbers tuned in the Inspector survive; chunks, levels,
    /// scenery and the scene are rebuilt.
    /// </summary>
    internal static partial class GameBuilder
    {
        const string Root = "Assets/ChickenRunner";
        const string ConfigFolder = Root + "/Config";
        const string GameFolder = Root + "/Game";
        const string ChunkFolder = GameFolder + "/Chunks";
        const string LevelFolder = GameFolder + "/Levels";
        const string ObstacleFolder = GameFolder + "/Obstacles";
        const string SceneryFolder = GameFolder + "/Scenery";
        const string MaterialFolder = GameFolder + "/Materials";
        public const string ScenePath = GameFolder + "/Game.unity";

        static readonly string[] s_layouts = { "lane_zone1", "fields_zone2", "market_zone3" };

        [MenuItem("Chicken Runner/Build Game", priority = 0)]
        public static void BuildFromMenu()
        {
            if (File.Exists(ScenePath) && !EditorUtility.DisplayDialog("Rebuild the game?",
                    "This replaces the game's chunk prefabs, levels, scenery and " + ScenePath + ".\n\n"
                    + "Tuning configs and obstacle definitions are kept as they are.", "Rebuild", "Cancel"))
            {
                return;
            }
            if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
            Build();
        }

        [MenuItem("Chicken Runner/Play Level/1. Pots and the sleeping dog", priority = 20)]
        static void PlayLevel1() => PlayLevel(0);

        [MenuItem("Chicken Runner/Play Level/2. Washing day", priority = 21)]
        static void PlayLevel2() => PlayLevel(1);

        [MenuItem("Chicken Runner/Play Level/3. Up on the roofs", priority = 22)]
        static void PlayLevel3() => PlayLevel(2);

        [MenuItem("Chicken Runner/Play Level/4. The canal", priority = 23)]
        static void PlayLevel4() => PlayLevel(3);

        [MenuItem("Chicken Runner/Play Level/5. Mango trees", priority = 24)]
        static void PlayLevel5() => PlayLevel(4);

        [MenuItem("Chicken Runner/Play Level/6. Buffalo and haystacks", priority = 25)]
        static void PlayLevel6() => PlayLevel(5);

        [MenuItem("Chicken Runner/Play Level/7. Rooftop run", priority = 26)]
        static void PlayLevel7() => PlayLevel(6);

        [MenuItem("Chicken Runner/Play Level/8. Market day", priority = 27)]
        static void PlayLevel8() => PlayLevel(7);

        [MenuItem("Chicken Runner/Play Level/9. The temple steps", priority = 28)]
        static void PlayLevel9() => PlayLevel(8);

        /// <summary>Opens the game scene and plays straight into a level, skipping the title, story and map.</summary>
        static void PlayLevel(int index)
        {
            if (EditorApplication.isPlaying) return;
            if (!File.Exists(ScenePath))
            {
                if (!EditorUtility.DisplayDialog("No game scene yet", "Build the game now, then play?", "Build", "Cancel")) return;
                if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
                Build();
                if (!File.Exists(ScenePath)) return;
            }
            if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
            if (EditorSceneManager.GetActiveScene().path != ScenePath) EditorSceneManager.OpenScene(ScenePath);
            PlayerPrefs.SetInt(GameSession.PlayLevelKey, index);
            PlayerPrefs.Save();
            EditorApplication.isPlaying = true;
        }

        [MenuItem("Chicken Runner/Open Game Scene", priority = 1)]
        public static void OpenScene()
        {
            if (!File.Exists(ScenePath))
            {
                if (EditorUtility.DisplayDialog("No game scene yet", "Build the game now?", "Build", "Cancel")) BuildFromMenu();
                return;
            }
            if (EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) EditorSceneManager.OpenScene(ScenePath);
        }

        public static void Build()
        {
            foreach (var folder in new[] { ConfigFolder, ChunkFolder, LevelFolder, ObstacleFolder, SceneryFolder, MaterialFolder })
                ArtAssets.EnsureFolder(folder);
            ArtAssets.ClearCache();
            ArtModels.ClearCache();
            ClearModelCache();
            if (ArtAssets.CardShader == null || Shader.Find(ArtAssets.GroundShaderName) == null)
            {
                Debug.LogError("The ChickenRunner/PaintedCard and PaintedGround shaders are missing (Assets/ChickenRunner/Art/Shaders).");
                return;
            }

            // Work in a fresh scene so the temporary objects never touch the scene the user had open.
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            try
            {
                var prims = PrimMaterial();
                // The canals' water: the light painted tile (road_textures.py: clear blue-green, sky and sun on it, ripples along
                // the flow), else the old dark one, tinted lighter. Their stone-lined banks: the granite tile.
                var lightWater = ArtAssets.Cutout("canal_water_light");
                var water = GroundMaterial("Water", ArtAssets.Texture(lightWater ?? ArtAssets.Cutout("canal_water"), true), 2.5f, null,
                    lightWater != null ? Color.white : new Color(0.82f, 0.92f, 1f), 0.05f, 6f, 40f);
                var stone = GroundMaterial("CanalStone", ArtAssets.Texture(ArtAssets.Cutout("granite"), true), 1.2f, null,
                    new Color(1f, 0.97f, 0.92f), 0.05f, 6f, 40f);
                // The hand pump's puddle: the same water, lighter and bluer and in a smaller tile, so it reads as the shallow
                // puddle painted under the pump rather than a dark patch of canal.
                var puddle = GroundMaterial("Puddle", ArtAssets.Texture(ArtAssets.Cutout("canal_water"), true), 1.2f, null,
                    new Color(0.95f, 1.05f, 1.25f), 0.03f, 6f, 40f);
                var obstacles = CreateObstacles();

                var tunings = new TuningConfig[StoryMap.ZoneCount + 1];
                var arts = new ZoneArt[StoryMap.ZoneCount + 1];
                var chunks = new Dictionary<string, Chunk>[StoryMap.ZoneCount + 1];
                var kits = new ZoneKit[StoryMap.ZoneCount + 1];
                for (int zone = 1; zone <= StoryMap.ZoneCount; zone++)
                {
                    EditorUtility.DisplayProgressBar("Building the game", "Zone " + zone, zone / 4f);
                    tunings[zone] = CreateTuning(zone);
                    var ground = ZoneGround(zone);
                    arts[zone] = ZoneArtBuilder.Build(zone, s_layouts[zone - 1], ground, SceneryFolder);
                    var kit = new ZoneKit { zone = zone, tuning = tunings[zone].Values, prims = prims, ground = ground, water = water, puddle = puddle, stone = stone, obstacles = obstacles };
                    kits[zone] = kit;
                    chunks[zone] = new Dictionary<string, Chunk>();
                    foreach (var design in ChunkDesigns(zone))
                        chunks[zone][design.name] = SaveChunk(design.build(kit), $"Z{zone}_{design.name}");
                }

                var levels = new LevelDefinition[s_levels.Length];
                for (int i = 0; i < s_levels.Length; i++)
                {
                    var design = s_levels[i];
                    levels[i] = CreateLevel(i, design, tunings[design.zone], arts[design.zone], chunks[design.zone]);
                    if (string.IsNullOrEmpty(design.plan)) continue;
                    EditorUtility.DisplayProgressBar("Building the game", "Level " + (i + 1) + " from its plan", 0.9f);
                    var plan = LoadPlan(design.plan);
                    if (plan == null) continue; // the error is logged; the level keeps its chunk pool
                    if (plan.zone != 0 && plan.zone != design.zone)
                        Debug.LogError($"Level plan {design.plan} is for zone {plan.zone}, but level {i + 1} is in zone {design.zone}.");
                    ApplyPlan(levels[i], plan, BuildPlanChunks(design.plan, plan, kits[design.zone]));
                    EditorUtility.SetDirty(levels[i]);
                }

                BuildScene(levels, arts[1], prims);
                EditorSceneManager.SaveScene(scene, ScenePath);
                AddSceneToBuildSettings(ScenePath);
                AssetDatabase.SaveAssets();
                Debug.Log("Chicken Runner built: " + ScenePath + ". Press Play: title, story, then level 1; each zone's first "
                    + "level (1, 4 and 7) is open on the map from the start. Chicken Runner > Play Level jumps straight into "
                    + "any level; tick 'Unlock All' on the Game object's GameSession to open them all on the map.");
            }
            finally
            {
                EditorUtility.ClearProgressBar();
            }
        }

        // ------------------------------------------------------------------ assets

        static Material PrimMaterial()
        {
            string path = MaterialFolder + "/Prims.mat";
            var shader = Shader.Find("Standard");
            if (GraphicsSettings.currentRenderPipeline != null) shader = Shader.Find("Universal Render Pipeline/Lit") ?? shader;
            var material = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (material == null)
            {
                material = new Material(shader);
                AssetDatabase.CreateAsset(material, path);
            }
            material.shader = shader;
            if (material.HasProperty("_Glossiness")) material.SetFloat("_Glossiness", 0.1f);
            if (material.HasProperty("_Smoothness")) material.SetFloat("_Smoothness", 0.1f);
            material.enableInstancing = true;
            EditorUtility.SetDirty(material);
            return material;
        }

        // The village road along the lane, as a band of the ground (PaintedGround's _RoadTex): from its front edge toward
        // the camera to its back edge by the houses. From the chase camera it fills the screen from 8.7% to 27% of its
        // height, where Kick Off's pavement lies, with the kid's running line (z = 0) along its middle and the roadside
        // things (hens, the hand pump, the neighbour's cot, z 1.1 to 1.4) on its back half. Below it, the earth verge, as
        // Kick Off's kerb. ArtSource/tools/models/road_textures.py paints the tiles to these.
        internal const float RoadFront = -1.25f;
        internal const float RoadBack = 2.05f;
        const float RoadTile = 4f;
        static readonly string[] s_roads = { "road_mud_lane", "road_cart_track", "road_cement" };

        /// <summary>
        /// The red earth for zones 1 and 3; zone 2's bund lane runs between paddy water. Down the lane, each zone's road: the
        /// lane's hardened mud street, the fields' cart track, the market's cement road.
        /// </summary>
        static Material ZoneGround(int zone)
        {
            var earth = ArtAssets.Texture(ArtAssets.Cutout("plain_red_earth") ?? ArtAssets.Cutout("ground_earth_lane"), true);
            Material ground;
            if (zone == 2)
            {
                var paddy = ArtAssets.Texture(ArtAssets.Cutout("paddy_water"), true);
                ground = GroundMaterial("Ground_Zone2", earth, 3.5f, paddy, Color.white, 0.14f, 10f, 55f);
                ground.SetFloat("_BandBack", RoadBack + 0.15f);   // the paddy from the cart track's back edge, by the crops
            }
            else
            {
                ground = GroundMaterial("Ground_Zone" + zone, earth, 3.5f, null, Color.white, 0.14f, 6f, 40f);
            }
            var road = ArtAssets.Texture(ArtAssets.Cutout(s_roads[Mathf.Clamp(zone, 1, 3) - 1]), true);
            ground.SetFloat("_UseRoad", road != null ? 1f : 0f);
            if (road != null)
            {
                ground.SetTexture("_RoadTex", road);
                ground.SetFloat("_RoadTile", RoadTile);
                ground.SetFloat("_RoadFront", RoadFront);
                ground.SetFloat("_RoadBack", RoadBack);
                ground.SetFloat("_RoadSoft", 0.32f);
                ground.SetFloat("_RoadWave", 0.2f);
            }
            else
            {
                Debug.LogWarning("The road tiles are missing (ArtSource/tools/models/road_textures.py): the lane is bare earth.");
            }
            EditorUtility.SetDirty(ground);
            return ground;
        }

        static Material GroundMaterial(string name, Texture2D main, float tile, Texture2D far, Color tint, float drift, float hazeFrom, float hazeTo)
        {
            string path = $"{MaterialFolder}/{name}.mat";
            var shader = Shader.Find(ArtAssets.GroundShaderName);
            var material = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (material == null)
            {
                material = new Material(shader);
                AssetDatabase.CreateAsset(material, path);
            }
            material.shader = shader;
            material.mainTexture = main;
            material.SetFloat("_Tile", tile);
            // Without the earth picture yet, a plain red-earth colour.
            material.SetColor("_Tint", main != null ? tint : new Color(0.74f, 0.43f, 0.26f));
            material.SetFloat("_Drift", drift);
            material.SetFloat("_UseFar", far != null ? 1f : 0f);
            if (far != null) material.SetTexture("_FarTex", far);
            // Paddy only behind the bund: up close in front of the camera the paddy tile is magnified into a pattern,
            // so the near side stays earth (the preview showed it).
            material.SetFloat("_BandFront", -40f);
            material.SetColor("_HazeColor", ArtAssets.Haze);
            material.SetFloat("_HazeFrom", hazeFrom);
            material.SetFloat("_HazeTo", hazeTo);
            EditorUtility.SetDirty(material);
            return material;
        }

        static TuningConfig CreateTuning(int zone)
        {
            string path = ConfigFolder + "/Tuning_Zone" + zone + ".asset";
            var existing = AssetDatabase.LoadAssetAtPath<TuningConfig>(path);
            if (existing != null)
            {
                // Kept, so numbers tuned in the Inspector survive a rebuild; unless the design has moved on since
                // (ChaseTuning.DesignVersion: the real-world pace), when the old numbers no longer fit the levels.
                if (existing.IsOutdated)
                {
                    existing.ResetToDesignValues();
                    EditorUtility.SetDirty(existing);
                    Debug.Log($"{path}: reset to the current design values (the kid runs {existing.Values.kidRunSpeed} m/s).");
                }
                return existing;
            }
            var config = ScriptableObject.CreateInstance<TuningConfig>();
            config.zone = zone;
            config.ResetToDesignValues();
            AssetDatabase.CreateAsset(config, path);
            return config;
        }

        static Obstacles CreateObstacles() => new Obstacles
        {
            pots = CreateObstacle("PotStack", "Clay pot stack", PenaltyKind.Stumble, 1f, HitReaction.Smash, Palette.Terracotta, "SMASH!"),
            dung = CreateObstacle("CowDung", "Cow dung", PenaltyKind.Slip, 1.15f, HitReaction.Splat, Palette.Dung, "SPLAT!"),
            dog = CreateObstacle("SleepingDog", "Sleeping street dog", PenaltyKind.Stumble, 1f, HitReaction.Wake, Palette.Dog, "WOOF!"),
            puddle = CreateObstacle("Puddle", "Hand-pump puddle", PenaltyKind.Slip, 1f, HitReaction.Splat, Palette.Water, "SPLOSH!"),
            clothesline = CreateObstacle("Clothesline", "Clothesline of sarees", PenaltyKind.Tangle, 1.1f, HitReaction.Wobble, Palette.Kumkum, "TANGLED!"),
            hens = CreateObstacle("Hens", "Hens and their basket", PenaltyKind.Stumble, 0.9f, HitReaction.Wake, Palette.Hen, "BAWK BAWK!"),
            tank = CreateObstacle("WaterTank", "Water tank on a roof", PenaltyKind.Stumble, 1f, HitReaction.Wobble, Palette.Ink, "CLONG!"),
            goats = CreateObstacle("Goats", "Goat kids crossing", PenaltyKind.Stumble, 1f, HitReaction.Wake, Palette.Dog, "MAA-AA!"),
            ducks = CreateObstacle("Ducks", "Ducks crossing", PenaltyKind.Stumble, 0.9f, HitReaction.Wake, Palette.Hen, "QUACK!"),
            sand = CreateObstacle("SandHeap", "Heap of building sand", PenaltyKind.Stumble, 1.1f, HitReaction.Splat, Palette.Hay, "FLUMP!"),
            branch = CreateObstacle("LowBranch", "Low neem branch", PenaltyKind.Tangle, 1f, HitReaction.Wobble, Palette.Leaf, "SWISH!"),
        };

        static ObstacleDefinition CreateObstacle(string file, string displayName, PenaltyKind penalty, float durationScale,
            HitReaction reaction, Color color, string bark)
        {
            string path = ObstacleFolder + "/Obstacle_" + file + ".asset";
            var existing = AssetDatabase.LoadAssetAtPath<ObstacleDefinition>(path);
            if (existing != null) return existing;
            var definition = ScriptableObject.CreateInstance<ObstacleDefinition>();
            definition.displayName = displayName;
            definition.penalty = penalty;
            definition.durationScale = durationScale;
            definition.reaction = reaction;
            definition.reactionColor = color;
            definition.bark = bark;
            AssetDatabase.CreateAsset(definition, path);
            return definition;
        }

        static Chunk SaveChunk(GameObject root, string name)
        {
            root.name = name;
            var prefab = PrefabUtility.SaveAsPrefabAsset(root, ChunkFolder + "/" + name + ".prefab");
            Object.DestroyImmediate(root);
            return prefab.GetComponent<Chunk>();
        }

        static LevelDefinition CreateLevel(int index, LevelDesign design, TuningConfig tuning, ZoneArt art, Dictionary<string, Chunk> chunks)
        {
            string path = $"{LevelFolder}/Level_{index + 1}.asset";
            var level = AssetDatabase.LoadAssetAtPath<LevelDefinition>(path);
            if (level == null)
            {
                level = ScriptableObject.CreateInstance<LevelDefinition>();
                AssetDatabase.CreateAsset(level, path);
            }
            level.displayName = design.title;
            level.subtitle = design.subtitle;
            level.tuning = tuning;
            level.art = art;
            level.runwayChunk = chunks["Runway"];
            level.startChunk = null;
            level.chunks = new List<Chunk>();
            foreach (var name in design.chunks)
            {
                if (chunks.TryGetValue(name, out var chunk)) level.chunks.Add(chunk);
                else Debug.LogError($"Level {index + 1} names a chunk {name} that zone {design.zone} does not have.");
            }
            level.loopChunks = true;
            level.shuffleRepeats = true;
            level.seed = design.seed;
            level.courseLengthOverride = design.courseLength;
            EditorUtility.SetDirty(level);
            return level;
        }

        static void AddSceneToBuildSettings(string path)
        {
            var current = EditorBuildSettings.scenes;
            if (current.Length > 0 && current[0].path == path && current[0].enabled) return;
            var scenes = new List<EditorBuildSettingsScene>(current);
            scenes.RemoveAll(s => s.path == path);
            scenes.Insert(0, new EditorBuildSettingsScene(path, true));
            EditorBuildSettings.scenes = scenes.ToArray();
        }

        /// <summary>
        /// Puts the game scene first in the build's scene list, if it has been built. The list lives in ProjectSettings,
        /// which is not in git, so a checkout that has the scene may still have an empty list (GameBuildHook).
        /// </summary>
        internal static void ListGameScene()
        {
            if (File.Exists(ScenePath)) AddSceneToBuildSettings(ScenePath);
        }

        // ------------------------------------------------------------------ scene

        static void BuildScene(LevelDefinition[] levels, ZoneArt firstArt, Material prims)
        {
            RenderSettings.ambientMode = AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.66f, 0.6f, 0.54f);
            var sun = new GameObject("Sun").AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.color = new Color(1f, 0.9f, 0.75f);
            sun.intensity = 1.1f;
            sun.shadows = LightShadows.None;
            sun.transform.rotation = Quaternion.Euler(38f, -35f, 0f);

            var game = new GameObject("Game");
            var flow = game.AddComponent<GameFlow>();
            var director = game.AddComponent<ChaseDirector>();
            var input = game.AddComponent<KidInput>();
            var hud = game.AddComponent<GreyboxHud>();
            var session = game.AddComponent<GameSession>();
            var menus = game.AddComponent<GameMenus>();

            var course = new GameObject("Course");
            var streamer = course.AddComponent<LevelStreamer>();

            var kid = BuildKid(prims);
            var rooster = BuildRooster(prims);

            var cameraObject = new GameObject("Main Camera") { tag = "MainCamera" };
            var camera = cameraObject.AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = ArtAssets.Haze;
            camera.fieldOfView = 34f;     // Kick Off's lens: with ChaseCamera's close framing, about 10 m back and 2.5 m up
            camera.nearClipPlane = 0.3f;
            camera.farClipPlane = 260f;
            cameraObject.AddComponent<AudioListener>();
            var chaseCamera = cameraObject.AddComponent<ChaseCamera>();
            chaseCamera.kid = kid;
            chaseCamera.rooster = rooster;
            chaseCamera.director = director;
            cameraObject.transform.position = new Vector3(2f, 1.8f, -16f);

            var scenery = new GameObject("Scenery");
            var backdrop = scenery.AddComponent<BackdropStreamer>();
            var groundPlane = new GameObject("GroundPlane", typeof(MeshFilter), typeof(MeshRenderer));
            groundPlane.transform.SetParent(scenery.transform, false);
            groundPlane.GetComponent<MeshFilter>().sharedMesh = ArtAssets.Quad;
            var groundRenderer = groundPlane.GetComponent<MeshRenderer>();
            groundRenderer.sharedMaterial = firstArt != null ? firstArt.Ground : null;
            groundRenderer.shadowCastingMode = ShadowCastingMode.Off;
            backdrop.follow = cameraObject.transform;
            backdrop.targetCamera = camera;
            backdrop.art = firstArt;
            backdrop.groundPlane = groundRenderer;

            flow.level = null; // the session loads levels
            flow.kid = kid;
            flow.rooster = rooster;
            flow.director = director;
            flow.streamer = streamer;
            flow.input = input;
            flow.chaseCamera = chaseCamera;
            flow.tapToRetry = false;
            hud.flow = flow;

            session.flow = flow;
            session.backdrop = backdrop;
            session.levels = levels;
            // Each zone's first level is open from the start, so every zone can be played straight away; the others keep
            // the doc's star gates.
            var open = new List<int>();
            for (int zone = 1; zone <= StoryMap.ZoneCount; zone++) open.Add(StoryMap.FirstLevelOf(zone));
            session.openFromStart = open.ToArray();
            session.storyPages = 5;

            menus.session = session;
            menus.title = Picture("F1_title_screen_v2.png", "F1_title_screen.png");
            menus.story = new[]
            {
                Picture("F2_story_craving_v2.png", "F2_story_craving.png"),
                Picture("F3_story_plan_v2.png", "F3_story_plan.png"),
                Picture("F4_story_basket_v2.png", "F4_story_basket.png"),
                Picture("F5_story_escape_v2.png", "F5_story_escape.png"),
                Picture("F6_story_wriggle_free_v2.png", "F6_story_wriggle_free.png"),
            };
            menus.won = menus.story[4];
            menus.escaped = Picture("F7_rooster_escaped.png");
            menus.finale = Picture("F8_story_amma_kitchen.png");
            menus.zones = new[] { Picture("C1_lane_mood.png"), Picture("D1_fields_mood.png"), Picture("E2_market_mood.png", "E1_rooftops_mood.png") };
        }

        /// <summary>The first of these reference pictures that exists (real, or its placeholder).</summary>
        static Texture2D Picture(params string[] names)
        {
            foreach (var name in names)
            {
                var path = ArtAssets.Reference(name);
                if (path != null) return ArtAssets.Texture(path);
            }
            return null;
        }

        static Texture2D Pose(string name) => ArtAssets.Texture(ArtAssets.Cutout(name));

        /// <summary>A quad with the PaintedCard shader that a CardFlipbook fills with frames, under a body pivot.</summary>
        static CardFlipbook FlipbookCard(Transform root, string materialName, Texture2D first, float height, float pivotY,
            out Transform body)
        {
            body = new GameObject("Body").transform;
            body.SetParent(root, false);
            body.localPosition = new Vector3(0f, pivotY, 0f);
            var card = new GameObject("Card", typeof(MeshFilter), typeof(MeshRenderer));
            card.transform.SetParent(body, false);
            card.GetComponent<MeshFilter>().sharedMesh = ArtAssets.Quad;
            var renderer = card.GetComponent<MeshRenderer>();
            string path = $"{MaterialFolder}/{materialName}.mat";
            var material = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (material == null)
            {
                material = new Material(ArtAssets.CardShader);
                AssetDatabase.CreateAsset(material, path);
            }
            material.mainTexture = first;
            material.SetColor("_HazeColor", ArtAssets.Haze);
            EditorUtility.SetDirty(material);
            renderer.sharedMaterial = material;
            renderer.shadowCastingMode = ShadowCastingMode.Off;
            renderer.receiveShadows = false;
            renderer.sortingOrder = CharacterOrder;
            var flipbook = card.AddComponent<CardFlipbook>();
            flipbook.pixelsPerMetre = first != null ? first.height / height : 300f;
            flipbook.offset = new Vector2(0f, -pivotY);
            flipbook.Show(first);
            return flipbook;
        }

        static KidController BuildKid(Material prims)
        {
            var root = new GameObject("Kid");
            var kid = root.AddComponent<KidController>();
            if (KidModel(root, kid)) return kid;   // the 3D kid; the painted flipbook below until she is built
            var run = Pose("run_contact");
            if (run == null)
            {
                Debug.LogWarning("No kid poses in ArtSource/cutouts/kid: the kid is a capsule.");
                PrimCapsule(root.transform, prims, new Vector3(0f, 0.52f, 0f), new Vector3(0.35f, 0.52f, 0.35f), new Color(0.15f, 0.45f, 0.85f));
                return kid;
            }
            var visual = root.AddComponent<KidCardVisual>();
            visual.kid = kid;
            visual.card = FlipbookCard(root.transform, "Kid_Card", run, 1.1f, 0f, out visual.body);
            visual.runContact = run;
            visual.runPassing = Pose("run_passing");
            visual.jumpUp = Pose("jump_up");
            visual.fall = Pose("fall");
            visual.land = Pose("land");
            visual.slide = Pose("slide");
            visual.vault = Pose("vault");
            visual.stumble = Pose("stumble");
            visual.dive = Pose("dive");
            return kid;
        }

        static RoosterBrain BuildRooster(Material prims)
        {
            var root = new GameObject("Rooster");
            var brain = root.AddComponent<RoosterBrain>();
            if (RoosterModel(root, brain)) return brain;
            var run = Pose("rooster_run_1");
            if (run == null)
            {
                Debug.LogWarning("No rooster poses in ArtSource/cutouts/rooster: the rooster is a ball.");
                PrimCapsule(root.transform, prims, new Vector3(0f, 0.3f, 0f), new Vector3(0.45f, 0.3f, 0.3f), new Color(0.72f, 0.22f, 0.1f));
                return brain;
            }
            var visual = root.AddComponent<RoosterCardVisual>();
            visual.rooster = brain;
            // The body pivots at mid-height so the tumble spins him about his middle, not his feet.
            visual.card = FlipbookCard(root.transform, "Rooster_Card", run, 0.62f, 0.3f, out visual.body);
            visual.run1 = run;
            visual.run2 = Pose("rooster_run_2");
            visual.flutter = Pose("rooster_flutter");
            visual.crow = Pose("rooster_crow");
            visual.startled = Pose("rooster_startled");
            visual.tumble = Pose("rooster_tumble");
            visual.peck = Pose("rooster_peck");
            visual.strut = Pose("rooster_strut");
            return brain;
        }

        static void PrimCapsule(Transform parent, Material material, Vector3 position, Vector3 scale, Color color)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Capsule);
            Object.DestroyImmediate(go.GetComponent<Collider>());
            go.transform.SetParent(parent, false);
            go.transform.localPosition = position;
            go.transform.localScale = scale;
            go.GetComponent<Renderer>().sharedMaterial = material;
            go.AddComponent<GreyboxColor>().SetColor(color);
        }
    }
}
