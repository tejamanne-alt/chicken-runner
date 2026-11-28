using System.Collections.Generic;
using ChickenRunner.Core;
using UnityEngine;

namespace ChickenRunner.EditorTools
{
    internal static partial class GameBuilder
    {
        /// <summary>
        /// Flat roofs, metres. The doc allows 2.2 to 2.6 m; the tuning report shows 2.6 m needs a frame-perfect double
        /// jump and about 2.37 m leaves a fair 150 ms window, so roofs sit just under that.
        /// </summary>
        internal const float Roof = 2.35f;

        /// <summary>Card sort orders: the lane's pieces over the scenery, the kid and rooster over those, foreground plants over all.</summary>
        internal const int SceneryOrder = 0;
        internal const int LaneOrder = 5;
        internal const int CharacterOrder = 10;
        internal const int ForegroundOrder = 20;

        /// <summary>What every chunk of one zone shares: materials, obstacle definitions and the zone's tuning.</summary>
        sealed class ZoneKit
        {
            public int zone;
            public ChaseTuning tuning;
            public Material prims;
            public Material ground;
            public Material water;
            public Material puddle;
            public Material stone;
            public Obstacles obstacles;
        }

        sealed class Obstacles
        {
            public ObstacleDefinition pots, dung, dog, puddle, clothesline, hens, tank, goats, ducks, sand, branch;
        }

        /// <summary>
        /// Builds one chunk: painted pieces where the art exists, grey-box shapes where it does not, the colliders the
        /// kid and rooster run on, pickups, rooster hops and mischief. Call <see cref="Finish"/> last: it lays the ground,
        /// leaving the canal holes open.
        /// </summary>
        sealed class Kit
        {
            const float LaneDepth = 0.6f;
            const float GroundFront = -40f;
            const float GroundBack = 4.5f;
            const float CanalBed = -0.28f;
            const float PlankBridgeLength = 3.9f;   // plank_model.LENGTH

            readonly ZoneKit _z;
            readonly Transform _root;
            readonly float _length;
            readonly List<Vector2> _holes = new List<Vector2>();
            readonly System.Random _random;

            public Kit(string name, float length, ZoneKit zone, int seed)
            {
                _z = zone;
                _length = length;
                _random = new System.Random(seed);
                _root = new GameObject(name).transform;
                _root.gameObject.AddComponent<Chunk>().length = length;
            }

            public float Length => _length;
            public Transform Root => _root;

            public GameObject Finish()
            {
                _holes.Sort((a, b) => a.x.CompareTo(b.x));
                float x = 0f;
                foreach (var hole in _holes)
                {
                    if (hole.x > x) GroundSlab(x, hole.x);
                    x = Mathf.Max(x, hole.y);
                }
                if (x < _length) GroundSlab(x, _length);
                return _root.gameObject;
            }

            void GroundSlab(float from, float to)
            {
                var slab = Box("Ground", _root, new Vector3((from + to) * 0.5f, -0.25f, (GroundFront + GroundBack) * 0.5f),
                    new Vector3(to - from, 0.5f, GroundBack - GroundFront), _z.ground, true);
                slab.isStatic = false; // chunks are pooled and moved at runtime
            }

            // ------------------------------------------------------------------ shapes and cards

            /// <summary>A cube with a collider (solid unless <paramref name="collider"/> is false) and the given material.</summary>
            GameObject Box(string name, Transform parent, Vector3 centre, Vector3 size, Material material, bool collider)
            {
                var go = GameObject.CreatePrimitive(PrimitiveType.Cube);
                go.name = name;
                if (!collider) Object.DestroyImmediate(go.GetComponent<Collider>());
                go.transform.SetParent(parent, false);
                go.transform.localPosition = centre;
                go.transform.localScale = size;
                go.GetComponent<Renderer>().sharedMaterial = material;
                return go;
            }

            /// <summary>A tinted grey-box primitive with no collider, for pieces with no painting yet.</summary>
            GameObject Prim(PrimitiveType type, string name, Transform parent, Vector3 position, Vector3 scale, Color color)
            {
                var go = GameObject.CreatePrimitive(type);
                go.name = name;
                Object.DestroyImmediate(go.GetComponent<Collider>());
                go.transform.SetParent(parent, false);
                go.transform.localPosition = position;
                go.transform.localScale = scale;
                go.GetComponent<Renderer>().sharedMaterial = _z.prims;
                color.a = 1f;
                go.AddComponent<GreyboxColor>().SetColor(color);
                return go;
            }

            /// <summary>
            /// A painted cut-out (its 3D model where it has one) standing with its bottom centre at (x, y, z) under
            /// <paramref name="parent"/>, sized by
            /// <paramref name="height"/> (or <paramref name="width"/>, or the manifest's real size when both are 0).
            /// Returns null, and its size as zero, when the cut-out does not exist.
            /// </summary>
            public GameObject Art(Transform parent, string piece, float x, float y, float z, out Vector2 size, float height = 0f,
                float width = 0f, bool mirror = false, int order = LaneOrder, float roomBehind = float.PositiveInfinity)
            {
                size = Vector2.zero;
                var texture = ArtAssets.CutoutTexture(piece);
                if (texture == null) return null;
                var real = ArtAssets.SizeOf(piece, texture, 1f);
                float aspect = real.x / Mathf.Max(0.001f, real.y);
                if (height > 0f) size = new Vector2(height * aspect, height);
                else if (width > 0f) size = new Vector2(width, width / aspect);
                else size = real;
                var card = ArtModels.Enabled
                    ? ArtModels.Place(parent ?? _root, piece, new Vector3(x, y, z), size, mirror, roomBehind: roomBehind)
                    : null;
                if (card == null) card = ArtAssets.Card(parent ?? _root, piece, ArtAssets.CardMaterial(texture), new Vector3(x, y, z), size, mirror);
                foreach (var renderer in card.GetComponentsInChildren<Renderer>()) renderer.sortingOrder = order;
                return card;
            }

