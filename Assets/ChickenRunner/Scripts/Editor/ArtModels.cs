using System;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEngine;

namespace ChickenRunner.EditorTools
{
    /// <summary>
    /// The 3D models built from the painted cut-outs by ArtSource/tools/models/build_models.py, in
    /// Assets/ChickenRunner/Art/Models/&lt;folder&gt;/&lt;name&gt;.fbx with models.json listing their real sizes.
    /// Wherever the game or a zone's scenery would stand a painted card, <see cref="Place"/> stands the piece's model
    /// instead: the same spot and size, its painted front facing the camera on the card's plane (a building runs back
    /// from there, a rounded thing sits half in front, half behind), toon-shaded with the card's distance haze.
    /// Pieces with no full model (made in Meshy from four views, or by TRELLIS) keep their card, unless the menu's
    /// Include Extruded Scenery Models stands their single-painting extrusions in.
    /// </summary>
    internal static class ArtModels
    {
        public const string Folder = "Assets/ChickenRunner/Art/Models";

#pragma warning disable 0649 // filled in by JsonUtility
        [Serializable]
        sealed class Entry
        {
            public string name, folder, kind, source;
            public float width, height, depth;
        }

        [Serializable]
        sealed class Index
        {
            public Entry[] models;
        }
#pragma warning restore 0649

        static Dictionary<string, Entry> s_index;
        static readonly Dictionary<string, GameObject> s_models = new Dictionary<string, GameObject>();
        static readonly Dictionary<string, Material> s_materials = new Dictionary<string, Material>();

        const string EnabledKey = "ChickenRunner.UseSceneryModels";
        const string MenuPath = "Chicken Runner/Use 3D Scenery Models";

        /// <summary>Whether the builders use the models (on unless switched off in the Chicken Runner menu).</summary>
        public static bool Enabled => EditorPrefs.GetBool(EnabledKey, true);

        [MenuItem(MenuPath, priority = 40)]
        static void Toggle()
        {
            EditorPrefs.SetBool(EnabledKey, !Enabled);
            Debug.Log(Enabled ? "Scenery: 3D models. Rebuild the game to see them." : "Scenery: painted cards. Rebuild the game to see them.");
        }

        [MenuItem(MenuPath, true)]
        static bool ToggleCheck()
        {
            Menu.SetChecked(MenuPath, Enabled);
            return true;
        }

        const string ExtrudedKey = "ChickenRunner.IncludeExtrudedModels";
        const string ExtrudedMenu = "Chicken Runner/Include Extruded Scenery Models";

        /// <summary>
        /// Whether pieces that only have a model extruded from their one painting (build_models.py) use it. Off by
        /// default: such a model can only guess the sides, back and top, so the painted card, which is exactly right
        /// from the camera, stands in until a full model (Meshy, TRELLIS) of the piece exists.
        /// </summary>
        public static bool IncludeExtruded => EditorPrefs.GetBool(ExtrudedKey, false);

        [MenuItem(ExtrudedMenu, priority = 41)]
        static void ToggleExtruded()
        {
            EditorPrefs.SetBool(ExtrudedKey, !IncludeExtruded);
            Debug.Log(IncludeExtruded ? "Extruded scenery models: used where a piece has no full model. Rebuild the game to see them."
                : "Extruded scenery models: not used; those pieces are their painted cards. Rebuild the game to see them.");
        }

        [MenuItem(ExtrudedMenu, true)]
        static bool ToggleExtrudedCheck()
        {
            Menu.SetChecked(ExtrudedMenu, IncludeExtruded);
            return Enabled;
        }

        public static void ClearCache()
        {
            s_index = null;
            s_models.Clear();
            s_materials.Clear();
        }

        static Entry Find(string piece)
        {
            if (s_index == null)
            {
                s_index = new Dictionary<string, Entry>();
                string path = Path.Combine(ArtAssets.RepoRoot, Folder, "models.json");
                if (File.Exists(path))
                {
                    var index = JsonUtility.FromJson<Index>(File.ReadAllText(path));
                    if (index?.models != null)
                        foreach (var e in index.models)
                            if (!string.IsNullOrEmpty(e.name) && e.width > 0f && e.height > 0f) s_index[e.name] = e;
                }
            }
            return piece != null && s_index.TryGetValue(piece, out var entry) ? entry : null;
        }

