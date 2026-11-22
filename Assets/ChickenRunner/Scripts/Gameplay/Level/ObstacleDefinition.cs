using UnityEngine;

namespace ChickenRunner
{
    public enum PenaltyKind
    {
        Stumble,
        Slip,
        Tangle,
    }

    public enum HitReaction
    {
        None,
        /// <summary>Pots smash into shards.</summary>
        Smash,
        /// <summary>A sleeping dog jumps up and barks.</summary>
        Wake,
        /// <summary>Sarees or ropes wobble.</summary>
        Wobble,
        /// <summary>Dung or mud splats.</summary>
        Splat,
    }

    /// <summary>What hitting one kind of obstacle does: the penalty, the reaction and (later) the sound.</summary>
    [CreateAssetMenu(menuName = "Chicken Runner/Obstacle Definition", fileName = "Obstacle_", order = 2)]
    public sealed class ObstacleDefinition : ScriptableObject
    {
        [SerializeField] internal string displayName = "Obstacle";
        [SerializeField] internal PenaltyKind penalty = PenaltyKind.Stumble;

        [Tooltip("Multiplies the zone's stumble duration, so a slip can last a little longer than a stumble.")]
        [SerializeField, Range(0.25f, 3f)] internal float durationScale = 1f;

        [SerializeField] internal HitReaction reaction = HitReaction.Smash;
        [SerializeField] internal Color reactionColor = new Color(0.75f, 0.35f, 0.2f);

        [Tooltip("Grey-box stand-in for the sound effect: a word that pops up where the hit happened.")]
        [SerializeField] internal string bark = "SMASH!";

        public string DisplayName => displayName;
        public PenaltyKind Penalty => penalty;
        public float DurationScale => durationScale;
        public HitReaction Reaction => reaction;
        public Color ReactionColor => reactionColor;
        public string Bark => bark;
    }
}