            /// <summary>
            /// Moves a placed piece back (along +z) until the nearest point of what it draws is at <paramref name="frontZ"/>:
            /// models are centred on their own origins, not all on their painting's plane, so a deep one (a stall's tables, a
            /// tree's crown, the cart's near side) can reach a metre or two toward the camera, over the running line. A piece
            /// already behind it stays.
            /// </summary>
            static void FrontAt(GameObject piece, float frontZ)
            {
                if (piece == null) return;
                var renderers = piece.GetComponentsInChildren<Renderer>();
                if (renderers.Length == 0) return;
                var bounds = renderers[0].bounds;
                foreach (var renderer in renderers) bounds.Encapsulate(renderer.bounds);
                float shift = frontZ - bounds.min.z;      // chunks are built at the origin: world z is the chunk's
                if (shift > 0f) piece.transform.position += new Vector3(0f, 0f, shift);
            }

            public GameObject Art(string piece, float x, float z, float height = 0f, float width = 0f, bool mirror = false) =>
                Art(_root, piece, x, 0f, z, out _, height, width, mirror);

            public GameObject Decal(string piece, float x, float z, float width, float turn)
            {
                var texture = ArtAssets.CutoutTexture(piece);
                if (texture == null) return null;
                var real = ArtAssets.SizeOf(piece, texture, 1f);
                var size = new Vector2(width, width * real.y / Mathf.Max(0.001f, real.x));
                // A model that lies flat (prints, a leaf) is laid face up; one that stands (a tuft, pebbles, a husk) stands,
                // turned at random.
                var card = ArtModels.Enabled ? ArtModels.Place(_root, piece, new Vector3(x, 0f, z), size, false,
                    ArtModels.LiesFlat(piece) || !ArtModels.Has(piece), turn) : null;
                if (card == null) card = ArtAssets.Card(_root, piece, ArtAssets.CardMaterial(texture), new Vector3(x, 0.004f, z), size, false, true, turn);
                foreach (var renderer in card.GetComponentsInChildren<Renderer>()) renderer.sortingOrder = LaneOrder - 1;
                return card;
            }

            // ------------------------------------------------------------------ obstacles