        /// <summary>True if this cut-out (a name, or a path such as ArtSource/cutouts/lane/house_pink.png) has a model.</summary>
        public static bool Has(string piece) => Model(Find(PieceName(piece))) != null;

        public static string PieceName(string imageOrName) =>
            string.IsNullOrEmpty(imageOrName) ? imageOrName : Path.GetFileNameWithoutExtension(imageOrName);

        static GameObject Model(Entry entry)
        {
            if (entry == null) return null;
            if ((string.IsNullOrEmpty(entry.source) || entry.source == "extruded") && !IncludeExtruded) return null;
            if (s_models.TryGetValue(entry.name, out var cached)) return cached;
            string path = $"{Folder}/{entry.folder}/{entry.name}.fbx";
            GameObject model = null;
            if (File.Exists(Path.Combine(ArtAssets.RepoRoot, path)))
            {
                AssetDatabase.ImportAsset(path);
                model = AssetDatabase.LoadAssetAtPath<GameObject>(path);
            }
            s_models[entry.name] = model;
            return model;
        }

        /// <summary>
        /// The piece's model standing where its card would: bottom centre at <paramref name="bottomCentre"/>,
        /// <paramref name="size"/> wide and high (or, <paramref name="flat"/>, lying on the ground centred there, turned
        /// <paramref name="turn"/> degrees). Like a card, the returned object's pivot is the middle of that rectangle, so
        /// callers can move it as they would a card. <paramref name="roomBehind"/> caps how far it may reach back
        /// (a house in front of a tree stops short of it). Null when the piece has no model.
        /// </summary>
        public static GameObject Place(Transform parent, string piece, Vector3 bottomCentre, Vector2 size, bool mirror = false,
            bool flat = false, float turn = 0f, float haze = 0f, float roomBehind = float.PositiveInfinity)
        {
            var entry = Find(PieceName(piece));
            var model = Model(entry);
            if (model == null) return null;

            var pivot = new GameObject(entry.name);
            pivot.transform.SetParent(parent, false);
            float sx = size.x / entry.width, sy = size.y / entry.height;
            float sz = (sx + sy) * 0.5f;
            bool building = entry.kind == "building";
            // A building's depth all lies behind its front; a rounded piece's half of it.
            float reach = entry.depth * sz * (building ? 1f : 0.5f);
            if (!flat && reach > roomBehind - 0.1f) sz *= Mathf.Max(0.15f, (roomBehind - 0.1f) / reach);

            // The models face Unity's +Z; turned round, their painted front faces the camera (-Z) as a card does.
            var facing = flat ? Quaternion.Euler(90f, -turn, 0f) * Quaternion.Euler(0f, 180f, 0f) : Quaternion.Euler(0f, 180f - turn, 0f);
            pivot.transform.localRotation = Quaternion.identity;
            if (flat)
                pivot.transform.localPosition = bottomCentre + new Vector3(0f, 0.002f + entry.depth * sz * 0.5f, 0f);
            else
                pivot.transform.localPosition = bottomCentre + new Vector3(0f, size.y * 0.5f, 0f);

            // Facing and size go on a holder, so the model keeps the transform its import gave it (an FBX root may carry
            // an axis correction of its own).
            var holder = new GameObject("Model").transform;
            holder.SetParent(pivot.transform, false);
            holder.localRotation = facing;
            holder.localScale = new Vector3(mirror ? -sx : sx, sy, sz);
            // The model stands on its own origin: drop it from the pivot to the card's bottom edge (or, lying flat, back
            // to the near edge, so it is centred where the card would be).
            var up = facing * Vector3.up;
            holder.localPosition = -up * size.y * 0.5f;
            var instance = (GameObject)PrefabUtility.InstantiatePrefab(model, holder);

            // In 2 mm steps, so pieces of a size share their materials.
            float outline = Mathf.Round(Mathf.Clamp(0.0025f * Mathf.Max(size.x, size.y), 0.003f, 0.012f) * 500f) / 500f;
            foreach (var renderer in instance.GetComponentsInChildren<Renderer>(true))
            {
                var mats = renderer.sharedMaterials;
                for (int i = 0; i < mats.Length; i++) mats[i] = Surface(mats[i], haze, flat ? 0f : outline);
                renderer.sharedMaterials = mats;
                renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
                renderer.receiveShadows = false;
            }
            return pivot;
        }

