using System.Collections.Generic;
using UnityEngine;

namespace ChickenRunner
{
    /// <summary>
    /// A level is data: which zone tuning to use and the order of hand-built chunks.
    /// Designers reorder <see cref="chunks"/> without touching code.
    /// </summary>
    [CreateAssetMenu(menuName = "Chicken Runner/Level Definition", fileName = "Level_", order = 1)]
    public sealed class LevelDefinition : ScriptableObject
    {
        [SerializeField] internal string displayName = "Level";
        [Tooltip("One line for the village map, e.g. what the level teaches.")]
        [SerializeField] internal string subtitle = "";
        [SerializeField] internal TuningConfig tuning;
        [Tooltip("The zone's painted backdrop and ground. Empty keeps whatever is showing.")]
        [SerializeField] internal ZoneArt art;

        [Tooltip("Flat chunk the kid starts on; also used after the course end so the rooster has somewhere to run.")]
        [SerializeField] internal Chunk runwayChunk;

        [Tooltip("The course, in order. Laid end to end after the runway until the course length is covered.")]
        [SerializeField] internal List<Chunk> chunks = new List<Chunk>();

        [Tooltip("Repeat the chunk list until the course length is covered. Off: the course ends with the list.")]
        [SerializeField] internal bool loopChunks = true;

        [Tooltip("After the first pass through the list, repeat the chunks in a shuffled order (never the same chunk "
            + "twice in a row). The shuffle is seeded, so the course is the same on every retry and can be learnt.")]
        [SerializeField] internal bool shuffleRepeats = true;
        [SerializeField] internal int seed = 1;

        [Tooltip("Metres. Zero uses the zone's course length.")]
        [SerializeField, Min(0f)] internal float courseLengthOverride;

        public string DisplayName => displayName;
        public string Subtitle => subtitle;
        public TuningConfig Tuning => tuning;
        public ZoneArt Art => art;
        public bool ShuffleRepeats => shuffleRepeats;
        public int Seed => seed;
        public Chunk RunwayChunk => runwayChunk;
        public IReadOnlyList<Chunk> Chunks => chunks;
        public bool LoopChunks => loopChunks;

        public float CourseLength =>
            courseLengthOverride > 0f ? courseLengthOverride : (tuning != null ? tuning.Values.courseLength : 500f);

        /// <summary>Levels without the basket intro start with this gap (the basket arrives in milestone 2).</summary>
        public float StartGap => tuning != null ? tuning.Values.startGapNoBasket : 12f;
    }
}