            /// <summary>An obstacle root with a trigger <paramref name="width"/> by <paramref name="height"/>, starting <paramref name="bottom"/> above the ground.</summary>
            Obstacle MakeObstacle(string name, float x, ObstacleDefinition definition, float width, float height, float bottom = 0f,
                bool hidden = false, float y = 0f)
            {
                var go = new GameObject(name);
                go.transform.SetParent(_root, false);
                go.transform.localPosition = new Vector3(x, y, 0f);
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

            public Obstacle PotStack(float x, bool hiddenUntilMischief = false, float y = 0f, bool? mirror = null)
            {
                var obstacle = MakeObstacle("PotStack", x, _z.obstacles.pots, 0.45f, 0.6f, 0f, hiddenUntilMischief, y);
                var v = obstacle.visual;
                bool flip = mirror ?? _random.NextDouble() < 0.5;
                if (Art(v, "pot_stack", 0f, 0f, 0.05f, out _, height: 0.68f, mirror: flip) == null)
                {
                    Prim(PrimitiveType.Sphere, "Pot", v, new Vector3(0f, 0.15f, 0f), new Vector3(0.46f, 0.3f, 0.46f), Palette.Terracotta);
                    Prim(PrimitiveType.Sphere, "Pot", v, new Vector3(0f, 0.38f, 0f), new Vector3(0.36f, 0.24f, 0.36f), Palette.Terracotta);
                    Prim(PrimitiveType.Sphere, "Pot", v, new Vector3(0f, 0.56f, 0f), new Vector3(0.26f, 0.18f, 0.26f), Palette.Terracotta);
                }
                return obstacle;
            }

            public void Dung(float x)
            {
                var obstacle = MakeObstacle("CowDung", x, _z.obstacles.dung, 0.55f, 0.2f);
                if (Art(obstacle.visual, "dung", 0f, 0f, 0.05f, out _, width: 0.6f) == null)
                    Prim(PrimitiveType.Cylinder, "Pat", obstacle.visual, new Vector3(0f, 0.03f, 0f), new Vector3(0.55f, 0.03f, 0.45f), Palette.Dung);
            }

            public void Dog(float x)
            {
                // its curled body (the painting's 0.95 m takes in the tail and paws): what a jump at 3.5 m/s must clear
                var obstacle = MakeObstacle("SleepingDog", x, _z.obstacles.dog, 0.75f, 0.36f);
                if (Art(obstacle.visual, "dog_sleeping", 0f, 0f, 0.05f, out _, width: 0.95f) == null)
                    Prim(PrimitiveType.Capsule, "Body", obstacle.visual, new Vector3(0f, 0.17f, 0f), new Vector3(0.32f, 0.38f, 0.32f), Palette.Dog)
                        .transform.localRotation = Quaternion.Euler(0f, 0f, 90f);
            }

            /// <summary>The hand pump behind the lane and its puddle across it.</summary>
            public void Puddle(float x, float width)
            {
                var obstacle = MakeObstacle("Puddle", x, _z.obstacles.puddle, width, 0.15f);
                // The painted puddle (road_textures.py): shallow water reflecting the pale sky in a rim of wet mud, laid
                // flat on the road; a disc of the canal water if it is missing.
                var painted = ArtAssets.CutoutTexture("puddle_water");
                if (painted != null)
                {
                    var card = ArtAssets.Card(obstacle.visual, "PuddleWater", ArtAssets.CardMaterial(painted), new Vector3(0f, 0.004f, 0f),
                        new Vector2(width * 1.15f, width * 1.15f * painted.height / Mathf.Max(1f, painted.width)), false, true);
                    foreach (var renderer in card.GetComponentsInChildren<Renderer>()) renderer.sortingOrder = LaneOrder - 1;
                }
                else
                {
                    var water = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                    water.name = "Water";
                    Object.DestroyImmediate(water.GetComponent<Collider>());
                    water.transform.SetParent(obstacle.visual, false);
                    water.transform.localPosition = new Vector3(0f, 0.004f, 0f);
                    water.transform.localScale = new Vector3(width, 0.004f, 0.9f);
                    water.GetComponent<Renderer>().sharedMaterial = _z.puddle != null ? _z.puddle : _z.water;
                }
                // Far enough back (its model is 1 m deep) that its bucket and spout stay off the running line.
                if (Art("hand_pump", x - width * 0.3f, 1.35f, height: 1.2f) == null)
                    Prim(PrimitiveType.Cylinder, "HandPump", _root, new Vector3(x - width * 0.3f, 0.55f, 1.35f), new Vector3(0.16f, 0.55f, 0.16f), Palette.Iron);
            }

            /// <summary>Sarees on a line across the lane, hanging from 1.6 m down to 0.7 m: slide under, or double jump over.</summary>
            public void Clothesline(float x, bool? mirror = null)
            {
                const float bottom = 0.7f;
                const float top = 1.6f;
                var obstacle = MakeObstacle("Clothesline", x, _z.obstacles.clothesline, 1.7f, top - bottom, bottom);
                bool flip = mirror ?? _random.NextDouble() < 0.5;
                // The game's own line (ArtSource/tools/models/clothesline_model.py): the painted one's posts and sarees, its
                // hems at 0.78 m so the slide's gap under them is clear; the painted card's cloth hangs to 0.3 m.
                var line = ArtModels.Stand(obstacle.visual, "lane", "clothesline_line", new Vector3(0f, 0f, 0.05f),
                    new Vector3(0f, 1f, 0.05f));
                if (line != null)
                {
                    if (flip) line.transform.localScale = new Vector3(-1f, 1f, 1f);
                    foreach (var renderer in line.GetComponentsInChildren<Renderer>()) renderer.sortingOrder = LaneOrder;
                }
                else if (Art(obstacle.visual, "clothesline", 0f, 0f, 0.05f, out _, width: 2.2f, mirror: flip) == null)
                {
                    Prim(PrimitiveType.Cube, "Sarees", obstacle.visual, new Vector3(0f, (top + bottom) * 0.5f, 0f), new Vector3(1.6f, top - bottom, 0.04f), Palette.Kumkum);
                    Prim(PrimitiveType.Cylinder, "PoleLeft", _root, new Vector3(x - 1f, 0.85f, 0f), new Vector3(0.07f, 0.85f, 0.07f), Palette.Wood);
                    Prim(PrimitiveType.Cylinder, "PoleRight", _root, new Vector3(x + 1f, 0.85f, 0f), new Vector3(0.07f, 0.85f, 0.07f), Palette.Wood);
                }
            }

            /// <summary>A rope cot, a trampoline: land on it or run into it for a high bounce. Starts at x.</summary>
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
                if (Art(visual, "rope_cot", length * 0.5f, 0f, 0.05f, out _, width: length) == null)
                    Prim(PrimitiveType.Cube, "Weave", visual, new Vector3(length * 0.5f, 0.44f, 0f), new Vector3(length, 0.06f, 0.8f), Palette.Rope);
                var bouncer = go.AddComponent<Bouncer>();
                bouncer.visual = visual;
            }

            /// <summary>A bullock cart: its bed is a platform, its side a wall to vault. Starts at x.</summary>
            public void Cart(float x)
            {
                const float width = 3.6f;
                var card = Art("bullock_cart", x + width * 0.5f, 0.05f, width: width);
                // Its near side just in front of the running line, so a kid on the bed shows above it (its mesh reaches a
                // metre in front of its origin).
                FrontAt(card, -0.3f);
                float bedLength = card != null ? width * 0.62f : 2.6f;
                const float bedTop = 0.95f;
                var solid = Box("CartBed", _root, new Vector3(x + bedLength * 0.5f, bedTop * 0.5f, 0f), new Vector3(bedLength, bedTop, 1.2f), _z.prims, true);
                solid.GetComponent<Renderer>().enabled = card == null;
                if (card == null) solid.AddComponent<GreyboxColor>().SetColor(Palette.Wood);
            }

            /// <summary>A flock of hens on the lane: jump them or scatter them.</summary>
            public void Hens(float x, int count) =>
                Flock("Hens", x, count, _z.obstacles.hens, new[] { "hen_1", "hen_2", "hen_3" }, 0.42f, 0.3f, 0.4f, Palette.Hen);

            /// <summary>Goat kids wandering across the street (one or two: a jump for her at most 0.9 m long): jump them or
            /// bump into them.</summary>
            public void Goats(float x, int count) =>
                Flock("Goats", x, count, _z.obstacles.goats ?? _z.obstacles.hens, new[] { "goat_kid" }, 0.55f, 0.34f, 0.45f, Palette.Dog);

