using System;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEngine;

namespace ChickenRunner.EditorTools
{
    /// <summary>
    /// Rebuilds the Blender scenes' painted cut-outs in Unity. The scene builders in ArtSource/tools write one layout
    /// per zone to Assets/ChickenRunner/Art/Layouts/*.json; this copies the art each layout uses from ArtSource into
    /// Assets/ChickenRunner/Art/Textures, makes a material per card look, and saves a prefab per zone in
    /// Assets/ChickenRunner/Art/Prefabs with the cards grouped by layer (Houses, Plants, Props, Backdrop, ...).
    /// Drop a prefab into a level scene at the origin: its lane runs along +X at depth 0, as the grey-box's does.
    /// The ground and the 3D bits (walls, fences, pebbles, grass) are not in the layouts yet.
    /// </summary>
    public static class ArtLayoutImporter
    {
        const string LayoutFolder = "Assets/ChickenRunner/Art/Layouts";
        const string TextureFolder = "Assets/ChickenRunner/Art/Textures";
        const string MaterialFolder = "Assets/ChickenRunner/Art/Materials";
        const string PrefabFolder = "Assets/ChickenRunner/Art/Prefabs";
        const string ShaderName = "ChickenRunner/PaintedCard";

#pragma warning disable 0649 // filled in by JsonUtility
        [Serializable]
        class Card
        {
            public string name;
            public string image;
            public string layer;
            public float x, y, z, w, h, turn, haze, fade_bottom, fade_sides;
            public bool mirror, flat, shadeless;
        }

        [Serializable]
        class Layout
        {
            public string zone;
            public float[] hazeColor;
            public Card[] cards;
        }
#pragma warning restore 0649

        [MenuItem("Chicken Runner/Import Art Layouts", priority = 20)]
        public static void ImportAll()
        {
            if (!Directory.Exists(LayoutFolder))
            {
                Debug.LogWarning($"No layouts in {LayoutFolder}: run a scene builder in ArtSource/tools first.");
                return;
            }
            var shader = Shader.Find(ShaderName);
            if (shader == null)
            {
                Debug.LogError($"Shader {ShaderName} not found.");
                return;
            }
            foreach (var file in Directory.GetFiles(LayoutFolder, "*.json"))
                Import(file, shader);
            AssetDatabase.SaveAssets();
        }

        static void Import(string file, Shader shader)
        {
            var layout = JsonUtility.FromJson<Layout>(File.ReadAllText(file));
            if (layout?.cards == null || layout.cards.Length == 0)
                return;
            var hazeColor = layout.hazeColor != null && layout.hazeColor.Length >= 3
                ? new Color(layout.hazeColor[0], layout.hazeColor[1], layout.hazeColor[2])
                : new Color(0.98f, 0.765f, 0.545f);
            var repoRoot = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            var root = new GameObject($"Art_{layout.zone}");
            var layers = new Dictionary<string, Transform>();
            var materials = new Dictionary<string, Material>();
            var quad = Resources.GetBuiltinResource<Mesh>("Quad.fbx");
            try
            {
                for (var i = 0; i < layout.cards.Length; i++)
                {
                    var card = layout.cards[i];
                    if (EditorUtility.DisplayCancelableProgressBar($"Importing {layout.zone}", card.name,
                            (float)i / layout.cards.Length))
                        break;
                    var texture = ImportTexture(repoRoot, card.image);
                    if (texture == null)
                        continue;
                    var material = MaterialFor(card, texture, hazeColor, shader, materials);
                    if (!layers.TryGetValue(card.layer, out var parent))
                    {
                        parent = new GameObject(card.layer).transform;
                        parent.SetParent(root.transform, false);
                        layers[card.layer] = parent;
                    }
                    var go = new GameObject(card.name, typeof(MeshFilter), typeof(MeshRenderer));
                    go.transform.SetParent(parent, false);
                    go.GetComponent<MeshFilter>().sharedMesh = quad;
                    var renderer = go.GetComponent<MeshRenderer>();
                    renderer.sharedMaterial = material;
                    renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
                    renderer.receiveShadows = false;
                    var sx = card.mirror ? -card.w : card.w;
                    if (card.flat)
                    {
                        // A decal lying on the ground, centred on its position, turned about the vertical.
                        go.transform.localPosition = new Vector3(card.x, card.y + 0.002f, card.z);
                        go.transform.localRotation = Quaternion.Euler(90f, -card.turn, 0f);
                        go.transform.localScale = new Vector3(sx, card.h, 1f);
                    }
                    else
                    {
                        // A card standing on the ground: the position is its bottom centre.
                        go.transform.localPosition = new Vector3(card.x, card.y + card.h / 2f, card.z);
                        go.transform.localRotation = Quaternion.Euler(0f, -card.turn, 0f);
                        go.transform.localScale = new Vector3(sx, card.h, 1f);
                    }
                }
            }
            finally
            {
                EditorUtility.ClearProgressBar();
            }
            EnsureFolder(PrefabFolder);
            var prefabPath = $"{PrefabFolder}/Art_{layout.zone}.prefab";
            PrefabUtility.SaveAsPrefabAsset(root, prefabPath);
            UnityEngine.Object.DestroyImmediate(root);
            Debug.Log($"Imported {layout.cards.Length} cards into {prefabPath}");
        }

