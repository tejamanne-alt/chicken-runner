using System.Collections.Generic;
using UnityEngine;

namespace ChickenRunner
{
    /// <summary>
    /// Lays a level's chunks end to end along +X, spawns them ahead of the rooster and recycles them behind
    /// the kid through a pool, so a 500 m course only ever has a handful of chunks alive.
    /// </summary>
    public sealed class LevelStreamer : MonoBehaviour
    {
        [Tooltip("Spawn chunks until this far beyond whichever of kid and rooster is further ahead.")]
        [SerializeField] internal float spawnAhead = 45f;
        [Tooltip("Recycle a chunk once its end is this far behind the kid.")]
        [SerializeField] internal float recycleBehind = 12f;
        [Tooltip("Where the runway chunk starts, relative to the kid's start at 0.")]
        [SerializeField] internal float runwayStart = -10f;
        [Tooltip("Flat ground after the course end, so the rooster has somewhere to run off to.")]
        [SerializeField] internal float runoutLength = 40f;

        struct Placement
        {
            public Chunk prefab;
            public float x;
        }

        readonly List<Placement> _course = new List<Placement>();
        readonly List<Chunk> _active = new List<Chunk>();
        readonly Dictionary<Chunk, Chunk> _prefabOf = new Dictionary<Chunk, Chunk>();
        readonly Dictionary<Chunk, Stack<Chunk>> _pool = new Dictionary<Chunk, Stack<Chunk>>();
        LevelDefinition _level;
        int _next;
        int _recycledMangoes;

        public int ActiveChunkCount => _active.Count;
        public int PlacementCount => _course.Count;

        public void Init(LevelDefinition level)
        {
            _level = level;
            BuildCourse();
        }

        void BuildCourse()
        {
            _course.Clear();
            float x = runwayStart;
            var runway = _level.RunwayChunk;
            if (runway != null) x = Place(runway, x);

            float end = _level.CourseLength;
            var chunks = _level.Chunks;
            bool anyChunk = false;
            foreach (var c in chunks) anyChunk |= c != null;

            if (anyChunk)
            {
                var order = new List<Chunk>(chunks);
                var random = new System.Random(_level.Seed);
                Chunk previous = null;
                int i = 0;
                while (x < end)
                {
                    if (i >= order.Count)
                    {
                        if (!_level.LoopChunks) break;
                        i = 0;
                        if (_level.ShuffleRepeats) Shuffle(order, random, previous);
                    }
                    var chunk = order[i++];
                    if (chunk == null) continue;
                    x = Place(chunk, x);
                    previous = chunk;
                }
            }

            if (runway != null)
            {
                while (x < end + runoutLength) x = Place(runway, x);
            }
            else if (!anyChunk)
            {
                Debug.LogError($"{_level.name} has no runway and no chunks; there is nothing to run on.", _level);
            }
        }

        /// <summary>Fisher-Yates, then moves a repeat of <paramref name="previous"/> away from the front.</summary>
        static void Shuffle(List<Chunk> order, System.Random random, Chunk previous)
        {
            for (int k = order.Count - 1; k > 0; k--)
            {
                int j = random.Next(k + 1);
                (order[k], order[j]) = (order[j], order[k]);
            }
            if (order.Count > 1 && order[0] == previous)
            {
                int swap = 1 + random.Next(order.Count - 1);
                (order[0], order[swap]) = (order[swap], order[0]);
            }
        }

        float Place(Chunk prefab, float x)
        {
            _course.Add(new Placement { prefab = prefab, x = x });
            return x + prefab.Length;
        }

        /// <summary>Recycles every chunk and rewinds to the start of the course.</summary>
        public void ResetCourse()
        {
            foreach (var chunk in _active) Release(chunk);
            _active.Clear();
            _next = 0;
            _recycledMangoes = 0;
        }

        public void Refresh(float kidX, float roosterX)
        {
            bool changed = false;
            float aheadX = Mathf.Max(kidX, roosterX) + spawnAhead;
            while (_next < _course.Count && _course[_next].x < aheadX)
            {
                Spawn(_course[_next]);
                _next++;
                changed = true;
            }

            for (int i = _active.Count - 1; i >= 0; i--)
            {
                var chunk = _active[i];
                if (chunk.EndX >= kidX - recycleBehind) continue;
                _recycledMangoes += chunk.CountMangoesBefore(float.PositiveInfinity);
                Release(chunk);
                _active.RemoveAt(i);
                changed = true;
            }

            // Chunk colliders moved this frame; make sure this frame's raycasts see them where they are now.
            if (changed) Physics.SyncTransforms();
        }

        /// <summary>Mangoes the kid has run past (taken or not), for the mango star.</summary>
        public int CountMangoesPassed(float kidX)
        {
            int count = _recycledMangoes;
            foreach (var chunk in _active) count += chunk.CountMangoesBefore(kidX);
            return count;
        }

        void Spawn(Placement placement)
        {
            Chunk chunk;
            if (_pool.TryGetValue(placement.prefab, out var stack) && stack.Count > 0)
            {
                chunk = stack.Pop();
            }
            else
            {
                chunk = Instantiate(placement.prefab, transform);
                chunk.name = placement.prefab.name;
                _prefabOf[chunk] = placement.prefab;
            }
            chunk.transform.position = new Vector3(placement.x, 0f, 0f);
            chunk.ResetChunk();
            chunk.gameObject.SetActive(true);
            _active.Add(chunk);
        }

        void Release(Chunk chunk)
        {
            chunk.gameObject.SetActive(false);
            var prefab = _prefabOf[chunk];
            if (!_pool.TryGetValue(prefab, out var stack))
            {
                stack = new Stack<Chunk>();
                _pool[prefab] = stack;
            }
            stack.Push(chunk);
        }
    }
}
