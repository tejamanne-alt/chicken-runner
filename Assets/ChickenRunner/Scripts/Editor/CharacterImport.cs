using System.Collections.Generic;
using System.IO;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEngine;

namespace ChickenRunner.EditorTools
{
    /// <summary>
    /// Import settings for the 3D characters and pickups built in ArtSource/tools/characters (Assets/ChickenRunner/Art/
    /// Characters/*.fbx): metres, a Generic rig with no root motion, each take renamed from "KidRig|Run" to "Run", and
    /// the loops from the clip list Blender writes beside each model (Kid.clips.json).
    /// </summary>
    internal sealed class CharacterImport : AssetPostprocessor
    {
        public const string Folder = "Assets/ChickenRunner/Art/Characters";

        static bool Ours(string path) => path.StartsWith(Folder + "/") && path.EndsWith(".fbx");

        void OnPreprocessModel()
        {
            if (!Ours(assetPath)) return;
            var importer = (ModelImporter)assetImporter;
            importer.globalScale = 1f;
            importer.useFileScale = true;
            importer.importBlendShapes = false;
            importer.importCameras = false;
            importer.importLights = false;
            bool animated = File.Exists(ClipListPath(assetPath));
            importer.animationType = animated ? ModelImporterAnimationType.Generic : ModelImporterAnimationType.None;
            importer.importAnimation = animated;
            importer.avatarSetup = animated ? ModelImporterAvatarSetup.CreateFromThisModel : ModelImporterAvatarSetup.NoAvatar;
        }

        void OnPreprocessAnimation()
        {
            if (!Ours(assetPath)) return;
            var importer = (ModelImporter)assetImporter;
            var loops = Loops(assetPath);
            var clips = importer.defaultClipAnimations;
            foreach (var clip in clips)
            {
                string name = ShortName(clip.takeName);
                clip.name = name;
                clip.loopTime = loops.Contains(name);
                clip.loopPose = false;
                clip.lockRootRotation = clip.lockRootHeightY = clip.lockRootPositionXZ = false;
            }
            importer.clipAnimations = clips;
        }

        /// <summary>"KidRig|Run" -> "Run".</summary>
        public static string ShortName(string take)
        {
            int bar = take.LastIndexOf('|');
            return bar >= 0 ? take.Substring(bar + 1) : take;
        }

        static string ClipListPath(string fbx) => Path.ChangeExtension(fbx, null) + ".clips.json";

        static HashSet<string> Loops(string fbx)
        {
            var loops = new HashSet<string>();
            string path = ClipListPath(fbx);
            if (!File.Exists(path)) return loops;
            // [{"name": "Run", "frames": 16, "loop": true, ...}, ...]
            foreach (Match m in Regex.Matches(File.ReadAllText(path), "\"name\"\\s*:\\s*\"([^\"]+)\"[^}]*?\"loop\"\\s*:\\s*true"))
                loops.Add(m.Groups[1].Value);
            return loops;
        }
    }
}
