using System.Collections.Generic;
using UnityEngine;

namespace ChickenRunner
{
    /// <summary>
    /// The rooster's authored route: where he flutters, how far and how high. Placed in chunks over obstacles,
    /// so his path shows the player the way. Between hops he runs on the ground.
    /// </summary>
    public sealed class RoosterHop : MonoBehaviour
    {
        static readonly List<RoosterHop> s_active = new List<RoosterHop>();

        [SerializeField, Min(0.2f)] internal float length = 2f;
        [SerializeField, Min(0f)] internal float height = 1f;

        public float StartX => transform.position.x;
        public float EndX => transform.position.x + length;

        /// <summary>Height above the hop's base at course position <paramref name="x"/>: a smooth arc.</summary>
        public float HeightAt(float x)
        {
            float t = Mathf.Clamp01((x - StartX) / length);
            return height * Mathf.Sin(Mathf.PI * t);
        }

        public float Progress(float x) => Mathf.Clamp01((x - StartX) / length);

        public static RoosterHop Find(float x)
        {
            foreach (var hop in s_active)
            {
                if (x >= hop.StartX && x < hop.EndX) return hop;
            }
            return null;
        }

        void OnEnable() => s_active.Add(this);
        void OnDisable() => s_active.Remove(this);

        void OnDrawGizmos()
        {
            Gizmos.color = new Color(0.9f, 0.2f, 0.1f);
            var start = transform.position;
            var previous = start;
            for (int i = 1; i <= 12; i++)
            {
                float x = start.x + length * i / 12f;
                var point = new Vector3(x, start.y + HeightAt(x), start.z);
                Gizmos.DrawLine(previous, point);
                previous = point;
            }
        }
    }
}
