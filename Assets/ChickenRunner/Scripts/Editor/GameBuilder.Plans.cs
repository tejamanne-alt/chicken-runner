using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace ChickenRunner.EditorTools
{
    /// <summary>
    /// Levels laid out piece by piece from a level plan (Art/Levels/levelN.json, written and audited by
    /// ArtSource/tools/levels/levelN.py with levelkit.py) instead of shuffled from a zone's chunk pool: all nine levels. Each section of the plan becomes
    /// one chunk, laid in order; the first is the level's own opening. Every item is placed with the same Kit calls as
    /// the hand-written chunks, so a plan's pots, dung and hops behave exactly like theirs; the plan only says where.
    /// </summary>
    internal static partial class GameBuilder
    {
        const string PlanFolder = Root + "/Art/Levels";

        // Filled by JsonUtility, never assigned in code.
#pragma warning disable 0649
        [Serializable]
        sealed class LevelPlan
        {
            public int level;
            public int zone;
            public string title;
            public string subtitle;
            public float courseLength;
            public List<PlanSection> sections = new List<PlanSection>();
        }

        [Serializable]
        sealed class PlanSection
        {
            public string name;
            public float x;
            public float length;
            public string note;
            public List<PlanItem> items = new List<PlanItem>();
        }

        /// <summary>One placed thing. Which fields mean anything depends on <see cref="kind"/>; see levelN.py's Plan.</summary>
        [Serializable]
        sealed class PlanItem
        {
            public string kind;
            public float x, y, z, w, h;
            public bool mirror;
            public bool hidden;
            public string id;
            public string piece;
            public float turn;
            public float width;
            public float length;
            public float height;
            public int index;
            public string target;
            public float diameter;
            public float hinge;
            public float walkFrom;
            // canals, roof rows, haystacks
            public bool bridge;
            public string[] fronts;
            public bool ladder;
            public bool big;
            public float end;
            // hens and temple steps
            public int count;
            public float landing;
        }
#pragma warning restore 0649

        /// <summary>The plan of a level, or null (with an error) when its file is missing or unreadable.</summary>
        static LevelPlan LoadPlan(string name)
        {
            string path = Path.Combine(ArtAssets.RepoRoot, PlanFolder, name + ".json");
            if (!File.Exists(path))
            {
                Debug.LogError("Level plan missing: " + path + ". Run ArtSource/tools/levels/" + name + ".py.");
                return null;
            }
            try
            {
                var plan = JsonUtility.FromJson<LevelPlan>(File.ReadAllText(path));
                if (plan == null || plan.sections == null || plan.sections.Count == 0) throw new Exception("no sections");
                return plan;
            }
            catch (Exception e)
            {
                Debug.LogError("Level plan " + path + " could not be read: " + e.Message);
                return null;
            }
        }

        /// <summary>One chunk per plan section, in course order, saved as Z{zone}_{plan}_{section} prefabs.</summary>
        static List<Chunk> BuildPlanChunks(string planName, LevelPlan plan, ZoneKit z)
        {
            var chunks = new List<Chunk>();
            for (int i = 0; i < plan.sections.Count; i++)
            {
                var section = plan.sections[i];
                var root = BuildPlanSection(section, z, 1000 * plan.level + i);
                chunks.Add(SaveChunk(root, $"Z{z.zone}_{planName}_{i:00}_{section.name}"));
            }
            return chunks;
        }

        static GameObject BuildPlanSection(PlanSection section, ZoneKit z, int seed)
        {
            var kit = new Kit(section.name, section.length, z, seed);
            var named = new Dictionary<string, Obstacle>();
            var mischief = new List<PlanItem>();
            foreach (var item in section.items)
            {
                float x = item.x - section.x; // plan positions are course x; the chunk's are its own
                switch (item.kind)
                {
                    case "pots":
                    {
                        var pots = kit.PotStack(x, item.hidden, item.y, item.mirror);
                        if (!string.IsNullOrEmpty(item.id)) named[item.id] = pots;
                        break;
                    }
                    case "hensbasket":
                    {
                        var basket = kit.HensBasket(x, item.hidden);
                        if (!string.IsNullOrEmpty(item.id)) named[item.id] = basket;
                        break;
                    }
                    case "tank": kit.Tank(x, item.y); break;
                    case "clothesline": kit.Clothesline(x, item.mirror); break;
                    case "canal": kit.Canal(x, item.width, item.bridge); break;
                    case "roofs":
                    {
                        // The plan placed what follows the row from the same card sizes; a mismatch means the art changed.
                        float end = kit.RoofRow(x, item.fronts ?? new string[0], item.ladder);
                        if (Mathf.Abs(end - (item.end - section.x)) > 0.05f)
                            Debug.LogError($"Level plan section {section.name}: the roof row at {item.x} ends at {end + section.x:0.00}, "
                                + $"not {item.end:0.00} as planned. Re-run the level's plan script (the house pictures changed?).");
                        break;
                    }
                    case "cot": kit.Cot(x); break;
                    case "mangotree": kit.MangoTree(x); break;
                    case "hens": kit.Hens(x, Mathf.Max(1, item.count)); break;
                    case "goats": kit.Goats(x, Mathf.Max(1, item.count)); break;
                    case "ducks": kit.Ducks(x, Mathf.Max(1, item.count)); break;
                    case "sand": kit.SandHeap(x); break;
                    case "lowbranch": kit.LowBranch(x, item.mirror); break;
                    case "sacks": kit.Sacks(x); break;
                    case "buffalo":
                    {
                        float end = kit.Buffalo(x);
                        if (Mathf.Abs(end - (x + item.width)) > 0.05f)
                            Debug.LogError($"Level plan section {section.name}: the buffalo at {item.x} is {end - x:0.00} m long, "
                                + $"not {item.width:0.00} as planned. Re-run the level's plan script.");
                        break;
                    }
                    case "stall":
                    {
                        float end = kit.Stall(x, item.piece);
                        if (Mathf.Abs(end - (x + item.width)) > 0.05f)
                            Debug.LogError($"Level plan section {section.name}: the stall {item.piece} at {item.x} is {end - x:0.00} m "
                                + $"wide, not {item.width:0.00} as planned. Re-run the level's plan script.");
                        break;
                    }
                    case "steps":
                    {
                        float end = kit.Steps(x, Mathf.Max(1, item.count), item.landing);
                        if (Mathf.Abs(end - (item.end - section.x)) > 0.05f)
                            Debug.LogError($"Level plan section {section.name}: the steps at {item.x} end at {end + section.x:0.00}, "
                                + $"not {item.end:0.00} as planned.");
                        break;
                    }
                    case "haystack":
                    {
                        float end = kit.Haystack(x, item.big);
                        if (Mathf.Abs(end - (x + item.width)) > 0.05f)
                            Debug.LogError($"Level plan section {section.name}: the haystack at {item.x} is {end - x:0.00} m wide, "
                                + $"not {item.width:0.00} as planned. Re-run the level's plan script.");
                        break;
                    }
                    case "dung": kit.Dung(x); break;
                    case "dog": kit.Dog(x); break;
                    case "puddle": kit.Puddle(x, item.width); break;
                    case "cart": kit.Cart(x); break;
                    case "hop": kit.Hop(x, item.length, item.height); break;
                    case "mischief": mischief.Add(item); break;
                    case "mango": kit.Mango(x, item.y); break;
                    case "chilli": kit.Chilli(x, item.y); break;
                    case "feather": kit.Feather(x, item.y, item.index); break;
                    case "prop":
                        kit.Art(kit.Root, item.piece, x, item.y, item.z, out _, item.h, item.w, item.mirror);
                        break;
                    case "decal": kit.Decal(item.piece, x, item.z, item.w, item.turn); break;
                    case "basket": BasketItem(kit, section, item); break;
                    case "neighbour": break; // laid with the basket, which wakes him
                    default:
                        Debug.LogError($"Level plan section {section.name}: unknown item kind '{item.kind}' at {item.x}.");
                        break;
                }
            }
            // A mischief spot names the obstacle it knocks into the lane, which may come later in the section.
            foreach (var item in mischief)
            {
                if (string.IsNullOrEmpty(item.target) || !named.TryGetValue(item.target, out var target))
                {
                    Debug.LogError($"Level plan section {section.name}: mischief at {item.x} names '{item.target}', which is not there.");
                    continue;
                }
                kit.Mischief(item.x - section.x, target);
            }
            return kit.Finish();
        }

        /// <summary>
        /// Level 1's basket over the rooster, hinged on its far rim, and the neighbour asleep (and, hidden, awake) on his
        /// cot behind the lane: the <see cref="BasketIntro"/> the game flow plays before the chase.
        /// </summary>
        static void BasketItem(Kit kit, PlanSection section, PlanItem item)
        {
            var go = new GameObject("BasketIntro");
            go.transform.SetParent(kit.Root, false);
            var intro = go.AddComponent<BasketIntro>();
            float diameter = item.diameter > 0f ? item.diameter : 0.9f;
            float hingeX = item.hinge > 0f ? item.hinge : item.x + diameter * 0.5f;

            var hinge = new GameObject("Hinge").transform;
            hinge.SetParent(go.transform, false);
            hinge.localPosition = new Vector3(hingeX - section.x, 0f, 0f);
            if (kit.Art(hinge, "chicken_basket", item.x - hingeX, 0f, 0f, out _, width: diameter, order: CharacterOrder + 1) == null)
            {
                Debug.LogWarning("The chicken_basket cut-out is missing; level 1's basket is a grey dome.");
                var dome = GameObject.CreatePrimitive(PrimitiveType.Sphere);
                UnityEngine.Object.DestroyImmediate(dome.GetComponent<Collider>());
                dome.name = "Basket";
                dome.transform.SetParent(hinge, false);
                dome.transform.localPosition = new Vector3(item.x - hingeX, 0f, 0f);
                dome.transform.localScale = new Vector3(diameter, diameter * 1.4f, diameter);
            }
            intro.hinge = hinge;
            intro.walkFrom = item.walkFrom != 0f ? item.walkFrom : -4.4f;
            intro.roosterX = item.x;

            foreach (var other in section.items)
            {
                if (other.kind != "neighbour") continue;
                float nx = other.x - section.x;
                intro.neighbourAsleep = kit.Art(go.transform, "neighbour_sleeping", nx, 0f, other.z, out _, height: 1.0f);
                intro.neighbourAwake = kit.Art(go.transform, "neighbour_awake", nx, 0f, other.z, out _, height: 1.25f);
                if (intro.neighbourAwake != null) intro.neighbourAwake.SetActive(false);
                if (intro.neighbourAsleep == null) Debug.LogWarning("The neighbour_sleeping cut-out is missing (ArtSource/tools/levels/cut_neighbour.py).");
            }
        }

        /// <summary>Points a level at its plan's chunks: the first section opens it, the rest follow in order, once.</summary>
        static void ApplyPlan(LevelDefinition level, LevelPlan plan, List<Chunk> chunks)
        {
            level.displayName = string.IsNullOrEmpty(plan.title) ? level.displayName : plan.title;
            level.subtitle = string.IsNullOrEmpty(plan.subtitle) ? level.subtitle : plan.subtitle;
            level.startChunk = chunks[0];
            level.chunks = chunks.GetRange(1, chunks.Count - 1);
            level.loopChunks = false;
            level.shuffleRepeats = false;
            if (plan.courseLength > 0f) level.courseLengthOverride = plan.courseLength;
        }
    }
}
