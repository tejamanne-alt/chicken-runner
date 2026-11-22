using UnityEngine;

namespace ChickenRunner
{
    /// <summary>Anything inside a chunk that changes during play and must be put back when the chunk is pooled.</summary>
    public interface IChunkPart
    {
        void ResetPart();
    }

    /// <summary>
    /// A hand-built stretch of course, 12 to 20 m long. Its origin is the start of the stretch and it runs along +X.
    /// Holds ground colliders, obstacles, pickups and the rooster's route markers as children.
    /// </summary>
    public sealed class Chunk : MonoBehaviour
    {
        [SerializeField, Min(1f)] internal float length = 16f;

        IChunkPart[] _parts;
        Pickup[] _pickups;

        public float Length => length;
        public float StartX => transform.position.x;
        public float EndX => transform.position.x + length;

        void Awake() => CacheParts();

        void CacheParts()
        {
            if (_parts != null) return;
            _parts = GetComponentsInChildren<IChunkPart>(true);
            _pickups = GetComponentsInChildren<Pickup>(true);
        }

        public void ResetChunk()
        {
            CacheParts();
            foreach (var part in _parts) part.ResetPart();
        }

        /// <summary>Mangoes in this chunk whose position is behind <paramref name="x"/>, for the mango star.</summary>
        public int CountMangoesBefore(float x)
        {
            CacheParts();
            int count = 0;
            foreach (var pickup in _pickups)
            {
                if (pickup.Kind == PickupKind.Mango && pickup.transform.position.x < x) count++;
            }
            return count;
        }

        void OnDrawGizmos()
        {
            var start = transform.position;
            Gizmos.color = new Color(1f, 0.6f, 0.1f, 0.8f);
            Gizmos.DrawLine(start, start + Vector3.up * 3f);
            Gizmos.DrawLine(start + Vector3.right * length, start + Vector3.right * length + Vector3.up * 3f);
            Gizmos.DrawLine(start + Vector3.up * 3f, start + Vector3.right * length + Vector3.up * 3f);
        }
    }
}
