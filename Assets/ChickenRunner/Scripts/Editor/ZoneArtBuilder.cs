using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;

namespace ChickenRunner.EditorTools
{
    /// <summary>
    /// Turns a zone's Blender layout into scenery the game can repeat along a course of any length (a ZoneArt):
    /// <list type="bullet">
    /// <item>The distant bands (cards 20 m wide or more: the far painting, the tree line, the field bands) become strips.
    /// Each depth's cards are one cycle laid end to end, repeated every cycle length; a cycle never ends on the same
    /// picture it starts with, so mirrored copies keep alternating and their seams keep matching.</item>
    /// <item>Everything else between the lane and the bands (houses, compounds, trees, animals, people) is one set,
    /// cut to the stretch of the course the scene covers and repeated every stretch length.</item>
    /// <item>What stood on the lane itself in the Blender previews (the obstacles, the kid and the rooster, the bund
    /// strip in front) is left out: the level's chunks put the real ones there.</item>
    /// </list>
    /// </summary>
    internal static class ZoneArtBuilder
    {
        const float StripWidth = 20f;
        const float LaneFront = -2.0f;
        const float LaneBack = 1.4f;
        const float RunningLine = 0.9f;
        const float NearDepth = 11f;
        const float CameraDistance = 30f;
        const float ViewSpread = 0.6f;

        public static ZoneArt Build(int zone, string layoutName, Material ground, string folder)
        {
            var layout = LayoutFile.Load($"{ArtLayoutImporter.LayoutFolder}/{layoutName}.json");
            string path = $"{folder}/ZoneArt_Zone{zone}.asset";
            var art = AssetDatabase.LoadAssetAtPath<ZoneArt>(path);
            if (art == null)
            {
                art = ScriptableObject.CreateInstance<ZoneArt>();
                AssetDatabase.CreateAsset(art, path);
            }
            art.zone = zone;
            art.ground = ground;
            art.sky = ArtAssets.Haze;
            art.groundTo = 95f;
            var tracks = new List<ZoneArt.Track>();

            if (layout == null)
            {
                Debug.LogWarning($"No layout {layoutName}.json: zone {zone} gets bare ground. Run ArtSource/tools/build_*_scene.py.");
            }
            else
            {
                var cards = layout.cards.Where(c => Keep(c, zone)).ToList();
                if (zone != 2) cards.AddRange(SideLanes(cards));   // the fields have their cart track, no side lanes
                var wide = cards.Where(c => !c.flat && c.w >= StripWidth).ToList();
                var rest = cards.Except(wide).ToList();

                foreach (var group in wide.GroupBy(c => Mathf.Round(c.z)).OrderByDescending(g => g.Key))
                {
                    var track = Strip(group.OrderBy(c => c.x).ToList(), $"{folder}/Zone{zone}_Strip_{group.Key:0}m.prefab");
                    if (track != null) tracks.Add(track);
                }
                var set = Set(rest, $"{folder}/Zone{zone}_Set.prefab");
                if (set != null) tracks.Add(set);
            }

            art.tracks = tracks.ToArray();
            EditorUtility.SetDirty(art);
            return art;
        }

        const string SideLaneImage = "ArtSource/cutouts/ground/side_lane_mud.png";
        const float SideLaneLength = 8f;

