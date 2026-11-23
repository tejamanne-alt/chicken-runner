using System;
using System.IO;
using ChickenRunner.Core;
using UnityEngine;

namespace ChickenRunner
{
    /// <summary>
    /// Reads and writes <see cref="SaveData"/> as JSON in the app's persistent data folder. Writes go to a temporary
    /// file first and then replace the save, so a crash mid-write never leaves a half-written save behind.
    /// A missing or unreadable save starts a new game rather than failing.
    /// </summary>
    public static class SaveService
    {
        const string FileName = "chicken-runner-save.json";

        public static string FilePath => Path.Combine(Application.persistentDataPath, FileName);

        public static SaveData Load()
        {
            try
            {
                // A crash between deleting the old save and moving the new one in leaves only the temporary file.
                string path = File.Exists(FilePath) ? FilePath : FilePath + ".tmp";
                if (File.Exists(path))
                {
                    var data = JsonUtility.FromJson<SaveData>(File.ReadAllText(path));
                    if (data != null)
                    {
                        data.Repair();
                        return data;
                    }
                }
            }
            catch (Exception e)
            {
                Debug.LogWarning("Could not read the save, starting a new game: " + e.Message);
            }
            return new SaveData();
        }

        public static void Save(SaveData data)
        {
            if (data == null) return;
            try
            {
                string temp = FilePath + ".tmp";
                File.WriteAllText(temp, JsonUtility.ToJson(data, true));
                if (File.Exists(FilePath)) File.Delete(FilePath);
                File.Move(temp, FilePath);
            }
            catch (Exception e)
            {
                Debug.LogWarning("Could not write the save: " + e.Message);
            }
        }

        public static void Delete()
        {
            try
            {
                if (File.Exists(FilePath)) File.Delete(FilePath);
            }
            catch (Exception e)
            {
                Debug.LogWarning("Could not delete the save: " + e.Message);
            }
        }
    }
}