        static Texture2D ImportTexture(string repoRoot, string image)
        {
            var source = Path.Combine(repoRoot, image);
            if (!File.Exists(source))
            {
                Debug.LogWarning($"Missing art: {image}");
                return null;
            }
            // ArtSource/cutouts/lane/house_pink.png -> Assets/ChickenRunner/Art/Textures/cutouts/lane/house_pink.png
            var relative = image.StartsWith("ArtSource/", StringComparison.Ordinal) ? image.Substring(10) : image;
            var assetPath = $"{TextureFolder}/{relative}";
            var full = Path.Combine(repoRoot, assetPath);
            if (!File.Exists(full) || File.GetLastWriteTimeUtc(full) < File.GetLastWriteTimeUtc(source))
            {
                EnsureFolder(Path.GetDirectoryName(assetPath)?.Replace('\\', '/'));
                File.Copy(source, full, true);
                AssetDatabase.ImportAsset(assetPath, ImportAssetOptions.ForceSynchronousImport);
                if (AssetImporter.GetAtPath(assetPath) is TextureImporter importer)
                {
                    importer.textureType = TextureImporterType.Default;
                    importer.alphaIsTransparency = true;
                    importer.wrapMode = TextureWrapMode.Clamp;
                    importer.mipmapEnabled = true;
                    importer.maxTextureSize = 2048;
                    importer.SaveAndReimport();
                }
            }
            return AssetDatabase.LoadAssetAtPath<Texture2D>(assetPath);
        }

        static Material MaterialFor(Card card, Texture2D texture, Color hazeColor, Shader shader,
            Dictionary<string, Material> cache)
        {
            var haze = Mathf.Round(card.haze * 20f) / 20f; // haze in steps of 0.05, so cards can share materials
            var key = $"{texture.name}_h{haze:0.00}_b{card.fade_bottom:0.00}_s{card.fade_sides:0.00}";
            if (cache.TryGetValue(key, out var material))
                return material;
            EnsureFolder(MaterialFolder);
            var path = $"{MaterialFolder}/{key}.mat";
            material = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (material == null)
            {
                material = new Material(shader);
                AssetDatabase.CreateAsset(material, path);
            }
            material.shader = shader;
            material.mainTexture = texture;
            material.SetColor("_HazeColor", hazeColor);
            material.SetFloat("_Haze", haze);
            material.SetFloat("_FadeBottom", card.fade_bottom);
            material.SetFloat("_FadeSides", card.fade_sides);
            EditorUtility.SetDirty(material);
            cache[key] = material;
            return material;
        }

        static void EnsureFolder(string path)
        {
            if (string.IsNullOrEmpty(path) || AssetDatabase.IsValidFolder(path))
                return;
            var parent = Path.GetDirectoryName(path)?.Replace('\\', '/');
            EnsureFolder(parent);
            AssetDatabase.CreateFolder(parent, Path.GetFileName(path));
        }
    }
}
