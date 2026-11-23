using System;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEngine;

namespace ChickenRunner.EditorTools
{
    /// <summary>One painted card of a Blender scene, as written by export_layout() in ArtSource/tools/stage.py.</summary>
#pragma warning disable 0649 // filled in by JsonUtility
    [Serializable]
    internal sealed class LayoutCard
    {
        public string name;
        public string image;
        public string layer;
        /// <summary>Unity axes: x along the lane, y up, z away from the camera. Standing cards: the bottom centre.</summary>
        public float x, y, z, w, h, turn, haze, fade_bottom, fade_sides;
        public bool mirror, flat, shadeless;
    }

    /// <summary>A zone's whole layout file, Assets/ChickenRunner/Art/Layouts/&lt;zone&gt;.json.</summary>
    [Serializable]
    internal sealed class LayoutFile
    {
        public string zone;
        public float[] hazeColor;
        public LayoutCard[] cards;

        public static LayoutFile Load(string path)
        {
            if (!File.Exists(path)) return null;
            var layout = JsonUtility.FromJson<LayoutFile>(File.ReadAllText(path));
            return layout?.cards == null || layout.cards.Length == 0 ? null : layout;
        }

        /// <summary>
        /// Makes the card under <paramref name="parent"/>: the piece's 3D model where it has one (see
        /// <see cref="ArtModels"/>; <paramref name="roomBehind"/> caps how far back it reaches), else its painted quad.
        /// Null when its art is missing.
        /// </summary>
        public static GameObject MakeCard(LayoutCard card, Transform parent, Vector3 offset = default,
            float roomBehind = float.PositiveInfinity)
        {
            if (ArtModels.Enabled)
            {
                var model = ArtModels.Place(parent, card.image, new Vector3(card.x, card.y, card.z) + offset, new Vector2(card.w, card.h),
                    card.mirror, card.flat, card.turn, card.haze, roomBehind);
                if (model != null)
                {
                    model.name = card.name;
                    return model;
                }
            }
            var texture = ArtAssets.Texture(card.image);
            var material = ArtAssets.CardMaterial(texture, card.haze, card.fade_bottom, card.fade_sides);
            if (material == null) return null;
            return ArtAssets.Card(parent, card.name, material, new Vector3(card.x, card.y, card.z) + offset, new Vector2(card.w, card.h),
                card.mirror, card.flat, card.turn);
        }
    }
#pragma warning restore 0649

    /// <summary>
    /// Rebuilds the Blender scenes' painted cut-outs in Unity, exactly as staged, for looking at a zone as a whole (as
    /// 3D models where the cut-out has one).
    /// The scene builders in ArtSource/tools write one layout per zone to Assets/ChickenRunner/Art/Layouts/*.json; this
    /// copies the art each layout uses into Assets/ChickenRunner/Art/Textures, makes a material per card look, and saves
    /// a prefab per zone in Assets/ChickenRunner/Art/Prefabs with the cards grouped by layer (Houses, Plants, ...).
    /// Drop a prefab into a scene at the origin: its lane runs along +X at depth 0. (The game itself uses the
    /// repeating scenery that Chicken Runner > Build Game makes from the same layouts.)
    /// </summary>
    public static class ArtLayoutImporter
    {
        public const string LayoutFolder = "Assets/ChickenRunner/Art/Layouts";
        const string PrefabFolder = "Assets/ChickenRunner/Art/Prefabs";

        [MenuItem("Chicken Runner/Import Art Layouts", priority = 20)]
        public static void ImportAll()
        {
            if (!Directory.Exists(LayoutFolder))
            {
                Debug.LogWarning($"No layouts in {LayoutFolder}: run a scene builder in ArtSource/tools first.");
                return;
            }
            if (ArtAssets.CardShader == null)
            {
                Debug.LogError($"Shader {ArtAssets.CardShaderName} not found.");
                return;
            }
            ArtAssets.ClearCache();
            ArtModels.ClearCache();
            foreach (var file in Directory.GetFiles(LayoutFolder, "*.json"))
                Import(file);
            AssetDatabase.SaveAssets();
        }

        static void Import(string file)
        {
            var layout = LayoutFile.Load(file);
            if (layout == null) return;
            var root = new GameObject($"Art_{layout.zone}");
            var layers = new Dictionary<string, Transform>();
            try
            {
                for (var i = 0; i < layout.cards.Length; i++)
                {
                    var card = layout.cards[i];
                    if (EditorUtility.DisplayCancelableProgressBar($"Importing {layout.zone}", card.name, (float)i / layout.cards.Length))
                        break;
                    if (!layers.TryGetValue(card.layer, out var parent))
                    {
                        parent = new GameObject(card.layer).transform;
                        parent.SetParent(root.transform, false);
                        layers[card.layer] = parent;
                    }
                    LayoutFile.MakeCard(card, parent, default, ArtModels.RoomBehind(card, layout.cards));
                }
            }
            finally
            {
                EditorUtility.ClearProgressBar();
            }
            ArtAssets.EnsureFolder(PrefabFolder);
            var prefabPath = $"{PrefabFolder}/Art_{layout.zone}.prefab";
            PrefabUtility.SaveAsPrefabAsset(root, prefabPath);
            UnityEngine.Object.DestroyImmediate(root);
            Debug.Log($"Imported {layout.cards.Length} cards into {prefabPath}");
        }
    }
}
