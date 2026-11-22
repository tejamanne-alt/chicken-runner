using ChickenRunner.Core;
using NUnit.Framework;

namespace ChickenRunner.Tests
{
    /// <summary>The doc's session-length promises, checked against the tuning tables with no level geometry.</summary>
    public class ChaseForecastTests
    {
        [TestCase(1)]
        [TestCase(2)]
        [TestCase(3)]
        public void CleanRunCatchesTheRoosterInAboutThirtySeconds(int zone)
        {
            var t = ChaseTuning.ForZone(zone);
            var run = ChaseForecast.Run(t, t.startGapNoBasket);
            Assert.That(run.outcome, Is.EqualTo(ChaseOutcome.Caught));
            Assert.That(run.time, Is.InRange(20f, 40f));
            Assert.That(run.panicBursts, Is.EqualTo(t.maxPanicBursts), "the last metres should be tense");
        }

        [Test]
        public void SmoothBasketLiftCatchesSoonerThanAClumsyOne()
        {
            var t = ChaseTuning.ForZone(1);
            var smooth = ChaseForecast.Run(t, t.startGapSmoothLift);
            var clumsy = ChaseForecast.Run(t, t.startGapClumsyLift);
            Assert.That(smooth.outcome, Is.EqualTo(ChaseOutcome.Caught));
            Assert.That(clumsy.outcome, Is.EqualTo(ChaseOutcome.Caught));
            Assert.That(smooth.time, Is.LessThan(clumsy.time));
        }

        [Test]
        public void AMessyRunLastsUpToNinetySecondsAndLoses()
        {
            var t = ChaseTuning.ForZone(1);
            var messy = ChaseForecast.RunWithMistakeEvery(t, t.startGapNoBasket, 3f);
            Assert.That(messy.outcome, Is.EqualTo(ChaseOutcome.EscapedCourseEnd));
            Assert.That(messy.time, Is.InRange(80f, 95f));
        }

        [Test]
        public void AFewMistakesStillWin()
        {
            var t = ChaseTuning.ForZone(1);
            var run = ChaseForecast.Run(t, t.startGapNoBasket, new[] { 3f, 9f, 15f });
            Assert.That(run.outcome, Is.EqualTo(ChaseOutcome.Caught));
            Assert.That(run.stumbles, Is.EqualTo(3));
        }

        [Test]
        public void TauntRescuesAStrugglingPlayer()
        {
            // A long run of mistakes early pushes the gap past 18 m; the taunt brings it back.
            var t = ChaseTuning.ForZone(1);
            var times = new float[8];
            for (int i = 0; i < times.Length; i++) times[i] = 1f + i * 0.75f;
            var run = ChaseForecast.Run(t, t.startGapNoBasket, times);
            Assert.That(run.taunts, Is.GreaterThan(0));
            Assert.That(run.outcome, Is.EqualTo(ChaseOutcome.Caught));
        }

        [Test]
        public void ChilliShortensTheChase()
        {
            var t = ChaseTuning.ForZone(1);
            var plain = ChaseForecast.Run(t, t.startGapNoBasket);
            var boosted = ChaseForecast.Run(t, t.startGapNoBasket, null, new[] { 2f });
            Assert.That(boosted.time, Is.LessThan(plain.time));
        }

        [Test]
        public void TightestSurvivableMistakeRateIsFound()
        {
            var t = ChaseTuning.ForZone(1);
            float interval = ChaseForecast.TightestSurvivableMistakeInterval(t, t.startGapNoBasket);
            Assert.That(interval, Is.InRange(3f, 15f));
            Assert.That(ChaseForecast.RunWithMistakeEvery(t, t.startGapNoBasket, interval, 2f, 1f / 60f).outcome,
                Is.EqualTo(ChaseOutcome.Caught));
        }
    }
}