            /// <summary>Ducks waddling across the bund road from one canal to the next: jump them or scatter them.</summary>
            public void Ducks(float x, int count) =>
                Flock("Ducks", x, count, _z.obstacles.ducks ?? _z.obstacles.hens, new[] { "duck_1", "duck_2" }, 0.5f, 0.28f, 0.4f, Palette.Hen);

            /// <summary>Animals across the lane, each a little behind the last: one trigger over all of them.</summary>
            void Flock(string name, float x, int count, ObstacleDefinition definition, string[] pieces, float height, float spacing,
                float top, Color fallback)
            {
                float width = 0.1f + count * spacing;
                var obstacle = MakeObstacle(name, x, definition, width, top);
                for (int i = 0; i < count; i++)
                {
                    string piece = pieces[(i + _random.Next(pieces.Length)) % pieces.Length];
                    float hx = -width * 0.5f + 0.05f + spacing * 0.5f + i * spacing;
                    if (Art(obstacle.visual, piece, hx, 0f, 0.05f + 0.08f * i, out _, height: height, mirror: _random.NextDouble() < 0.3) == null)
                        Prim(PrimitiveType.Sphere, name, obstacle.visual, new Vector3(hx, height * 0.45f, 0f), new Vector3(0.3f, height * 0.7f, 0.25f), fallback);
                }
            }

            /// <summary>A heap of river sand tipped at the road's edge for a house being built (an iron pan and a few
            /// bricks beside it): jump it, or flounder into it.</summary>
            public void SandHeap(float x)
            {
                var obstacle = MakeObstacle("SandHeap", x, _z.obstacles.sand ?? _z.obstacles.pots, 0.7f, 0.4f);
                // ArtSource/tools/models/roadside_models.py: 1.24 m across, 0.45 m high
                var heap = ArtModels.Stand(obstacle.visual, "lane", "sand_heap", new Vector3(0f, 0f, 0.05f), new Vector3(0f, 1f, 0.05f));
                if (heap != null) foreach (var renderer in heap.GetComponentsInChildren<Renderer>()) renderer.sortingOrder = LaneOrder;
                else Prim(PrimitiveType.Sphere, "Sand", obstacle.visual, new Vector3(0f, 0.1f, 0f), new Vector3(1.2f, 0.7f, 1.1f), Palette.Hay);
            }

            /// <summary>A roadside neem's low limb across the street, its leaves hanging from 1.6 m down to 0.75 m: slide
            /// under, or double jump over. The trunk stands just behind the road.</summary>
            public void LowBranch(float x, bool? mirror = null)
            {
                const float bottom = 0.75f;
                const float top = 1.6f;
                var obstacle = MakeObstacle("LowBranch", x, _z.obstacles.branch ?? _z.obstacles.clothesline, 1.1f, top - bottom, bottom);
                bool flip = mirror ?? _random.NextDouble() < 0.5;
                // ArtSource/tools/models/roadside_models.py: the limb 1.6 m up, the lowest leaves at 0.78 m
                var tree = ArtModels.Stand(obstacle.visual, "lane", "low_branch", Vector3.zero, new Vector3(0f, 1f, 0f));
                if (tree != null)
                {
                    if (flip) tree.transform.localScale = new Vector3(-1f, 1f, 1f);
                    foreach (var renderer in tree.GetComponentsInChildren<Renderer>()) renderer.sortingOrder = LaneOrder;
                }
                else Prim(PrimitiveType.Cube, "Leaves", obstacle.visual, new Vector3(0f, (top + bottom) * 0.5f, 0f), new Vector3(1.1f, top - bottom, 0.6f), Palette.Leaf);
            }

            /// <summary>Sacks of paddy stacked at the roadside for the cart: a platform to hop onto. Starts at x.</summary>
            public void Sacks(float x)
            {
                const float width = 1.15f, height = 0.8f;
                var card = Art("jute_sacks", x + width * 0.5f, 0.05f, height: height);
                FrontAt(card, -0.3f);
                var solid = Box("Sacks", _root, new Vector3(x + width * 0.45f, height * 0.5f, 0f), new Vector3(width * 0.9f, height, 1.0f), _z.prims, true);
                solid.GetComponent<Renderer>().enabled = card == null;
                if (card == null) solid.AddComponent<GreyboxColor>().SetColor(Palette.Rope);
            }

            public Obstacle HensBasket(float x, bool hiddenUntilMischief = false)
            {
                var obstacle = MakeObstacle("HensBasket", x, _z.obstacles.hens, 0.6f, 0.5f, 0f, hiddenUntilMischief);
                if (Art(obstacle.visual, "hens_basket", 0f, 0f, 0.05f, out _, height: 0.6f) == null)
                    Prim(PrimitiveType.Cylinder, "Basket", obstacle.visual, new Vector3(0f, 0.27f, 0f), new Vector3(0.6f, 0.27f, 0.6f), Palette.Rope);
                return obstacle;
            }

            /// <summary>A water tank on a roof at height <paramref name="y"/>: jump it.</summary>
            public void Tank(float x, float y)
            {
                var obstacle = MakeObstacle("WaterTank", x, _z.obstacles.tank, 0.45f, 0.65f, 0f, false, y);
                if (Art(obstacle.visual, "black_tank", 0f, 0f, 0.05f, out _, height: 0.75f) == null)
                    Prim(PrimitiveType.Cylinder, "Tank", obstacle.visual, new Vector3(0f, 0.35f, 0f), new Vector3(0.55f, 0.35f, 0.55f), Palette.Ink);
            }

