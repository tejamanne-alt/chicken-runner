using ChickenRunner.Core;
using NUnit.Framework;

namespace ChickenRunner.Tests
{
    public class ChaseTuningTests
    {
        [Test]
        public void CopyFromKeepsTheInstanceAndCopiesEveryValue()
        {
            var live = ChaseTuning.ForZone(1);
            var held = live;
            live.kidRunSpeed = 99f;
            live.maxPanicBursts = 7;
            live.canalWidths = new[] { 1f };

            live.CopyFrom(ChaseTuning.ForZone(2));

            Assert.That(held, Is.SameAs(live));
            Assert.That(live.kidRunSpeed, Is.EqualTo(3.5f));
            Assert.That(live.roosterRunSpeed, Is.EqualTo(3.15f));
            Assert.That(live.maxPanicBursts, Is.EqualTo(2));
            Assert.That(live.canalWidths, Is.EqualTo(new[] { 1.2f, 1.8f, 2.6f }));
        }

        [Test]
        public void CopyFromDoesNotShareTheCanalArray()
        {
            var source = ChaseTuning.ForZone(2);
            var target = ChaseTuning.ForZone(1);
            target.CopyFrom(source);
            target.canalWidths[0] = 9f;
            Assert.That(source.canalWidths[0], Is.EqualTo(1.2f));
        }

        [Test]
        public void ZoneSpeedsMatchTheDoc()
        {
            // Kick Off's pace for every zone: 3.5 m/s, a small child running hard.
            for (int zone = 1; zone <= 3; zone++) Assert.That(ChaseTuning.ForZone(zone).kidRunSpeed, Is.EqualTo(3.5f));
            Assert.That(ChaseTuning.ForZone(1).roosterRunSpeed, Is.EqualTo(3.2f));
            Assert.That(ChaseTuning.ForZone(2).roosterRunSpeed, Is.EqualTo(3.15f));
            Assert.That(ChaseTuning.ForZone(3).courseLength, Is.EqualTo(300f));
        }
    }
}
