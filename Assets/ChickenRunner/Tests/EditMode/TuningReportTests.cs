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
        public void Zone3MistakesAndChilliesAreWorthMoreAtItsSpeed()
        {
            // Stumble and chilli are defined in seconds, so at 8 m/s they move more metres than the doc's figures.
            var report = TuningReport.Build(ChaseTuning.ForZone(3));
            Assert.That(report.Warnings.Count, Is.EqualTo(3), string.Join(" | ", report.Warnings));
            Assert.That(report.Warnings, Has.Some.Contains("stumble costs 3.08 m"));
            Assert.That(report.Warnings, Has.Some.Contains("chilli gains 6.16 m"));
            Assert.That(report.Warnings, Has.Some.Contains("tallest roof"));
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
            t.roosterRunSpeed = 6.2f;
            var report = TuningReport.Build(t);
            Assert.That(report.Warnings, Has.Some.Contains("never catches"));
        }

        [Test]
        public void WidestCanalFitsADoubleJump()
        {
            var t = ChaseTuning.ForZone(2);
            Assert.That(TuningReport.DoubleJumpLength(t), Is.GreaterThan(4.5f));
            Assert.That(JumpMath.JumpLengthAt(t, t.kidRunSpeed), Is.LessThan(4.5f), "the widest canal should need the double jump");
        }
    }
}
