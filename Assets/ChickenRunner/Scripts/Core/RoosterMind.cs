using System;

namespace ChickenRunner.Core
{
    public enum RoosterMood
    {
        /// <summary>Runs about 8% slower than the kid's clean pace, so good play always closes the gap.</summary>
        Running,
        /// <summary>More than tauntDistance ahead: stops, turns and crows. The rubber band.</summary>
        Taunting,
        /// <summary>The kid got within panicDistance: a short sprint that sheds feathers.</summary>
        Panicking,
    }

    /// <summary>
    /// Decides the rooster's speed from the gap. Pure logic: the Unity RoosterBrain moves him and plays the gags.
    /// </summary>
    public sealed class RoosterMind
    {
        readonly ChaseTuning _tuning;
        float _moodTimer;
        float _tauntCooldown;
        float _panicCooldown;

        public RoosterMind(ChaseTuning tuning)
        {
            _tuning = tuning ?? throw new ArgumentNullException(nameof(tuning));
        }

        public RoosterMood Mood { get; private set; }
        public int PanicBursts { get; private set; }
        public int Taunts { get; private set; }

        /// <summary>True only on the tick the mood changed, so the view can trigger a gag once.</summary>
        public bool MoodChangedThisTick { get; private set; }

        public float Speed
        {
            get
            {
                switch (Mood)
                {
                    case RoosterMood.Taunting: return 0f;
                    case RoosterMood.Panicking: return _tuning.roosterRunSpeed * _tuning.panicSpeedMultiplier;
                    default: return _tuning.roosterRunSpeed;
                }
            }
        }

        public void Reset()
        {
            Mood = RoosterMood.Running;
            _moodTimer = 0f;
            _tauntCooldown = 0f;
            _panicCooldown = 0f;
            PanicBursts = 0;
            Taunts = 0;
            MoodChangedThisTick = false;
        }

        /// <summary>Advances the mood by dt for the current gap and returns this tick's speed in m/s.</summary>
        /// <param name="canStartTaunt">False while he is mid-flutter, so he never stops to crow in mid-air.</param>
        public float Tick(float dt, float gap, bool canStartTaunt = true)
        {
            MoodChangedThisTick = false;
            _tauntCooldown = Math.Max(0f, _tauntCooldown - dt);
            _panicCooldown = Math.Max(0f, _panicCooldown - dt);

            switch (Mood)
            {
                case RoosterMood.Running:
                    if (gap > _tuning.tauntDistance && _tauntCooldown <= 0f && canStartTaunt)
                    {
                        Enter(RoosterMood.Taunting, _tuning.tauntDuration);
                        Taunts++;
                    }
                    else if (gap < _tuning.panicDistance && _panicCooldown <= 0f && PanicBurstsLeft)
                    {
                        Enter(RoosterMood.Panicking, _tuning.panicDuration);
                        PanicBursts++;
                    }
                    break;

                case RoosterMood.Taunting:
                    _moodTimer -= dt;
                    if (_moodTimer <= 0f)
                    {
                        _tauntCooldown = _tuning.tauntCooldown;
                        Enter(RoosterMood.Running, 0f);
                    }
                    break;

                case RoosterMood.Panicking:
                    _moodTimer -= dt;
                    if (_moodTimer <= 0f)
                    {
                        _panicCooldown = _tuning.panicCooldown;
                        Enter(RoosterMood.Running, 0f);
                    }
                    break;
            }
            return Speed;
        }

        bool PanicBurstsLeft => _tuning.maxPanicBursts < 0 || PanicBursts < _tuning.maxPanicBursts;

        void Enter(RoosterMood mood, float duration)
        {
            Mood = mood;
            _moodTimer = duration;
            MoodChangedThisTick = true;
        }
    }
}
