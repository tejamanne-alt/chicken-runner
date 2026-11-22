using ChickenRunner.Core;
using NUnit.Framework;

namespace ChickenRunner.Tests
{
    public class JumpMathTests
    {
        static ChaseTuning Zone1 => ChaseTuning.ForZone(1);

        [Test]
        public void FullJumpIsAsHighAndLongAsTheDocSays()
        {
            var t = Zone1;
            float g = JumpMath.Gravity(t);
            float v = JumpMath.JumpVelocity(t);
            Assert.That(v * v / (2f * g), Is.EqualTo(1.4f).Within(1e-3f), "apex height");
            Assert.That(JumpMath.JumpLengthAt(t, 6f), Is.EqualTo(3.7f).Within(1e-3f), "length at zone 1 speed");
        }

        [Test]
        public void JumpGetsLongerAtFasterZoneSpeeds()
        {
            var t = Zone1;
            Assert.That(JumpMath.JumpLengthAt(t, 7f), Is.EqualTo(3.7f * 7f / 6f).Within(1e-3f));
            Assert.That(JumpMath.JumpLengthAt(t, 8f), Is.GreaterThan(JumpMath.JumpLengthAt(t, 7f)));
        }

        [Test]
        public void DoubleJumpAtTheApexReachesTheDocHeight()
        {
            var t = Zone1;
            float g = JumpMath.Gravity(t);
            float v2 = JumpMath.DoubleJumpVelocity(t);
            float apex = t.jumpHeight + v2 * v2 / (2f * g);
            Assert.That(apex, Is.EqualTo(2.6f).Within(1e-3f));
        }

        [Test]
        public void InstantReleaseGivesTheTapHeight()
        {
            var t = Zone1;
            float g = JumpMath.Gravity(t) * JumpMath.LowJumpGravityMultiplier(t);
            float v = JumpMath.JumpVelocity(t);
            Assert.That(v * v / (2f * g), Is.EqualTo(t.tapJumpHeight).Within(1e-3f));
        }

        [Test]
        public void CotBounceReachesItsHeight()
        {
            var t = Zone1;
            float v = JumpMath.BounceVelocity(t);
            Assert.That(v * v / (2f * JumpMath.Gravity(t)), Is.EqualTo(t.cotBounceHeight).Within(1e-3f));
        }

        [Test]
        public void TapJumpClearsAPotStack()
        {
            // Grey-box pot stacks are 0.6 m tall.
            Assert.That(Zone1.tapJumpHeight, Is.GreaterThan(0.6f));
        }

        [Test]
        public void DoubleJumpWindowShrinksToNothingAtTheApex()
        {
            var t = Zone1;
            Assert.That(JumpMath.DoubleJumpWindowFor(t, 2.2f), Is.GreaterThan(0.3f));
            Assert.That(JumpMath.DoubleJumpWindowFor(t, 2.6f), Is.EqualTo(0f));
        }
    }
}
