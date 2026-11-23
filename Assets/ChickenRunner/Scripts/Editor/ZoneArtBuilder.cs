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

        static bool Keep(LayoutCard c, int zone)
        {
            if (c.layer == "Characters" || c.layer == "Ground") return false;
            // Zone 2's canals cross the lane wherever the level puts them, so nothing may lie on the lane there.
            if (c.flat) return zone != 2 || c.z < LaneFront || c.z > LaneBack;
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
                var go = LayoutFile.MakeCard(card, root.transform);
                if (go == null) continue;
                made++;
                // Plants between the camera and the lane draw over the kid; everything behind the lane under her.
                go.GetComponent<Renderer>().sortingOrder = card.z <= LaneFront ? GameBuilder.ForegroundOrder : GameBuilder.SceneryOrder;
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