            // ------------------------------------------------------------------ buildings and climbables

            /// <summary>
            /// A row of flat-roofed house fronts touching each other, starting at x: their roofs make one run 2.35 m up.
            /// The first front can carry a ladder (the turmeric house's, mirrored to face the kid). Returns the row's end.
            /// </summary>
            public float RoofRow(float x, string[] fronts, bool ladder)
            {
                const float cardHeight = Roof + 0.15f; // the parapet stands a little above the roof the kid runs on
                const float roof = Roof;
                float start = x;
                for (int i = 0; i < fronts.Length; i++)
                {
                    bool withLadder = ladder && i == 0;
                    string piece = withLadder ? "house_turmeric_ladder" : fronts[i];
                    // Its depth kept to 1 m behind its front, so it never runs back through the zone's scenery behind it.
                    var card = Art(_root, piece, 0f, 0f, 0.4f, out var size, height: cardHeight, mirror: withLadder, roomBehind: 1.0f);
                    float width = card != null ? size.x : 2.6f;
                    if (card != null) card.transform.localPosition = new Vector3(x + width * 0.5f, cardHeight * 0.5f, 0.4f);
                    var wall = Box("House", _root, new Vector3(x + width * 0.5f, roof * 0.5f, 0f), new Vector3(width, roof, 1.2f), _z.prims, true);
                    wall.GetComponent<Renderer>().enabled = card == null;
                    if (card == null) wall.AddComponent<GreyboxColor>().SetColor(Palette.Walls[i % Palette.Walls.Length]);
                    if (withLadder) StandLadder(wall, x, width, cardHeight);
                    x += width;
                }
                // His flutter up onto the roof: still rising as it passes the wall's top edge (2.41 m there), so he never
                // clips the parapet, and landing 0.4 m onto the roof.
                Hop(start - 1.6f, 2.0f, 0.9f);
                return x;
            }

            /// <summary>
            /// The bamboo ladder the kid climbs, against the house front starting at x (the card mirrored, so the ladder
            /// is at its left end): where the painting had it before cutouts.py painted it off the card, foot 8.4% of
            /// the way along the front, leaning the way the painted one did, resting on the parapet. Its wall gets the
            /// <see cref="Ladder"/> with the same foot and head.
            /// </summary>
            void StandLadder(GameObject wall, float x, float width, float cardHeight)
            {
                const float front = 0.4f;               // the house front: its card's z
                const float rest = Roof + 0.08f;        // on the parapet's coping
                // The painted ladder's middle moves 13.5% of the front's width along it over 93% of its height.
                float lean = 0.135f * width / (0.93f * cardHeight);
                var foot = new Vector3(x + 0.084f * width, 0f, front - 0.45f);
                var head = new Vector3(foot.x + lean * rest, rest, front - 0.05f);
                var ladder = wall.AddComponent<Ladder>();
                ladder.foot = foot - wall.transform.localPosition;
                ladder.head = head - wall.transform.localPosition;
                ladder.rungSpacing = 0.27f;   // as built by ArtSource/tools/models/ladder_model.py

                var model = ArtModels.Stand(_root, "lane", "bamboo_ladder", foot, head);
                if (model == null)
                {
                    // Not built: two grey-box rails and the rungs, leaning the same way.
                    model = new GameObject("Ladder");
                    model.transform.SetParent(_root, false);
                    model.transform.localPosition = foot;
                    model.transform.localRotation = Quaternion.FromToRotation(Vector3.up, (head - foot).normalized);
                    foreach (float side in new[] { -0.17f, 0.17f })
                        Prim(PrimitiveType.Cube, "Rail", model.transform, new Vector3(side, 1.3f, 0f), new Vector3(0.05f, 2.6f, 0.05f), Palette.Wood);
                    for (float y = 0.27f; y < 2.5f; y += 0.27f)
                        Prim(PrimitiveType.Cube, "Rung", model.transform, new Vector3(0f, y, 0f), new Vector3(0.38f, 0.035f, 0.035f), Palette.Wood);
                }
                foreach (var renderer in model.GetComponentsInChildren<Renderer>()) renderer.sortingOrder = LaneOrder + 1;
            }

