using System;
using System.Collections.Generic;
using System.IO;
using System.Security.Cryptography;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEngine;

namespace ChickenRunner.EditorTools
{
    /// <summary>
    /// Brings painted art from ArtSource into the Unity project for the builders: copies images into
    /// Assets/ChickenRunner/Art/Textures (same sub-folders as under ArtSource), makes one PaintedCard material per look,
    /// builds card quads, reads cut-out sizes from ArtSource/cutouts/lane/manifest.json and picks the real reference
    /// image or its placeholder the way ArtSource/tools/refs.py does. Missing art is never an error: callers get null
    /// and fall back to grey-box shapes, so the game builds at any stage of the art.
    /// </summary>
    internal static class ArtAssets
    {
        public const string TextureFolder = "Assets/ChickenRunner/Art/Textures";
        public const string MaterialFolder = "Assets/ChickenRunner/Art/Materials";
        public const string CardShaderName = "ChickenRunner/PaintedCard";
        public const string GroundShaderName = "ChickenRunner/PaintedGround";
        public static readonly Color Haze = new Color(0.98f, 0.765f, 0.545f);

        static readonly string[] s_cutoutFolders = { "lane", "market", "fields", "animals", "people", "plants", "ground", "kid", "rooster", "textures" };
        static Dictionary<string, PieceSize> s_manifest;
        static Dictionary<string, string> s_rejected;
        static readonly Dictionary<string, Material> s_materials = new Dictionary<string, Material>();
        static Mesh s_quad;

        public static string RepoRoot => Path.GetFullPath(Path.Combine(Application.dataPath, ".."));

        public static Mesh Quad => s_quad != null ? s_quad : s_quad = Resources.GetBuiltinResource<Mesh>("Quad.fbx");

        /// <summary>Forget cached materials and manifest, so a rebuild sees new art.</summary>
        public static void ClearCache()
        {
            s_materials.Clear();
            s_manifest = null;
            s_rejected = null;
        }

        // ------------------------------------------------------------------ finding art

        /// <summary>Repo-relative path of a cut-out by name, searched across the cut-out folders; null if there is none.</summary>
        public static string Cutout(string name)
        {
            foreach (var folder in s_cutoutFolders)
            {
                string path = $"ArtSource/cutouts/{folder}/{name}.png";
                if (File.Exists(Path.Combine(RepoRoot, path))) return path;
            }
            return null;
        }

        /// <summary>
        /// Repo-relative path of a reference image (e.g. "F1_title_screen.png"): the real one unless it is missing or
        /// listed in placeholders/rejected.json with its current hash, else its placeholder, else null.
        /// </summary>
        public static string Reference(string fileName)
        {
            string real = "ArtSource/references/" + fileName;
            string full = Path.Combine(RepoRoot, real);
            if (File.Exists(full) && (!Rejected().TryGetValue(fileName, out var hash) || hash != Sha256(full))) return real;
            string placeholder = "ArtSource/placeholders/" + fileName;
            return File.Exists(Path.Combine(RepoRoot, placeholder)) ? placeholder : null;
        }

        static Dictionary<string, string> Rejected()
        {
            if (s_rejected != null) return s_rejected;
            s_rejected = new Dictionary<string, string>();
            string path = Path.Combine(RepoRoot, "ArtSource/placeholders/rejected.json");
            if (File.Exists(path))
            {
                foreach (Match m in Regex.Matches(File.ReadAllText(path), "\"([^\"]+)\"\\s*:\\s*\"([0-9a-fA-F]{64})\""))
                    s_rejected[m.Groups[1].Value] = m.Groups[2].Value.ToLowerInvariant();
            }
            return s_rejected;
        }

        static string Sha256(string path)
        {
            using (var sha = SHA256.Create())
            using (var stream = File.OpenRead(path))
                return BitConverter.ToString(sha.ComputeHash(stream)).Replace("-", "").ToLowerInvariant();
        }

        // ------------------------------------------------------------------ sizes

