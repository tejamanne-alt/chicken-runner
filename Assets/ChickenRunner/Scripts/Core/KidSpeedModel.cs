using System;

namespace ChickenRunner.Core
{
    /// <summary>
    /// The kid's forward speed: base run speed, slowed by mistakes and lifted by chilli boosts.
    /// Mistakes and boosts multiply, so a chilli taken mid-stumble still helps.
    /// </summary>
    public sealed class KidSpeedModel
    {
        readonly ChaseTuning _tuning;
        float _penaltyTimer;
        float _penaltyFactor = 1f;
        float _boostTimer;

        public KidSpeedModel(ChaseTuning tuning)
        {
            _tuning = tuning ?? throw new ArgumentNullException(nameof(tuning));
        }

        public bool IsPenalised => _penaltyTimer > 0f;
        public bool IsBoosted => _boostTimer > 0f;

        public float Multiplier =>
            (IsPenalised ? _penaltyFactor : 1f) * (IsBoosted ? 1f + _tuning.boostSpeedBonus : 1f);

        public float Speed => _tuning.kidRunSpeed * Multiplier;

        public void Reset()
        {
            _penaltyTimer = 0f;
            _penaltyFactor = 1f;
            _boostTimer = 0f;
        }

        /// <summary>A stumble, slip or tangle. Overlapping penalties keep the harsher factor and the longer timer; they never stack.</summary>
        public void ApplyPenalty(float speedFactor, float duration)
        {
            if (IsPenalised)
            {
                _penaltyFactor = Math.Min(_penaltyFactor, speedFactor);
                _penaltyTimer = Math.Max(_penaltyTimer, duration);
            }
            else
            {
                _penaltyFactor = speedFactor;
                _penaltyTimer = duration;
            }
        }

        public void ApplyStumble(float durationScale = 1f) =>
            ApplyPenalty(_tuning.stumbleSpeedFactor, _tuning.stumbleDuration * durationScale);

        /// <summary>A chilli; a second one refreshes the timer rather than stacking speed.</summary>
        public void StartBoost() => _boostTimer = _tuning.boostDuration;

        public void Tick(float dt)
        {
            if (_penaltyTimer > 0f)
            {
                _penaltyTimer -= dt;
                if (_penaltyTimer <= 0f)
                {
                    _penaltyTimer = 0f;
                    _penaltyFactor = 1f;
                }
            }
            if (_boostTimer > 0f) _boostTimer = Math.Max(0f, _boostTimer - dt);
        }

        /// <summary>Metres a penalty costs against clean running at the given base speed.</summary>
        public static float DistanceLost(float baseSpeed, float speedFactor, float duration) =>
            baseSpeed * (1f - speedFactor) * duration;
    }
}
