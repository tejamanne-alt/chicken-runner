using System;
using System.Collections.Generic;

namespace ChickenRunner.Core
{
    public enum GestureEvent
    {
        JumpPress,
        JumpRelease,
        SwipeDown,
        SwipeUp,
    }

    /// <summary>
    /// One-thumb gestures from a single pointer: tap or hold anywhere to jump, swipe down to slide, swipe up to climb.
    ///
    /// A touch waits up to <see cref="CommitTime"/> before it becomes a jump, so a swipe down never starts with a jump.
    /// A downward swipe that arrives late (within <see cref="LateSwipeWindow"/> of the jump) still counts,
    /// which in the air becomes a fast drop. A swipe up also counts as a held jump, so with no ladder nearby it jumps.
    ///
    /// Coordinates are in screen heights (pixels / screen height), y up, so thresholds are the same on every phone.
    /// </summary>
    public sealed class GestureRecognizer
    {
        enum Phase { Idle, Pending, Holding, Consumed }

        public float CommitTime = 0.06f;
        public float SwipeThreshold = 0.05f;
        public float LateSwipeWindow = 0.2f;

        Phase _phase;
        bool _wasDown;
        float _startX, _startY, _startTime;
        float _holdStartY, _holdStartTime;
        bool _lateSwipeUsed;

        public bool IsHolding => _phase == Phase.Holding;

        public void Reset()
        {
            _phase = Phase.Idle;
            _wasDown = false;
            _lateSwipeUsed = false;
        }

        /// <summary>Feed the pointer state once per frame; recognised gestures are appended to <paramref name="output"/>.</summary>
        public void Process(bool isDown, float x, float y, float time, List<GestureEvent> output)
        {
            if (output == null) throw new ArgumentNullException(nameof(output));

            if (isDown && !_wasDown)
            {
                _phase = Phase.Pending;
                _startX = x;
                _startY = y;
                _startTime = time;
                _lateSwipeUsed = false;
            }

            if (isDown)
            {
                if (_phase == Phase.Pending) ResolvePending(x, y, time, false, output);
                else if (_phase == Phase.Holding) CheckLateSwipe(y, time, output);
            }
            else if (_wasDown)
            {
                if (_phase == Phase.Pending) ResolvePending(x, y, time, true, output);
                if (_phase == Phase.Holding) output.Add(GestureEvent.JumpRelease);
                _phase = Phase.Idle;
            }

            _wasDown = isDown;
        }

        /// <summary>Drop the current touch without emitting anything more (for example when the game pauses).</summary>
        public void Cancel()
        {
            if (_phase != Phase.Idle && _wasDown) _phase = Phase.Consumed;
        }

        void ResolvePending(float x, float y, float time, bool released, List<GestureEvent> output)
        {
            float dx = x - _startX;
            float dy = y - _startY;
            bool vertical = Math.Abs(dy) >= SwipeThreshold && Math.Abs(dy) >= Math.Abs(dx);

            if (vertical && dy < 0f)
            {
                output.Add(GestureEvent.SwipeDown);
                _phase = Phase.Consumed;
                return;
            }

            if (vertical)
            {
                output.Add(GestureEvent.SwipeUp);
                BeginHold(y, time, output);
            }
            else if (released || time - _startTime >= CommitTime || Math.Abs(dx) >= SwipeThreshold)
            {
                // A sideways drift is a sloppy tap, not a gesture of its own.
                BeginHold(y, time, output);
            }
        }

        void BeginHold(float y, float time, List<GestureEvent> output)
        {
            output.Add(GestureEvent.JumpPress);
            _phase = Phase.Holding;
            _holdStartY = y;
            _holdStartTime = time;
        }

        void CheckLateSwipe(float y, float time, List<GestureEvent> output)
        {
            if (_lateSwipeUsed || time - _holdStartTime > LateSwipeWindow) return;
            if (_holdStartY - y >= SwipeThreshold)
            {
                _lateSwipeUsed = true;
                output.Add(GestureEvent.JumpRelease);
                output.Add(GestureEvent.SwipeDown);
                _phase = Phase.Consumed;
            }
        }
    }
}