        /// <summary>A cut-out's pixel size and its real-world scale, from the cut-out manifest.</summary>
        public struct PieceSize
        {
            public int pxWidth;
            public int pxHeight;
            public float pxPerMetre;
            public float heightM;
            public float widthM;
        }

        public static bool TryGetSize(string name, out PieceSize size)
        {
            if (s_manifest == null) LoadManifest();
            return s_manifest.TryGetValue(name, out size);
        }

        /// <summary>
        /// World size of a cut-out: from its pixels per metre, else its height or width in metres from the manifest,
        /// else <paramref name="fallbackHeight"/>, keeping the picture's proportions.
        /// </summary>
        public static Vector2 SizeOf(string name, Texture2D texture, float fallbackHeight)
        {
            float aspect = texture != null && texture.height > 0 ? texture.width / (float)texture.height : 1f;
            if (TryGetSize(name, out var s))
            {
                if (s.pxHeight > 0) aspect = s.pxWidth / (float)s.pxHeight;
                if (s.pxPerMetre > 0f && s.pxHeight > 0) return new Vector2(s.pxWidth / s.pxPerMetre, s.pxHeight / s.pxPerMetre);
                if (s.heightM > 0f) return new Vector2(s.heightM * aspect, s.heightM);
                if (s.widthM > 0f) return new Vector2(s.widthM, s.widthM / aspect);
            }
            return new Vector2(fallbackHeight * aspect, fallbackHeight);
        }

        static void LoadManifest()
        {
            s_manifest = new Dictionary<string, PieceSize>();
            string path = Path.Combine(RepoRoot, "ArtSource/cutouts/lane/manifest.json");
            if (!File.Exists(path)) return;
            foreach (Match m in Regex.Matches(File.ReadAllText(path), "\"([^\"]+)\"\\s*:\\s*\\{([^{}]*)\\}"))
            {
                string body = m.Groups[2].Value;
                var size = new PieceSize();
                var px = Regex.Match(body, "\"px\"\\s*:\\s*\\[\\s*(\\d+)\\s*,\\s*(\\d+)\\s*\\]");
                if (px.Success)
                {
                    size.pxWidth = int.Parse(px.Groups[1].Value);
                    size.pxHeight = int.Parse(px.Groups[2].Value);
                }
                size.pxPerMetre = Number(body, "px_per_m");
                size.heightM = Number(body, "height_m");
                size.widthM = Number(body, "width_m");
                s_manifest[m.Groups[1].Value] = size;
            }
        }

        static float Number(string body, string key)
        {
            var m = Regex.Match(body, "\"" + key + "\"\\s*:\\s*([-0-9.eE]+)");
            return m.Success && float.TryParse(m.Groups[1].Value, System.Globalization.NumberStyles.Float,
                System.Globalization.CultureInfo.InvariantCulture, out float v) ? v : 0f;
        }

        // ------------------------------------------------------------------ textures and materials

        /// <summary>
        /// Copies an ArtSource image into the project (when new or changed) and returns it, or null if the source is
        /// missing. Cards clamp; ground tiles repeat. Pictures keep their exact pixel size (no power-of-two rescale), so
        /// a pose's size in the world can be worked out from its pixels.
        /// </summary>
        public static Texture2D Texture(string repoPath, bool repeat = false)
        {
            if (string.IsNullOrEmpty(repoPath)) return null;
            string source = Path.Combine(RepoRoot, repoPath);
            if (!File.Exists(source))
            {
                Debug.LogWarning($"Missing art: {repoPath}");
                return null;
            }
            string relative = repoPath.StartsWith("ArtSource/", StringComparison.Ordinal) ? repoPath.Substring(10) : repoPath;
            string assetPath = $"{TextureFolder}/{relative}";
            string full = Path.Combine(RepoRoot, assetPath);
            bool copy = !File.Exists(full) || File.GetLastWriteTimeUtc(full) < File.GetLastWriteTimeUtc(source);
            if (copy)
            {
                EnsureFolder(Path.GetDirectoryName(assetPath)?.Replace('\\', '/'));
                File.Copy(source, full, true);
                AssetDatabase.ImportAsset(assetPath, ImportAssetOptions.ForceSynchronousImport);
            }
            if (AssetImporter.GetAtPath(assetPath) is TextureImporter importer)
            {
                var wrap = repeat ? TextureWrapMode.Repeat : TextureWrapMode.Clamp;
                if (copy || importer.wrapMode != wrap || importer.npotScale != TextureImporterNPOTScale.None)
                {
                    importer.textureType = TextureImporterType.Default;
                    importer.alphaIsTransparency = true;
                    importer.wrapMode = wrap;
                    importer.npotScale = TextureImporterNPOTScale.None;
                    importer.mipmapEnabled = true;
                    importer.maxTextureSize = 2048;
                    importer.SaveAndReimport();
                }
            }
            return AssetDatabase.LoadAssetAtPath<Texture2D>(assetPath);
        }

