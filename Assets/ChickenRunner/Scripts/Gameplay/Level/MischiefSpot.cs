using System.Collections.Generic;
using UnityEngine;

namespace ChickenRunner
{
    /// <summary>
    /// Where the rooster knocks something into the kid's path: when he runs past this point,
    /// the hidden <see cref="target"/> obstacle tumbles into the lane. It only fires if the kid is far enough
    /// behind to react, so mischief creates a fresh obstacle, never a cheap hit.
    /// </summary>
    public sealed class MischiefSpot : MonoBehaviour, IChunkPart
    {
        static readonly List<MischiefSpot> s_active = new List<MischiefSpot>();

        [SerializeField] internal Obstacle target;

        bool _used;

        public static IReadOnlyList<MischiefSpot> Active => s_active;
        public float X => transform.position.x;

        /// <summary>Called when the rooster passes. Returns true if the obstacle was knocked into the lane.</summary>
        public bool TryTrigger(float kidX, float minKidDistance)
        {
            if (_used || target == null) return false;
            _used = true;
            if (target.X - kidX < minKidDistance) return false;
            target.Reveal();
            return true;
        }

        public void ResetPart() => _used = false;

        void OnEnable() => s_active.Add(this);
        void OnDisable() => s_active.Remove(this);

        void OnDrawGizmos()
        {
            Gizmos.color = new Color(0.9f, 0.5f, 0.1f);
            Gizmos.DrawWireSphere(transform.position + Vector3.up * 0.3f, 0.3f);
            if (target != null) Gizmos.DrawLine(transform.position + Vector3.up * 0.3f, target.transform.position + Vector3.up * 0.3f);
        }
    }
}
