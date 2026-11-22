using ChickenRunner.Core;
using NUnit.Framework;

namespace ChickenRunner.Tests
{
    public class KidSpeedModelTests
    {
        const float Step = 1f / 120f;

        static float DistanceOver(KidSpeedModel model, float seconds)
        {
            float distance = 0f;
            int steps = (int)System.Math.Round(seconds / Step);
            for (int i = 0; i < steps; i++)
            {
                distance += model.Speed * Step;
                model.Tick(Step);
            }
            return distance;
        }

        [Test]
        public void CleanRunIsTheZoneSpeed()
        {
            var model = new KidSpeedModel(ChaseTuning.ForZone(1));
            Assert.That(DistanceOver(model, 2f), Is.EqualTo(12f).Within(0.05f));
        }

        [Test]
        public void AStumbleCostsTwoToThreeMetres()
        {
            var t = ChaseTuning.ForZone(1);
            var model = new KidSpeedModel(t);
            model.ApplyStumble();
            float lost = 2f * t.kidRunSpeed - DistanceOver(model, 2f);
            Assert.That(lost, Is.InRange(2f, 3f));
            Assert.That(lost, Is.EqualTo(KidSpeedModel.DistanceLost(t.kidRunSpeed, t.stumbleSpeedFactor, t.stumbleDuration)).Within(0.05f));
        }

        [Test]
        public void AChilliGainsAboutFiveMetres()
        {
            var t = ChaseTuning.ForZone(1);
            var model = new KidSpeedModel(t);
            model.StartBoost();
            float gained = DistanceOver(model, 3f) - 3f * t.kidRunSpeed;
            Assert.That(gained, Is.InRange(4f, 5.5f));
        }

        [Test]
        public void OverlappingStumblesDoNotStack()
        {
            var t = ChaseTuning.ForZone(1);
            var once = new KidSpeedModel(t);
            once.ApplyStumble();
            var twice = new KidSpeedModel(t);
            twice.ApplyStumble();
            twice.Tick(0.1f);
            twice.ApplyStumble();
            Assert.That(twice.Multiplier, Is.EqualTo(once.Multiplier));
        }

        [Test]
        public void AChilliStillHelpsDuringAStumble()
        {
            var t = ChaseTuning.ForZone(1);
            var model = new KidSpeedModel(t);
            model.ApplyStumble();
            float stumbling = model.Speed;
            model.StartBoost();
            Assert.That(model.Speed, Is.GreaterThan(stumbling));
        }

        [Test]
        public void PenaltyWearsOff()
        {
            var t = ChaseTuning.ForZone(1);
            var model = new KidSpeedModel(t);
            model.ApplyStumble();
            Assert.That(model.IsPenalised, Is.True);
            model.Tick(t.stumbleDuration + Step);
            Assert.That(model.IsPenalised, Is.False);
            Assert.That(model.Speed, Is.EqualTo(t.kidRunSpeed));
        }
    }
}
