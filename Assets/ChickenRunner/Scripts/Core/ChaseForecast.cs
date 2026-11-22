using System;
using System.Collections.Generic;

namespace ChickenRunner.Core
{
    public struct ForecastResult
    {
        public ChaseOutcome outcome;
        public float time;
        public float kidDistance;
        public float roosterDistance;
        public int stumbles;
        public int taunts;
        public int panicBursts;
    }

    /// <summary>
    /// A one-dimensional run of the chase rules with no level geometry: how long a clean run takes,
    /// and how many mistakes a player can afford. Used by tests and by the TuningConfig inspector.
    /// </summary>
    public static class ChaseForecast
    {
        public const float DefaultStep = 1f / 120f;

        /// <summary>Simulates a run; the kid stumbles at each stumbleTimes entry and eats a chilli at each boostTimes entry (seconds from the start).</summary>
        public static ForecastResult Run(ChaseTuning t, float startGap, IList<float> stumbleTimes = null,
            IList<float> boostTimes = null, float dt = DefaultStep, float maxTime = 600f)
        {
            var stumbles = Sorted(stumbleTimes);
            var boosts = Sorted(boostTimes);
            var speed = new KidSpeedModel(t);
            var mind = new RoosterMind(t);
            mind.Reset();

            var result = new ForecastResult { roosterDistance = startGap };
            int nextStumble = 0, nextBoost = 0;
            float kid = 0f, rooster = startGap, time = 0f;

            while (time < maxTime)
            {
                while (nextStumble < stumbles.Count && stumbles[nextStumble] <= time)
                {
                    speed.ApplyStumble();
                    result.stumbles++;
                    nextStumble++;
                }
                while (nextBoost < boosts.Count && boosts[nextBoost] <= time)
                {
                    speed.StartBoost();
                    nextBoost++;
                }

                float gap = rooster - kid;
                var outcome = ChaseRules.Evaluate(t, gap, rooster, t.courseLength);
                if (outcome != ChaseOutcome.Ongoing)
                {
                    result.outcome = outcome;
                    break;
                }

                float kidSpeed = speed.Speed;
                float roosterSpeed = mind.Tick(dt, gap);
                kid += kidSpeed * dt;
                rooster += roosterSpeed * dt;
                speed.Tick(dt);
                time += dt;
            }

            result.time = time;
            result.kidDistance = kid;
            result.roosterDistance = rooster;
            result.taunts = mind.Taunts;
            result.panicBursts = mind.PanicBursts;
            return result;
        }

        /// <summary>A run where the kid makes one mistake every <paramref name="interval"/> seconds, starting at <paramref name="firstAt"/>.</summary>
        public static ForecastResult RunWithMistakeEvery(ChaseTuning t, float startGap, float interval, float firstAt = 2f,
            float dt = DefaultStep, float maxTime = 600f)
        {
            if (interval <= 0f) throw new ArgumentOutOfRangeException(nameof(interval));
            var times = new List<float>();
            for (float at = firstAt; at < maxTime; at += interval) times.Add(at);
            return Run(t, startGap, times, null, dt, maxTime);
        }

        /// <summary>
        /// The most frequent mistake rate (one every N seconds) that still ends in a catch, searched in 0.25 s steps.
        /// Returns float.PositiveInfinity when even a clean run fails.
        /// </summary>
        public static float TightestSurvivableMistakeInterval(ChaseTuning t, float startGap, float dt = 1f / 60f)
        {
            if (Run(t, startGap, null, null, dt).outcome != ChaseOutcome.Caught) return float.PositiveInfinity;
            for (float interval = 1f; interval <= 60f; interval += 0.25f)
            {
                if (RunWithMistakeEvery(t, startGap, interval, 2f, dt).outcome == ChaseOutcome.Caught) return interval;
            }
            return float.PositiveInfinity;
        }

        static List<float> Sorted(IList<float> times)
        {
            var list = times == null ? new List<float>() : new List<float>(times);
            list.Sort();
            return list;
        }
    }
}