            /// <summary>A canal across the lane, <paramref name="width"/> wide from x: wade it, jump it, or cross the plank bridge.</summary>
            public void Canal(float x, float width, bool bridge)
            {
                _holes.Add(new Vector2(x, x + width));
                var bed = Box("CanalBed", _root, new Vector3(x + width * 0.5f, CanalBed - 0.25f, (GroundFront + GroundBack) * 0.5f),
                    new Vector3(width, 0.5f, GroundBack - GroundFront), _z.prims, true);
                bed.GetComponent<Renderer>().enabled = false;
                // The water's surface hides the kid's feet while she wades.
                Box("Water", _root, new Vector3(x + width * 0.5f, -0.06f, (GroundFront + GroundBack) * 0.5f),
                    new Vector3(width, 0.01f, GroundBack - GroundFront), _z.water, false);
                // Its stone-lined banks, as the fields' canals are painted: a granite kerb down each side, the plank bridge's
                // sleepers resting on them. Looks only: the lane's own ground ends at the same edges.
                if (_z.stone != null)
                {
                    foreach (float edge in new[] { x + 0.12f, x + width - 0.12f })
                        Box("Bank", _root, new Vector3(edge, -0.15f, (GroundFront + GroundBack) * 0.5f),
                            new Vector3(0.24f, 0.34f, GroundBack - GroundFront), _z.stone, false);
                }
                Hop(x - 0.6f, width + 1.2f, 0.5f + width * 0.1f);
                if (!bridge)
                {
                    // Below the banks' level, so only a kid down on the canal bed wades, never one at its edge.
                    var water = new GameObject("WaterZone");
                    water.transform.SetParent(_root, false);
                    water.transform.localPosition = new Vector3(x + width * 0.5f, 0f, 0f);
                    var trigger = water.AddComponent<BoxCollider>();
                    trigger.isTrigger = true;
                    trigger.size = new Vector3(width, 0.28f, LaneDepth);
                    trigger.center = new Vector3(0f, CanalBed + 0.04f, 0f);
                    water.AddComponent<WaterZone>();
                    return;
                }
                var plank = Box("Plank", _root, new Vector3(x + width * 0.5f, -0.05f, 0f), new Vector3(width + 0.4f, 0.1f, 0.9f), _z.prims, true);
                // The hand-built plank bridge (ArtSource/tools/models/plank_model.py, 3.9 m for a 3.5 m canal), stood on
                // the walkway's top and stretched along the lane for another width; the box stays as what she walks on.
                var top = new Vector3(x + width * 0.5f, 0f, 0f);
                var bridgeModel = ArtModels.Stand(_root, "fields", "plank_bridge", top, top + Vector3.up);
                if (bridgeModel != null)
                {
                    bridgeModel.transform.localScale = new Vector3((width + 0.4f) / PlankBridgeLength, 1f, 1f);
                    foreach (var renderer in bridgeModel.GetComponentsInChildren<Renderer>()) renderer.sortingOrder = LaneOrder;
                    plank.GetComponent<Renderer>().enabled = false;
                    return;
                }
                plank.AddComponent<GreyboxColor>().SetColor(Palette.Wood);
                foreach (float z in new[] { -0.45f, 0.45f })
                    Prim(PrimitiveType.Cube, "Rail", _root, new Vector3(x + width * 0.5f, 0.55f, z), new Vector3(width + 0.4f, 0.05f, 0.05f), Palette.Bamboo);
                for (float px = x - 0.2f; px <= x + width + 0.21f; px += width + 0.4f)
                {
                    foreach (float z in new[] { -0.45f, 0.45f })
                        Prim(PrimitiveType.Cylinder, "Post", _root, new Vector3(px, 0.3f, z), new Vector3(0.06f, 0.35f, 0.06f), Palette.Bamboo);
                }
            }

            /// <summary>A haystack from x: a small one (1.05 m) to hop onto or over, a big one (1.85 m) to double jump or vault.</summary>
            public float Haystack(float x, bool big)
            {
                float height = big ? 2.0f : 1.25f;
                float top = big ? 1.85f : 1.05f;
                var card = Art(_root, big ? "haystack" : "haystack_small", 0f, 0f, 0.15f, out var size, height: height,
                    mirror: _random.NextDouble() < 0.5);
                float width = card != null ? size.x : (big ? 2.2f : 1.2f);
                if (card != null) card.transform.localPosition = new Vector3(x + width * 0.5f, height * 0.5f, 0.15f);
                float solid = width * 0.8f;
                var stack = Box("Haystack", _root, new Vector3(x + width * 0.5f, top * 0.5f, 0f), new Vector3(solid, top, 1.4f), _z.prims, true);
                stack.GetComponent<Renderer>().enabled = card == null;
                if (card == null) stack.AddComponent<GreyboxColor>().SetColor(Palette.Hay);
                // His hop clears the stack's top by 0.25 m even at its edges (a hop's height is a sine over its length);
                // top + 0.4 at the middle left him 0.17 m inside a big stack's shoulders.
                float length = width + 1.6f;
                float edge = Mathf.Sin(Mathf.PI * (0.8f + width * 0.1f) / length);
                Hop(x - 0.8f, length, (top + 0.25f) / Mathf.Max(0.3f, edge));
                return x + width;
            }

            /// <summary>A buffalo wallowing across the lane: bounce off its back, or climb over it slowly. Starts at x.</summary>
            public float Buffalo(float x)
            {
                var card = Art(_root, "buffalo_mud", 0f, 0f, 0.15f, out var size, height: 1.5f);
                float width = card != null ? size.x : 2.6f;
                if (card != null) card.transform.localPosition = new Vector3(x + width * 0.5f, 0.75f, 0.15f);
                Decal("cracked_mud", x + width * 0.5f, 0f, 1.8f, 0f);
                const float back = 1.1f;
                var body = Box("Buffalo", _root, new Vector3(x + width * 0.5f, back * 0.5f, 0f), new Vector3(width * 0.7f, back, 1.0f), _z.prims, true);
                body.GetComponent<Renderer>().enabled = card == null;
                if (card == null) body.AddComponent<GreyboxColor>().SetColor(Palette.Ink);

                var backGo = new GameObject("Back");
                backGo.transform.SetParent(_root, false);
                backGo.transform.localPosition = new Vector3(x + width * 0.5f, 0f, 0f);
                var trigger = backGo.AddComponent<BoxCollider>();
                trigger.isTrigger = true;
                trigger.size = new Vector3(width * 0.6f, 0.2f, LaneDepth);
                trigger.center = new Vector3(0f, back + 0.1f, 0f);
                var bouncer = backGo.AddComponent<Bouncer>();
                bouncer.bounceHeight = 2.6f;
                bouncer.bark = "MOO!";
                Hop(x - 1f, width + 2f, 1.6f);
                return x + width;
            }

