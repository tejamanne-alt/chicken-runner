using ChickenRunner.Core;
using NUnit.Framework;

namespace ChickenRunner.Tests
{
    /// <summary>Level 1's basket lift: a steady hold earns the short head start, a drop the long one.</summary>
    public class BasketLiftTests
    {
        const float Dt = 1f / 60f;
        const float LiftSeconds = 1.6f;
        const float DropRate = 2.5f;

        static float Hold(ref BasketLift lift, float seconds, bool held = true)
        {
            float t = 0f;
            for (; t < seconds && !lift.Done; t += Dt) lift.Step(held, Dt, LiftSeconds, DropRate);
            return t;
        }

        [Test]
        public void ASteadyHoldLiftsItInTheLiftTimeWithNoDrop()
        {
            var lift = new BasketLift();
            float took = Hold(ref lift, 5f);
            Assert.That(lift.Done, Is.True);
            Assert.That(took, Is.EqualTo(LiftSeconds).Within(2 * Dt));
            Assert.That(lift.Drops, Is.Zero);
            var t = ChaseTuning.ForZone(1);
            Assert.That(lift.Gap(t), Is.EqualTo(t.startGapSmoothLift));
        }

        [Test]
        public void LettingGoHalfWayIsADropAndTheBasketFallsBack()
        {
            var lift = new BasketLift();
            Hold(ref lift, 0.8f);
            Assert.That(lift.Lift, Is.InRange(0.45f, 0.55f));
            Assert.That(lift.Step(false, Dt, LiftSeconds, DropRate), Is.True, "the let-go frame reports the drop");
            Hold(ref lift, 0.5f, held: false);
            Assert.That(lift.Lift, Is.Zero);
            Assert.That(lift.Drops, Is.EqualTo(1));
            Hold(ref lift, 5f);
            var t = ChaseTuning.ForZone(1);
            Assert.That(lift.Done, Is.True);
            Assert.That(lift.Gap(t), Is.EqualTo(t.startGapClumsyLift));
        }

        [Test]
        public void AQuickTapBeforeTheRimLeavesTheGroundIsNotADrop()
        {
            var lift = new BasketLift();
            Hold(ref lift, 0.1f);
            Assert.That(lift.Lift, Is.LessThan(BasketLift.DropThreshold));
            Assert.That(lift.Step(false, Dt, LiftSeconds, DropRate), Is.False);
            Assert.That(lift.Drops, Is.Zero);
        }

        [Test]
        public void NotHoldingDoesNothingAndCountsNothing()
        {
            var lift = new BasketLift();
            Hold(ref lift, 2f, held: false);
            Assert.That(lift.Lift, Is.Zero);
            Assert.That(lift.Drops, Is.Zero);
        }

        [Test]
        public void ResetStartsOverAndAHeldPressCarriesIn()
        {
            var lift = new BasketLift();
            Hold(ref lift, 0.8f);
            lift.Step(false, Dt, LiftSeconds, DropRate);
            lift.Reset(heldNow: true);
            Assert.That(lift.Lift, Is.Zero);
            Assert.That(lift.Drops, Is.Zero);
            // The press carried in and released at once is below the threshold: still no drop.
            Assert.That(lift.Step(false, Dt, LiftSeconds, DropRate), Is.False);
        }

        [Test]
        public void TheSmoothHeadStartIsTheShorterOne()
        {
            var t = ChaseTuning.ForZone(1);
            Assert.That(t.startGapSmoothLift, Is.LessThan(t.startGapClumsyLift));
        }
    }
}
