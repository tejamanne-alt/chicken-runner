using System.Collections.Generic;
using UnityEngine;

namespace ChickenRunner
{
    /// <summary>
    /// Fills the world around the lane with a zone's painted scenery for a course of any length: each of the
    /// <see cref="ZoneArt"/>'s tracks is repeated every track period, and only the copies near the camera are alive.
    /// Also moves a big ground plane along with the camera (its material tiles in world space, so it never shows a
    /// seam) and sets the camera's background colour. Cosmetic only: nothing here has colliders.
    /// </summary>
    public sealed class BackdropStreamer : MonoBehaviour
    {
        [SerializeField] internal Transform follow;
        [SerializeField] internal Camera targetCamera;
        [SerializeField] internal ZoneArt art;
        [Tooltip("A flat quad (any size): stretched under the scenery from the zone's groundFrom to groundTo.")]
        [SerializeField] internal MeshRenderer groundPlane;
        [SerializeField, Min(50f)] internal float groundWidth = 500f;

        readonly List<Dictionary<int, GameObject>> _live = new List<Dictionary<int, GameObject>>();
        readonly List<Stack<GameObject>> _pool = new List<Stack<GameObject>>();
        readonly List<Stack<GameObject>> _alternatePool = new List<Stack<GameObject>>();
        readonly List<int> _drop = new List<int>();
        ZoneArt _shown;

        public ZoneArt Shown => _shown;

        void Start()
        {
            if (art != null && _shown == null) Show(art);
        }

        /// <summary>Swaps to another zone's scenery; does nothing if it is already showing.</summary>
        public void Show(ZoneArt zoneArt)
        {
            if (zoneArt == null || zoneArt == _shown) return;
            Clear();
            _shown = art = zoneArt;
            foreach (var _ in zoneArt.Tracks)
            {
                _live.Add(new Dictionary<int, GameObject>());
                _pool.Add(new Stack<GameObject>());
                _alternatePool.Add(new Stack<GameObject>());
            }
            if (targetCamera != null)
            {
                targetCamera.clearFlags = CameraClearFlags.SolidColor;
                targetCamera.backgroundColor = zoneArt.Sky;
            }
            if (groundPlane != null)
            {
                groundPlane.gameObject.SetActive(zoneArt.Ground != null);
                if (zoneArt.Ground != null) groundPlane.sharedMaterial = zoneArt.Ground;
            }
            Refresh();
        }

        void Clear()
        {
            foreach (var live in _live)
            {
                foreach (var go in live.Values) Destroy(go);
            }
            foreach (var pool in _pool)
            {
                foreach (var go in pool) Destroy(go);
            }
            foreach (var pool in _alternatePool)
            {
                foreach (var go in pool) Destroy(go);
            }
            _live.Clear();
            _pool.Clear();
            _alternatePool.Clear();
            _shown = null;
        }

        void LateUpdate() => Refresh();

        static bool UsesAlternate(ZoneArt.Track track, int k) => track.alternate != null && (k & 1) != 0;

        Stack<GameObject> PoolFor(ZoneArt.Track track, int t, int k) => UsesAlternate(track, k) ? _alternatePool[t] : _pool[t];

        void Refresh()
        {
            if (_shown == null || follow == null) return;
            float x = follow.position.x;
            var tracks = _shown.Tracks;
            for (int t = 0; t < tracks.Length && t < _live.Count; t++)
            {
                var track = tracks[t];
                if (track?.prefab == null) continue;
                // Copy k covers [contentMin + k * period, contentMax + k * period].
                int first = Mathf.FloorToInt((x - track.reach - track.contentMax) / track.period);
                int last = Mathf.CeilToInt((x + track.reach - track.contentMin) / track.period);
                var live = _live[t];

                _drop.Clear();
                foreach (var k in live.Keys)
                {
                    if (k < first || k > last) _drop.Add(k);
                }
                foreach (var k in _drop)
                {
                    var go = live[k];
                    go.SetActive(false);
                    PoolFor(track, t, k).Push(go);
                    live.Remove(k);
                }

                for (int k = first; k <= last; k++)
                {
                    if (live.ContainsKey(k)) continue;
                    // Every other copy is the alternate arrangement, when the track has one.
                    var pool = PoolFor(track, t, k);
                    var prefab = UsesAlternate(track, k) ? track.alternate : track.prefab;
                    var go = pool.Count > 0 ? pool.Pop() : Instantiate(prefab, transform);
                    go.transform.localPosition = new Vector3(k * track.period, 0f, 0f);
                    go.SetActive(true);
                    live[k] = go;
                }
            }

            if (groundPlane != null && groundPlane.gameObject.activeSelf)
            {
                float depth = Mathf.Max(1f, _shown.GroundTo - _shown.GroundFrom);
                var ground = groundPlane.transform;
                ground.position = new Vector3(x, 0f, (_shown.GroundFrom + _shown.GroundTo) * 0.5f);
                ground.rotation = Quaternion.Euler(90f, 0f, 0f);
                ground.localScale = new Vector3(groundWidth, depth, 1f);
            }
        }
    }
}
