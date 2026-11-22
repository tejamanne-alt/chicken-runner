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
    /// Milestone 1: builds the whole grey-box chase from code. Tuning assets for the three zones, obstacle
    /// definitions, six lane chunks plus a runway as prefabs, a level that loops them, and the Chase scene.
    ///
    /// Re-running it rebuilds the chunk prefabs, the level and the scene, but keeps existing tuning and
    /// obstacle assets, so numbers tuned in the Inspector survive.
    /// </summary>
    public static class GreyboxBuilder
    {
        const string Root = "Assets/ChickenRunner";
        const string ConfigFolder = Root + "/Config";
        const string GreyboxFolder = Root + "/Greybox";
        const string ChunkFolder = GreyboxFolder + "/Chunks";
        const string ObstacleFolder = GreyboxFolder + "/Obstacles";
        const string MaterialPath = GreyboxFolder + "/Greybox.mat";
        const string LevelPath = GreyboxFolder + "/Level_Greybox.asset";
        public const string ScenePath = GreyboxFolder + "/Chase_Greybox.unity";

        [MenuItem("Chicken Runner/Build Grey-box Level", priority = 0)]
        public static void BuildFromMenu()
        {
            bool exists = File.Exists(ScenePath);
            if (exists && !EditorUtility.DisplayDialog("Rebuild the grey-box?",
                    "This replaces the grey-box chunk prefabs, the grey-box level and " + ScenePath + ".\n\n"
                    + "Tuning configs and obstacle definitions are kept as they are.", "Rebuild", "Cancel"))
            {
                return;
            }
            if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
            Build();
        }

        [MenuItem("Chicken Runner/Open Grey-box Scene", priority = 1)]
        public static void OpenScene()
        {
            if (!File.Exists(ScenePath))
            {
                if (EditorUtility.DisplayDialog("No grey-box scene yet", "Build the grey-box level now?", "Build", "Cancel"))
                    BuildFromMenu();
                return;
            }
            if (EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) EditorSceneManager.OpenScene(ScenePath);
        }

        public static void Build()
        {
            EnsureFolder(ConfigFolder);
            EnsureFolder(GreyboxFolder);
            EnsureFolder(ChunkFolder);
            EnsureFolder(ObstacleFolder);

            // Work in a fresh scene so the temporary objects never touch the scene the user had open.
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            var material = CreateMaterial();
            var zone1 = CreateTuning(1);
            CreateTuning(2);
            CreateTuning(3);
            var obstacles = new ObstacleSet
            {
                pots = CreateObstacle("PotStack", "Clay pot stack", PenaltyKind.Stumble, 1f, HitReaction.Smash, Palette.Terracotta, "SMASH!"),
                dung = CreateObstacle("CowDung", "Cow dung", PenaltyKind.Slip, 1.15f, HitReaction.Splat, Palette.Dung, "SPLAT!"),
                dog = CreateObstacle("SleepingDog", "Sleeping street dog", PenaltyKind.Stumble, 1f, HitReaction.Wake, Palette.Dog, "WOOF!"),
                puddle = CreateObstacle("Puddle", "Hand-pump puddle", PenaltyKind.Slip, 1f, HitReaction.Splat, Palette.Water, "SPLOSH!"),
                clothesline = CreateObstacle("Clothesline", "Clothesline of sarees", PenaltyKind.Tangle, 1.1f, HitReaction.Wobble, Palette.Kumkum, "TANGLED!"),
            };

            var runway = SaveChunk(BuildRunway(material), "Chunk_Runway");
            var chunks = new List<Chunk>
            {
                SaveChunk(BuildPots(material, obstacles), "Chunk_01_Pots"),
                SaveChunk(BuildDungAndDog(material, obstacles), "Chunk_02_DungAndDog"),
                SaveChunk(BuildClotheslines(material, obstacles), "Chunk_03_Clotheslines"),
                SaveChunk(BuildCot(material, obstacles), "Chunk_04_CotBounce"),
                SaveChunk(BuildCart(material, obstacles), "Chunk_05_BullockCart"),
                SaveChunk(BuildMischief(material, obstacles), "Chunk_06_Mischief"),
            };

            var level = CreateLevel(zone1, runway, chunks);
            BuildScene(level, material);

            EditorSceneManager.SaveScene(scene, ScenePath);
            AddSceneToBuildSettings(ScenePath);
            AssetDatabase.SaveAssets();
            Debug.Log("Chicken Runner grey-box built: " + ScenePath + ". Press Play, then tap or press Space to start the chase.");
        }

        // ------------------------------------------------------------------ assets

        static void EnsureFolder(string path)
        {
            if (AssetDatabase.IsValidFolder(path)) return;
            string parent = Path.GetDirectoryName(path).Replace('\\', '/');
            EnsureFolder(parent);
            AssetDatabase.CreateFolder(parent, Path.GetFileName(path));
        }

        static Material CreateMaterial()
        {
            var shader = FindLitShader();
            var material = AssetDatabase.LoadAssetAtPath<Material>(MaterialPath);
            if (material == null)
            {
                material = new Material(shader) { name = "Greybox" };
                AssetDatabase.CreateAsset(material, MaterialPath);
            }
            else if (material.shader != shader)
            {
                material.shader = shader;
            }
            if (material.HasProperty("_Smoothness")) material.SetFloat("_Smoothness", 0.1f);
            if (material.HasProperty("_Glossiness")) material.SetFloat("_Glossiness", 0.1f);
            material.enableInstancing = true;
            EditorUtility.SetDirty(material);
            return material;
        }

        /// <summary>The lit shader of whichever pipeline is active, so the grey-box renders in Built-in or URP.</summary>
        static Shader FindLitShader()
        {
            Shader shader = null;
            if (GraphicsSettings.currentRenderPipeline != null) shader = Shader.Find("Universal Render Pipeline/Lit");
            if (shader == null) shader = Shader.Find("Standard");
            if (shader == null)
            {
                var probe = GameObject.CreatePrimitive(PrimitiveType.Cube);
                shader = probe.GetComponent<Renderer>().sharedMaterial.shader;
                Object.DestroyImmediate(probe);
            }
            return shader;
        }

        static TuningConfig CreateTuning(int zone)
        {
            string path = ConfigFolder + "/Tuning_Zone" + zone + ".asset";
            var existing = AssetDatabase.LoadAssetAtPath<TuningConfig>(path);
            if (existing != null) return existing;
            var config = ScriptableObject.CreateInstance<TuningConfig>();
            config.zone = zone;
            config.values = ChaseTuning.ForZone(zone);
            AssetDatabase.CreateAsset(config, path);
            return config;
        }

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

        static LevelDefinition CreateLevel(TuningConfig tuning, Chunk runway, List<Chunk> chunks)
        {
            var level = AssetDatabase.LoadAssetAtPath<LevelDefinition>(LevelPath);
            if (level == null)
            {
                level = ScriptableObject.CreateInstance<LevelDefinition>();
                AssetDatabase.CreateAsset(level, LevelPath);
            }
            level.displayName = "Grey-box lane";
            level.tuning = tuning;
            level.runwayChunk = runway;
            level.chunks = chunks;
            level.loopChunks = true;
            level.courseLengthOverride = 0f;
            EditorUtility.SetDirty(level);
            return level;
        }

        static void AddSceneToBuildSettings(string path)
        {
            var scenes = new List<EditorBuildSettingsScene>(EditorBuildSettings.scenes);
            scenes.RemoveAll(s => s.path == path);
            scenes.Insert(0, new EditorBuildSettingsScene(path, true));
            EditorBuildSettings.scenes = scenes.ToArray();
        }

        // ------------------------------------------------------------------ scene

        static void BuildScene(LevelDefinition level, Material material)
        {
            RenderSettings.ambientMode = AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.62f, 0.56f, 0.5f);

            var sun = new GameObject("Sun").AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.color = new Color(1f, 0.9f, 0.75f);
            sun.intensity = 1.25f;
            sun.shadows = LightShadows.Soft;
            sun.transform.rotation = Quaternion.Euler(38f, -35f, 0f);

            var game = new GameObject("Game");
            var flow = game.AddComponent<GameFlow>();
            var director = game.AddComponent<ChaseDirector>();
            var input = game.AddComponent<KidInput>();
            var hud = game.AddComponent<GreyboxHud>();

            var course = new GameObject("Course");
            var streamer = course.AddComponent<LevelStreamer>();

            var kid = BuildKid(material);
            var rooster = BuildRooster(material);

            var cameraObject = new GameObject("Main Camera") { tag = "MainCamera" };
            var camera = cameraObject.AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = Palette.Sky;
            camera.fieldOfView = 30f;
            camera.nearClipPlane = 0.3f;
            camera.farClipPlane = 200f;
            cameraObject.AddComponent<AudioListener>();
            var chaseCamera = cameraObject.AddComponent<ChaseCamera>();
            chaseCamera.kid = kid;
            chaseCamera.rooster = rooster;
            chaseCamera.director = director;
            cameraObject.transform.position = new Vector3(2f, 1.8f, -16f);

            flow.level = level;
            flow.kid = kid;
            flow.rooster = rooster;
            flow.director = director;
            flow.streamer = streamer;
            flow.input = input;
            flow.chaseCamera = chaseCamera;
            hud.flow = flow;

            // A far strip of hills along the whole course, so the horizon is not empty sky.
            var backdrop = new GameObject("Backdrop").transform;
            float courseEnd = level.CourseLength + 100f;
            Prim(PrimitiveType.Cube, "Hills", backdrop, new Vector3(courseEnd * 0.5f - 50f, 1.5f, 40f), new Vector3(courseEnd + 100f, 6f, 1f), Palette.Hills, material);
        }

        static KidController BuildKid(Material material)
        {
            var root = new GameObject("Kid");
            var kid = root.AddComponent<KidController>();
            var visual = root.AddComponent<KidVisual>();

            var body = new GameObject("Body").transform;
            body.SetParent(root.transform, false);

            // Toddler proportions: short body, big head, leopard-print hairband.
            var torso = Prim(PrimitiveType.Capsule, "Torso", body, new Vector3(0f, 0.31f, 0f), new Vector3(0.32f, 0.31f, 0.32f), Palette.Kit, material);
            Prim(PrimitiveType.Sphere, "Head", body, new Vector3(0f, 0.82f, 0f), new Vector3(0.44f, 0.44f, 0.44f), Palette.Skin, material);
            Prim(PrimitiveType.Cylinder, "Hairband", body, new Vector3(0f, 0.92f, 0f), new Vector3(0.46f, 0.03f, 0.46f), Palette.Hairband, material);
            Prim(PrimitiveType.Cube, "Nose", body, new Vector3(0.21f, 0.8f, 0f), new Vector3(0.07f, 0.06f, 0.06f), Palette.Skin * 0.85f, material);
            Prim(PrimitiveType.Cube, "Eye", body, new Vector3(0.19f, 0.88f, -0.08f), new Vector3(0.05f, 0.07f, 0.05f), Palette.Ink, material);

            visual.kid = kid;
            visual.body = body;
            visual.kit = torso.GetComponent<GreyboxColor>();
            visual.kitColor = Palette.Kit;
            return kid;
        }

        static RoosterBrain BuildRooster(Material material)
        {
            var root = new GameObject("Rooster");
            var brain = root.AddComponent<RoosterBrain>();
            var visual = root.AddComponent<RoosterVisual>();

            var body = new GameObject("Body").transform;
            body.SetParent(root.transform, false);
            Prim(PrimitiveType.Sphere, "Torso", body, new Vector3(0f, 0.3f, 0f), new Vector3(0.46f, 0.36f, 0.3f), Palette.RoosterBody, material);
            Prim(PrimitiveType.Cube, "Tail", body, new Vector3(-0.24f, 0.46f, 0f), new Vector3(0.1f, 0.34f, 0.22f), Palette.Ink, material)
                .transform.localRotation = Quaternion.Euler(0f, 0f, -28f);
            Prim(PrimitiveType.Cube, "LegFront", body, new Vector3(0.05f, 0.08f, 0.06f), new Vector3(0.04f, 0.16f, 0.04f), Palette.Beak, material);
            Prim(PrimitiveType.Cube, "LegBack", body, new Vector3(-0.05f, 0.08f, -0.06f), new Vector3(0.04f, 0.16f, 0.04f), Palette.Beak, material);

            var head = new GameObject("Head").transform;
            head.SetParent(body, false);
            head.localPosition = new Vector3(0.18f, 0.5f, 0f);
            Prim(PrimitiveType.Sphere, "Neck", head, Vector3.zero, new Vector3(0.2f, 0.24f, 0.2f), Palette.RoosterNeck, material);
            Prim(PrimitiveType.Cube, "Comb", head, new Vector3(0.01f, 0.14f, 0f), new Vector3(0.12f, 0.09f, 0.04f), Palette.Comb, material);
            Prim(PrimitiveType.Cube, "Beak", head, new Vector3(0.12f, 0f, 0f), new Vector3(0.08f, 0.04f, 0.04f), Palette.Beak, material);
            Prim(PrimitiveType.Cube, "Wattle", head, new Vector3(0.07f, -0.08f, 0f), new Vector3(0.04f, 0.06f, 0.03f), Palette.Comb, material);
            Prim(PrimitiveType.Cube, "Eye", head, new Vector3(0.07f, 0.04f, -0.09f), new Vector3(0.03f, 0.03f, 0.02f), Palette.Ink, material);

            var wing = new GameObject("Wing").transform;
            wing.SetParent(body, false);
            wing.localPosition = new Vector3(0f, 0.34f, -0.16f);
            Prim(PrimitiveType.Cube, "Feathers", wing, new Vector3(-0.04f, 0f, 0f), new Vector3(0.26f, 0.14f, 0.04f), Palette.RoosterWing, material);

            visual.brain = brain;
            visual.body = body;
            visual.head = head;
            visual.wing = wing;
            return brain;
        }

        // ------------------------------------------------------------------ chunks

        sealed class ObstacleSet
        {
            public ObstacleDefinition pots, dung, dog, puddle, clothesline;
        }

        /// <summary>Flat start: the kid starts at x = 0 (local 10), the rooster at 12 m pecking at local 22.</summary>
        static GameObject BuildRunway(Material m)
        {
            var kit = new ChunkKit("Runway", 24f, m, 100);
            kit.MangoLine(14f, 5, 2f, 0.6f);
            return kit.Root;
        }

        /// <summary>Teaches the jump: two pot stacks with mango arcs tracing the jump.</summary>
        static GameObject BuildPots(Material m, ObstacleSet o)
        {
            var kit = new ChunkKit("Pots", 16f, m, 1);
            kit.PotStack(5f, o.pots);
            kit.JumpArc(5f);
            kit.Hop(5f - 0.9f, 1.8f, 0.9f);
            kit.PotStack(11f, o.pots);
            kit.JumpArc(11f);
            kit.Hop(11f - 0.9f, 1.8f, 0.9f);
            return kit.Root;
        }

        /// <summary>Dung to jump, a sleeping dog to jump, and a chilli to win distance back.</summary>
        static GameObject BuildDungAndDog(Material m, ObstacleSet o)
        {
            var kit = new ChunkKit("DungAndDog", 18f, m, 2);
            kit.Dung(4.5f, o.dung);
            kit.JumpArc(4.5f);
            kit.Hop(4f, 1f, 0.45f);
            kit.MangoLine(6.8f, 3, 0.8f, 0.55f);
            kit.Dog(10.5f, o.dog);
            kit.JumpArc(10.5f);
            kit.Hop(9.7f, 1.6f, 0.8f);
            kit.Chilli(15f, 0.6f);
            return kit.Root;
        }

        /// <summary>Teaches the slide: two clotheslines, mangoes low underneath. The rooster runs straight under.</summary>
        static GameObject BuildClotheslines(Material m, ObstacleSet o)
        {
            var kit = new ChunkKit("Clotheslines", 16f, m, 3);
            kit.Clothesline(5f, o.clothesline, Palette.SareeA, Palette.SareeB);
            kit.MangoLine(4.4f, 3, 0.6f, 0.3f);
            kit.Clothesline(11f, o.clothesline, Palette.SareeC, Palette.SareeA);
            kit.MangoLine(10.4f, 3, 0.6f, 0.3f);
            return kit.Root;
        }

        /// <summary>A rope cot: land on it (or run into it) for a high bounce along a mango arc, then a pot stack.</summary>
        static GameObject BuildCot(Material m, ObstacleSet o)
        {
            var kit = new ChunkKit("CotBounce", 18f, m, 4);
            kit.Cot(3f);
            kit.Arc(2.9f, 4.8f, 2.4f, 6);
            kit.Hop(3f, 4.8f, 2.2f);
            kit.PotStack(13f, o.pots);
            kit.JumpArc(13f);
            kit.Hop(13f - 0.9f, 1.8f, 0.9f);
            return kit.Root;
        }

        /// <summary>A bullock cart: jump onto the bed and run across, or hit its side and vault slowly. Double jump for the high mangoes.</summary>
        static GameObject BuildCart(Material m, ObstacleSet o)
        {
            var kit = new ChunkKit("BullockCart", 18f, m, 5);
            kit.Cart(5f);
            kit.MangoLine(5.5f, 4, 0.6f, 1.55f);
            kit.MangoLine(5.8f, 3, 0.7f, 2.9f);
            kit.Hop(4.3f, 4f, 1.6f);
            kit.PotStack(13.5f, o.pots);
            kit.JumpArc(13.5f);
            kit.Hop(13.5f - 0.9f, 1.8f, 0.9f);
            return kit.Root;
        }

        /// <summary>
        /// The rooster's mischief: a puddle, then he knocks a pot stack into the lane behind him,
        /// then a clothesline. Jump, react, slide.
        /// </summary>
        static GameObject BuildMischief(Material m, ObstacleSet o)
        {
            var kit = new ChunkKit("Mischief", 20f, m, 6);
            kit.Puddle(4f, 1.6f, o.puddle);
            kit.JumpArc(4f);
            kit.Hop(3f, 2f, 0.5f);
            var knocked = kit.PotStack(12f, o.pots, hiddenUntilMischief: true);
            kit.Mischief(13f, knocked);
            kit.Veranda(10.5f, 3f);
            kit.Clothesline(17f, o.clothesline, Palette.SareeB, Palette.SareeC);
            kit.MangoLine(16.4f, 3, 0.6f, 0.3f);
            return kit.Root;
        }

        /// <summary>Builds one chunk's hierarchy out of primitives.</summary>
        sealed class ChunkKit
        {
            const float LaneDepth = 0.6f;

            readonly Material _material;
            readonly Transform _root;
            readonly System.Random _random;

            public GameObject Root => _root.gameObject;

            public ChunkKit(string name, float length, Material material, int seed)
            {
                _material = material;
                _random = new System.Random(seed);
                _root = new GameObject(name).transform;
                _root.gameObject.AddComponent<Chunk>().length = length;

                // Red-earth lane, solid. Slightly different shade per chunk so speed reads even in grey-box.
                // Not marked static: chunks are pooled and moved at runtime.
                Prim(PrimitiveType.Cube, "Ground", _root, new Vector3(length * 0.5f, -0.25f, 1.5f),
                    new Vector3(length, 0.5f, 6f), Color.Lerp(Palette.Earth, Palette.EarthDark, (float)_random.NextDouble() * 0.5f), material,
                    keepCollider: true);

                var decor = new GameObject("Decor").transform;
                decor.SetParent(_root, false);
                for (float x = 1f; x < length; x += 2f)
                {
                    // Kolam dots along the front edge of the lane.
                    Prim(PrimitiveType.Cube, "Kolam", decor, new Vector3(x, 0.005f, -0.9f), new Vector3(0.18f, 0.01f, 0.18f), Palette.Kolam, material);
                }
                Houses(decor, length);
            }

            void Houses(Transform parent, float length)
            {
                float x = (float)_random.NextDouble();
                while (x < length - 1.5f)
                {
                    float width = Mathf.Min(2.5f + (float)_random.NextDouble() * 2f, length - x);
                    float height = 2.3f + (float)_random.NextDouble() * 1.1f;
                    var wall = Palette.Walls[_random.Next(Palette.Walls.Length)];
                    var house = new GameObject("House").transform;
                    house.SetParent(parent, false);
                    house.localPosition = new Vector3(x + width * 0.5f, 0f, 3.8f);
                    Prim(PrimitiveType.Cube, "Walls", house, new Vector3(0f, height * 0.5f, 0f), new Vector3(width, height, 1.6f), wall, _material);
                    Prim(PrimitiveType.Cube, "Roof", house, new Vector3(0f, height + 0.08f, 0f), new Vector3(width + 0.15f, 0.16f, 1.75f), wall * 0.8f, _material);
                    Prim(PrimitiveType.Cube, "Door", house, new Vector3(0f, 0.7f, -0.81f), new Vector3(0.7f, 1.4f, 0.02f), Palette.Door, _material);
                    if (_random.NextDouble() < 0.35)
                    {
                        // A palm behind the houses.
                        Prim(PrimitiveType.Cylinder, "Trunk", house, new Vector3(width * 0.3f, 2.4f, 1.6f), new Vector3(0.2f, 2.4f, 0.2f), Palette.Trunk, _material);
                        Prim(PrimitiveType.Sphere, "Fronds", house, new Vector3(width * 0.3f, 4.9f, 1.6f), new Vector3(1.8f, 0.6f, 1.8f), Palette.Leaf, _material);
                    }
                    x += width + 0.3f + (float)_random.NextDouble() * 0.9f;
                }
            }

            /// <summary>An obstacle root with a trigger <paramref name="width"/> by <paramref name="height"/>, starting <paramref name="bottom"/> above the ground.</summary>
            Obstacle MakeObstacle(string name, float x, ObstacleDefinition definition, float width, float height, float bottom = 0f,
                bool hidden = false)
            {
                var go = new GameObject(name);
                go.transform.SetParent(_root, false);
                go.transform.localPosition = new Vector3(x, 0f, 0f);
                var trigger = go.AddComponent<BoxCollider>();
                trigger.isTrigger = true;
                trigger.size = new Vector3(width, height, LaneDepth);
                trigger.center = new Vector3(0f, bottom + height * 0.5f, 0f);
                var visual = new GameObject("Visual").transform;
                visual.SetParent(go.transform, false);
                var obstacle = go.AddComponent<Obstacle>();
                obstacle.definition = definition;
                obstacle.visual = visual;
                obstacle.hiddenUntilMischief = hidden;
                return obstacle;
            }

            public Obstacle PotStack(float x, ObstacleDefinition definition, bool hiddenUntilMischief = false)
            {
                var obstacle = MakeObstacle("PotStack", x, definition, 0.45f, 0.6f, 0f, hiddenUntilMischief);
                var v = obstacle.visual;
                Prim(PrimitiveType.Sphere, "Pot", v, new Vector3(0f, 0.15f, 0f), new Vector3(0.46f, 0.3f, 0.46f), Palette.Terracotta, _material);
                Prim(PrimitiveType.Sphere, "Pot", v, new Vector3(0f, 0.38f, 0f), new Vector3(0.36f, 0.24f, 0.36f), Palette.Terracotta * 0.92f, _material);
                Prim(PrimitiveType.Sphere, "Pot", v, new Vector3(0f, 0.56f, 0f), new Vector3(0.26f, 0.18f, 0.26f), Palette.Terracotta, _material);
                return obstacle;
            }

            public void Dung(float x, ObstacleDefinition definition)
            {
                var obstacle = MakeObstacle("CowDung", x, definition, 0.55f, 0.2f);
                Prim(PrimitiveType.Cylinder, "Pat", obstacle.visual, new Vector3(0f, 0.03f, 0f), new Vector3(0.55f, 0.03f, 0.45f), Palette.Dung, _material);
                Prim(PrimitiveType.Cylinder, "Pat", obstacle.visual, new Vector3(0f, 0.08f, 0f), new Vector3(0.32f, 0.03f, 0.26f), Palette.Dung * 0.9f, _material);
            }

            public void Dog(float x, ObstacleDefinition definition)
            {
                var obstacle = MakeObstacle("SleepingDog", x, definition, 0.9f, 0.36f);
                var v = obstacle.visual;
                Prim(PrimitiveType.Capsule, "Body", v, new Vector3(0f, 0.17f, 0f), new Vector3(0.32f, 0.38f, 0.32f), Palette.Dog, _material)
                    .transform.localRotation = Quaternion.Euler(0f, 0f, 90f);
                Prim(PrimitiveType.Sphere, "Head", v, new Vector3(0.44f, 0.18f, 0f), new Vector3(0.24f, 0.22f, 0.22f), Palette.Dog, _material);
                Prim(PrimitiveType.Cube, "Ear", v, new Vector3(0.44f, 0.3f, -0.07f), new Vector3(0.06f, 0.08f, 0.04f), Palette.Dog * 0.7f, _material);
                Prim(PrimitiveType.Cube, "Snout", v, new Vector3(0.58f, 0.15f, 0f), new Vector3(0.08f, 0.08f, 0.1f), Palette.Ink, _material);
            }

            public void Puddle(float x, float width, ObstacleDefinition definition)
            {
                var obstacle = MakeObstacle("Puddle", x, definition, width, 0.15f);
                Prim(PrimitiveType.Cylinder, "Water", obstacle.visual, new Vector3(0f, 0.01f, 0f), new Vector3(width, 0.01f, 0.9f), Palette.Water, _material);
                // The hand pump stands just behind the lane; only its puddle is in the way.
                var pump = new GameObject("HandPump").transform;
                pump.SetParent(_root, false);
                pump.localPosition = new Vector3(x - width * 0.3f, 0f, 1.1f);
                Prim(PrimitiveType.Cylinder, "Barrel", pump, new Vector3(0f, 0.55f, 0f), new Vector3(0.16f, 0.55f, 0.16f), Palette.Iron, _material);
                Prim(PrimitiveType.Cube, "Handle", pump, new Vector3(-0.25f, 1.05f, 0f), new Vector3(0.5f, 0.05f, 0.05f), Palette.Iron, _material)
                    .transform.localRotation = Quaternion.Euler(0f, 0f, 15f);
                Prim(PrimitiveType.Cube, "Spout", pump, new Vector3(0.12f, 0.8f, -0.05f), new Vector3(0.18f, 0.06f, 0.06f), Palette.Iron, _material);
            }

            public void Clothesline(float x, ObstacleDefinition definition, Color left, Color right)
            {
                // Sarees hang from 1.7 m down to 0.65 m: slide under (0.525 m tall) or double jump over.
                const float bottom = 0.65f;
                const float top = 1.7f;
                var obstacle = MakeObstacle("Clothesline", x, definition, 0.5f, top - bottom, bottom);
                var v = obstacle.visual;
                Prim(PrimitiveType.Cube, "SareeLeft", v, new Vector3(0f, (top + bottom) * 0.5f, -0.38f), new Vector3(0.04f, top - bottom, 0.74f), left, _material);
                Prim(PrimitiveType.Cube, "SareeRight", v, new Vector3(0f, (top + bottom) * 0.5f + 0.05f, 0.38f), new Vector3(0.04f, top - bottom - 0.1f, 0.74f), right, _material);
                Prim(PrimitiveType.Cube, "Rope", v, new Vector3(0f, top, 0f), new Vector3(0.02f, 0.02f, 2f), Palette.Ink, _material);
                Prim(PrimitiveType.Cylinder, "PoleFront", _root, new Vector3(x, 0.9f, -1f), new Vector3(0.07f, 0.9f, 0.07f), Palette.Trunk, _material);
                Prim(PrimitiveType.Cylinder, "PoleBack", _root, new Vector3(x, 0.9f, 1f), new Vector3(0.07f, 0.9f, 0.07f), Palette.Trunk, _material);
            }

            public void Cot(float x)
            {
                const float length = 1.9f;
                var go = new GameObject("RopeCot");
                go.transform.SetParent(_root, false);
                go.transform.localPosition = new Vector3(x, 0f, 0f);
                var trigger = go.AddComponent<BoxCollider>();
                trigger.isTrigger = true;
                trigger.size = new Vector3(length, 0.5f, LaneDepth);
                trigger.center = new Vector3(length * 0.5f, 0.25f, 0f);
                var visual = new GameObject("Visual").transform;
                visual.SetParent(go.transform, false);
                Prim(PrimitiveType.Cube, "Weave", visual, new Vector3(length * 0.5f, 0.44f, 0f), new Vector3(length, 0.06f, 0.8f), Palette.Rope, _material);
                Prim(PrimitiveType.Cube, "RailFront", visual, new Vector3(length * 0.5f, 0.44f, -0.42f), new Vector3(length + 0.1f, 0.08f, 0.06f), Palette.Trunk, _material);
                Prim(PrimitiveType.Cube, "RailBack", visual, new Vector3(length * 0.5f, 0.44f, 0.42f), new Vector3(length + 0.1f, 0.08f, 0.06f), Palette.Trunk, _material);
                foreach (float lx in new[] { 0.05f, length - 0.05f })
                {
                    foreach (float lz in new[] { -0.42f, 0.42f })
                        Prim(PrimitiveType.Cube, "Leg", visual, new Vector3(lx, 0.2f, lz), new Vector3(0.07f, 0.4f, 0.07f), Palette.Trunk, _material);
                }
                go.AddComponent<Bouncer>().visual = visual;
            }

            /// <summary>Solid: its top is a platform and its side is a wall the kid vaults slowly.</summary>
            public void Cart(float x)
            {
                const float length = 2.6f;
                const float height = 1f;
                var go = new GameObject("BullockCart");
                go.transform.SetParent(_root, false);
                go.transform.localPosition = new Vector3(x, 0f, 0f);
                var solid = go.AddComponent<BoxCollider>();
                solid.size = new Vector3(length, height, 1.2f);
                solid.center = new Vector3(length * 0.5f, height * 0.5f, 0f);
                Prim(PrimitiveType.Cube, "Bed", go.transform, new Vector3(length * 0.5f, height - 0.08f, 0f), new Vector3(length, 0.16f, 1.2f), Palette.Wood, _material);
                Prim(PrimitiveType.Cube, "Sides", go.transform, new Vector3(length * 0.5f, height * 0.45f, 0f), new Vector3(length, height * 0.9f, 1.0f), Palette.Wood * 0.75f, _material);
                foreach (float z in new[] { -0.72f, 0.72f })
                {
                    Prim(PrimitiveType.Cylinder, "Wheel", go.transform, new Vector3(length * 0.5f, 0.5f, z), new Vector3(1f, 0.04f, 1f), Palette.Trunk, _material)
                        .transform.localRotation = Quaternion.Euler(90f, 0f, 0f);
                }
            }

            /// <summary>A low veranda wall behind the lane, so the knocked-over pots have somewhere to come from.</summary>
            public void Veranda(float x, float length)
            {
                Prim(PrimitiveType.Cube, "Veranda", _root, new Vector3(x + length * 0.5f, 0.3f, 1.7f), new Vector3(length, 0.6f, 1.2f), Palette.Walls[0], _material);
            }

            public void Hop(float x, float length, float height)
            {
                var go = new GameObject("RoosterHop");
                go.transform.SetParent(_root, false);
                go.transform.localPosition = new Vector3(x, 0f, 0f);
                var hop = go.AddComponent<RoosterHop>();
                hop.length = length;
                hop.height = height;
            }

            public void Mischief(float x, Obstacle target)
            {
                var go = new GameObject("MischiefSpot");
                go.transform.SetParent(_root, false);
                go.transform.localPosition = new Vector3(x, 0f, 0f);
                go.AddComponent<MischiefSpot>().target = target;
            }

            public void Mango(float x, float y)
            {
                var pickup = PickupRoot("Mango", x, y, PickupKind.Mango, 0.25f);
                Prim(PrimitiveType.Sphere, "Fruit", pickup.visual, Vector3.zero, new Vector3(0.22f, 0.28f, 0.22f), Palette.Mango, _material);
                Prim(PrimitiveType.Cube, "Leaf", pickup.visual, new Vector3(0.04f, 0.15f, 0f), new Vector3(0.1f, 0.03f, 0.05f), Palette.Leaf, _material);
            }

            public void Chilli(float x, float y)
            {
                var pickup = PickupRoot("Chilli", x, y, PickupKind.Chilli, 0.3f);
                Prim(PrimitiveType.Capsule, "Pod", pickup.visual, Vector3.zero, new Vector3(0.12f, 0.2f, 0.12f), Palette.Chilli, _material)
                    .transform.localRotation = Quaternion.Euler(0f, 0f, 55f);
                Prim(PrimitiveType.Cube, "Stalk", pickup.visual, new Vector3(-0.15f, 0.12f, 0f), new Vector3(0.04f, 0.1f, 0.04f), Palette.Leaf, _material);
                pickup.spinSpeed = 300f;
            }

            Pickup PickupRoot(string name, float x, float y, PickupKind kind, float radius)
            {
                var go = new GameObject(name);
                go.transform.SetParent(_root, false);
                go.transform.localPosition = new Vector3(x, y, 0f);
                var sphere = go.AddComponent<SphereCollider>();
                sphere.isTrigger = true;
                sphere.radius = radius;
                var visual = new GameObject("Visual").transform;
                visual.SetParent(go.transform, false);
                var pickup = go.AddComponent<Pickup>();
                pickup.kind = kind;
                pickup.visual = visual;
                return pickup;
            }

            public void MangoLine(float x, int count, float spacing, float y)
            {
                for (int i = 0; i < count; i++) Mango(x + i * spacing, y);
            }

            /// <summary>Mangoes along a full single jump centred on <paramref name="centreX"/>, so they teach the timing.</summary>
            public void JumpArc(float centreX)
            {
                var t = ChaseTuning.ForZone(1);
                float length = JumpMath.JumpLengthAt(t, t.kidRunSpeed);
                Arc(centreX - length * 0.5f, length, t.jumpHeight, 5);
            }

            /// <summary>Mangoes along a parabola of the kid's feet, lifted to the middle of the body.</summary>
            public void Arc(float startX, float length, float peak, int count)
            {
                for (int i = 0; i < count; i++)
                {
                    float s = (i + 1f) / (count + 1f);
                    Mango(startX + s * length, 0.55f + 4f * peak * s * (1f - s));
                }
            }
        }

        /// <summary>Creates a primitive with the shared material and a colour tint; colliders are removed unless asked for.</summary>
        static GameObject Prim(PrimitiveType type, string name, Transform parent, Vector3 localPosition, Vector3 localScale, Color color,
            Material material, bool keepCollider = false)
        {
            var go = GameObject.CreatePrimitive(type);
            go.name = name;
            if (!keepCollider) Object.DestroyImmediate(go.GetComponent<Collider>());
            go.transform.SetParent(parent, false);
            go.transform.localPosition = localPosition;
            go.transform.localScale = localScale;
            go.GetComponent<Renderer>().sharedMaterial = material;
            color.a = 1f;
            go.AddComponent<GreyboxColor>().SetColor(color);
            return go;
        }

        static class Palette
        {
            public static readonly Color Sky = new Color(0.98f, 0.84f, 0.6f);
            public static readonly Color Hills = new Color(0.72f, 0.62f, 0.55f);
            public static readonly Color Earth = new Color(0.74f, 0.43f, 0.26f);
            public static readonly Color EarthDark = new Color(0.62f, 0.34f, 0.2f);
            public static readonly Color Kolam = new Color(0.97f, 0.95f, 0.9f);
            public static readonly Color[] Walls =
            {
                new Color(0.94f, 0.93f, 0.86f), // lime-wash
                new Color(0.33f, 0.4f, 0.7f),   // indigo
                new Color(0.96f, 0.77f, 0.27f), // turmeric
                new Color(0.93f, 0.72f, 0.68f),
                new Color(0.58f, 0.78f, 0.9f),
            };
            public static readonly Color Door = new Color(0.35f, 0.2f, 0.12f);
            public static readonly Color Trunk = new Color(0.45f, 0.3f, 0.18f);
            public static readonly Color Leaf = new Color(0.3f, 0.6f, 0.2f);
            public static readonly Color Wood = new Color(0.6f, 0.38f, 0.2f);
            public static readonly Color Rope = new Color(0.85f, 0.75f, 0.5f);
            public static readonly Color Iron = new Color(0.25f, 0.3f, 0.35f);
            public static readonly Color Ink = new Color(0.1f, 0.08f, 0.08f);

            public static readonly Color Terracotta = new Color(0.78f, 0.36f, 0.2f);
            public static readonly Color Dung = new Color(0.36f, 0.26f, 0.12f);
            public static readonly Color Dog = new Color(0.82f, 0.66f, 0.42f);
            public static readonly Color Water = new Color(0.35f, 0.55f, 0.85f);
            public static readonly Color Kumkum = new Color(0.85f, 0.12f, 0.3f);
            public static readonly Color SareeA = new Color(0.85f, 0.12f, 0.3f);
            public static readonly Color SareeB = new Color(0.98f, 0.62f, 0.1f);
            public static readonly Color SareeC = new Color(0.2f, 0.6f, 0.55f);

            public static readonly Color Mango = new Color(1f, 0.72f, 0.12f);
            public static readonly Color Chilli = new Color(0.9f, 0.1f, 0.05f);

            public static readonly Color Kit = new Color(0.15f, 0.45f, 0.85f);
            public static readonly Color Skin = new Color(0.82f, 0.6f, 0.45f);
            public static readonly Color Hairband = new Color(0.9f, 0.68f, 0.2f);

            public static readonly Color RoosterBody = new Color(0.72f, 0.22f, 0.1f);
            public static readonly Color RoosterNeck = new Color(0.95f, 0.55f, 0.15f);
            public static readonly Color RoosterWing = new Color(0.45f, 0.15f, 0.08f);
            public static readonly Color Comb = new Color(0.9f, 0.08f, 0.08f);
            public static readonly Color Beak = new Color(0.95f, 0.8f, 0.2f);
        }
    }
}
