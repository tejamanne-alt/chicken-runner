using ChickenRunner.Core;
using NUnit.Framework;

namespace ChickenRunner.Tests
{
    public class TuningReportTests
    {
        [Test]
        public void Zone1DocValuesFlagOnlyTheRoofHeight()
        {
            var report = TuningReport.Build(ChaseTuning.ForZone(1));
            Assert.That(report.Warnings.Count, Is.EqualTo(1), string.Join(" | ", report.Warnings));
            StringAssert.Contains("tallest roof", report.Warnings[0]);
        }

        [Test]
        public void Zone3DocValuesFlagOnlyTheRoofHeight()
        {
            // Stumble and chilli are checked in seconds of running, so they hold at the zone's pace as at any other.
            var report = TuningReport.Build(ChaseTuning.ForZone(3));
            Assert.That(report.Warnings.Count, Is.EqualTo(1), string.Join(" | ", report.Warnings));
            StringAssert.Contains("tallest roof", report.Warnings[0]);
        }

        [Test]
        public void AStumbleOutOfTheDocsRangeIsFlagged()
        {
            var t = ChaseTuning.ForZone(2);
            t.stumbleDuration = 2f;
            Assert.That(TuningReport.Build(t).Warnings, Has.Some.Contains("stumble costs"));
        }

        [Test]
        public void HigherDoubleJumpClearsTheRoofWarning()
        {
            var t = ChaseTuning.ForZone(1);
            t.doubleJumpTotalHeight = 2.85f;
            Assert.That(TuningReport.Build(t).Warnings, Is.Empty, string.Join(" | ", TuningReport.Build(t).Warnings));
        }

        [Test]
        public void FieldsZoneHasNoWarnings()
        {
            var report = TuningReport.Build(ChaseTuning.ForZone(2));
            Assert.That(report.Warnings, Is.Empty, string.Join(" | ", report.Warnings));
        }

        [Test]
        public void LowerRoofsClearTheWarning()
        {
            var t = ChaseTuning.ForZone(1);
            t.roofHeightMax = 2.35f;
            Assert.That(TuningReport.Build(t).Warnings, Is.Empty, string.Join(" | ", TuningReport.Build(t).Warnings));
        }

        [Test]
        public void ARoosterFasterThanTheKidIsFlagged()
        {
            var t = ChaseTuning.ForZone(1);
            t.roosterRunSpeed = 3.6f;
            var report = TuningReport.Build(t);
            Assert.That(report.Warnings, Has.Some.Contains("never catches"));
        }

        [Test]
        public void WidestCanalFitsADoubleJump()
        {
            var t = ChaseTuning.ForZone(2);
            Assert.That(TuningReport.DoubleJumpLength(t), Is.GreaterThan(2.6f));
            Assert.That(JumpMath.JumpLengthAt(t, t.kidRunSpeed), Is.LessThan(2.6f), "the widest canal should need the double jump");
        }
    }
}
