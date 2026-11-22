using System.Collections.Generic;
using ChickenRunner.Core;
using NUnit.Framework;

namespace ChickenRunner.Tests
{
    public class GestureRecognizerTests
    {
        const float Frame = 1f / 60f;

        GestureRecognizer _g;
        List<GestureEvent> _events;
        float _time;

        [SetUp]
        public void SetUp()
        {
            _g = new GestureRecognizer { CommitTime = 0.06f, SwipeThreshold = 0.05f, LateSwipeWindow = 0.2f };
            _events = new List<GestureEvent>();
            _time = 0f;
        }

        void Feed(bool down, float x, float y, int frames = 1)
        {
            for (int i = 0; i < frames; i++)
            {
                _g.Process(down, x, y, _time, _events);
                _time += Frame;
            }
        }

        [Test]
        public void QuickTapIsAJumpPressAndRelease()
        {
            Feed(true, 1f, 0.5f, 2);
            Feed(false, 1f, 0.5f);
            Assert.That(_events, Is.EqualTo(new[] { GestureEvent.JumpPress, GestureEvent.JumpRelease }));
        }

        [Test]
        public void HoldJumpsAtCommitTimeAndReleasesOnLift()
        {
            Feed(true, 1f, 0.5f, 3);
            Assert.That(_events, Is.Empty, "still waiting to see if it is a swipe");
            Feed(true, 1f, 0.5f, 2);
            Assert.That(_events, Is.EqualTo(new[] { GestureEvent.JumpPress }));
            Assert.That(_g.IsHolding, Is.True);
            Feed(true, 1f, 0.5f, 20);
            Feed(false, 1f, 0.5f);
            Assert.That(_events, Is.EqualTo(new[] { GestureEvent.JumpPress, GestureEvent.JumpRelease }));
        }

        [Test]
        public void SwipeDownSlidesWithoutJumping()
        {
            Feed(true, 1f, 0.5f);
            Feed(true, 1f, 0.42f);
            Feed(true, 1f, 0.3f, 5);
            Feed(false, 1f, 0.3f);
            Assert.That(_events, Is.EqualTo(new[] { GestureEvent.SwipeDown }));
        }

        [Test]
        public void FlickDownInASingleFrameStillSlides()
        {
            Feed(true, 1f, 0.5f);
            Feed(false, 1f, 0.4f);
            Assert.That(_events, Is.EqualTo(new[] { GestureEvent.SwipeDown }));
        }

        [Test]
        public void SwipeUpIsAHeldJump()
        {
            Feed(true, 1f, 0.5f);
            Feed(true, 1f, 0.6f, 4);
            Assert.That(_events, Is.EqualTo(new[] { GestureEvent.SwipeUp, GestureEvent.JumpPress }));
            Assert.That(_g.IsHolding, Is.True);
        }

        [Test]
        public void LateSwipeDownAfterTheJumpBecomesADrop()
        {
            Feed(true, 1f, 0.5f, 5);
            Assert.That(_events, Is.EqualTo(new[] { GestureEvent.JumpPress }));
            Feed(true, 1f, 0.4f);
            Assert.That(_events, Is.EqualTo(new[] { GestureEvent.JumpPress, GestureEvent.JumpRelease, GestureEvent.SwipeDown }));
            Feed(false, 1f, 0.4f);
            Assert.That(_events.Count, Is.EqualTo(3), "no second release");
        }

        [Test]
        public void SidewaysDriftIsStillATap()
        {
            Feed(true, 1f, 0.5f);
            Feed(true, 1.08f, 0.51f);
            Feed(false, 1.08f, 0.51f);
            Assert.That(_events, Is.EqualTo(new[] { GestureEvent.JumpPress, GestureEvent.JumpRelease }));
        }

        [Test]
        public void CancelSwallowsTheRestOfTheTouch()
        {
            Feed(true, 1f, 0.5f, 5);
            _g.Cancel();
            Assert.That(_g.IsHolding, Is.False);
            Feed(true, 1f, 0.5f, 5);
            Feed(false, 1f, 0.5f);
            Assert.That(_events, Is.EqualTo(new[] { GestureEvent.JumpPress }));
        }
    }
}
