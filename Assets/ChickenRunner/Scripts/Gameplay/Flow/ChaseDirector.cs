using System.Globalization;
using ChickenRunner.Core;
using UnityEngine;

namespace ChickenRunner
{
    /// <summary>
    /// Tracks the gap, decides win and loss, keeps the run's stats and stars, and exposes the numbers
    /// that drive music intensity and camera framing. The HUD only reads from here.
    /// </summary>
    public sealed class ChaseDirector : MonoBehaviour
    {
        static readonly Color s_lossColor = new Color(0.9f, 0.15f, 0.1f);
        static readonly Color s_gainColor = new Color(0.1f, 0.6f, 0.2f);

        KidController _kid;
        RoosterBrain _rooster;
        LevelStreamer _streamer;
        ChaseTuning _t;

        public ChaseTuning Tuning => _t;
        public float CourseLength { get; private set; }

        /// <summary>Metres from the kid to the rooster, centre to centre. The gap is the score.</summary>
        public float Gap => _rooster != null && _kid != null ? _rooster.X - _kid.X : 0f;

        public ChaseOutcome Outcome { get; private set; }
        public float Elapsed { get; private set; }
        public int Mangoes { get; private set; }
        public int MangoesPassed { get; private set; }
        public int Chillies { get; private set; }
        public int Feathers { get; private set; }
        public int Stumbles { get; private set; }
        public float MetresLost { get; private set; }
        public StarResult Stars { get; private set; }

        /// <summary>How far along the course the rooster is, 0 to 1. At 1 he escapes.</summary>
        public float RoosterProgress => CourseLength > 0f && _rooster != null ? Mathf.Clamp01(_rooster.X / CourseLength) : 0f;

        /// <summary>The gap the camera should keep in frame; beyond framingMaxGap the HUD shows an edge arrow.</summary>
        public float FramedGap => _t != null ? Mathf.Clamp(Gap, 0f, _t.framingMaxGap) : 0f;

        /// <summary>
        /// 0 to 1 for the music: the doc's two extra layers come in under 5 m and under 2 m.
        /// Nothing listens to it until the audio pass in milestone 3.
        /// </summary>
        public float Intensity
        {
            get
            {
                float gap = Gap;
                if (gap < 2f) return 1f;
                if (gap < 5f) return 0.66f;
                return 0.33f * Mathf.Clamp01(1f - (gap - 5f) / 20f);
            }
        }

        public void Init(LevelDefinition level, KidController kid, RoosterBrain rooster, LevelStreamer streamer)
        {
            if (_kid != null) Unsubscribe();
            _t = level.Tuning.Values;
            CourseLength = level.CourseLength;
            _kid = kid;
            _rooster = rooster;
            _streamer = streamer;
            _kid.HitObstacle += OnHit;
            _kid.Collected += OnCollected;
        }

        public void ResetChase()
        {
            Outcome = ChaseOutcome.Ongoing;
            Elapsed = 0f;
            Mangoes = 0;
            MangoesPassed = 0;
            Chillies = 0;
            Feathers = 0;
            Stumbles = 0;
            MetresLost = 0f;
            Stars = default;
        }

        public ChaseOutcome Tick(float dt)
        {
            if (Outcome != ChaseOutcome.Ongoing) return Outcome;
            Elapsed += dt;
            Outcome = ChaseRules.Evaluate(_t, Gap, _rooster.X, CourseLength, _kid.Position.y - _rooster.Position.y);
            return Outcome;
        }

        /// <summary>Locks in the stars once the chase has an outcome.</summary>
        public void Finish()
        {
            MangoesPassed = _streamer.CountMangoesPassed(_kid.X);
            Stars = ChaseRules.Stars(_t, Outcome, Mangoes, MangoesPassed, Stumbles);
        }

        void OnHit(Obstacle obstacle, float metresLost)
        {
            if (Outcome != ChaseOutcome.Ongoing) return;
            Stumbles++;
            MetresLost += metresLost;
            WorldBarks.Show("-" + metresLost.ToString("0.0", CultureInfo.InvariantCulture) + " m",
                _kid.transform.position + Vector3.up * 1.6f, s_lossColor);
        }

        void OnCollected(Pickup pickup)
        {
            switch (pickup.Kind)
            {
                case PickupKind.Mango:
                    Mangoes++;
                    break;
                case PickupKind.Chilli:
                    Chillies++;
                    float gain = _t.kidRunSpeed * _t.boostSpeedBonus * _t.boostDuration;
                    WorldBarks.Show("CHILLI! +" + gain.ToString("0", CultureInfo.InvariantCulture) + " m",
                        _kid.transform.position + Vector3.up * 1.6f, s_gainColor);
                    break;
                case PickupKind.Feather:
                    Feathers++;
                    break;
            }
        }

        void Unsubscribe()
        {
            _kid.HitObstacle -= OnHit;
            _kid.Collected -= OnCollected;
        }

        void OnDestroy()
        {
            if (_kid != null) Unsubscribe();
        }
    }
}
