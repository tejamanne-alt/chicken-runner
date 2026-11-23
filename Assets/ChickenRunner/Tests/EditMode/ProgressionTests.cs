using System;
using ChickenRunner.Core;
using NUnit.Framework;

namespace ChickenRunner.Tests
{
    public class ProgressionTests
    {
        static StarResult Stars(bool grab, bool mangoes = false, bool clean = false) =>
            new StarResult { grab = grab, mangoes = mangoes, clean = clean };

        static readonly StarResult One = Stars(true);
        static readonly StarResult Three = Stars(true, true, true);
        static readonly StarResult Lost = default;

        [TestCase(0, 1)]
        [TestCase(2, 1)]
        [TestCase(3, 2)]
        [TestCase(8, 3)]
        public void ThreeLevelsToAZone(int level, int zone)
        {
            Assert.That(StoryMap.ZoneOf(level), Is.EqualTo(zone));
        }

        [Test]
        public void ANewGameHasOnlyTheFirstLevelOpen()
        {
            var p = new Progress();
            Assert.That(p.IsLevelOpen(0), Is.True);
            for (int i = 1; i < StoryMap.LevelCount; i++) Assert.That(p.IsLevelOpen(i), Is.False, "level " + i);
            Assert.That(p.TotalStars, Is.Zero);
            Assert.That(p.IsZoneOpen(1), Is.True);
            Assert.That(p.IsZoneOpen(2), Is.False);
        }

        [Test]
        public void WinningALevelOpensTheNextOne()
        {
            var p = new Progress();
            var report = p.Record(0, One, 12);
            Assert.That(report.firstWin, Is.True);
            Assert.That(report.nextLevel, Is.EqualTo(1));
            Assert.That(p.IsLevelOpen(1), Is.True);
            Assert.That(p.IsLevelOpen(2), Is.False);
        }

        [Test]
        public void ALossBanksMangoesButEarnsNoStarsAndOpensNothing()
        {
            var p = new Progress();
            var report = p.Record(0, Lost, 9);
            Assert.That(report.newStars, Is.Zero);
            Assert.That(report.firstWin, Is.False);
            Assert.That(report.nextLevel, Is.EqualTo(-1));
            Assert.That(p.Mangoes, Is.EqualTo(9));
            Assert.That(p.IsLevelOpen(1), Is.False);
        }

        [Test]
        public void StarsAreKeptStarByStarAcrossRuns()
        {
            var p = new Progress();
            Assert.That(p.Record(0, Stars(true, mangoes: true), 10).newStars, Is.EqualTo(2));
            Assert.That(p.Record(0, Stars(true, clean: true), 3).newStars, Is.EqualTo(1));
            Assert.That(p.Record(0, Three, 10).newStars, Is.Zero);
            Assert.That(p.StarCount(0), Is.EqualTo(3));
            Assert.That(p.Record(0, One, 1).firstWin, Is.False);
            Assert.That(p.Data.bestMangoes[0], Is.EqualTo(10));
        }

        [Test]
        public void TheFieldsOpenAtFiveOfTheLanesNineStars()
        {
            var p = new Progress();
            p.Record(0, One, 0);
            p.Record(1, One, 0);
            p.Record(2, One, 0);
            Assert.That(p.IsZoneOpen(2), Is.False, "3 stars");
            Assert.That(p.IsLevelOpen(3), Is.False);

            p.Record(0, Stars(true, true), 0);
            Assert.That(p.IsZoneOpen(2), Is.False, "4 stars");
            var report = p.Record(1, Stars(true, clean: true), 0);
            Assert.That(report.zoneOpened, Is.EqualTo(2), "5 stars");
            Assert.That(p.IsLevelOpen(3), Is.True);
        }

        [Test]
        public void AZoneNeedsItsFirstLevelsPredecessorWonToo()
        {
            var p = new Progress();
            p.Record(0, Three, 0);
            p.Record(1, Three, 0);
            Assert.That(p.IsZoneOpen(2), Is.True, "6 stars");
            Assert.That(p.IsLevelOpen(3), Is.False, "level 3 of the lane is not won yet");
            Assert.That(p.Record(2, One, 0).nextLevel, Is.EqualTo(3));
        }

        [Test]
        public void TheTerracesOpenAtTwelveOfEighteen()
        {
            var p = new Progress();
            for (int i = 0; i < 3; i++) p.Record(i, Three, 0);  // 9
            p.Record(3, Stars(true, true), 0);                    // 11
            p.Record(4, Lost, 0);
            Assert.That(p.IsLevelOpen(5), Is.False);
            p.Record(4, One, 0);                                  // 12, but level 6 needs level 5 won first
            Assert.That(p.IsZoneOpen(3), Is.True);
            Assert.That(p.IsLevelOpen(6), Is.False);
            Assert.That(p.Record(5, One, 0).nextLevel, Is.EqualTo(6));
        }

        [Test]
        public void OnlyTheZonesBeforeCountTowardOpeningOne()
        {
            var p = new Progress();
            p.Data.stars[3] = 0b111;
            p.Data.stars[4] = 0b111;
            Assert.That(p.StarsBefore(2), Is.Zero);
            Assert.That(p.StarsBefore(3), Is.EqualTo(6));
        }

        [Test]
        public void EachFeatherCountsOnce()
        {
            var p = new Progress();
            Assert.That(p.Record(0, Lost, 0, 0b001).newFeathers, Is.EqualTo(1));
            Assert.That(p.Record(0, One, 0, 0b011).newFeathers, Is.EqualTo(1));
            Assert.That(p.Record(0, One, 0, 0b011).newFeathers, Is.Zero);
            Assert.That(p.FeathersFound(0), Is.EqualTo(2));
            Assert.That(p.TotalFeathers, Is.EqualTo(2));
        }

        [Test]
        public void TheMapPointsAtTheFirstOpenLevelNotYetWon()
        {
            var p = new Progress();
            Assert.That(p.SuggestedLevel(), Is.Zero);
            p.Record(0, One, 0);
            Assert.That(p.SuggestedLevel(), Is.EqualTo(1));
        }

        [Test]
        public void SpendingNeedsEnoughMangoes()
        {
            var p = new Progress();
            p.Record(0, Lost, 30);
            Assert.That(p.Spend(40), Is.False);
            Assert.That(p.Mangoes, Is.EqualTo(30));
            Assert.That(p.Spend(25), Is.True);
            Assert.That(p.Mangoes, Is.EqualTo(5));
        }

        [Test]
        public void ADamagedSaveIsRepaired()
        {
            var data = new SaveData { stars = new[] { 0b111, -3, 0b1111 }, bestMangoes = null, mangoes = -5, lastLevel = 40 };
            var p = new Progress(data);
            Assert.That(data.stars.Length, Is.EqualTo(StoryMap.LevelCount));
            Assert.That(data.bestMangoes.Length, Is.EqualTo(StoryMap.LevelCount));
            Assert.That(p.StarCount(0), Is.EqualTo(3));
            Assert.That(p.StarCount(1), Is.Zero);
            Assert.That(p.StarCount(2), Is.EqualTo(3), "unknown bits are dropped");
            Assert.That(p.Mangoes, Is.Zero);
            Assert.That(data.lastLevel, Is.Zero);
        }

        [Test]
        public void LevelsOutsideTheStoryAreRejected()
        {
            var p = new Progress();
            Assert.Throws<ArgumentOutOfRangeException>(() => p.Record(9, One, 0));
            Assert.Throws<ArgumentOutOfRangeException>(() => p.IsLevelOpen(-1));
        }
    }
}
