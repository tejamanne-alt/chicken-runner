using System.IO;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEngine;
#if UNITY_IOS
using UnityEditor.iOS.Xcode;
#endif

namespace ChickenRunner.EditorTools
{
    /// <summary>
    /// The project's Player Settings, kept in code: ProjectSettings/ is not in the repository (only its
    /// ProjectVersion.txt is), so a fresh checkout would get whatever Unity generates. Applied whenever the editor loads,
    /// and from Chicken Runner > Apply Project Settings:
    ///   * the bundle identifier / package name, <see cref="ApplicationId"/>, on iOS, Android and desktop;
    ///   * iOS signing: automatic, with the Apple developer team <see cref="AppleTeamId"/>, and the same written into the
    ///     exported Xcode project's targets after each iOS build, so Xcode opens with the right team every time;
    ///   * Active Input Handling: the Input System package only. The game reads touches, the mouse and keys through it
    ///     (KidInput), and its menus are IMGUI, which needs neither. The editor reads this setting when it starts, so
    ///     after changing it this offers a restart, as Player Settings does.
    /// </summary>
    [InitializeOnLoad]
    public sealed class ProjectDefaults : IPostprocessBuildWithReport
    {
        public const string ApplicationId = "com.astradite.chickendinner";
        public const string AppleTeamId = "JYC5MKYDS7";

        /// <summary>Player Settings' activeInputHandler: 0 the Input Manager (old), 1 the Input System package, 2 both.</summary>
        const int InputSystemOnly = 1;
        const string AskedKey = "ChickenRunner.InputHandlingRestartAsked";

        static ProjectDefaults()
        {
            EditorApplication.delayCall += Apply;
        }

        [MenuItem("Chicken Runner/Apply Project Settings", priority = 40)]
        public static void Apply()
        {
            bool changed = false;
            foreach (var target in new[] { NamedBuildTarget.iOS, NamedBuildTarget.Android, NamedBuildTarget.Standalone })
            {
                if (PlayerSettings.GetApplicationIdentifier(target) == ApplicationId) continue;
                PlayerSettings.SetApplicationIdentifier(target, ApplicationId);
                changed = true;
            }
            if (PlayerSettings.iOS.appleDeveloperTeamID != AppleTeamId)
            {
                PlayerSettings.iOS.appleDeveloperTeamID = AppleTeamId;
                changed = true;
            }
            if (!PlayerSettings.iOS.appleEnableAutomaticSigning) changed = true;
            PlayerSettings.iOS.appleEnableAutomaticSigning = true;   // stored, not left to the editor preference's default

            bool restart = false;
            var settings = Unsupported.GetSerializedAssetInterfaceSingleton("PlayerSettings");
            if (settings != null)
            {
                var so = new SerializedObject(settings);
                // Unity 6's "Override Default Package Name": without it Android makes its own from the company and product.
                var overrideId = so.FindProperty("overrideDefaultApplicationIdentifier");
                if (overrideId != null && overrideId.propertyType == SerializedPropertyType.Boolean) overrideId.boolValue = true;
                var handler = so.FindProperty("activeInputHandler");
                if (handler != null && handler.intValue != InputSystemOnly)
                {
                    handler.intValue = InputSystemOnly;
                    restart = true;
                }
                if (so.ApplyModifiedPropertiesWithoutUndo()) changed = true;
            }
            else
            {
                Debug.LogWarning("[Chicken Runner] Player Settings not found: set Active Input Handling to the Input System Package by hand.");
            }

            if (!changed)
            {
                SessionState.EraseBool(AskedKey);
                return;
            }
            AssetDatabase.SaveAssets();
            Debug.Log($"[Chicken Runner] Player Settings: {ApplicationId} on iOS, Android and desktop; iOS signs automatically "
                + $"with team {AppleTeamId}; Active Input Handling: Input System Package (New).");
            if (!restart || Application.isBatchMode || SessionState.GetBool(AskedKey, false)) return;
            SessionState.SetBool(AskedKey, true);
            if (EditorUtility.DisplayDialog("Restart Unity",
                    "Chicken Runner uses the Input System package only (Active Input Handling: Input System Package (New)). "
                    + "The editor needs a restart to switch. Restart now?", "Restart", "Later"))
                EditorApplication.OpenProject(Directory.GetCurrentDirectory());
        }

        public int callbackOrder => 100;

        /// <summary>The same bundle identifier and signing in the exported Xcode project, on both its targets.</summary>
        public void OnPostprocessBuild(BuildReport report)
        {
#if UNITY_IOS
            if (report.summary.platform != BuildTarget.iOS) return;
            string path = PBXProject.GetPBXProjectPath(report.summary.outputPath);
            var project = new PBXProject();
            project.ReadFromFile(path);
            string app = project.GetUnityMainTargetGuid(), framework = project.GetUnityFrameworkTargetGuid();
            project.SetBuildProperty(app, "PRODUCT_BUNDLE_IDENTIFIER", ApplicationId);
            foreach (string target in new[] { app, framework })
            {
                project.SetBuildProperty(target, "CODE_SIGN_STYLE", "Automatic");
                project.SetBuildProperty(target, "DEVELOPMENT_TEAM", AppleTeamId);
                project.SetBuildProperty(target, "PROVISIONING_PROFILE_SPECIFIER", "");
            }
            project.SetBuildProperty(app, "CODE_SIGN_IDENTITY", "Apple Development");
            project.WriteToFile(path);
#endif
        }
    }
}