        /// <summary>
        /// The village's side lanes: a narrow mud lane running back from the road between two houses, wherever the set
        /// leaves a gap of 3 m or more between them with nobody standing in it, at most one every 20 m
        /// (side_lane_mud.png from ArtSource/tools/models/road_textures.py, faded at its edges and far end).
        /// </summary>
        static IEnumerable<LayoutCard> SideLanes(List<LayoutCard> cards)
        {
            if (!File.Exists(Path.Combine(ArtAssets.RepoRoot, SideLaneImage))) yield break;
            // Buildings: the lane's houses, and the market's big pieces (its terrace houses, stalls and mandapam are props).
            var blocks = cards.Where(c => !c.flat && c.z > LaneBack && c.z < NearDepth
                    && (c.layer == "Houses" || (c.w >= 2.5f && c.h >= 2f && c.layer != "Backdrop" && c.layer != "Plants")))
                .Select(c => new Vector2(c.x - c.w * 0.5f, c.x + c.w * 0.5f)).OrderBy(b => b.x).ToList();
            var figures = cards.Where(c => !c.flat && c.layer != "Houses" && c.w < 2.5f && c.z > LaneBack && c.z < 6f && c.h > 0.5f).ToList();
            float last = float.NegativeInfinity;
            int made = 0;
            for (int i = 0; i + 1 < blocks.Count; i++)
            {
                float from = blocks[i].y;
                for (int j = 0; j <= i; j++) from = Mathf.Max(from, blocks[j].y);
                float to = blocks[i + 1].x;
                if (to - from < 3f) continue;
                float cx = (from + to) * 0.5f;
                if (cx - last < 20f) continue;
                if (figures.Any(f => Mathf.Abs(f.x - cx) < 1.2f + f.w * 0.5f)) continue;
                last = cx;
                yield return new LayoutCard
                {
                    name = "side_lane_" + made++,
                    image = SideLaneImage,
                    layer = "Ground",
                    x = cx,
                    y = 0f,
                    z = GameBuilder.RoadBack - 0.3f + SideLaneLength * 0.5f,
                    w = Mathf.Min(2.6f, to - from - 0.6f),
                    h = SideLaneLength,
                    flat = true,
                };
            }
        }

        static bool Keep(LayoutCard c, int zone)
        {
            if (c.layer == "Characters" || c.layer == "Ground") return false;
            // Zone 2's canals cross the lane wherever the level puts them, so nothing may lie on the lane there; and
            // nowhere does a ground detail lie on the running line itself, where a husk or a tuft reads as an obstacle
            // (the level plans lay their own, off it).
            if (c.flat) return (zone != 2 || c.z < LaneFront || c.z > LaneBack) && Mathf.Abs(c.z) >= RunningLine;
            return c.z <= LaneFront || c.z >= LaneBack;
        }

        /// <summary>One depth's wide cards as a repeating cycle.</summary>
        static ZoneArt.Track Strip(List<LayoutCard> cards, string prefabPath)
        {
            if (cards.Count == 0) return null;
            // Drop a last card that repeats the first one's look, so the next cycle continues the alternation.
            if (cards.Count > 1 && cards[0].image == cards[cards.Count - 1].image && cards[0].mirror == cards[cards.Count - 1].mirror)
                cards.RemoveAt(cards.Count - 1);
            float step = cards.Count > 1 ? (cards[cards.Count - 1].x - cards[0].x) / (cards.Count - 1) : cards[0].w;
            float period = cards[cards.Count - 1].x - cards[0].x + step;
            return Save(cards, prefabPath, period);
        }

        /// <summary>The near scenery, cut to the stretch the Blender scene covers.</summary>
        static ZoneArt.Track Set(List<LayoutCard> cards, string prefabPath)
        {
            var near = cards.Where(c => c.z < NearDepth).ToList();
            if (near.Count == 0) return null;
            float start = near.Min(c => c.x) - 2f;
            float period = near.Max(c => c.x) - start + 2f;
            var inside = cards.Where(c => c.x >= start && c.x < start + period).ToList();
            return Save(inside, prefabPath, period);
        }

        static ZoneArt.Track Save(List<LayoutCard> cards, string prefabPath, float period)
        {
            var root = new GameObject(Path.GetFileNameWithoutExtension(prefabPath));
            int made = 0;
            foreach (var card in cards)
            {
                var go = LayoutFile.MakeCard(card, root.transform, default, ArtModels.RoomBehind(card, cards));
                if (go == null) continue;
                made++;
                // Plants between the camera and the lane draw over the kid; everything behind the lane under her.
                foreach (var renderer in go.GetComponentsInChildren<Renderer>())
                    renderer.sortingOrder = card.z <= LaneFront ? GameBuilder.ForegroundOrder : GameBuilder.SceneryOrder;
            }
            if (made == 0)
            {
                Object.DestroyImmediate(root);
                return null;
            }
            var prefab = PrefabUtility.SaveAsPrefabAsset(root, prefabPath);
            Object.DestroyImmediate(root);
            float deepest = cards.Max(c => c.z);
            return new ZoneArt.Track
            {
                prefab = prefab,
                period = Mathf.Max(1f, period),
                contentMin = cards.Min(c => c.x - c.w * 0.5f),
                contentMax = cards.Max(c => c.x + c.w * 0.5f),
                reach = Mathf.Max(10f, (CameraDistance + deepest) * ViewSpread + 5f),
            };
        }
    }
}