            /// <summary>
            /// A mango tree behind the lane with a branch over it from x+1 to x+5, 2.3 m up: jump at the branch to pull
            /// yourself up (a quick climb), or double jump onto it. Mangoes run along it.
            /// </summary>
            public void MangoTree(float x)
            {
                var tree = Art(_root, "tree_mango_1", x + 3f, 0f, 0.9f, out _, height: 5.2f);
                FrontAt(tree, 0.45f);        // its crown and roots behind the road, its crown still over it from the camera
                if (tree == null)
                {
                    Prim(PrimitiveType.Cylinder, "Trunk", _root, new Vector3(x + 1.2f, 1.3f, 0.9f), new Vector3(0.4f, 1.3f, 0.4f), Palette.Wood);
                    Prim(PrimitiveType.Sphere, "Crown", _root, new Vector3(x + 3f, 3.6f, 0.9f), new Vector3(5f, 2.6f, 2f), Palette.Leaf);
                }
                var branch = Box("Branch", _root, new Vector3(x + 3f, 2.22f, 0f), new Vector3(4f, 0.16f, 0.8f), _z.prims, true);
                branch.GetComponent<Renderer>().enabled = false;
                branch.AddComponent<Ladder>();
                // The rooster runs on whatever is highest under him, so he flutters up onto the branch rather than popping up.
                Hop(x + 0.2f, 1.0f, 0.5f);
                MangoLine(x + 1.4f, 6, 0.6f, 2.85f);
            }

            /// <summary>
            /// A market stall standing on the lane's edge from x. Its awning, about 2.1 m up, bounces a jumping kid;
            /// she runs under it otherwise. Returns where the stall ends.
            /// </summary>
            public float Stall(float x, string piece)
            {
                var card = Art(_root, piece, 0f, 0f, 0.55f, out var size);
                float width = card != null ? size.x : 3.2f;
                float height = card != null ? size.y : 2.8f;
                if (card != null)
                {
                    card.transform.localPosition = new Vector3(x + width * 0.5f, height * 0.5f, 0.55f);
                    FrontAt(card, 0.45f);    // its tables and goods behind the running line
                }
                else Prim(PrimitiveType.Cube, "Awning", _root, new Vector3(x + width * 0.5f, height * 0.76f, 0.4f), new Vector3(width, 0.1f, 1.2f), Palette.Kumkum);

                var awning = new GameObject("Awning");
                awning.transform.SetParent(_root, false);
                awning.transform.localPosition = new Vector3(x + width * 0.5f, 0f, 0f);
                var trigger = awning.AddComponent<BoxCollider>();
                trigger.isTrigger = true;
                trigger.size = new Vector3(width * 0.8f, 0.2f, LaneDepth);
                trigger.center = new Vector3(0f, Mathf.Clamp(height * 0.74f, 1.95f, 2.3f), 0f);
                var bouncer = awning.AddComponent<Bouncer>();
                bouncer.bounceHeight = 2.0f;
                bouncer.bark = "";
                return x + width;
            }

            /// <summary>Temple steps from x: <paramref name="count"/> steps up, a landing, the same steps down. Returns the end.</summary>
            public float Steps(float x, int count, float landing)
            {
                const float rise = 0.25f;
                const float tread = 0.7f;
                float end = x + count * tread * 2f + landing;
                // The hand-built granite flight (ArtSource/tools/models/steps_model.py: six steps, a 6 m landing, six down)
                // over the step boxes, which stay as what she walks on; another size keeps the grey boxes.
                GameObject model = null;
                if (count == 6 && Mathf.Abs(landing - 6f) < 0.01f)
                {
                    var middle = new Vector3((x + end) * 0.5f, 0f, 0.6f);
                    model = ArtModels.Stand(_root, "market", "temple_steps", middle, middle + Vector3.up);
                }
                for (int i = 0; i < count; i++)
                {
                    float from = x + i * tread;
                    float to = end - i * tread;
                    // 1.8 m deep from just in front of the running line (-0.3) back, so the steps never hide the runners
                    var step = Box("Step", _root, new Vector3((from + to) * 0.5f, i * rise + rise * 0.5f, 0.6f), new Vector3(to - from, rise, 1.8f), _z.prims, true);
                    if (model != null) step.GetComponent<Renderer>().enabled = false;
                    else step.AddComponent<GreyboxColor>().SetColor(Color.Lerp(Palette.Granite, Palette.Granite * 0.85f, i % 2));
                }
                float top = count * rise;
                for (int k = 0; k < 2; k++)
                    Art(_root, "lamp_step", x + count * tread + landing * (0.25f + 0.5f * k), top, 1.2f, out _, height: 1.9f);
                Art(_root, "lantern", x + count * tread + landing * 0.5f, top, 0.9f, out _, height: 0.45f);
                return end;
            }

            // ------------------------------------------------------------------ rooster route and mischief

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

            // ------------------------------------------------------------------ pickups

            public void Mango(float x, float y)
            {
                var pickup = PickupRoot("Mango", x, y, PickupKind.Mango, 0.25f);
                if (PickupModel(pickup.visual, "Mango", Quaternion.Euler(0f, 0f, 12f))) return;
                Prim(PrimitiveType.Sphere, "Fruit", pickup.visual, Vector3.zero, new Vector3(0.22f, 0.28f, 0.22f), Palette.Mango);
                Prim(PrimitiveType.Cube, "Leaf", pickup.visual, new Vector3(0.04f, 0.15f, 0f), new Vector3(0.1f, 0.03f, 0.05f), Palette.Leaf);
            }

