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
            Assert.That(live.kidRunSpeed, Is.EqualTo(7f));
            Assert.That(live.maxPanicBursts, Is.EqualTo(2));
            Assert.That(live.canalWidths, Is.EqualTo(new[] { 2.5f, 3.5f, 4.5f }));
        }

        [Test]
        public void CopyFromDoesNotShareTheCanalArray()
        {
            var source = ChaseTuning.ForZone(2);
            var target = ChaseTuning.ForZone(1);
            target.CopyFrom(source);
            target.canalWidths[0] = 9f;
            Assert.That(source.canalWidths[0], Is.EqualTo(2.5f));
        }

        [Test]
        public void ZoneSpeedsMatchTheDoc()
        {
            Assert.That(ChaseTuning.ForZone(1).kidRunSpeed, Is.EqualTo(6f));
            Assert.That(ChaseTuning.ForZone(2).roosterRunSpeed, Is.EqualTo(6.4f));
            Assert.That(ChaseTuning.ForZone(3).courseLength, Is.EqualTo(700f));
        }
    }
}
