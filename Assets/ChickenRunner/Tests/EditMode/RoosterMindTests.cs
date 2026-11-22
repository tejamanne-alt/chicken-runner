using ChickenRunner.Core;
using NUnit.Framework;

namespace ChickenRunner.Tests
{
    public class RoosterMindTests
    {
        const float Step = 1f / 120f;

        static RoosterMind NewMind(ChaseTuning t)
        {
            var mind = new RoosterMind(t);
            mind.Reset();
            return mind;
        }

        [Test]
        public void RunsAboutEightPercentSlowerThanTheKid()
        {
            foreach (int zone in new[] { 1, 2, 3 })
            {
                var t = ChaseTuning.ForZone(zone);
                Assert.That(1f - t.roosterRunSpeed / t.kidRunSpeed, Is.InRange(0.06f, 0.1f), "zone " + zone);
                Assert.That(NewMind(t).Tick(Step, 10f), Is.EqualTo(t.roosterRunSpeed));
            }
        }

        [Test]
        public void TauntsBeyondEighteenMetresThenRunsAgain()
        {
            var t = ChaseTuning.ForZone(1);
            var mind = NewMind(t);
            Assert.That(mind.Tick(Step, 18.5f), Is.EqualTo(0f));
            Assert.That(mind.Mood, Is.EqualTo(RoosterMood.Taunting));
            Assert.That(mind.MoodChangedThisTick, Is.True);

            float elapsed = Step;
            while (mind.Mood == RoosterMood.Taunting && elapsed < 10f)
            {
                mind.Tick(Step, 18.5f);
                elapsed += Step;
            }
            Assert.That(elapsed, Is.EqualTo(t.tauntDuration).Within(2f * Step));
            Assert.That(mind.Mood, Is.EqualTo(RoosterMood.Running));

            // The cooldown stops him taunting again straight away.
            mind.Tick(Step, 18.5f);
            Assert.That(mind.Mood, Is.EqualTo(RoosterMood.Running));
        }

        [Test]
        public void PanicsWhenTheKidGetsClose()
        {
            var t = ChaseTuning.ForZone(1);
            var mind = NewMind(t);
            Assert.That(mind.Tick(Step, 1.5f), Is.GreaterThan(t.kidRunSpeed));
            Assert.That(mind.Mood, Is.EqualTo(RoosterMood.Panicking));
            Assert.That(mind.PanicBursts, Is.EqualTo(1));
        }

        [Test]
        public void PanicBurstsAreLimited()
        {
            var t = ChaseTuning.ForZone(1);
            var mind = NewMind(t);
            for (float time = 0f; time < 60f; time += Step) mind.Tick(Step, 1.5f);
            Assert.That(mind.PanicBursts, Is.EqualTo(t.maxPanicBursts));
            Assert.That(mind.Mood, Is.EqualTo(RoosterMood.Running));
        }

        [Test]
        public void UnlimitedPanicWhenMaxIsNegative()
        {
            var t = ChaseTuning.ForZone(1);
            t.maxPanicBursts = -1;
            var mind = NewMind(t);
            for (float time = 0f; time < 30f; time += Step) mind.Tick(Step, 1.5f);
            Assert.That(mind.PanicBursts, Is.GreaterThan(3));
        }
    }
}
