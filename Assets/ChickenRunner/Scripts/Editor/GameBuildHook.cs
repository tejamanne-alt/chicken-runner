using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;

namespace ChickenRunner.EditorTools
{
    /// <summary>
    /// Makes Unity's own Build and Build And Run buttons (Build Profiles) build the game. The game scene and the build's
    /// scene list are generated (Chicken Runner > Build Game) and neither is in git, so on a fresh checkout the list is
    /// empty: Unity then builds the open scene, and asks to save it first if it is untitled. Before every build from those
    /// buttons this builds the game if its scene is missing, puts the scene first in the list and applies the project's
    /// Player Settings (ProjectDefaults); then Unity's own steps carry on (the build folder, the platform's build). The
    /// scene list is also set whenever the editor loads, if the game has been built.
    /// </summary>
    [InitializeOnLoad]
    static class GameBuildHook
    {
        static GameBuildHook()
        {
            BuildPlayerWindow.RegisterGetBuildPlayerOptionsHandler(GetBuildPlayerOptions);
            EditorApplication.delayCall += GameBuilder.ListGameScene;
        }

        static BuildPlayerOptions GetBuildPlayerOptions(BuildPlayerOptions options)
        {
            if (!File.Exists(GameBuilder.ScenePath))
            {
                // an empty message cancels quietly: the user chose Cancel when asked to save their open scene
                if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) throw new BuildPlayerWindow.BuildMethodException();
                GameBuilder.Build();
                if (!File.Exists(GameBuilder.ScenePath))
                    throw new BuildPlayerWindow.BuildMethodException("Building the game scene failed (see the Console above), so there is nothing to build.");
            }
            GameBuilder.ListGameScene();
            ProjectDefaults.Apply();
            return BuildPlayerWindow.DefaultBuildMethods.GetBuildPlayerOptions(options);
        }
    }
}