            public void Chilli(float x, float y)
            {
                var pickup = PickupRoot("Chilli", x, y, PickupKind.Chilli, 0.3f);
                pickup.spinSpeed = 300f;
                if (PickupModel(pickup.visual, "Chilli", Quaternion.Euler(0f, 0f, -30f))) return;
                Prim(PrimitiveType.Capsule, "Pod", pickup.visual, Vector3.zero, new Vector3(0.12f, 0.2f, 0.12f), Palette.Chilli)
                    .transform.localRotation = Quaternion.Euler(0f, 0f, 55f);
                Prim(PrimitiveType.Cube, "Stalk", pickup.visual, new Vector3(-0.15f, 0.12f, 0f), new Vector3(0.04f, 0.1f, 0.04f), Palette.Leaf);
                pickup.spinSpeed = 300f;
            }

            /// <summary>One of the level's three hidden tail feathers, <paramref name="index"/> 0 to 2, on a harder route.</summary>
            public void Feather(float x, float y, int index)
            {
                var pickup = PickupRoot("Feather" + index, x, y, PickupKind.Feather, 0.3f);
                pickup.featherIndex = index;
                pickup.spinSpeed = 120f;
                if (PickupModel(pickup.visual, "Feather", Quaternion.identity)) return;
                Prim(PrimitiveType.Capsule, "Vane", pickup.visual, Vector3.zero, new Vector3(0.12f, 0.3f, 0.04f), Palette.Feather)
                    .transform.localRotation = Quaternion.Euler(0f, 0f, -30f);
                Prim(PrimitiveType.Cube, "Quill", pickup.visual, new Vector3(-0.08f, -0.2f, 0f), new Vector3(0.02f, 0.16f, 0.02f), Palette.Beak)
                    .transform.localRotation = Quaternion.Euler(0f, 0f, -30f);
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

            /// <summary>Mangoes along a full single jump centred on <paramref name="centreX"/>, at this zone's speed.</summary>
            public void JumpArc(float centreX, float lift = 0f)
            {
                float length = JumpMath.JumpLengthAt(_z.tuning, _z.tuning.kidRunSpeed);
                Arc(centreX - length * 0.5f, length, _z.tuning.jumpHeight, 5, lift);
            }

            /// <summary>Mangoes along a parabola of the kid's feet, lifted to the middle of the body.</summary>
            public void Arc(float startX, float length, float peak, int count, float lift = 0f)
            {
                for (int i = 0; i < count; i++)
                {
                    float s = (i + 1f) / (count + 1f);
                    Mango(startX + s * length, lift + 0.55f + 4f * peak * s * (1f - s));
                }
            }

            /// <summary>A stray ground detail (leaf, husk, footprints) somewhere along the lane, for life.</summary>
            public void Litter(int count)
            {
                string[] pieces = { "leaf_1", "leaf_2", "twigs", "husk", "footprints", "hen_prints", "pebbles", "tuft_1", "tuft_2" };
                for (int i = 0; i < count; i++)
                {
                    float x = (float)_random.NextDouble() * _length;
                    if (InHole(x)) continue;
                    Decal(pieces[_random.Next(pieces.Length)], x, -0.9f + (float)_random.NextDouble() * 2.2f, 0.45f + (float)_random.NextDouble() * 0.4f,
                        (float)_random.NextDouble() * 360f);
                }
            }

            bool InHole(float x)
            {
                foreach (var hole in _holes)
                {
                    if (x > hole.x - 0.5f && x < hole.y + 0.5f) return true;
                }
                return false;
            }
        }

        static class Palette
        {
            public static readonly Color Terracotta = new Color(0.78f, 0.36f, 0.2f);
            public static readonly Color Dung = new Color(0.36f, 0.26f, 0.12f);
            public static readonly Color Dog = new Color(0.82f, 0.66f, 0.42f);
            public static readonly Color Water = new Color(0.35f, 0.55f, 0.85f);
            public static readonly Color Kumkum = new Color(0.85f, 0.12f, 0.3f);
            public static readonly Color Wood = new Color(0.6f, 0.38f, 0.2f);
            public static readonly Color Bamboo = new Color(0.78f, 0.66f, 0.38f);
            public static readonly Color Rope = new Color(0.85f, 0.75f, 0.5f);
            public static readonly Color Hay = new Color(0.86f, 0.72f, 0.36f);
            public static readonly Color Hen = new Color(0.9f, 0.86f, 0.78f);
            public static readonly Color Iron = new Color(0.25f, 0.3f, 0.35f);
            public static readonly Color Ink = new Color(0.1f, 0.08f, 0.08f);
            public static readonly Color Granite = new Color(0.62f, 0.58f, 0.55f);
            public static readonly Color Leaf = new Color(0.3f, 0.6f, 0.2f);
            public static readonly Color Mango = new Color(1f, 0.72f, 0.12f);
            public static readonly Color Chilli = new Color(0.9f, 0.1f, 0.05f);
            public static readonly Color Feather = new Color(0.85f, 0.35f, 0.08f);
            public static readonly Color Beak = new Color(0.95f, 0.8f, 0.2f);
            public static readonly Color[] Walls =
            {
                new Color(0.94f, 0.93f, 0.86f),
                new Color(0.33f, 0.4f, 0.7f),
                new Color(0.96f, 0.77f, 0.27f),
                new Color(0.93f, 0.72f, 0.68f),
            };
        }
    }
}
