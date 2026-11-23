using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Animations;
using UnityEngine;

namespace ChickenRunner.EditorTools
{
    internal static partial class GameBuilder
    {
        /// <summary>The 3D models face Unity's +Z; turned to run toward +X, then 25 degrees toward the camera.</summary>
        static readonly Quaternion s_facing = Quaternion.Euler(0f, 115f, 0f);
        static readonly Dictionary<string, Material> s_toon = new Dictionary<string, Material>();
        static readonly Dictionary<string, GameObject> s_models = new Dictionary<string, GameObject>();

        /// <summary>A character or pickup model from Assets/ChickenRunner/Art/Characters, imported with CharacterImport's settings; null if it is not there.</summary>
        static GameObject Model(string name)
        {
            if (s_models.TryGetValue(name, out var cached)) return cached;
            string path = $"{CharacterImport.Folder}/{name}.fbx";
            GameObject model = null;
            if (File.Exists(Path.Combine(ArtAssets.RepoRoot, path)))
            {
                AssetDatabase.ImportAsset(path, ImportAssetOptions.ForceUpdate);
                model = AssetDatabase.LoadAssetAtPath<GameObject>(path);
            }
            s_models[name] = model;
            return model;
        }

        static void ClearModelCache()
        {
            s_toon.Clear();
            s_models.Clear();
        }

        /// <summary>The toon-shaded copy of an imported material: its colour or texture, two-tone with an ink outline.</summary>
        static Material Toon(Material source, float outline)
        {
            if (source == null) return null;
            string key = source.name + outline.ToString("0.000");
            if (s_toon.TryGetValue(key, out var cached)) return cached;
            string path = $"{MaterialFolder}/Toon_{source.name}.mat";
            var shader = Shader.Find("ChickenRunner/Toon");
            var material = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (material == null)
            {
                material = new Material(shader);
                AssetDatabase.CreateAsset(material, path);
            }
            material.shader = shader;
            var texture = source.HasProperty("_MainTex") ? source.mainTexture : null;
            if (texture == null && source.HasProperty("_BaseMap")) texture = source.GetTexture("_BaseMap");
            material.mainTexture = texture;
            var color = source.HasProperty("_Color") ? source.color : source.HasProperty("_BaseColor") ? source.GetColor("_BaseColor") : Color.white;
            material.color = texture != null ? Color.white : color;
            string n = source.name;
            material.SetFloat("_Gloss", n.Contains("Gold") || n.Contains("Silver") ? 0.5f : n.Contains("Chilli") || n.Contains("Mango") ? 0.6f
                : n.Contains("Red") || n.Contains("Tail") ? 0.2f : 0f);
            material.SetColor("_ShadowTint", n.Contains("Skin") || n.Contains("Face") ? new Color(0.78f, 0.66f, 0.7f) : new Color(0.68f, 0.62f, 0.78f));
            material.SetFloat("_OutlineWidth", outline);
            EditorUtility.SetDirty(material);
            s_toon[key] = material;
            return material;
        }

        static void ToonUp(GameObject instance, float outline)
        {
            foreach (var renderer in instance.GetComponentsInChildren<Renderer>(true))
            {
                renderer.sharedMaterials = renderer.sharedMaterials.Select(m => Toon(m, outline)).ToArray();
                renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
                renderer.receiveShadows = false;
                if (renderer is SkinnedMeshRenderer skinned) skinned.updateWhenOffscreen = true;
            }
        }

        /// <summary>An Animator Controller with one state per clip in the model, named as the clip ("Run", "Dive", ...).</summary>
        static RuntimeAnimatorController Controller(string name, string defaultState)
        {
            string modelPath = $"{CharacterImport.Folder}/{name}.fbx";
            var clips = AssetDatabase.LoadAllAssetsAtPath(modelPath).OfType<AnimationClip>()
                .Where(c => !c.name.StartsWith("__preview__")).ToList();
            if (clips.Count == 0) return null;
            string path = $"{GameFolder}/{name}.controller";
            AssetDatabase.DeleteAsset(path);
            var controller = AnimatorController.CreateAnimatorControllerAtPath(path);
            var machine = controller.layers[0].stateMachine;
            foreach (var clip in clips)
            {
                var state = machine.AddState(CharacterImport.ShortName(clip.name));
                state.motion = clip;
                if (state.name == defaultState) machine.defaultState = state;
            }
            return controller;
        }

        /// <summary>Puts the model under <paramref name="root"/>, facing the run, toon-shaded and animated by its controller.</summary>
        static Animator PlaceModel(GameObject root, GameObject model, string controllerName, string defaultState)
        {
            // The turn goes on a holder, so the model keeps the transform its import gave it.
            var holder = new GameObject("Model").transform;
            holder.SetParent(root.transform, false);
            holder.localRotation = s_facing;
            var instance = (GameObject)PrefabUtility.InstantiatePrefab(model, holder);
            ToonUp(instance, 0.004f);
            var animator = instance.GetComponent<Animator>() ?? instance.AddComponent<Animator>();
            animator.runtimeAnimatorController = Controller(controllerName, defaultState);
            animator.applyRootMotion = false;
            animator.cullingMode = AnimatorCullingMode.AlwaysAnimate;
            return animator;
        }

        /// <summary>The 3D kid, if Kid.fbx has been built (ArtSource/tools/characters/build_character.py kid).</summary>
        static bool KidModel(GameObject root, KidController kid)
        {
            var model = Model("Kid");
            if (model == null) return false;
            var visual = root.AddComponent<KidModelVisual>();
            visual.kid = kid;
            visual.animator = PlaceModel(root, model, "Kid", "Idle");
            foreach (var renderer in visual.animator.GetComponentsInChildren<Renderer>())
            {
                var mats = renderer.sharedMaterials;
                for (int i = 0; i < mats.Length; i++)
                {
                    if (mats[i] != null && mats[i].name.Contains("KidFace"))
                    {
                        visual.faceRenderer = renderer;
                        visual.faceMaterialIndex = i;
                    }
                }
            }
            visual.faceNeutral = Face("neutral");
            visual.faceGrin = Face("grin");
            visual.faceShocked = Face("shocked");
            visual.faceStraining = Face("straining");
            return true;
        }

        static Texture2D Face(string expression)
        {
            string path = $"{CharacterImport.Folder}/KidFaces/KidFace_{expression}.png";
            AssetDatabase.ImportAsset(path);
            return AssetDatabase.LoadAssetAtPath<Texture2D>(path);
        }

        /// <summary>The 3D rooster, if Rooster.fbx has been built.</summary>
        static bool RoosterModel(GameObject root, RoosterBrain brain)
        {
            var model = Model("Rooster");
            if (model == null) return false;
            var visual = root.AddComponent<RoosterModelVisual>();
            visual.rooster = brain;
            visual.animator = PlaceModel(root, model, "Rooster", "Idle");
            return true;
        }

        /// <summary>A pickup's 3D model under its spinning visual; false (draw the grey-box shape) if it is not built yet.</summary>
        static bool PickupModel(Transform visual, string name, Quaternion tilt)
        {
            var model = Model(name);
            if (model == null) return false;
            var holder = new GameObject(name).transform;
            holder.SetParent(visual, false);
            holder.localRotation = tilt;
            var instance = (GameObject)PrefabUtility.InstantiatePrefab(model, holder);
            ToonUp(instance, 0.003f);
            return true;
        }
    }
}