        /// <summary>The toon copy of a model's imported material: its painting, lit softly from the side, with a thin ink
        /// outline and the card's haze.</summary>
        static Material Surface(Material source, float haze, float outline)
        {
            if (source == null) return null;
            haze = Mathf.Round(haze * 20f) / 20f;
            string key = $"{source.name}_h{haze:0.00}_o{outline:0.000}";
            if (s_materials.TryGetValue(key, out var cached) && cached != null) return cached;
            const string folder = ArtAssets.MaterialFolder + "/Models";
            ArtAssets.EnsureFolder(folder);
            string path = $"{folder}/{key}.mat";
            var shader = Shader.Find("ChickenRunner/Toon");
            var material = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (material == null)
            {
                material = new Material(shader);
                AssetDatabase.CreateAsset(material, path);
            }
            if (shader != null) material.shader = shader;
            var texture = source.HasProperty("_MainTex") ? source.mainTexture : null;
            if (texture == null && source.HasProperty("_BaseMap")) texture = source.GetTexture("_BaseMap");
            material.mainTexture = texture;
            material.color = Color.white;
            // Shade gently: the painting already has its own light and shadow.
            material.SetColor("_ShadowTint", new Color(0.86f, 0.8f, 0.86f));
            material.SetFloat("_Threshold", -0.15f);
            material.SetFloat("_Softness", 0.25f);
            material.SetFloat("_Gloss", 0f);
            material.SetFloat("_OutlineWidth", outline);
            material.SetColor("_HazeColor", ArtAssets.Haze);
            material.SetFloat("_Haze", haze);
            material.enableInstancing = true;
            EditorUtility.SetDirty(material);
            s_materials[key] = material;
            return material;
        }

        /// <summary>
        /// How far behind <paramref name="card"/> its model may reach before running into another standing piece
        /// whose span overlaps it (a house stops short of the tree behind it).
        /// </summary>
        public static float RoomBehind(LayoutCard card, IList<LayoutCard> cards)
        {
            float room = float.PositiveInfinity;
            if (card.flat) return room;
            foreach (var other in cards)
            {
                if (other == card || other.flat || other.z <= card.z + 0.05f) continue;
                if (Mathf.Abs(other.x - card.x) >= (other.w + card.w) * 0.5f * 0.8f) continue;
                if (other.y > card.y + card.h || other.y + other.h < card.y) continue;
                room = Mathf.Min(room, other.z - card.z);
            }
            return room;
        }
    }

    /// <summary>Import settings for the scenery models: metres, no rig, no animation, cameras or lights.</summary>
    internal sealed class ArtModelImport : AssetPostprocessor
    {
        void OnPreprocessModel()
        {
            if (!assetPath.StartsWith(ArtModels.Folder + "/") || !assetPath.EndsWith(".fbx")) return;
            var importer = (ModelImporter)assetImporter;
            importer.globalScale = 1f;
            importer.useFileScale = true;
            importer.importBlendShapes = false;
            importer.importCameras = false;
            importer.importLights = false;
            importer.importAnimation = false;
            importer.animationType = ModelImporterAnimationType.None;
            importer.avatarSetup = ModelImporterAvatarSetup.NoAvatar;
            importer.materialImportMode = ModelImporterMaterialImportMode.ImportViaMaterialDescription;
            importer.materialLocation = ModelImporterMaterialLocation.InPrefab;
            importer.meshCompression = ModelImporterMeshCompression.Medium;
        }
    }
}
