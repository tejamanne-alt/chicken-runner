using System;

namespace ChickenRunner.Core
{
    /// <summary>
    /// Level 1's opening: the kid lifts the basket off the rooster while the player holds. Holding raises it steadily;
    /// letting go part way drops it back with a clunk, which is a drop. Fully up, the rooster bursts out with the
    /// short head start if it was never dropped, the long one if it was (<see cref="ChaseTuning.startGapSmoothLift"/>,
    /// <see cref="ChaseTuning.startGapClumsyLift"/>).
    /// </summary>
    public struct BasketLift
    {
        /// <summary>Below this much lift a let-go is a false start, not a drop: the rim had barely left the ground.</summary>
        public const float DropThreshold = 0.12f;

        public float Lift;
        public int Drops;
        bool _held;

        public bool Done => Lift >= 1f;

        /// <summary>The head start the lift has earned so far.</summary>
        public float Gap(ChaseTuning t) => Drops == 0 ? t.startGapSmoothLift : t.startGapClumsyLift;

        /// <summary>
        /// Advances by <paramref name="dt"/>: <paramref name="held"/> lifts at 1/<paramref name="liftSeconds"/> a
        /// second, not holding lowers at <paramref name="dropRate"/>. Returns true on the frame a hold is let go with
        /// the basket up (a drop).
        /// </summary>
        public bool Step(bool held, float dt, float liftSeconds, float dropRate)
        {
            if (Done) return false;
            bool dropped = false;
            if (held) Lift = Math.Min(1f, Lift + dt / Math.Max(0.1f, liftSeconds));
            else
            {
                if (_held && Lift > DropThreshold)
                {
                    Drops++;
                    dropped = true;
                }
                Lift = Math.Max(0f, Lift - dropRate * dt);
            }
            _held = held;
            return dropped;
        }

        /// <summary>Starts a new lift; <paramref name="heldNow"/> is whether the press that began it is still down.</summary>
        public void Reset(bool heldNow = false)
        {
            Lift = 0f;
            Drops = 0;
            _held = heldNow;
        }
    }
}
