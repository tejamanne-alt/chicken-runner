using System.Collections.Generic;
using UnityEngine;

namespace ChickenRunner
{
    /// <summary>
    /// Grey-box stand-in for sound effects and voice barks: short words that float up from a point in the world
    /// ("SMASH!", "WOOF!", "-2.3 m"). The HUD draws them; the audio pass replaces them in milestone 3.
    /// </summary>
    public static class WorldBarks
    {
        public struct Bark
        {
            public string text;
            public Vector3 position;
            public Color color;
            public float age;
            public float lifetime;
        }

        const int MaxBarks = 16;
        static readonly List<Bark> s_barks = new List<Bark>(MaxBarks);

        public static IReadOnlyList<Bark> Active => s_barks;

        public static void Show(string text, Vector3 position, Color color, float lifetime = 0.9f)
        {
            if (s_barks.Count >= MaxBarks) s_barks.RemoveAt(0);
            s_barks.Add(new Bark { text = text, position = position, color = color, lifetime = lifetime });
        }

        public static void Tick(float dt)
        {
            for (int i = s_barks.Count - 1; i >= 0; i--)
            {
                var bark = s_barks[i];
                bark.age += dt;
                if (bark.age >= bark.lifetime)
                {
                    s_barks.RemoveAt(i);
                    continue;
                }
                bark.position += Vector3.up * (0.8f * dt);
                s_barks[i] = bark;
            }
        }

        public static void Clear() => s_barks.Clear();
    }
}
