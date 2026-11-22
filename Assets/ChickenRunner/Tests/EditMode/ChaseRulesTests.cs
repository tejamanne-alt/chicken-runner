using ChickenRunner.Core;
using NUnit.Framework;

namespace ChickenRunner.Tests
{
    public class ChaseRulesTests
    {
        static readonly ChaseTuning T = ChaseTuning.ForZone(1);

        [TestCase(0.8f, ChaseOutcome.Caught)]
        [TestCase(0.81f, ChaseOutcome.Ongoing)]
        [TestCase(25f, ChaseOutcome.Ongoing)]
        [TestCase(25.01f, ChaseOutcome.EscapedTooFar)]
        public void GapDecidesTheGrabAndTheEscape(float gap, ChaseOutcome expected)
        {
            Assert.That(ChaseRules.Evaluate(T, gap, 100f, 500f), Is.EqualTo(expected));
        }

        [Test]
        public void RoosterReachingTheCourseEndEscapes()
        {
            Assert.That(ChaseRules.Evaluate(T, 5f, 500f, 500f), Is.EqualTo(ChaseOutcome.EscapedCourseEnd));
        }

        [Test]
        public void AGrabAtTheFinishLineStillCounts()
        {
            Assert.That(ChaseRules.Evaluate(T, 0.5f, 500f, 500f), Is.EqualTo(ChaseOutcome.Caught));
        }

        [Test]
        public void ThreeStarsForACleanGreedyGrab()
        {
            var stars = ChaseRules.Stars(T, ChaseOutcome.Caught, 8, 10, 0);
            Assert.That(stars.Count, Is.EqualTo(3));
        }

        [Test]
        public void StarsNeedTheGrab()
        {
            Assert.That(ChaseRules.Stars(T, ChaseOutcome.EscapedCourseEnd, 10, 10, 0).Count, Is.EqualTo(0));
        }

        [Test]
        public void MangoStarNeedsMostOfTheMangoesPassed()
        {
            Assert.That(ChaseRules.Stars(T, ChaseOutcome.Caught, 6, 10, 0).mangoes, Is.False);
            Assert.That(ChaseRules.Stars(T, ChaseOutcome.Caught, 7, 10, 0).mangoes, Is.True);
        }

        [Test]
        public void OneStumbleLosesTheCleanStar()
        {
            var stars = ChaseRules.Stars(T, ChaseOutcome.Caught, 10, 10, 1);
            Assert.That(stars.clean, Is.False);
            Assert.That(stars.Count, Is.EqualTo(2));
        }
    }
}