        public static Texture2D CutoutTexture(string name) => Texture(Cutout(name));

        public static Shader CardShader => Shader.Find(CardShaderName);

        /// <summary>A PaintedCard material for this look, shared by every card that looks the same.</summary>
        public static Material CardMaterial(Texture2D texture, float haze = 0f, float fadeBottom = 0f, float fadeSides = 0f)
        {
            if (texture == null) return null;
            haze = Mathf.Round(haze * 20f) / 20f; // haze in steps of 0.05, so cards can share materials
            string key = $"{texture.name}_h{haze:0.00}_b{fadeBottom:0.00}_s{fadeSides:0.00}";
            if (s_materials.TryGetValue(key, out var material) && material != null) return material;
            EnsureFolder(MaterialFolder);
            string path = $"{MaterialFolder}/{key}.mat";
            material = AssetDatabase.LoadAssetAtPath<Material>(path);
            var shader = CardShader;
            if (material == null)
            {
                material = new Material(shader);
                AssetDatabase.CreateAsset(material, path);
            }
            if (shader != null) material.shader = shader;
            material.mainTexture = texture;
            material.SetColor("_HazeColor", Haze);
            material.SetFloat("_Haze", haze);
            material.SetFloat("_FadeBottom", fadeBottom);
            material.SetFloat("_FadeSides", fadeSides);
            material.enableInstancing = true;
            EditorUtility.SetDirty(material);
            s_materials[key] = material;
            return material;
        }

        /// <summary>
        /// A card quad standing with its bottom centre at <paramref name="bottomCentre"/> (or, if
        /// <paramref name="flat"/>, lying on the ground centred there, turned <paramref name="turn"/> degrees).
        /// </summary>
        public static GameObject Card(Transform parent, string name, Material material, Vector3 bottomCentre, Vector2 size,
            bool mirror = false, bool flat = false, float turn = 0f)
        {
            var go = new GameObject(name, typeof(MeshFilter), typeof(MeshRenderer));
            go.transform.SetParent(parent, false);
            go.GetComponent<MeshFilter>().sharedMesh = Quad;
            var renderer = go.GetComponent<MeshRenderer>();
            renderer.sharedMaterial = material;
            renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            renderer.receiveShadows = false;
            float sx = mirror ? -size.x : size.x;
            if (flat)
            {
                go.transform.localPosition = bottomCentre + new Vector3(0f, 0.002f, 0f);
                go.transform.localRotation = Quaternion.Euler(90f, -turn, 0f);
            }
            else
            {
                go.transform.localPosition = bottomCentre + new Vector3(0f, size.y * 0.5f, 0f);
                go.transform.localRotation = Quaternion.Euler(0f, -turn, 0f);
            }
            go.transform.localScale = new Vector3(sx, size.y, 1f);
            return go;
        }

        public static void EnsureFolder(string path)
        {
            if (string.IsNullOrEmpty(path) || AssetDatabase.IsValidFolder(path)) return;
            string parent = Path.GetDirectoryName(path)?.Replace('\\', '/');
            EnsureFolder(parent);
            AssetDatabase.CreateFolder(parent, Path.GetFileName(path));
        }
    }
}
