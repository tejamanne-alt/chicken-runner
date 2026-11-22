using System;

namespace ChickenRunner.Core
{
    public enum ChaseOutcome
    {
        Ongoing,
        /// <summary>The kid got inside grabDistance and dives.</summary>
        Caught,
        /// <summary>The gap passed escapeDistance.</summary>
        EscapedTooFar,
        /// <summary>The rooster reached the end of the course before the grab.</summary>
        EscapedCourseEnd,
    }

    public struct StarResult
    {
        public bool grab;
        public bool mangoes;
        public bool clean;

        public int Count => (grab ? 1 : 0) + (mangoes ? 1 : 0) + (clean ? 1 : 0);
    }

    /// <summary>Win, loss and stars. Positions are metres along the course; the kid starts at 0.</summary>
    public static class ChaseRules
    {
        /// <param name="heightDifference">Kid's height minus the rooster's; the grab waits until they are level.</param>
        public static ChaseOutcome Evaluate(ChaseTuning t, float gap, float roosterPosition, float courseLength,
            float heightDifference = 0f)
        {
            if (gap <= t.grabDistance && Math.Abs(heightDifference) <= t.grabHeightTolerance) return ChaseOutcome.Caught;
            if (gap > t.escapeDistance) return ChaseOutcome.EscapedTooFar;
            if (roosterPosition >= courseLength) return ChaseOutcome.EscapedCourseEnd;
            return ChaseOutcome.Ongoing;
        }

        public static bool IsEscape(ChaseOutcome outcome) =>
            outcome == ChaseOutcome.EscapedTooFar || outcome == ChaseOutcome.EscapedCourseEnd;

        /// <summary>
        /// One star for the grab, one for collecting at least mangoStarFraction of the mangoes the kid ran past,
        /// one for no stumbles. A lost level earns none.
        /// </summary>
        public static StarResult Stars(ChaseTuning t, ChaseOutcome outcome, int mangoesCollected, int mangoesPassed, int stumbles)
        {
            var result = new StarResult();
            if (outcome != ChaseOutcome.Caught) return result;
            result.grab = true;
            result.mangoes = mangoesPassed <= 0 || mangoesCollected >= t.mangoStarFraction * mangoesPassed;
            result.clean = stumbles == 0;
            return result;
        }
    }
}
